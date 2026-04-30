"""Z-Kart marketplace endpoints."""

from fastapi import APIRouter, HTTPException, status
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
    }


@router.get("/products", response_model=List[Dict[str, Any]])
async def list_products(category: str = None) -> List[Dict[str, Any]]:
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

        return [_product_response(p) for p in products]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/products/{product_id}", response_model=Dict[str, Any])
async def get_product(product_id: int) -> Dict[str, Any]:
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

        return _product_response(product)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/purchase", response_model=Dict[str, Any])
async def purchase_product(request: PurchaseRequest) -> Dict[str, Any]:
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
                scratch_card_id = db.add_scratch_card_trigger(request.user_id, purchase_id, final_price)
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


@router.get("/categories", response_model=List[str])
async def get_categories() -> List[str]:
    """Get all product categories.

    Returns:
        List of category names
    """
    try:
        products = db.get_all_products()
        categories = sorted(set(p["category"] for p in products))
        return categories
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
