def read_sales_data(filename):
    """
    Reads sales data from file handling encoding issues

    Returns: list of raw lines (strings)

    Expected Output Format:
    ['T001|2024-12-01|P101|Laptop|2|45000|C001|North', ...]

    Requirements:
    - Use 'with' statement
    - Handle different encodings (try 'utf-8', 'latin-1', 'cp1252')
    - Handle FileNotFoundError with appropriate error message
    - Skip the header row
    - Remove empty lines
    """
    encodings_to_try = ["utf-8", "latin-1", "cp1252"]

    try:
        last_decode_error = None

        for enc in encodings_to_try:
            try:
                with open(filename, "r", encoding=enc) as f:
                    raw_lines = f.read().splitlines()
                last_decode_error = None
                break
            except UnicodeDecodeError as e:
                last_decode_error = e
                raw_lines = None

        # If all strict decoding attempts failed, do a safe fallback read
        if raw_lines is None:
            # fallback: keep as much text as possible
            with open(filename, "r", encoding="latin-1", errors="replace") as f:
                raw_lines = f.read().splitlines()

        # Remove empty lines (after stripping whitespace)
        cleaned = [ln.strip() for ln in raw_lines if ln.strip()]

        # Skip header row if present
        # Expecting: TransactionID|Date|ProductID|ProductName|Quantity|UnitPrice|CustomerID|Region
        if cleaned and cleaned[0].lower().startswith("transactionid|"):
            cleaned = cleaned[1:]

        return cleaned

    except FileNotFoundError:
        print(f"Error: File not found -> {filename}")
        return []


def parse_transactions(raw_lines):
    """
    Parses raw lines into clean list of dictionaries

    Returns: list of dictionaries with keys:
    ['TransactionID', 'Date', 'ProductID', 'ProductName',
     'Quantity', 'UnitPrice', 'CustomerID', 'Region']

    Requirements:
    - Split by pipe delimiter '|'
    - Handle commas within ProductName (remove or replace)
    - Remove commas from numeric fields and convert to proper types
    - Convert Quantity to int
    - Convert UnitPrice to float
    - Skip rows with incorrect number of fields
    """
    parsed = []

    for line in raw_lines:
        line = line.strip()
        if not line:
            continue

        parts = line.split("|")

        # Fix rows that have extra pipes inside ProductName:
        # Expected order:
        # 0 TransactionID | 1 Date | 2 ProductID | 3 ProductName | 4 Quantity | 5 UnitPrice | 6 CustomerID | 7 Region
        if len(parts) > 8:
            transaction_id = parts[0].strip()
            date = parts[1].strip()
            product_id = parts[2].strip()

            # last 4 are always: Quantity, UnitPrice, CustomerID, Region
            quantity_str = parts[-4].strip()
            unitprice_str = parts[-3].strip()
            customer_id = parts[-2].strip()
            region = parts[-1].strip()

            product_name = "|".join(parts[3:-4]).strip()

        elif len(parts) == 8:
            transaction_id, date, product_id, product_name, quantity_str, unitprice_str, customer_id, region = [
                p.strip() for p in parts
            ]
        else:
            # incorrect number of fields
            continue

        # Clean ProductName: remove commas (keep the record)
        product_name = product_name.replace(",", "").strip()

        # Clean numeric fields: remove commas like "45,000"
        quantity_str = quantity_str.replace(",", "").strip()
        unitprice_str = unitprice_str.replace(",", "").strip()

        # Convert types (skip if can't convert)
        try:
            quantity = int(quantity_str)
            unit_price = float(unitprice_str)
        except (ValueError, TypeError):
            continue

        parsed.append({
            "TransactionID": transaction_id,
            "Date": date,
            "ProductID": product_id,
            "ProductName": product_name,
            "Quantity": quantity,
            "UnitPrice": unit_price,
            "CustomerID": customer_id,
            "Region": region
        })

    return parsed


def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    """
    Validates transactions and applies optional filters

    Returns: tuple (valid_transactions, invalid_count, filter_summary)
    """

    required_fields = [
        "TransactionID", "Date", "ProductID", "ProductName",
        "Quantity", "UnitPrice", "CustomerID", "Region"
    ]

    total_input = len(transactions)
    invalid_count = 0
    valid = []

    # -----------------------------
    # 1) Validate
    # -----------------------------
    for t in transactions:
        # required fields present + not blank
        missing = False
        for k in required_fields:
            if k not in t:
                missing = True
                break
            v = t.get(k)
            if v is None:
                missing = True
                break
            if isinstance(v, str) and v.strip() == "":
                missing = True
                break

        if missing:
            invalid_count += 1
            continue

        # type/value checks
        try:
            qty = int(t["Quantity"])
            price = float(t["UnitPrice"])
        except (ValueError, TypeError):
            invalid_count += 1
            continue

        if qty <= 0 or price <= 0:
            invalid_count += 1
            continue

        # ID format checks
        tid = str(t["TransactionID"]).strip()
        pid = str(t["ProductID"]).strip()
        cid = str(t["CustomerID"]).strip()

        if not tid.startswith("T"):
            invalid_count += 1
            continue
        if not pid.startswith("P"):
            invalid_count += 1
            continue
        if not cid.startswith("C"):
            invalid_count += 1
            continue

        # Region required (already checked not blank, keep explicit for clarity)
        reg = str(t["Region"]).strip()
        if reg == "":
            invalid_count += 1
            continue

        # store normalized values back
        t["Quantity"] = qty
        t["UnitPrice"] = price
        t["TransactionID"] = tid
        t["ProductID"] = pid
        t["CustomerID"] = cid
        t["Region"] = reg

        valid.append(t)

    # -----------------------------
    # 2) Print available regions + amount range (based on VALID)
    # -----------------------------
    available_regions = sorted({v["Region"] for v in valid})
    print("Available regions:", available_regions)

    if valid:
        amounts = [v["Quantity"] * v["UnitPrice"] for v in valid]
        amt_min = min(amounts)
        amt_max = max(amounts)
        print(f"Transaction amount range (valid only): min={amt_min:.2f}, max={amt_max:.2f}")
    else:
        print("Transaction amount range: N/A (no valid transactions)")

    # -----------------------------
    # 3) Apply filters
    # -----------------------------
    filtered_by_region = 0
    filtered_by_amount = 0

    current = valid

    # Region filter
    if region is not None:
        region_clean = str(region).strip()
        before = len(current)
        current = [v for v in current if v["Region"].lower() == region_clean.lower()]
        filtered_by_region = before - len(current)
        print(f"After region filter ({region_clean}): {len(current)} records")

    # Amount filters
    if min_amount is not None or max_amount is not None:
        before = len(current)

        def amount_ok(v):
            amt = v["Quantity"] * v["UnitPrice"]
            if min_amount is not None and amt < float(min_amount):
                return False
            if max_amount is not None and amt > float(max_amount):
                return False
            return True

        current = [v for v in current if amount_ok(v)]
        filtered_by_amount = before - len(current)

        print(
            "After amount filter "
            f"(min={min_amount if min_amount is not None else 'None'}, "
            f"max={max_amount if max_amount is not None else 'None'}): "
            f"{len(current)} records"
        )

    # -----------------------------
    # 4) Summary
    # -----------------------------
    filter_summary = {
        "total_input": total_input,
        "invalid": invalid_count,
        "filtered_by_region": filtered_by_region,
        "filtered_by_amount": filtered_by_amount,
        "final_count": len(current)
    }

    return current, invalid_count, filter_summary
