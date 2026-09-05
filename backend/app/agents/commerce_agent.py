"""
Commerce Agent — handles product recommendations, shopping assistant queries,
upsell / cross-sell suggestions. Uses semantic text relevance + synonym matching.
"""
import re
from typing import List, Dict, Any, Optional, Set


# Keyword & Synonym Map for semantic search intent
SYNONYM_MAP: Dict[str, List[str]] = {
    "earphones": ["earphones", "earphone", "earbuds", "earbud", "airpods", "in-ear", "headphones", "headphone", "tws", "airdopes", "buds"],
    "earbud": ["earphones", "earphone", "earbuds", "earbud", "airpods", "in-ear", "headphones", "headphone", "tws", "airdopes", "buds"],
    "earbuds": ["earphones", "earphone", "earbuds", "earbud", "airpods", "in-ear", "headphones", "headphone", "tws", "airdopes", "buds"],
    "headphones": ["headphones", "headphone", "earphones", "earbud", "earbuds", "airpods", "audio", "headset"],
    "laptop": ["laptop", "laptops", "notebook", "macbook", "vivobook", "pavilion", "nitro", "pc", "computer"],
    "phone": ["phone", "phones", "smartphone", "mobile", "iphone", "galaxy", "android", "oneplus", "redmi"],
    "smartphone": ["phone", "phones", "smartphone", "mobile", "iphone", "galaxy", "android", "oneplus", "redmi"],
    "tv": ["tv", "television", "smart tv", "4k tv", "qled", "led"],
    "shoes": ["shoes", "shoe", "footwear", "sneaker", "sneakers", "running", "air max", "ultraboost"],
    "gaming": ["gaming", "rtx", "gpu", "gamer", "rog", "nitro"],
    "camera": ["camera", "photography", "mirrorless", "gopro", "eos"],
    "jeans": ["jeans", "denim", "pants", "trousers"],
    "dress": ["dress", "skirt", "women"],
    "shirt": ["shirt", "tshirt", "t-shirt", "kurta"],
    "book": ["book", "books", "novel", "read", "author", "fiction", "habits", "psychology"],
    "vacuum": ["vacuum", "dyson", "cleaner"],
    "cooker": ["cooker", "fryer", "kitchen", "stove", "pot"]
}

CATEGORY_KEYWORDS = {
    "electronics": ["phone", "smartphone", "mobile", "laptop", "computer", "tablet", "headphone", "earphone", "earbuds", "tv", "television",
                    "camera", "keyboard", "mouse", "charger", "speaker", "smart", "gaming", "airpods"],
    "fashion": ["shirt", "jeans", "dress", "shoe", "sneaker", "hoodie", "kurta", "saree", "jacket", "wear"],
    "home": ["fan", "cooler", "vacuum", "kitchen", "cookware", "furniture", "shelf", "lamp", "decor", "fryer", "stove"],
    "sports": ["cricket", "football", "yoga", "badminton", "tennis", "fitness", "gym", "running", "cycle", "mat"],
    "books": ["book", "novel", "read", "author", "fiction", "non-fiction", "self-help", "finance", "habits"],
    "beauty": ["skincare", "makeup", "perfume", "lotion", "shampoo", "moisturizer", "cream"],
}

PRICE_PATTERNS = [
    (r"under\s*[₹rs.]*\s*(\d[\d,]*)", "max"),
    (r"below\s*[₹rs.]*\s*(\d[\d,]*)", "max"),
    (r"less\s*than\s*[₹rs.]*\s*(\d[\d,]*)", "max"),
    (r"budget\s*[₹rs.]*\s*(\d[\d,]*)", "max"),
    (r"above\s*[₹rs.]*\s*(\d[\d,]*)", "min"),
    (r"more\s*than\s*[₹rs.]*\s*(\d[\d,]*)", "min"),
    (r"between\s*[₹rs.]*\s*(\d[\d,]*)\s*(?:and|to|-)\s*[₹rs.]*\s*(\d[\d,]*)", "range"),
]


def expand_query_keywords(query: str) -> Set[str]:
    """Expand query terms into a clean set of word-level synonyms."""
    words = set(re.findall(r'\b\w+\b', query.lower()))
    expanded = set(words)
    for w in words:
        if w in SYNONYM_MAP:
            expanded.update(SYNONYM_MAP[w])
    return expanded


def parse_query_intent(query: str) -> Dict[str, Any]:
    """Extract structured intent and expanded terms from shopping query."""
    query_lower = query.lower()
    raw_words = re.findall(r'\b\w+\b', query_lower)
    intent = {
        "raw_query": query,
        "categories": [],
        "price_constraint": None,
        "expanded_terms": list(expand_query_keywords(query_lower)),
        "keywords": raw_words,
    }

    # Category detection
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', query_lower):
                if cat not in intent["categories"]:
                    intent["categories"].append(cat)

    # Price extraction
    for pattern, ptype in PRICE_PATTERNS:
        m = re.search(pattern, query_lower)
        if m:
            if ptype == "range":
                lo = int(m.group(1).replace(",", ""))
                hi = int(m.group(2).replace(",", ""))
                intent["price_constraint"] = {"type": "range", "min": lo, "max": hi}
            else:
                val = int(m.group(1).replace(",", ""))
                intent["price_constraint"] = {"type": ptype, "value": val}
            break

    # Modifiers
    intent["budget_focus"] = any(w in query_lower for w in ["budget", "cheap", "affordable", "value"])
    intent["premium_focus"] = any(w in query_lower for w in ["premium", "best", "top", "pro", "ultra"])
    intent["gaming"] = any(w in query_lower for w in ["gaming", "gamer", "gpu", "rtx"])
    intent["coding"] = any(w in query_lower for w in ["coding", "programming", "developer", "work"])

    return intent


