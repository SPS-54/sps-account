from datetime import datetime

def format_thb(amount: float) -> str:
    """Formats float to Thai Baht currency format e.g. ฿1,250,000.00"""
    return f"฿{amount:,.2f}"

def format_thai_date(date_str: str) -> str:
    """Converts YYYY-MM-DD to Thai Buddhist Era Date (e.g., 22 ส.ค. 2569)"""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        thai_months = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
        year_be = dt.year + 543
        return f"{dt.day} {thai_months[dt.month - 1]} {year_be}"
    except Exception:
        return date_str
