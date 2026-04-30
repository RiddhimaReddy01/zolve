"""Z-Kart marketplace endpoints."""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List, Dict, Any

from models import PurchaseRequest
from database import Database

router = APIRouter(prefix="/api/zkart", tags=["marketplace"])
db = Database()


class ProductModel:
    """Product response model."""
    def __init__(self, product: Dict[str, Any]):
        self.id = product["id"]
        self.name = product["name"]
        self.category = product["category"]
        self.base_price = product["base_price"]
        self.coin_discount_pct = product["coin_discount_pct"]
        self.coins_required = product["coins_required"]
        self.stock = product["stock"]


def _discounted_price(product: Dict[str, Any]) -> float:
    """Calculate the customer price after the Z-Kart coin discount."""
    return round(product["base_price"] * (1 - product["coin_discount_pct"] / 100), 2)


def _product_response(product: Dict[str, Any]) -> Dict[str, Any]:
    final_price = _discounted_price(product)
    bonus_value = round(product["base_price"] - final_price, 2)
    return {
        "id": product["id"],
        "name": product["name"],
        "category": product["category"],
        "base_price": product["base_price"],
        "coin_discount_pct": product["coin_discount_pct"],
        "coin_discount": round(product["base_price"] - final_price, 2),
        "coins_required": product["coins_required"],
        "stock": product["stock"],
        "final_price": final_price,
        "discounted_price": final_price,
        "image_url": product.get("image_url"),
        "description": product.get("description") or "Exclusive Z-Kart offer with boosted savings when you use Z-Coins.",
        "rating": product.get("rating", 4.6),
        "review_count": product.get("review_count", 0),
        "bonus_value": bonus_value,
        "bonus_label": f"Save ${bonus_value:.2f} when you use {product['coins_required']} Z-Coins",
        "reviews": [
            {
                "author": "Maya",
                "rating": 5,
                "text": "Amazing! I used my Z-Coins and saved 15% on top of the regular price. The redemption was super smooth. Definitely buying again!",
            },
            {
                "author": "Aarav",
                "rating": 4,
                "text": "Good value for money. The Z-Coin discount actually matters—paid way less than I would have elsewhere.",
            },
            {
                "author": "Priya",
                "rating": 5,
                "text": "Love how my financial wins turn into shopping rewards! The price breakdown shows exactly how much I saved with coins. Worth it.",
            },
            {
                "author": "Rohit",
                "rating": 5,
                "text": "First time using Z-Coins here and I'm impressed. The product arrived quickly and the savings felt real. Highly recommend!",
            },
            {
                "author": "Neha",
                "rating": 4,
                "text": "Great selection and fair pricing. The coin discount makes a tangible difference. Looking forward to using this more.",
            },
        ],
    }


@router.get("/products")
async def list_products(category: str = None):
    """List all products, optionally filtered by category.

    Args:
        category: Optional category filter (e.g., 'Food', 'Travel')

    Returns:
        List of products
    """
    try:
        products = db.get_all_products()

        if category:
            products = [p for p in products if p["category"].lower() == category.lower()]

        response_data = [_product_response(p) for p in products]
        return JSONResponse(content=response_data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/products/{product_id}")
async def get_product(product_id: int):
    """Get product details.

    Args:
        product_id: Product ID

    Returns:
        Product details
    """
    try:
        product = db.get_product(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        response_data = _product_response(product)
        return JSONResponse(content=response_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/purchase")
async def purchase_product(request: PurchaseRequest):
    """Purchase a product with coins.

    Args:
        request: PurchaseRequest with user_id, product_id, coins_to_spend

    Returns:
        dict with purchase confirmation
    """
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM products WHERE id = ?", (request.product_id,))
            product_row = cursor.fetchone()
            if not product_row:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
            product = dict(product_row)

            cursor.execute("SELECT * FROM users WHERE id = ?", (request.user_id,))
            user_row = cursor.fetchone()
            if not user_row:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            user = dict(user_row)

            if product["stock"] <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{product['name']} is out of stock",
                )

            if request.coins_to_spend != product["coins_required"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product requires exactly {product['coins_required']} coins, got {request.coins_to_spend}",
                )

            if user["coin_balance"] < product["coins_required"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient coins. Need {product['coins_required']}, have {user['coin_balance']}",
                )

            final_price = _discounted_price(product)
            new_balance = user["coin_balance"] - request.coins_to_spend
            new_stock = product["stock"] - 1

            cursor.execute(
                "UPDATE users SET coin_balance = ? WHERE id = ?",
                (new_balance, request.user_id),
            )
            cursor.execute(
                "UPDATE products SET stock = ? WHERE id = ?",
                (new_stock, request.product_id),
            )
            cursor.execute(
                """
                INSERT INTO purchases (user_id, product_id, coins_spent, price_paid)
                VALUES (?, ?, ?, ?)
                """,
                (request.user_id, request.product_id, request.coins_to_spend, final_price),
            )
            purchase_id = cursor.lastrowid
            cursor.execute(
                """
                INSERT INTO coin_transactions (user_id, amount, event_type, description)
                VALUES (?, ?, ?, ?)
                """,
                (
                    request.user_id,
                    -request.coins_to_spend,
                    "purchase",
                    f"Purchased {product['name']} for {request.coins_to_spend} coins",
                ),
            )

            # Trigger scratch card if purchase > $20
            scratch_card_triggered = False
            scratch_card_id = None
            if final_price > 20.0:
                cursor.execute(
                    """
                    INSERT INTO scratch_card_triggers (user_id, purchase_id, purchase_amount)
                    VALUES (?, ?, ?)
                    """,
                    (request.user_id, purchase_id, final_price),
                )
                scratch_card_id = cursor.lastrowid
                scratch_card_triggered = True

        response = {
            "success": True,
            "purchase_id": purchase_id,
            "product_name": product["name"],
            "coins_spent": request.coins_to_spend,
            "price_paid": final_price,
            "final_price": final_price,
            "new_balance": new_balance,
            "message": f"Successfully purchased {product['name']} with {request.coins_to_spend} coins.",
        }

        if scratch_card_triggered:
            response["scratch_card_triggered"] = True
            response["scratch_card_id"] = scratch_card_id

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/categories")
async def get_categories():
    """Get all product categories.

    Returns:
        List of category names
    """
    try:
        products = db.get_all_products()
        categories = sorted(set(p["category"] for p in products))
        return JSONResponse(content=categories)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
