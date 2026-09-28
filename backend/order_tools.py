import json
from pathlib import Path


DATA_DIR = Path(__file__).parent / "data"

ORDERS_FILE = DATA_DIR / "orders.json"
PRODUCTS_FILE = DATA_DIR / "products.json"


# =========================================================
# ORDERS
# =========================================================

def get_all_orders():
    with open(ORDERS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Supports the current combined orders.json format
    if isinstance(data, dict):
        return data.get("orders", [])

    # Also supports the old list-only format
    if isinstance(data, list):
        return data

    return []


def get_order_details(order_id):
    normalized_id = order_id.upper().strip()

    for order in get_all_orders():

        if order.get("order_id", "").upper() == normalized_id:

            return {
                "success": True,
                "order": order
            }

    return {
        "success": False,
        "message": f"Order {order_id} not found."
    }


# =========================================================
# PRODUCTS
# =========================================================

def get_all_products():

    with open(PRODUCTS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Normal products.json format
    if isinstance(data, list):
        return data

    # Also support products stored inside orders.json
    if isinstance(data, dict):
        return data.get("products", [])

    return []


def find_products_by_skin_type(skin_type):

    products = get_all_products()

    skin_type = skin_type.lower().strip()

    return [
        product
        for product in products
        if skin_type in [
            skin.lower()
            for skin in product.get("skin_types", [])
        ]
    ]