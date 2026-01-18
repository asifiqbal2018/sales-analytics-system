import requests


BASE_URL = "https://dummyjson.com/products"


def fetch_all_products():
    """
    Fetches all products from DummyJSON API

    Returns: list of product dictionaries

    Requirements:
    - Fetch all available products (use limit=100)
    - Handle connection errors with try-except
    - Return empty list if API fails
    - Print status message (success/failure)
    """
    try:
        url = f"{BASE_URL}?limit=100"
        resp = requests.get(url, timeout=15)

        if resp.status_code != 200:
            print(f"API Fetch Failed: Status Code {resp.status_code}")
            return []

        data = resp.json()
        products = data.get("products", [])

        # Normalize to expected fields only
        cleaned = []
        for p in products:
            cleaned.append({
                "id": p.get("id"),
                "title": p.get("title"),
                "category": p.get("category"),
                "brand": p.get("brand"),
                "price": p.get("price"),
                "rating": p.get("rating"),
            })

        print(f"API Fetch Success: {len(cleaned)} products loaded")
        return cleaned

    except requests.exceptions.RequestException as e:
        print(f"API Fetch Failed: {e}")
        return []
    except Exception as e:
        print(f"API Fetch Failed (unexpected): {e}")
        return []


def create_product_mapping(api_products):
    """
    Creates a mapping of product IDs to product info

    Returns:
    {
        1: {'title': 'iPhone 9', 'category': 'smartphones', 'brand': 'Apple', 'rating': 4.69},
        ...
    }
    """
    mapping = {}
    for p in api_products:
        try:
            pid = p.get("id")
            if pid is None:
                continue
            pid = int(pid)

            mapping[pid] = {
                "title": p.get("title"),
                "category": p.get("category"),
                "brand": p.get("brand"),
                "rating": p.get("rating")
            }
        except (ValueError, TypeError):
            continue

    return mapping


def _extract_numeric_product_id(product_id_str):
    """
    Extract numeric part from ProductID.
    Examples:
      'P101' -> 101
      'P5'   -> 5
    Returns int or None if not possible.
    """
    if product_id_str is None:
        return None

    s = str(product_id_str).strip()
    if not s:
        return None

    # Expect it to start with 'P', but handle gracefully anyway
    if s[0].upper() == "P":
        s = s[1:]

    # keep only digits (extra safety)
    digits = "".join(ch for ch in s if ch.isdigit())
    if not digits:
        return None

    try:
        return int(digits)
    except ValueError:
        return None


def enrich_sales_data(transactions, product_mapping):
    """
    Enriches transaction data with API product information.

    - Extract numeric ID from ProductID (P101 → 101)
    - If found in product_mapping, add API fields and API_Match=True
    - Else set API_Match=False and API fields None
    - Save enriched data to 'data/enriched_sales_data.txt'
    """
    enriched = []

    for t in transactions:
        # Make a copy so we don’t mutate original list unexpectedly
        row = dict(t)

        try:
            numeric_id = _extract_numeric_product_id(row.get("ProductID"))
            api_info = product_mapping.get(numeric_id) if numeric_id is not None else None

            if api_info:
                row["API_Category"] = api_info.get("category")
                row["API_Brand"] = api_info.get("brand")
                row["API_Rating"] = api_info.get("rating")
                row["API_Match"] = True
            else:
                row["API_Category"] = None
                row["API_Brand"] = None
                row["API_Rating"] = None
                row["API_Match"] = False

        except Exception:
            # Any unexpected issue should not crash enrichment
            row["API_Category"] = None
            row["API_Brand"] = None
            row["API_Rating"] = None
            row["API_Match"] = False

        enriched.append(row)

    # Save to file as required
    save_enriched_data(enriched, filename="data/enriched_sales_data.txt")

    return enriched


def save_enriched_data(enriched_transactions, filename="data/enriched_sales_data.txt"):
    """
    Saves enriched transactions back to file

    Expected File Format (pipe delimited):
    TransactionID|Date|ProductID|ProductName|Quantity|UnitPrice|CustomerID|Region|API_Category|API_Brand|API_Rating|API_Match
    ...

    Requirements:
    - Create output file with all original + new fields
    - Use pipe delimiter
    - Handle None values appropriately (write blank)
    """
    header = [
        "TransactionID", "Date", "ProductID", "ProductName",
        "Quantity", "UnitPrice", "CustomerID", "Region",
        "API_Category", "API_Brand", "API_Rating", "API_Match"
    ]

    def norm(v):
        # Write blanks for None, keep True/False as-is, numbers as-is
        if v is None:
            return ""
        return str(v)

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("|".join(header) + "\n")
            for t in enriched_transactions:
                row = [norm(t.get(col)) for col in header]
                f.write("|".join(row) + "\n")

        print(f"Enriched file saved: {filename}")

    except Exception as e:
        print(f"Failed to save enriched file: {e}")
