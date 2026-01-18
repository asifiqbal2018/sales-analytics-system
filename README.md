# Sales Analytics System

A complete Python-based Sales Analytics System that reads raw sales data, cleans and validates it, performs analytical processing, enriches transactions using an external API, and generates a comprehensive text report.

This project demonstrates:
- File handling with encoding issues
- Data cleaning and validation
- Analytical processing using lists, dictionaries, and functions
- API integration and data enrichment
- Report generation
- Robust, user-friendly main application flow


## Repository Structure

sales-analytics-system/
│ README.md
│ main.py
│ requirements.txt
│
├─ utils/
│ ├─ init.py
│ ├─ file_handler.py
│ ├─ data_processor.py
│ └─ api_handler.py
│
├─ data/
│ ├─ sales_data.txt # provided input file
│ └─ enriched_sales_data.txt # generated (after running)
│
└─ output/
└─ sales_report.txt # generated (after running)


✅ All file paths are **relative** (no hardcoded system paths).

---

## Features Overview

### Part 1: File Handling & Data Cleaning
- Reads pipe-delimited (`|`) files
- Handles non-UTF-8 encodings (`utf-8`, `latin-1`, `cp1252`)
- Skips header and empty lines
- Fixes:
  - commas in product names
  - commas in numeric values
  - extra pipes inside product names
- Skips malformed rows

### Part 1.3: Validation & Filtering
Validation rules:
- Quantity > 0
- UnitPrice > 0
- Required fields present
- TransactionID starts with `T`
- ProductID starts with `P`
- CustomerID starts with `C`

Optional filters:
- Region
- Minimum transaction amount
- Maximum transaction amount

---

### Part 2: Data Processing & Analytics
- Total revenue calculation
- Region-wise sales analysis
- Top selling products
- Customer purchase analysis
- Daily sales trends
- Peak sales day detection
- Low-performing product detection

---

### Part 3: API Integration & Enrichment
- Fetches product data from DummyJSON API:
https://dummyjson.com/products?limit=100

- Matches sales ProductID (`P101 → 101`) with API product ID
- Enriches transactions with:
- API_Category
- API_Brand
- API_Rating
- API_Match (True/False)
- Saves enriched output to:
data/enriched_sales_data.txt


---

### Part 4: Report Generation
Generates a detailed text report:
output/sales_report.txt


Report sections:
1. Header
2. Overall Summary
3. Region-wise Performance
4. Top 5 Products
5. Top 5 Customers
6. Daily Sales Trend
7. Product Performance Analysis
8. API Enrichment Summary

---

### Part 5: Main Application
- Interactive command-line execution
- Optional filtering based on user input
- Step-by-step progress output
- Graceful error handling
- End-to-end execution from raw data to final report

---

## Requirements

- Python 3.9 or higher
- External library:
  - `requests`


## Setup Instructions (VS Code Recommended)

### 1) Open the project folder
- Open VS Code
- `File → Open Folder`
- Select `sales-analytics-system`


### 2) Create and activate virtual environment (recommended)

#### Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
3) Install dependencies
pip install -r requirements.txt
4) Select Python interpreter in VS Code
Press Ctrl + Shift + P

Select Python: Select Interpreter

Choose .venv

How to Run the Application
From the project root directory:

python main.py
Example Console Output
========================================
SALES ANALYTICS SYSTEM
========================================

[1/10] Reading sales data...
✓ Successfully read 80 transactions

[2/10] Parsing and cleaning data...
✓ Parsed 80 records

[3/10] Filter Options Available:
Available regions: ['East', 'North', 'South', 'West']
Transaction amount range (valid only): min=500.00, max=90000.00

Do you want to filter data? (y/n): n

[4/10] Validating transactions...
✓ Valid: 70 | Invalid: 10

[5/10] Analyzing sales data...
✓ Analysis complete

[6/10] Fetching product data from API...
✓ Fetched 100 products

[7/10] Enriching sales data...
✓ Enriched 55/70 transactions (78.6%)

[8/10] Saving enriched data...
✓ Saved to: data/enriched_sales_data.txt

[9/10] Generating report...
✓ Report saved to: output/sales_report.txt

[10/10] Process Complete!
========================================
Output Files
Enriched Sales Data
Path: data/enriched_sales_data.txt

Columns:

TransactionID|Date|ProductID|ProductName|Quantity|UnitPrice|CustomerID|Region|API_Category|API_Brand|API_Rating|API_Match
Sales Report
Path: output/sales_report.txt

Contains formatted tables and summaries for:
    -Revenue
    -Regions
    -Products
    -Customers
    -Daily trends
    -API enrichment results
    -Troubleshooting
    -Module import errors

Ensure:
    -You run from project root
    -utils/__init__.py exists



At least 10 meaningful commits

Author Notes
This project was built to be:
    -Modular
    -Readable
    -Robust
    -Rubric-compliant
    -Easy to exte
