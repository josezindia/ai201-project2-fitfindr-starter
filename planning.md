# FitFindr — planning.md

---

## Tools

The agent uses three tools, each with a defined interface, called in sequence based on what the previous tool returns.

### Tool 1: search_listings

**What it does:**
Searches the mock listings dataset for items matching the user's description, filtered by size and price, and returns a sorted list of matches.

**Input parameters:**
- `description` (str): Keywords describing what the user is looking for (e.g. "vintage graphic tee")
- `size` (str | None): Size to filter by, or None to skip size filtering
- `max_price` (float | None): Maximum price inclusive, or None to skip price filtering

**What it returns:**
A list of matching listing dicts sorted by relevance (best match first). Each dict contains: id (str), title (str), description (str), category (str), style_tags (list of strings), size (str), condition (str), price (float), colors (list of strings), brand (str or None), platform (str).

**What happens if it fails or returns nothing:**
Returns an empty list. The agent stops, tells the user no listings were found, and suggests they try different keywords, a higher price, or no size filter.

---

### Tool 2: suggest_outfit

**What it does:**
Suggests 1-2 complete outfits based on a thrifted item and the user's existing wardrobe.

**Input parameters:**
- `new_item` (dict): The listing dict for the item the user is considering buying
- `wardrobe` (dict): A wardrobe dict with an 'items' key containing the user's existing pieces

**What it returns:**
A non-empty string with 1-2 outfit suggestions. Each suggestion names specific wardrobe pieces to pair with the new item, describes the overall vibe (e.g. "90s grunge", "clean casual"), and includes one styling tip (e.g. "tuck the front corner slightly for shape"). If the wardrobe is empty, returns general styling advice instead (e.g. what types of bottoms or shoes would pair well).

**What happens if it fails or returns nothing:**
If the wardrobe is empty, the agent returns general styling advice for the item instead of crashing or returning an empty string.

---

### Tool 3: create_fit_card

**What it does:**
Generates a short, shareable Instagram/TikTok-style caption for the thrifted outfit.

**Input parameters:**
- `outfit` (str): The outfit suggestion string from suggest_outfit()
- `new_item` (dict): The listing dict for the thrifted item

**What it returns:**
A 2-4 sentence string written like a real OOTD caption. It mentions the item name, price, and platform once each, describes the outfit vibe in specific terms, and sounds casual and authentic — not like a product description. Example: "thrifted this faded band tee off depop for $22 and honestly it was made for my wide-legs 🖤 full look in my stories"

**What happens if it fails or returns nothing:**
If outfit is empty or missing, return a descriptive error message string instead of raising an exception.

---

## Planning Loop

**How does your agent decide which tool to call next?**

1. Call `search_listings(description, size, max_price)` — searches the listings data and returns a sorted list of matches based on what the user typed.
2. Check if results is empty. If yes, set `session["error"] = "No listings found. Try different keywords, a higher price, or remove the size filter."` and stop — do NOT move to the next tool.
3. If results is not empty, grab the best match with `session["selected_item"] = results[0]` and call `suggest_outfit(selected_item, wardrobe)` — this builds 1-2 outfit ideas using the found item and the user's wardrobe.
4. Store the outfit suggestion with `session["outfit_suggestion"] = result` and call `create_fit_card(outfit_suggestion, selected_item)` — this turns the outfit into a short Instagram-style caption.
5. Store the caption with `session["fit_card"] = result` and return the full session to the UI — the three panels show the top listing, outfit idea, and caption.

---

## State Management

**How does information from one tool get passed to the next?**

The agent uses a `session` dict to store and pass information between tools during one interaction:

- `session["selected_item"]` — the top listing dict returned by `search_listings`. This gets passed directly into `suggest_outfit` so the user doesn't have to re-enter it.
- `session["outfit_suggestion"]` — the outfit suggestion string returned by `suggest_outfit`. This gets passed directly into `create_fit_card`.
- `session["fit_card"]` — the final caption string returned by `create_fit_card`. This is what the user sees in the last output panel.
- `session["error"]` — set if `search_listings` returns nothing. Tells the user what went wrong and stops the agent early.

---

## Error Handling

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Sets session["error"] = "No listings found. Try different keywords, a higher price, or remove the size filter." and stops — does not call the next tool. |
| suggest_outfit | Wardrobe is empty | Returns general styling advice for the item (what bottoms, shoes, or accessories would pair well) instead of crashing or returning empty. |
| create_fit_card | Outfit input is empty or missing | Returns a descriptive error message string like "Unable to generate fit card — outfit description was empty." instead of raising an exception. |

---

## Architecture

```
[User]
    │
    │ query (description, size, max_price, wardrobe)
    ▼
[Planning Loop]
    │
    │ search_listings(description, size, max_price)
    ▼
[search_listings] ──── results=[] ────► [session: error="No listings found..."] ──► [STOP → User sees error]
    │
    │ results=[item, ...]
    ▼
[Session State: selected_item = results[0]]
    │
    │ suggest_outfit(selected_item, wardrobe)
    ▼
[suggest_outfit] ──── wardrobe empty ────► general styling advice string
    │
    │ outfit suggestion string
    ▼
[Session State: outfit_suggestion = result]
    │
    │ create_fit_card(outfit_suggestion, selected_item)
    ▼
[create_fit_card] ──── outfit empty ────► error message string
    │
    │ caption string
    ▼
[Session State: fit_card = result]
    │
    ▼
[UI: 3 panels]
    ├── Top listing found → selected_item
    ├── Outfit idea → outfit_suggestion
    └── Your fit card → fit_card
```

---

## AI Tool Plan

**Milestone 3 — Individual tool implementations:**
I will use Claude. I will give it the Tool 1, 2, and 3 sections from planning.md (inputs, return values, failure modes) one tool at a time and ask it to implement each function in tools.py using load_listings() from the data loader. Before using the generated code I will check that it matches the parameters I defined, handles the failure mode I described, and test it with at least 3 queries in the terminal.

**Milestone 4 — Planning loop and state management:**
I will use Claude. I will give it the Planning Loop, State Management, and Architecture sections from planning.md including the diagram, and ask it to implement run_agent() in agent.py. Before using the generated code I will check that it branches on the search_listings result, stores values in the session dict, and does not call all three tools unconditionally.

---

## A Complete Interaction (Step by Step)

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
Call `search_listings("vintage graphic tee", size=None, max_price=30.0)`. It searches the listings data and returns a sorted list of matches. The agent sets `session["selected_item"] = results[0]` — the top match: "Faded Band Tee — $22, Depop, Good condition."

**Step 2:**
Call `suggest_outfit(session["selected_item"], wardrobe)`. The agent passes the Faded Band Tee from Step 1 and the user's wardrobe containing baggy jeans and chunky sneakers. It returns a string like "Pair this with your wide-leg jeans and chunky sneakers for a classic 90s grunge look." The agent sets `session["outfit_suggestion"] = result`.

**Step 3:**
Call `create_fit_card(session["outfit_suggestion"], session["selected_item"])`. The agent passes the outfit suggestion from Step 2 and the Faded Band Tee listing from Step 1. It returns a short Instagram-style caption. The agent sets `session["fit_card"] = result`.

**Final output to user:**
The UI displays three panels:
- Top listing found → "Faded Band Tee — $22, Depop, Good condition"
- Outfit idea → "Pair this with your wide-leg jeans and chunky sneakers for a classic 90s grunge look."
- Your fit card → "thrifted this faded band tee off depop for $22 and honestly it was made for my wide-legs 🖤 full look in my stories"