def score_product_for_query(product: Dict[str, Any], intent: Dict[str, Any]) -> float:
    """
    Score a product's TRUE semantic relevance using exact word boundary regex.
    Text relevance dominates category & ratings. Returns 0.0–1.0.
    """
    name_val = product.get("name")
    name_lower = str(name_val).lower() if name_val is not None else ""

    brand_val = product.get("brand")
    brand_lower = str(brand_val).lower() if brand_val is not None else ""

    desc_val = product.get("description")
    desc_lower = str(desc_val).lower() if desc_val is not None else ""

    tags_val = product.get("tags") or []
    tags = [str(t).lower() for t in tags_val if t is not None]

    price = product.get("price") or 0
    cat_val = product.get("category") or ""
    cat = cat_val.value if hasattr(cat_val, "value") else str(cat_val)

    expanded_terms = intent.get("expanded_terms", [])
    raw_keywords = intent.get("keywords", [])

    text_score = 0.0

    # 1. Direct Word-Boundary Match in Name / Brand (Highest Weight)
    for kw in raw_keywords:
        if len(kw) > 2:
            pat = r'\b' + re.escape(kw) + r'\b'
            if re.search(pat, name_lower):
                text_score += 0.50
            elif re.search(pat, brand_lower):
                text_score += 0.15

    # 2. Expanded Synonym Matches in Name, Tags, or Description
    for term in expanded_terms:
        if len(term) > 2:
            pat = r'\b' + re.escape(term) + r'\b'
            if re.search(pat, name_lower):
                text_score += 0.30
            elif any(re.search(pat, t) for t in tags):
                text_score += 0.25
            elif re.search(pat, desc_lower):
                text_score += 0.10

    # Cap raw text relevance score
    text_score = min(0.88, text_score)

    # CRITICAL: If there is ZERO text relevance to the query, score stays 0.0!
    if text_score == 0.0:
        return 0.0

    # 3. Category Boost ONLY if text matched
    category_boost = 0.05 if cat in intent.get("categories", []) else 0.0

    # 4. Price Constraint Adjustment
    price_score = 0.0
    pc = intent.get("price_constraint")
    if pc:
        if pc["type"] == "max":
            if price <= pc["value"]:
                price_score += 0.05
            else:
                text_score *= 0.5  # Penalize out of budget
        elif pc["type"] == "min":
            if price >= pc["value"]:
                price_score += 0.05
        elif pc["type"] == "range":
            if pc["min"] <= price <= pc["max"]:
                price_score += 0.05

    # 5. Special Intent Modifiers (Gaming, Coding)
    modifier_score = 0.0
    if intent.get("gaming") and any(re.search(r'\b' + re.escape(t) + r'\b', name_lower) or t in tags for t in ["gaming", "rtx", "rog", "nitro"]):
        modifier_score += 0.10
    if intent.get("coding") and any(t in tags or t in name_lower for t in ["coding", "laptop", "macos", "windows"]):
        modifier_score += 0.05

    # 6. Customer Rating as a Minor Tie-Breaker (Max 0.048)
    rating_tiebreaker = (product.get("rating", 4.0) / 100.0)

    final_score = text_score + category_boost + price_score + modifier_score + rating_tiebreaker
    return round(min(0.98, max(0.0, final_score)), 3)


def recommend_products(
    products: List[Dict[str, Any]],
    query: str,
    limit: int = 6,
) -> Dict[str, Any]:
    """Return semantically relevant product recommendations for a query."""
    intent = parse_query_intent(query)
    scored = []
    for p in products:
        rel_score = score_product_for_query(p, intent)
        scored.append({**p, "relevance_score": rel_score})

    # Sort strictly by relevance score descending, then by customer rating descending
    scored.sort(key=lambda x: (-x["relevance_score"], -x.get("rating", 0)))

    # Filter out products that have low relevance (below 0.15 threshold)
    relevant_products = [x for x in scored if x["relevance_score"] >= 0.15]

    has_strong_matches = len(relevant_products) > 0
    top = relevant_products[:limit] if has_strong_matches else scored[:limit]

    # Build human-readable explanation
    if has_strong_matches:
        category_str = f" in {', '.join(intent['categories'])}" if intent["categories"] else ""
        explanation = f"Found {len(relevant_products)} relevant product(s){category_str} matching '{query}'. Ranked by relevance."
    else:
        explanation = f"No direct semantic matches found for '{query}'. Showing popular alternatives across categories."

    return {
        "query": query,
        "intent": intent,
        "recommendations": top,
        "explanation": explanation,
        "total_found": len(relevant_products),
    }


def get_upsell_suggestions(product: Dict[str, Any], all_products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return upsell products (same category, higher value)."""
    cat = product.get("category")
    price = product.get("price", 0)
    upsell_ids = product.get("upsell_ids") or []

    candidates = [
        p for p in all_products
        if p["id"] in upsell_ids and p.get("price", 0) > price
    ]
    if not candidates:
        candidates = [
            p for p in all_products
            if p.get("category") == cat and p.get("price", 0) > price and p["id"] != product["id"]
        ]

    candidates.sort(key=lambda x: -x.get("rating", 0))
    return candidates[:3]


def get_crosssell_suggestions(product: Dict[str, Any], all_products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return cross-sell products (complementary categories)."""
    crosssell_ids = product.get("crosssell_ids") or []
    candidates = [p for p in all_products if p["id"] in crosssell_ids]
    if not candidates:
        price = product.get("price", 0)
        cat = product.get("category")
        candidates = [
            p for p in all_products
            if p.get("category") != cat and p.get("price", 0) < price * 0.5
        ]
    candidates.sort(key=lambda x: -x.get("popularity_score", 0))
    return candidates[:4]
