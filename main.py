import os
import sys
import subprocess
import threading
from datetime import datetime
from pathlib import Path

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from core.analysis_engine import AnalysisEngine
from core.exporter import DataExporter
from core.logger import AppLogger


class PhotoshootAutomationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Photoshoot Automation v2")
        self.root.geometry("900x650")
        self.root.minsize(900, 650)
        self.logger = AppLogger.get_logger("GUI")
        self.engine = AnalysisEngine()
        self.exporter = DataExporter()

        self.new_items_path = tk.StringVar()
        self.product_bible_path = tk.StringVar()
        self.tracker_path = tk.StringVar()
        self.uploaded_skus_path = tk.StringVar()
        self.current_difference_df = None
        self.stage1_output_path = None
        self.stage2_output_path = None
        self.report_window = None
        self.reports_frame = None

        self._build_ui()
        self._enable_drag_drop()

    def _build_ui(self):
        header = ttk.Frame(self.root, padding=15)
        header.pack(fill=tk.X)
        ttk.Label(header, text="Photoshoot Automation", font=("Segoe UI", 18, "bold")).pack(anchor=tk.W)
        ttk.Label(header, text="Drag & Drop or Browse Excel Files").pack(anchor=tk.W)
        ttk.Separator(self.root).pack(fill=tk.X, padx=10, pady=5)

        form = ttk.Frame(self.root, padding=15)
        form.pack(fill=tk.X)
        self._create_file_input(form, "New Items File (*)", self.new_items_path, 0)
        self._create_file_input(form, "Product Bible (*)", self.product_bible_path, 1)
        self._create_file_input(form, "Content Tracker (*)", self.tracker_path, 2)
        self._create_file_input(form, "Uploaded SKUs (Optional)", self.uploaded_skus_path, 3)

        buttons = ttk.Frame(self.root, padding=10)
        buttons.pack(fill=tk.X)
        self.stage1_btn = ttk.Button(buttons, text="1. Run Stage 1", command=self._run_stage_1)
        self.stage1_btn.pack(side=tk.LEFT, padx=5)
        self.stage2_btn = ttk.Button(buttons, text="2. Run Stage 2", command=self._run_stage_2, state=tk.DISABLED)
        self.stage2_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons, text="Clear", command=self._clear_all).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons, text="Reports", command=self._open_reports).pack(side=tk.RIGHT, padx=5)

        console = ttk.LabelFrame(self.root, text="Execution Logs", padding=10)
        console.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.log_text = tk.Text(console, wrap=tk.WORD, state=tk.DISABLED, height=12)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _create_file_input(self, parent, label_text, var, row):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W, pady=6)
        ttk.Entry(parent, textvariable=var, width=60).grid(row=row, column=1, padx=8, pady=6, sticky=tk.EW)
        ttk.Button(parent, text="Browse...", command=lambda: self._browse_file(var)).grid(row=row, column=2, pady=6)
        parent.columnconfigure(1, weight=1)

    def _browse_file(self, var):
        filename = filedialog.askopenfilename(filetypes=[("Excel/CSV Files", "*.xlsx *.xls *.csv"), ("All Files", "*.*")])
        if filename:
            var.set(filename)

    def _enable_drag_drop(self):
        try:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind("<<Drop>>", self._handle_drop)
        except Exception as exc:
            self.logger.warning(f"Drag-and-drop setup warning: {exc}")

    def _handle_drop(self, event):
        try:
            files = [Path(f) for f in self.root.tk.splitlist(event.data) if Path(f).is_file()]
            variables = [self.new_items_path, self.product_bible_path, self.tracker_path, self.uploaded_skus_path]
            for var in variables:
                if not var.get() and files:
                    var.set(str(files.pop(0)))
        except Exception as exc:
            self._log(f"[DROP ERROR] {exc}")

    def _clear_all(self):
        for var in (self.new_items_path, self.product_bible_path, self.tracker_path, self.uploaded_skus_path):
            var.set("")
        self.current_difference_df = None
        self.stage1_output_path = None
        self.stage2_output_path = None
        self.stage2_btn.config(state=tk.DISABLED)
        self._log("[CLEAR] Input files and current results cleared.")

    def _log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _run_stage_1(self):
        if not all((self.new_items_path.get(), self.product_bible_path.get(), self.tracker_path.get())):
            messagebox.showwarning("Missing Files", "Please select all required input files.")
            return

        def task():
            self._log("\n=== STAGE 1 STARTED ===")
            success, df_diff, metrics = self.engine.run_stage_1_matching(
                self.new_items_path.get(), self.product_bible_path.get(), self.tracker_path.get(),
                self.uploaded_skus_path.get() or None
            )
            if success:
                self.current_difference_df = df_diff
                out_path = self.exporter.export_photoshoot_items(df_diff, "Stage1_Difference_List")
                self.stage1_output_path = out_path
                self._log(f"[STAGE 1 SUCCESS] Raw difference items: {len(df_diff)}")
                self._log(f"Difference File Saved to:\n{out_path}")
                self.stage2_btn.config(state=tk.NORMAL)
                messagebox.showinfo("Stage 1 Complete", f"Raw Difference List exported successfully!\n\nRows: {len(df_diff)}\nFile: {out_path.name}")
            else:
                self._log(f"[STAGE 1 ERROR] {df_diff}")
                messagebox.showerror("Stage 1 Error", str(df_diff))
        threading.Thread(target=task, daemon=True).start()

    def _run_stage_2(self):
        if self.current_difference_df is None or self.current_difference_df.empty:
            messagebox.showwarning("No Data", "Please run Stage 1 first to generate the Difference List.")
            return

        def task():
            self._log("\n=== STAGE 2 STARTED ===")
            success, df_final, metrics = self.engine.run_stage_2_elimination(self.current_difference_df)
            if success:
                out_path = self.exporter.export_stage_2_results(
                    df_final,
                    self.engine.major_appliances_df,
                    "Stage2_Final_Photoshoot_List"
                )
                self.stage2_output_path = out_path
                major_count = len(self.engine.major_appliances_df)
                self._log(f"[STAGE 2 SUCCESS] Final photoshoot items: {len(df_final)}")
                self._log(f"[STAGE 2] Major Appliances separated: {major_count}")
                self._log(f"Final File Saved to:\n{out_path}")
                messagebox.showinfo("Stage 2 Complete", f"Filtering completed!\n\nFinal Products: {len(df_final)}\nMajor Appliances: {major_count}\n\nFile: {out_path.name}")
            else:
                self._log("[STAGE 2 ERROR] Failed during filtering.")
                messagebox.showerror("Stage 2 Error", "Failed during filtering. Check the execution logs.")
        threading.Thread(target=task, daemon=True).start()

    def _open_report(self, path):
        try:
            path = Path(path)
            if not path.exists():
                messagebox.showwarning("Report Missing", "The selected report no longer exists.")
                return
            if sys.platform.startswith("win"):
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(path)])
            else:
                subprocess.Popen(["xdg-open", str(path)])
        except Exception as exc:
            messagebox.showerror("Open Report Error", str(exc))

    def _delete_report(self, path, parent):
        path = Path(path)
        if not path.exists():
            self._refresh_reports_list(parent)
            return
        if not messagebox.askyesno("Delete Report", f"Delete this report?\n\n{path.name}"):
            return
        try:
            path.unlink()
            self._log(f"[REPORTS] Deleted: {path.name}")
            self._refresh_reports_list(parent)
        except Exception as exc:
            messagebox.showerror("Delete Error", str(exc))

    def _delete_all_reports(self):
        output_dir = Path(self.exporter.output_dir)
        reports = [p for p in output_dir.glob("*.xlsx") if p.is_file()] if output_dir.exists() else []
        if not reports:
            messagebox.showinfo("No Reports", "There are no generated reports to delete.")
            return
        if not messagebox.askyesno("Delete All Reports", f"This will permanently delete {len(reports)} generated report(s).\n\nYour input files will NOT be deleted.\n\nAre you sure you want to continue?"):
            return
        deleted = failed = 0
        for report in reports:
            try:
                report.unlink()
                deleted += 1
            except Exception as exc:
                failed += 1
                self.logger.error(f"Could not delete report {report}: {exc}")
        self.stage1_output_path = None
        self.stage2_output_path = None
        self._log(f"[REPORTS] Deleted {deleted} report(s).")
        if self.reports_frame is not None and self.reports_frame.winfo_exists():
            self._refresh_reports_list(self.reports_frame)
        if failed:
            messagebox.showwarning("Delete Completed", f"Deleted: {deleted}\nFailed: {failed}")
        else:
            messagebox.showinfo("Reports Deleted", f"Successfully deleted {deleted} report(s).")

    def _refresh_reports_list(self, parent):
        for widget in parent.winfo_children():
            widget.destroy()
        output_dir = Path(self.exporter.output_dir)
        reports = [p for p in output_dir.glob("*.xlsx") if p.is_file()] if output_dir.exists() else []
        reports.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        if not reports:
            ttk.Label(parent, text="No reports have been generated yet.").pack(pady=30)
            return
        for index, report in enumerate(reports):
            latest = index == 0
            frame = ttk.LabelFrame(parent, text="LATEST REPORT" if latest else "Generated Report", padding=10)
            frame.pack(fill=tk.X, pady=5)
            name = report.name.upper()
            report_type = ("Stage 2 — Final Photoshoot Report" if "STAGE2" in name else "Stage 1 — Raw Difference Report" if "STAGE1" in name else "Pipeline Summary" if "SUMMARY" in name else "Generated Report")
            if latest:
                ttk.Label(frame, text="LATEST", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 3))
            ttk.Label(frame, text=report_type, font=("Arial", 11, "bold")).pack(anchor=tk.W)
            ttk.Label(frame, text=report.name).pack(anchor=tk.W, pady=(3, 0))
            generated = datetime.fromtimestamp(report.stat().st_mtime).strftime("%b %d, %Y %I:%M:%S %p")
            ttk.Label(frame, text=f"Generated: {generated}").pack(anchor=tk.W, pady=(3, 5))
            buttons = ttk.Frame(frame)
            buttons.pack(anchor=tk.E)
            ttk.Button(buttons, text="Open", command=lambda p=report: self._open_report(p)).pack(side=tk.LEFT, padx=3)
            ttk.Button(buttons, text="Delete", command=lambda p=report, f=parent: self._delete_report(p, f)).pack(side=tk.LEFT, padx=3)

    def _close_reports(self):
        if self.report_window is not None and self.report_window.winfo_exists():
            self.report_window.destroy()
        self.report_window = None
        self.reports_frame = None

    def _open_reports(self):
        if self.report_window is not None and self.report_window.winfo_exists():
            self.report_window.deiconify()
            self.report_window.lift()
            self.report_window.focus_force()
            self._refresh_reports_list(self.reports_frame)
            return
        self.report_window = tk.Toplevel(self.root)
        self.report_window.title("Generated Reports")
        self.report_window.geometry("800x550")
        self.report_window.minsize(650, 400)
        self.report_window.protocol("WM_DELETE_WINDOW", self._close_reports)
        ttk.Label(self.report_window, text="Generated Reports", font=("Arial", 15, "bold")).pack(anchor=tk.W, padx=15, pady=(15, 5))
        ttk.Label(self.report_window, text="Open or delete reports generated by the tool.").pack(anchor=tk.W, padx=15, pady=(0, 10))
        ttk.Button(self.report_window, text="Delete All Reports", command=self._delete_all_reports).pack(anchor=tk.E, padx=15, pady=(0, 10))

        container = ttk.Frame(self.report_window)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        canvas = tk.Canvas(container, highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)
        self.reports_frame = ttk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=self.reports_frame, anchor="nw")
        self.reports_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(canvas_window, width=e.width))
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        self._refresh_reports_list(self.reports_frame)


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    PhotoshootAutomationApp(root)
    root.mainloop()
