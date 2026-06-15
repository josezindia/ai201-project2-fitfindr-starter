from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

# ── search_listings tests ─────────────────────────────────────────────────────

def test_search_returns_results():
    # Should find at least one match for a common item
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_empty_results():
    # Impossible query should return empty list, not crash
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []

def test_search_price_filter():
    # No result should exceed the max price
    results = search_listings("jacket", size=None, max_price=10)
    assert all(item["price"] <= 10 for item in results)

# ── suggest_outfit tests ──────────────────────────────────────────────────────

def test_suggest_outfit_with_wardrobe():
    # Should return a non-empty string with a full wardrobe
    results = search_listings("vintage graphic tee", max_price=50)
    result = suggest_outfit(results[0], get_example_wardrobe())
    assert isinstance(result, str)
    assert len(result) > 0

def test_suggest_outfit_empty_wardrobe():
    # Should return general advice, not crash
    results = search_listings("vintage graphic tee", max_price=50)
    result = suggest_outfit(results[0], get_empty_wardrobe())
    assert isinstance(result, str)
    assert len(result) > 0

# ── create_fit_card tests ─────────────────────────────────────────────────────

def test_create_fit_card_returns_caption():
    # Should return a non-empty caption string
    results = search_listings("vintage graphic tee", max_price=50)
    outfit = suggest_outfit(results[0], get_example_wardrobe())
    result = create_fit_card(outfit, results[0])
    assert isinstance(result, str)
    assert len(result) > 0

def test_create_fit_card_empty_outfit():
    # Should return error message string, not crash
    results = search_listings("vintage graphic tee", max_price=50)
    result = create_fit_card("", results[0])
    assert "Error" in result