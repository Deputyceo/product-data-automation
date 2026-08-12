# Product Data Automation

A Python desktop application for automating product-data reconciliation, SKU comparison, configurable filtering, and Excel report generation.

## Features

- Drag-and-drop spreadsheet input
- Browse and Clear controls for each input
- Stage 1: raw SKU difference against reference datasets
- Stage 2: configurable filtering and category separation
- Major Appliances separated into a dedicated Excel worksheet
- Timestamped Excel reports
- Report manager with Open, Delete, and Delete All
- Latest-report indicator and scrollable report history
- Local processing of user-provided spreadsheet files

## Workflow

### Stage 1 — Raw Difference

The application compares the source dataset against configured reference datasets and returns the raw SKU difference. Stage 1 does not apply the Stage 2 business-rule filters.

### Stage 2 — Final Processing

The raw difference is processed with configurable filtering rules. Special categories can be separated into dedicated report worksheets while the remaining records continue through the normal filtering pipeline.

## Tech Stack

- Python
- Tkinter / TkinterDnD2
- Pandas
- OpenPyXL

## Installation

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

## Input Data

The application works with spreadsheet files containing a SKU column. Additional product attributes can be used by Stage 2 depending on the configuration.

No company datasets are included in this repository.

## Privacy and Portfolio Safety

This repository contains application code and generic example configuration only. Real company spreadsheets, generated reports, logs, local environment files, and proprietary datasets are intentionally excluded.

Do not commit real business data to this repository.

## Project Structure

```text
product-data-automation/
├── main.py
├── config.py
├── requirements.txt
├── .gitignore
├── README.md
├── core/
├── gui/
├── ui/
├── models/
└── data/
```

## Portfolio Project

This project demonstrates practical automation skills including data reconciliation, Pandas-based processing, Excel automation, desktop GUI development, drag-and-drop workflows, configurable filtering, and report management.