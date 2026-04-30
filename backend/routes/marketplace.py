"""Z-Kart marketplace endpoints."""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any

from models import PurchaseRequest, ErrorResponse
from database import Database
from exceptions import InsufficientCoinsError, ProductError, UserNotFoundError

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

        return [
            {
                "id": p["id"],
                "name": p["name"],
                "category": p["category"],
                "base_price": p["base_price"],
                "coin_discount_pct": p["coin_discount_pct"],
                "coins_required": p["coins_required"],
                "stock": p["stock"],
            }
            for p in products
        ]
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

        return {
            "id": product["id"],
            "name": product["name"],
            "category": product["category"],
            "base_price": product["base_price"],
            "coin_discount_pct": product["coin_discount_pct"],
            "coins_required": product["coins_required"],
            "stock": product["stock"],
        }
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
        # Validate product exists
        product = db.get_product(request.product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        # Validate user
        user = db.get_user(request.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Check balance
        if user["coin_balance"] < request.coins_to_spend:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient coins. Need {request.coins_to_spend}, have {user['coin_balance']}",
            )

        # Validate coins match product requirement
        if request.coins_to_spend != product["coins_required"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product requires {product['coins_required']} coins, got {request.coins_to_spend}",
            )

        # Deduct coins
        db.update_user_balance(request.user_id, -request.coins_to_spend)

        # Record purchase
        purchase_id = db.record_purchase(
            request.user_id,
            request.product_id,
            request.coins_to_spend,
            product["base_price"],
        )

        # Log transaction
        db.add_coin_transaction(
            request.user_id,
            -request.coins_to_spend,
            "purchase",
            f"Purchased {product['name']} for {request.coins_to_spend} coins",
        )

        return {
            "success": True,
            "purchase_id": purchase_id,
            "product_name": product["name"],
            "coins_spent": request.coins_to_spend,
            "new_balance": user["coin_balance"] - request.coins_to_spend,
            "message": f"Successfully purchased {product['name']}!",
        }

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
