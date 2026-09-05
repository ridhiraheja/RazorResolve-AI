from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.database import get_db
from app.models import Product, ProductCategory
from app.agents.commerce_agent import recommend_products, get_upsell_suggestions, get_crosssell_suggestions
from typing import Optional

router = APIRouter(prefix="/products", tags=["products"])


def _product_to_dict(p: Product) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "category": p.category,
        "price": p.price,
        "original_price": p.original_price,
        "brand": p.brand,
        "rating": p.rating,
        "review_count": p.review_count,
        "stock": p.stock,
        "popularity_score": p.popularity_score,
        "conversion_rate": p.conversion_rate,
        "tags": p.tags or [],
        "upsell_ids": p.upsell_ids or [],
        "crosssell_ids": p.crosssell_ids or [],
        "description": p.description,
        "image_url": p.image_url,
    }


@router.get("")
async def list_products(
    category: Optional[str] = None,
    limit: int = Query(40, le=100),
    db: AsyncSession = Depends(get_db),
):
    q = select(Product).order_by(desc(Product.popularity_score))
    if category:
        try:
            q = q.where(Product.category == ProductCategory(category))
        except ValueError:
            pass
    q = q.limit(limit)
    result = await db.execute(q)
    products = result.scalars().all()
    return {"products": [_product_to_dict(p) for p in products]}


@router.get("/{product_id}")
async def get_product(product_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")

    all_r = await db.execute(select(Product))
    all_products = [_product_to_dict(x) for x in all_r.scalars().all()]
    pd = _product_to_dict(p)

    return {
        **pd,
        "upsell_suggestions": get_upsell_suggestions(pd, all_products),
        "crosssell_suggestions": get_crosssell_suggestions(pd, all_products),
    }


@router.post("/recommend")
async def get_recommendations(body: dict, db: AsyncSession = Depends(get_db)):
    query = body.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")

    limit = body.get("limit", 5)
    result = await db.execute(select(Product).order_by(desc(Product.popularity_score)))
    all_products = [_product_to_dict(p) for p in result.scalars().all()]

    return recommend_products(all_products, query, limit=limit)
