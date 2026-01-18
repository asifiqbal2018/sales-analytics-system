import os
from datetime import datetime


def calculate_total_revenue(transactions):
    """
    Calculates total revenue from all transactions

    Returns: float (total revenue)
    """
    total = 0.0
    for t in transactions:
        try:
            qty = int(t.get("Quantity", 0))
            price = float(t.get("UnitPrice", 0.0))
        except (ValueError, TypeError):
            continue
        total += qty * price
    return float(total)


def region_wise_sales(transactions):
    """
    Analyzes sales by region

    Returns: dictionary with region statistics (sorted by total_sales desc)
    """
    region_totals = {}
    region_counts = {}
    grand_total = 0.0

    for t in transactions:
        region = str(t.get("Region", "")).strip()
        if not region:
            continue

        try:
            qty = int(t.get("Quantity", 0))
            price = float(t.get("UnitPrice", 0.0))
        except (ValueError, TypeError):
            continue

        amount = qty * price
        grand_total += amount

        region_totals[region] = region_totals.get(region, 0.0) + amount
        region_counts[region] = region_counts.get(region, 0) + 1

    stats = {}
    for reg, total_sales in region_totals.items():
        pct = (total_sales / grand_total * 100.0) if grand_total > 0 else 0.0
        stats[reg] = {
            "total_sales": float(total_sales),
            "transaction_count": int(region_counts.get(reg, 0)),
            "percentage": round(pct, 2)
        }

    sorted_items = sorted(stats.items(), key=lambda x: x[1]["total_sales"], reverse=True)
    return dict(sorted_items)


def top_selling_products(transactions, n=5):
    """
    Finds top n products by total quantity sold

    Returns: list of tuples
    [
        ('Laptop', 45, 2250000.0),  # (ProductName, TotalQuantity, TotalRevenue)
        ...
    ]
    """
    prod_qty = {}
    prod_rev = {}

    for t in transactions:
        name = str(t.get("ProductName", "")).strip()
        if not name:
            continue

        try:
            qty = int(t.get("Quantity", 0))
            price = float(t.get("UnitPrice", 0.0))
        except (ValueError, TypeError):
            continue

        amount = qty * price
        prod_qty[name] = prod_qty.get(name, 0) + qty
        prod_rev[name] = prod_rev.get(name, 0.0) + amount

    rows = []
    for name in prod_qty:
        rows.append((name, int(prod_qty[name]), float(prod_rev.get(name, 0.0))))

    # Sort by TotalQuantity desc (then revenue desc)
    rows.sort(key=lambda x: (x[1], x[2]), reverse=True)
    return rows[: max(0, int(n))]


def customer_analysis(transactions):
    """
    Analyzes customer purchase patterns

    Returns: dictionary of customer statistics (sorted by total_spent desc)
    """
    cust = {}

    for t in transactions:
        cid = str(t.get("CustomerID", "")).strip()
        pname = str(t.get("ProductName", "")).strip()

        if not cid:
            continue

        try:
            qty = int(t.get("Quantity", 0))
            price = float(t.get("UnitPrice", 0.0))
        except (ValueError, TypeError):
            continue

        amount = qty * price

        if cid not in cust:
            cust[cid] = {
                "total_spent": 0.0,
                "purchase_count": 0,
                "products_bought": []  # keep unique list
            }

        cust[cid]["total_spent"] += amount
        cust[cid]["purchase_count"] += 1

        if pname and pname not in cust[cid]["products_bought"]:
            cust[cid]["products_bought"].append(pname)

    # finalize avg_order_value
    for cid, info in cust.items():
        pc = info["purchase_count"]
        info["total_spent"] = float(info["total_spent"])
        info["avg_order_value"] = round((info["total_spent"] / pc), 2) if pc > 0 else 0.0

    # sort by total_spent desc
    sorted_items = sorted(cust.items(), key=lambda x: x[1]["total_spent"], reverse=True)
    return dict(sorted_items)


def daily_sales_trend(transactions):
    """
    Analyzes sales trends by date

    Returns: dictionary sorted by date (chronological)
    """
    daily = {}

    for t in transactions:
        dt = str(t.get("Date", "")).strip()
        cid = str(t.get("CustomerID", "")).strip()

        if not dt:
            continue

        try:
            qty = int(t.get("Quantity", 0))
            price = float(t.get("UnitPrice", 0.0))
        except (ValueError, TypeError):
            continue

        amount = qty * price

        if dt not in daily:
            daily[dt] = {
                "revenue": 0.0,
                "transaction_count": 0,
                "unique_customers_set": set()
            }

        daily[dt]["revenue"] += amount
        daily[dt]["transaction_count"] += 1
        if cid:
            daily[dt]["unique_customers_set"].add(cid)

    # convert set -> count, round revenue
    out = {}
    for dt, info in daily.items():
        out[dt] = {
            "revenue": float(info["revenue"]),
            "transaction_count": int(info["transaction_count"]),
            "unique_customers": int(len(info["unique_customers_set"]))
        }

    # sort chronologically by date string (YYYY-MM-DD)
    return dict(sorted(out.items(), key=lambda x: x[0]))


