"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.

    Args:
        description: Keywords describing what the user is looking for
                     (e.g., "vintage graphic tee").
        size:        Size string to filter by, or None to skip size filtering.
                     Matching is case-insensitive (e.g., "M" matches "S/M").
        max_price:   Maximum price (inclusive), or None to skip price filtering.

    Returns:
        A list of matching listing dicts, sorted by relevance (best match first).
        Returns an empty list if nothing matches — does NOT raise an exception.

    Each listing dict has the following fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand, platform

    TODO:
        1. Load all listings with load_listings().
        2. Filter by max_price and size (if provided).
        3. Score each remaining listing by keyword overlap with `description`.
        4. Drop any listings with a score of 0 (no relevant matches).
        5. Sort by score, highest first, and return the listing dicts.

    Before writing code, fill in the Tool 1 section of planning.md.
    """
    # Start with all listings from the dataset
    listings = load_listings()
    
    # We'll collect items that pass the filters here
    filtered = []

    for item in listings:
        # Skip this item if it costs more than the user's budget
        if max_price is not None and item["price"] > max_price:
            continue
    
        # Skip this item if the size doesn't match what the user wants
        if size is not None and size.lower() not in item["size"].lower():
            continue

        # Item passed both filters — keep it
        filtered.append(item)

    # Score each item by how many description keywords appear in its text
    keywords = description.lower().split()

    scored = []
    for item in filtered:
            # Combine title, description and style tags into one searchable string
            searchable = (
                item["title"] + " " +
                item["description"] + " " +
                " ".join(item["style_tags"])
            ).lower()


            # Count how many keywords match
            score = sum(1 for word in keywords if word in searchable)


            # Only keep items that match at least one keyword
            if score > 0:
                scored.append((score, item))

    # Sort by score highest first
    scored.sort(key=lambda x: x[0], reverse=True)
        
    # Return just the item dicts, not the scores
    return [item for score, item in scored]
        


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.

    Args:
        new_item: A listing dict (the item the user is considering buying).
        wardrobe: A wardrobe dict with an 'items' key containing a list of
                  wardrobe item dicts. May be empty — handle this gracefully.

    Returns:
        A non-empty string with outfit suggestions.
        If the wardrobe is empty, offer general styling advice for the item
        rather than raising an exception or returning an empty string.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If empty: call the LLM with a prompt for general styling ideas
           (what kinds of items pair well, what vibe it suits, etc.).
        3. If not empty: format the wardrobe items into a prompt and ask
           the LLM to suggest specific outfit combinations using the new item
           and named pieces from the wardrobe.
        4. Return the LLM's response as a string.

    Before writing code, fill in the Tool 2 section of planning.md.
    """
    # Replace this with your implementation

    # Step 1: Check if the wardrobe is empty
    wardrobe_items = wardrobe.get("items", [])
    is_empty = len(wardrobe_items) == 0

    # Initialize the Groq client
    client = _get_groq_client()
    if is_empty:
        # Step 2: No wardrobe — ask LLM for general styling advice
        prompt = f"""A user is considering buying this secondhand item:

Item: {new_item['title']}
Description: {new_item['description']}
Style tags: {', '.join(new_item['style_tags'])}
Colors: {', '.join(new_item['colors'])}


They have no wardrobe entered yet. Give them 1-2 general styling ideas — 
what types of bottoms, shoes, or accessories would pair well with this item 
and what overall vibe it suits."""
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    else:
        # Step 3: Wardrobe exists — ask LLM for specific outfit combinations
        wardrobe_text = "\n".join(
            f"- {item['name']} ({item.get('color', '')})"
            for item in wardrobe_items
        )

        prompt = f"""A user is considering buying this secondhand item:
Item: {new_item['title']}
Description: {new_item['description']}
Style tags: {', '.join(new_item['style_tags'])}
Colors: {', '.join(new_item['colors'])}

Their current wardrobe includes:
{wardrobe_text}

Suggest 1-2 specific outfit combinations using the new item and named pieces
from their wardrobe. Describe the overall vibe and include one styling tip."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Generate a short, shareable outfit caption for the thrifted find.
    Args:
        outfit:   The outfit suggestion string from suggest_outfit().
        new_item: The listing dict for the thrifted item.
    Returns:
        A 2–4 sentence string usable as an Instagram/TikTok caption.
        If outfit is empty or missing, return a descriptive error message
        string — do NOT raise an exception.
    """
    # Step 1: Guard against empty or whitespace-only outfit string
    if not outfit or not outfit.strip():
        return "Error: no outfit suggestion provided — cannot generate a fit card."

    # Step 2: Build the prompt
    client = _get_groq_client()
    prompt = f"""Write a 2-4 sentence Instagram/TikTok caption for this thrifted outfit.

New item: {new_item['title']} — ${new_item['price']} on {new_item['platform']}
Outfit: {outfit}

Guidelines:
- Casual and authentic, like a real OOTD post (not a product description)
- Mention the item name, price, and platform naturally (once each)
- Capture the outfit vibe in specific terms
- Keep it to 2-4 sentences"""

    # Step 3: Call the LLM with higher temperature for variety
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0,
    )

    return response.choices[0].message.content
