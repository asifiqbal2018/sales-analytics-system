from utils.file_handler import read_sales_data, parse_transactions, validate_and_filter
from utils.data_processor import (
    calculate_total_revenue,
    region_wise_sales,
    top_selling_products,
    customer_analysis,
    daily_sales_trend,
    find_peak_sales_day,
    low_performing_products,
    generate_sales_report
)
from utils.api_handler import (
    fetch_all_products,
    create_product_mapping,
    enrich_sales_data
)


def _print_banner():
    print("=" * 40)
    print("SALES ANALYTICS SYSTEM")
    print("=" * 40)


def _fmt_money(x):
    try:
        return f"₹{float(x):,.2f}"
    except Exception:
        return "₹0.00"


def _safe_float(s):
    try:
        return float(str(s).strip())
    except Exception:
        return None


def _ask_yes_no(prompt, default="n"):
    ans = input(prompt).strip().lower()
    if not ans:
        ans = default
    return ans in ("y", "yes")


def _ask_optional_str(prompt):
    s = input(prompt).strip()
    return s if s else None


def _ask_optional_float(prompt):
    s = input(prompt).strip()
    if not s:
        return None
    val = _safe_float(s)
    return val


def main():
    """
    Main execution function following required workflow.
    """
    try:
        _print_banner()

        # [1/10] Read sales data
        print("\n[1/10] Reading sales data...")
        raw_lines = read_sales_data("data/sales_data.txt")
        if not raw_lines:
            print("✗ No data read. Please check file path: data/sales_data.txt")
            return
        print(f"✓ Successfully read {len(raw_lines)} transactions")

        # [2/10] Parse and clean
        print("\n[2/10] Parsing and cleaning data...")
        transactions = parse_transactions(raw_lines)
        print(f"✓ Parsed {len(transactions)} records")

        # [3/10] Display filter options and ask user
        # NOTE: validate_and_filter prints:
        # - Available regions
        # - Transaction amount range
        print("\n[3/10] Filter Options Available:")
        # Run a "preview validation" without filters so user can see regions + range
        preview_valid, preview_invalid, _ = validate_and_filter(transactions)
        # We only used this for display; we will re-run with actual filters next.

        want_filter = _ask_yes_no("\nDo you want to filter data? (y/n): ", default="n")

        region = None
        min_amount = None
        max_amount = None

        if want_filter:
            region = _ask_optional_str("Enter region (or press Enter to skip): ")
            min_amount = _ask_optional_float("Enter minimum amount (or press Enter to skip): ")
            max_amount = _ask_optional_float("Enter maximum amount (or press Enter to skip): ")

        # [4/10] Validate + filter for real
        print("\n[4/10] Validating transactions...")
        valid_tx, invalid_count, filter_summary = validate_and_filter(
            transactions,
            region=region,
            min_amount=min_amount,
            max_amount=max_amount
        )
        print(f"✓ Valid: {len(valid_tx)} | Invalid: {invalid_count}")

        if len(valid_tx) == 0:
            print("✗ No valid transactions left after validation/filtering. Exiting.")
            return

        # [5/10] Analysis
        print("\n[5/10] Analyzing sales data...")

        total_revenue = calculate_total_revenue(valid_tx)
        reg_stats = region_wise_sales(valid_tx)
        top_products = top_selling_products(valid_tx, n=5)
        cust_stats = customer_analysis(valid_tx)
        trend = daily_sales_trend(valid_tx)
        peak_day = find_peak_sales_day(valid_tx)
        low_products = low_performing_products(valid_tx, threshold=10)

        print("✓ Analysis complete")

        # Optional: show a small summary on console (nice + informative)
        print("\n--- Quick Summary ---")
        print(f"Total Revenue: {_fmt_money(total_revenue)}")
        print(f"Total Transactions: {len(valid_tx)}")
        avg_order = (total_revenue / len(valid_tx)) if len(valid_tx) else 0.0
        print(f"Average Order Value: {_fmt_money(avg_order)}")
        if peak_day[0]:
            print(f"Peak Day: {peak_day[0]} | Revenue: {_fmt_money(peak_day[1])} | Tx: {peak_day[2]}")
        print("---------------------")

        # [6/10] Fetch API Products
        print("\n[6/10] Fetching product data from API...")
        api_products = fetch_all_products()
        if api_products:
            print(f"✓ Fetched {len(api_products)} products")
        else:
            print("✗ API fetch failed (continuing with no enrichment matches).")

        # [7/10] Enrich
        print("\n[7/10] Enriching sales data...")
        product_mapping = create_product_mapping(api_products)
        enriched_tx = enrich_sales_data(valid_tx, product_mapping)

        matched = sum(1 for t in enriched_tx if t.get("API_Match") is True)
        total_enriched = len(enriched_tx)
        pct = (matched / total_enriched * 100.0) if total_enriched else 0.0
        print(f"✓ Enriched {matched}/{total_enriched} transactions ({pct:.1f}%)")

        # [8/10] Save enriched (already saved inside enrich_sales_data via save_enriched_data)
        print("\n[8/10] Saving enriched data...")
        print("✓ Saved to: data/enriched_sales_data.txt")

        # [9/10] Generate report
        print("\n[9/10] Generating report...")
        generate_sales_report(valid_tx, enriched_tx, output_file="output/sales_report.txt")
        print("✓ Report saved to: output/sales_report.txt")

        # [10/10] Complete
        print("\n[10/10] Process Complete!")
        print("=" * 40)
        print("Files generated:")
        print(" - data/enriched_sales_data.txt")
        print(" - output/sales_report.txt")
        print("=" * 40)

    except KeyboardInterrupt:
        print("\n\nProcess cancelled by user.")
    except Exception as e:
        # user-friendly error, no crash dump
        print("\n✗ Something went wrong, but the program did not crash.")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