def find_peak_sales_day(transactions):
    """
    Identifies the date with highest revenue

    Returns: tuple (date, revenue, transaction_count)
    Example: ('2024-12-15', 185000.0, 12)
    """
    trend = daily_sales_trend(transactions)
    if not trend:
        return (None, 0.0, 0)

    # max by revenue; if tie pick earliest date
    best_date = None
    best_rev = -1.0
    best_cnt = 0

    for dt, info in trend.items():
        rev = float(info["revenue"])
        cnt = int(info["transaction_count"])
        if (rev > best_rev) or (rev == best_rev and (best_date is None or dt < best_date)):
            best_date = dt
            best_rev = rev
            best_cnt = cnt

    return (best_date, float(best_rev), int(best_cnt))


def low_performing_products(transactions, threshold=10):
    """
    Identifies products with low sales (total quantity < threshold)

    Returns: list of tuples sorted by TotalQuantity asc
    [
        ('Webcam', 4, 12000.0),
        ...
    ]
    """
    prod_qty = {}
    prod_rev = {}

    for t in transactions:
        name = str(t.get("ProductName", "")).strip()
        if not name:
            continue

        try:
            qty = int(t.get("Quantity", 0))
            price = float(t.get("UnitPrice", 0.0))
        except (ValueError, TypeError):
            continue

        amount = qty * price
        prod_qty[name] = prod_qty.get(name, 0) + qty
        prod_rev[name] = prod_rev.get(name, 0.0) + amount

    th = int(threshold)
    rows = []
    for name, qty in prod_qty.items():
        if int(qty) < th:
            rows.append((name, int(qty), float(prod_rev.get(name, 0.0))))

    # Sort by TotalQuantity asc (then revenue asc)
    rows.sort(key=lambda x: (x[1], x[2]))
    return rows

