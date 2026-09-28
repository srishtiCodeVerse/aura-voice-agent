from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from backend.order_tools import (
    get_order_details,
    find_products_by_skin_type,
    get_all_products
)
import re


app = FastAPI(title="Aura Skincare Voice Agent")


# ---------------- CORS ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- REQUEST MODEL ----------------

class ChatRequest(BaseModel):
    message: str


# ---------------- BASIC ROUTES ----------------

@app.get("/")
def root():
    return {
        "message": "Aura Skincare AI Voice Agent is running!"
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/orders/{order_id}")
def order_details(order_id: str):
    return get_order_details(order_id)


# ---------------- ORDER ID DETECTION ----------------

def find_order_id(message: str):
    text = message.lower().strip()

    patterns = [
        r"\bord[\s-]?(\d+)\b",
        r"\border(?:\s+id)?[\s:-]*(\d+)\b",
        r"\border\s+dash\s+(\d+)\b"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return f"ORD-{match.group(1)}"

    return None


# ---------------- PRODUCT FUNCTIONS ----------------

def find_product(message: str):
    text = message.lower().strip()
    products = get_all_products()

    for product in products:
        product_name = product["name"].lower()

        if product_name in text:
            return product

    for product in products:
        product_words = [
            word
            for word in product["name"].lower().split()
            if len(word) > 2
        ]

        matches = sum(
            1 for word in product_words
            if word in text
        )

        if len(product_words) >= 2 and matches >= 2:
            return product

    return None


def product_search_reply(message: str):
    text = message.lower().strip()
    products = get_all_products()

    category_map = {
        "serum": "Serum",
        "serums": "Serum",
        "moisturizer": "Moisturizer",
        "moisturisers": "Moisturizer",
        "moisturiser": "Moisturizer",
        "cleanser": "Cleanser",
        "cleansers": "Cleanser",
        "face wash": "Cleanser",
        "facewash": "Cleanser",
        "sunscreen": "Sunscreen",
        "sunscreens": "Sunscreen",
        "acne care": "Acne Care"
    }

    selected_category = None

    for keyword, category in category_map.items():
        if keyword in text:
            selected_category = category
            break

    if not selected_category:
        return None

    search_words = [
        "show",
        "list",
        "available",
        "have",
        "products",
        "product",
        "which",
        "what"
    ]

    if not any(word in text for word in search_words):
        return None

    matches = [
        product
        for product in products
        if product["category"].lower()
        == selected_category.lower()
    ]

    if not matches:
        return None

    product_text = "\n".join(
        [
            f"• {p['name']} — ₹{p['price']}"
            for p in matches
        ]
    )

    return (
        f"Here are the Aura {selected_category} products:\n\n"
        f"{product_text}\n\n"
        "Would you like details about any product?"
    )


def product_details_reply(message: str):

    product = find_product(message)

    if not product:
        return None

    text = message.lower()

    detail_words = [
        "tell me about",
        "about",
        "details",
        "detail",
        "price",
        "cost",
        "how much",
        "what is",
        "information",
        "info",
        "describe",
        "description",
        "suitable",
        "good for",
        "use"
    ]

    if not any(word in text for word in detail_words):
        return None

    skin_types = ", ".join(product["skin_types"])

    return (
        f"Here are the details for {product['name']}:\n\n"
        f"💰 Price: ₹{product['price']}\n"
        f"🧴 Category: {product['category']}\n"
        f"✨ Description: {product['description']}\n"
        f"🌿 Suitable for: {skin_types} skin."
    )


# ---------------- RECOMMENDATIONS ----------------

def recommend_products(message: str):
    text = message.lower()

    skin_type = None

    if "oily" in text or "oil skin" in text:
        skin_type = "oily"

    elif "dry" in text:
        skin_type = "dry"

    elif "sensitive" in text:
        skin_type = "sensitive"

    elif "acne" in text or "pimple" in text:
        skin_type = "acne-prone"

    elif "combination" in text:
        skin_type = "combination"

    if not skin_type:
        return None

    products = find_products_by_skin_type(skin_type)

    if not products:
        return None

    return skin_type, products


# ---------------- SKINCARE REPLIES ----------------

def local_skincare_reply(message: str):

    text = message.lower().strip()

    search_reply = product_search_reply(message)

    if search_reply:
        return search_reply

    product_reply = product_details_reply(message)

    if product_reply:
        return product_reply

    recommendation = recommend_products(message)

    if recommendation and any(
        word in text
        for word in [
            "recommend",
            "suggest",
            "product",
            "buy",
            "which",
            "best"
        ]
    ):
        skin_type, products = recommendation

        product_text = "\n".join(
            [
                f"• {p['name']} — ₹{p['price']}"
                for p in products[:4]
            ]
        )

        return (
            f"For {skin_type} skin, here are some Aura recommendations:\n\n"
            f"{product_text}\n\n"
            "Would you like details about any of these products?"
        )

    if (
        ("oily" in text or "oil" in text)
        and (
            "acne" in text
            or "pimple" in text
            or "breakout" in text
        )
    ):
        return (
            "For oily and acne-prone skin, keep your routine simple. "
            "Use a gentle cleanser twice a day, a lightweight "
            "non-comedogenic moisturizer, and sunscreen every morning. "
            "Avoid scrubbing your skin too much or picking pimples."
        )

    if "oily" in text or "oil" in text:
        return (
            "For oily skin, use a gentle cleanser twice a day, "
            "a lightweight non-comedogenic moisturizer, and sunscreen "
            "during the daytime. Avoid over-washing your face."
        )

    if "dry" in text or "dehydrated" in text:
        return (
            "For dry skin, use a gentle cleanser, a rich hydrating "
            "moisturizer, and sunscreen during the daytime. "
            "Look for ingredients such as hyaluronic acid and ceramides."
        )

    if (
        "acne" in text
        or "pimple" in text
        or "pimples" in text
        or "breakout" in text
    ):
        return (
            "For acne-prone skin, keep your routine simple. "
            "Use a gentle cleanser, a non-comedogenic moisturizer, "
            "and sunscreen. Avoid picking or squeezing pimples."
        )

    if (
        "morning routine" in text
        or "morning skincare" in text
        or "morning skin care" in text
    ):
        return (
            "A simple morning skincare routine is: "
            "1. Gentle cleanser, "
            "2. Optional serum, "
            "3. Moisturizer, "
            "4. Sunscreen."
        )

    if (
        "night routine" in text
        or "night skincare" in text
        or "night skin care" in text
    ):
        return (
            "A simple night skincare routine is: "
            "1. Cleanser, "
            "2. Optional treatment or serum, "
            "3. Moisturizer."
        )

    if "sunscreen" in text or "spf" in text:
        return (
            "Choose a broad-spectrum sunscreen with SPF 30 or higher "
            "and apply it as the final step of your morning routine."
        )

    if "moisturizer" in text or "moisturiser" in text:
        return (
            "For oily skin, try a lightweight non-comedogenic moisturizer. "
            "For dry skin, look for a richer moisturizer with ingredients "
            "such as ceramides or hyaluronic acid."
        )

    if (
        "routine" in text
        or "skin care" in text
        or "skincare" in text
    ):
        return (
            "A simple skincare routine includes cleanser, moisturizer, "
            "and sunscreen in the morning. At night, cleanse your face "
            "and apply moisturizer."
        )

    if any(
        word in text
        for word in ["hello", "hi", "hey", "hii"]
    ):
        return (
            "Hi! I'm Aura 🌸 I can help you with Aura Skincare "
            "products, orders, delivery, returns, cancellations, "
            "and basic skincare questions."
        )

    return (
        "I can help with Aura Skincare products, orders, delivery, "
        "returns, cancellations, and basic skincare questions."
    )


# ---------------- CHAT ----------------

@app.post("/chat")
def chat(request: ChatRequest):

    message = request.message.strip()

    if not message:
        return {
            "success": False,
            "reply": "Please tell me what you would like help with."
        }

    order_id = find_order_id(message)

    if order_id:

        result = get_order_details(order_id)

        if result.get("success"):

            order = result["order"]
            text = message.lower()

            # Cancellation
            if "cancel" in text:

                if order["status"].lower() == "processing":

                    reply = (
                        f"Yes. Order {order['order_id']} is currently "
                        f"Processing, so it is eligible for cancellation. "
                        f"The product is {order['product']} and the "
                        f"order value is ₹{order['value']}."
                    )

                else:

                    reply = (
                        f"Order {order['order_id']} is currently "
                        f"{order['status']}. Orders can only be cancelled "
                        f"while they are in Processing status. "
                        f"This order cannot be cancelled."
                    )

                return {
                    "success": True,
                    "reply": reply,
                    "type": "order"
                }

            # Return
            if "return" in text:

                if order["status"].lower() == "delivered":

                    reply = (
                        f"Order {order['order_id']} is currently "
                        f"Delivered. Aura Skincare accepts returns "
                        f"within 7 days of delivery for unopened and "
                        f"unused products in their original packaging."
                    )

                else:

                    reply = (
                        f"Order {order['order_id']} is currently "
                        f"{order['status']}. Return eligibility depends "
                        f"on the delivery status and return policy."
                    )

                return {
                    "success": True,
                    "reply": reply,
                    "type": "order"
                }

            # Tracking / delivery
            if (
                "track" in text
                or "where" in text
                or "status" in text
                or "arrive" in text
                or "delivery" in text
                or "when" in text
            ):

                if order["status"].lower() == "delivered":

                    reply = (
                        f"Order {order['order_id']} has already been "
                        f"delivered. The product was {order['product']}. "
                        f"{order['notes']}"
                    )

                else:

                    reply = (
                        f"Order {order['order_id']} is currently "
                        f"{order['status']}. The product is "
                        f"{order['product']}. {order['notes']}"
                    )

                return {
                    "success": True,
                    "reply": reply,
                    "type": "order"
                }

            reply = (
                f"Your order {order['order_id']} is currently "
                f"{order['status']}. The product is "
                f"{order['product']} and the order value is "
                f"₹{order['value']}. {order['notes']}"
            )

            return {
                "success": True,
                "reply": reply,
                "type": "order"
            }

        return {
            "success": False,
            "reply": f"I couldn't find an order with ID {order_id}."
        }

    # General order request
    order_words = [
        "where is my order",
        "track my order",
        "track order",
        "order status",
        "my order",
        "order tracking"
    ]

    if any(
        word in message.lower()
        for word in order_words
    ):
        return {
            "success": True,
            "reply": (
                "Sure! Please give me your order ID, "
                "for example ORD-103."
            ),
            "type": "order_request"
        }

    # Shipping
    if (
        "shipping fee" in message.lower()
        or "delivery fee" in message.lower()
        or "shipping charge" in message.lower()
    ):
        return {
            "success": True,
            "reply": (
                "Aura Skincare offers free delivery on orders above ₹499. "
                "Orders of ₹499 or below have a ₹50 shipping fee. "
                "Standard delivery takes 3 to 5 business days."
            ),
            "type": "shipping"
        }

    reply = local_skincare_reply(message)

    return {
        "success": True,
        "reply": reply,
        "type": "skincare"
    }