def generate_sales_report(transactions, enriched_transactions, output_file='output/sales_report.txt'):
    """
    Generates a comprehensive formatted text report (in required order)
    and saves to output_file.
    """

    # -----------------------------
    # Helpers
    # -----------------------------
    def fmt_money(x):
        try:
            return f"₹{float(x):,.2f}"
        except Exception:
            return "₹0.00"

    def fmt_pct(x):
        try:
            return f"{float(x):.2f}%"
        except Exception:
            return "0.00%"

    def safe_float(x, default=0.0):
        try:
            return float(x)
        except Exception:
            return default

    def safe_int(x, default=0):
        try:
            return int(x)
        except Exception:
            return default

    def line(char="=", width=60):
        return char * width

    def make_table(headers, rows):
        # rows = list[list[str]]
        str_rows = [[("" if c is None else str(c)) for c in r] for r in rows]
        widths = [len(str(h)) for h in headers]
        for r in str_rows:
            for i, c in enumerate(r):
                widths[i] = max(widths[i], len(c))

        def fmt_row(r):
            return "  ".join(str(r[i]).ljust(widths[i]) for i in range(len(headers)))

        out = []
        out.append(fmt_row(headers))
        out.append("  ".join("-" * w for w in widths))
        for r in str_rows:
            out.append(fmt_row(r))
        return "\n".join(out)

    # -----------------------------
    # Core Metrics (use your existing computed data)
    # -----------------------------
    total_tx = len(transactions)

    # Total revenue
    total_revenue = 0.0
    for t in transactions:
        qty = safe_int(t.get("Quantity", 0))
        price = safe_float(t.get("UnitPrice", 0.0))
        total_revenue += qty * price

    avg_order_value = (total_revenue / total_tx) if total_tx > 0 else 0.0

    # Date range
    dates = [str(t.get("Date", "")).strip() for t in transactions if str(t.get("Date", "")).strip()]
    date_min = min(dates) if dates else "N/A"
    date_max = max(dates) if dates else "N/A"

    # -----------------------------
    # REGION-WISE PERFORMANCE
    # -----------------------------
    region_totals = {}
    region_counts = {}
    for t in transactions:
        reg = str(t.get("Region", "")).strip()
        if not reg:
            continue
        qty = safe_int(t.get("Quantity", 0))
        price = safe_float(t.get("UnitPrice", 0.0))
        amt = qty * price
        region_totals[reg] = region_totals.get(reg, 0.0) + amt
        region_counts[reg] = region_counts.get(reg, 0) + 1

    region_rows = []
    for reg, sales in region_totals.items():
        pct = (sales / total_revenue * 100.0) if total_revenue > 0 else 0.0
        region_rows.append([reg, fmt_money(sales), fmt_pct(pct), str(region_counts.get(reg, 0))])

    region_rows.sort(key=lambda r: safe_float(r[1].replace("₹", "").replace(",", ""), 0.0), reverse=True)

    # Average transaction value per region
    avg_tx_value_per_region = {}
    for reg, sales in region_totals.items():
        cnt = region_counts.get(reg, 0)
        avg_tx_value_per_region[reg] = (sales / cnt) if cnt > 0 else 0.0

    # -----------------------------
    # TOP 5 PRODUCTS (by Quantity)
    # -----------------------------
    prod_qty = {}
    prod_rev = {}
    for t in transactions:
        name = str(t.get("ProductName", "")).strip()
        if not name:
            continue
        qty = safe_int(t.get("Quantity", 0))
        price = safe_float(t.get("UnitPrice", 0.0))
        prod_qty[name] = prod_qty.get(name, 0) + qty
        prod_rev[name] = prod_rev.get(name, 0.0) + qty * price

    prod_rows = [(name, q, prod_rev.get(name, 0.0)) for name, q in prod_qty.items()]
    prod_rows.sort(key=lambda x: (x[1], x[2]), reverse=True)
    top5_products = prod_rows[:5]

    top_prod_table_rows = []
    for i, (name, q, rev) in enumerate(top5_products, start=1):
        top_prod_table_rows.append([str(i), name, str(q), fmt_money(rev)])

    # -----------------------------
    # TOP 5 CUSTOMERS (by Total Spent)
    # -----------------------------
    cust_spend = {}
    cust_count = {}
    for t in transactions:
        cid = str(t.get("CustomerID", "")).strip()
        if not cid:
            continue
        qty = safe_int(t.get("Quantity", 0))
        price = safe_float(t.get("UnitPrice", 0.0))
        amt = qty * price
        cust_spend[cid] = cust_spend.get(cid, 0.0) + amt
        cust_count[cid] = cust_count.get(cid, 0) + 1

    cust_rows = [(cid, spent, cust_count.get(cid, 0)) for cid, spent in cust_spend.items()]
    cust_rows.sort(key=lambda x: x[1], reverse=True)
    top5_customers = cust_rows[:5]

    top_cust_table_rows = []
    for i, (cid, spent, cnt) in enumerate(top5_customers, start=1):
        top_cust_table_rows.append([str(i), cid, fmt_money(spent), str(cnt)])

    # -----------------------------
    # DAILY SALES TREND
    # -----------------------------
    daily = {}
    for t in transactions:
        dt = str(t.get("Date", "")).strip()
        if not dt:
            continue
        cid = str(t.get("CustomerID", "")).strip()
        qty = safe_int(t.get("Quantity", 0))
        price = safe_float(t.get("UnitPrice", 0.0))
        amt = qty * price

        if dt not in daily:
            daily[dt] = {"revenue": 0.0, "tx": 0, "customers": set()}
        daily[dt]["revenue"] += amt
        daily[dt]["tx"] += 1
        if cid:
            daily[dt]["customers"].add(cid)

    daily_rows = []
    for dt in sorted(daily.keys()):
        daily_rows.append([
            dt,
            fmt_money(daily[dt]["revenue"]),
            str(daily[dt]["tx"]),
            str(len(daily[dt]["customers"]))
        ])

    # Peak sales day
    peak_day = None
    peak_rev = -1.0
    peak_cnt = 0
    for dt, info in daily.items():
        if info["revenue"] > peak_rev:
            peak_day = dt
            peak_rev = info["revenue"]
            peak_cnt = info["tx"]

    # -----------------------------
    # LOW PERFORMING PRODUCTS
    # -----------------------------
    threshold = 10
    low_products = [(name, q, prod_rev.get(name, 0.0)) for name, q in prod_qty.items() if q < threshold]
    low_products.sort(key=lambda x: (x[1], x[2]))  # qty asc

    # -----------------------------
    # API ENRICHMENT SUMMARY
    # -----------------------------
    enriched_total = len(enriched_transactions)
    enriched_match = sum(1 for t in enriched_transactions if t.get("API_Match") is True)
    success_rate = (enriched_match / enriched_total * 100.0) if enriched_total > 0 else 0.0

    # products that couldn't be enriched (unique by ProductName)
    not_enriched_products = sorted({
        str(t.get("ProductName", "")).strip()
        for t in enriched_transactions
        if t.get("API_Match") is False and str(t.get("ProductName", "")).strip()
    })

    # -----------------------------
    # Write Report
    # -----------------------------
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    width = 60

    report_lines = []

    # 1) HEADER
    report_lines.append(line("=", width))
    report_lines.append("       SALES ANALYTICS REPORT".center(width))
    report_lines.append(f"Generated: {now}".center(width))
    report_lines.append(f"Records Processed: {total_tx}".center(width))
    report_lines.append(line("=", width))
    report_lines.append("")

    # 2) OVERALL SUMMARY
    report_lines.append("OVERALL SUMMARY")
    report_lines.append(line("-", width))
    report_lines.append(f"Total Revenue:        {fmt_money(total_revenue)}")
    report_lines.append(f"Total Transactions:   {total_tx}")
    report_lines.append(f"Average Order Value:  {fmt_money(avg_order_value)}")
    report_lines.append(f"Date Range:           {date_min} to {date_max}")
    report_lines.append("")

    # 3) REGION-WISE PERFORMANCE
    report_lines.append("REGION-WISE PERFORMANCE")
    report_lines.append(line("-", width))
    if region_rows:
        report_lines.append(make_table(
            ["Region", "Sales", "% of Total", "Transactions"],
            region_rows
        ))
    else:
        report_lines.append("No region data available.")
    report_lines.append("")

    # 4) TOP 5 PRODUCTS
    report_lines.append("TOP 5 PRODUCTS")
    report_lines.append(line("-", width))
    if top_prod_table_rows:
        report_lines.append(make_table(
            ["Rank", "Product Name", "Quantity Sold", "Revenue"],
            top_prod_table_rows
        ))
    else:
        report_lines.append("No product data available.")
    report_lines.append("")

    # 5) TOP 5 CUSTOMERS
    report_lines.append("TOP 5 CUSTOMERS")
    report_lines.append(line("-", width))
    if top_cust_table_rows:
        report_lines.append(make_table(
            ["Rank", "Customer ID", "Total Spent", "Order Count"],
            top_cust_table_rows
        ))
    else:
        report_lines.append("No customer data available.")
    report_lines.append("")

    # 6) DAILY SALES TREND
    report_lines.append("DAILY SALES TREND")
    report_lines.append(line("-", width))
    if daily_rows:
        report_lines.append(make_table(
            ["Date", "Revenue", "Transactions", "Unique Customers"],
            daily_rows
        ))
    else:
        report_lines.append("No daily trend data available.")
    report_lines.append("")

    # 7) PRODUCT PERFORMANCE ANALYSIS
    report_lines.append("PRODUCT PERFORMANCE ANALYSIS")
    report_lines.append(line("-", width))
    if peak_day:
        report_lines.append(f"Best selling day: {peak_day} | Revenue: {fmt_money(peak_rev)} | Transactions: {peak_cnt}")
    else:
        report_lines.append("Best selling day: N/A")

    report_lines.append("")
    report_lines.append("Low performing products (qty < 10):")
    if low_products:
        low_rows = [[name, str(q), fmt_money(rev)] for name, q, rev in low_products]
        report_lines.append(make_table(["Product Name", "Total Quantity", "Total Revenue"], low_rows))
    else:
        report_lines.append("None")

    report_lines.append("")
    report_lines.append("Average transaction value per region:")
    if avg_tx_value_per_region:
        avg_rows = [[reg, fmt_money(val)] for reg, val in sorted(avg_tx_value_per_region.items(), key=lambda x: x[1], reverse=True)]
        report_lines.append(make_table(["Region", "Avg Tx Value"], avg_rows))
    else:
        report_lines.append("N/A")
    report_lines.append("")

    # 8) API ENRICHMENT SUMMARY
    report_lines.append("API ENRICHMENT SUMMARY")
    report_lines.append(line("-", width))
    report_lines.append(f"Total transactions enriched: {enriched_total}")
    report_lines.append(f"Successful enrichments:      {enriched_match}")
    report_lines.append(f"Success rate:               {success_rate:.2f}%")
    report_lines.append("")
    report_lines.append("Products that couldn't be enriched:")
    if not_enriched_products:
        for p in not_enriched_products:
            report_lines.append(f"- {p}")
    else:
        report_lines.append("None")
    report_lines.append("")

    # Write to file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"Sales report generated: {output_file}")
