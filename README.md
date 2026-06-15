# FitFindr 🛍️

A multi-tool AI agent that helps users find secondhand pieces and figure out how to wear them. The agent searches mock thrift listings, suggests outfit combinations based on the user's wardrobe, and generates a shareable Instagram-style caption.

---

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a file called `.env` in the project root and paste this inside it:
```
GROQ_API_KEY=your_key_here
```
Replace `your_key_here` with your actual key from [console.groq.com](https://console.groq.com). This file is already in `.gitignore` — never commit it.

3. Run the app:
```bash
python app.py
```

Then open the URL shown in your terminal.

---

## Project Structure

```
ai201-project2-fitfindr-starter/
│
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
│
├── utils/
│   └── data_loader.py         # Helper functions: load_listings(), get_example_wardrobe()
│
├── tests/
│   └── test_tools.py          # Pytest tests for all three tools
│
├── tools.py                   # The 3 tools: search_listings, suggest_outfit, create_fit_card
├── agent.py                   # Planning loop: run_agent()
├── app.py                     # Gradio UI: handle_query()
├── planning.md                # Spec document written before implementation
├── requirements.txt           # Python dependencies
└── .env                       # Your Groq API key (not committed)
```

---

## Tool Inventory

### search_listings(description, size, max_price)
- **Input:** description (str) — keywords describing the item; size (str | None) — size filter; max_price (float | None) — price ceiling
- **Output:** A list of matching listing dicts sorted by relevance. Each dict contains: id, title, description, category, style_tags, size, condition, price, colors, brand, platform.
- **Purpose:** Searches the mock listings dataset and returns the best matches for the user's query.

### suggest_outfit(new_item, wardrobe)
- **Input:** new_item (dict) — the top listing dict from search_listings; wardrobe (dict) — a wardrobe dict with an 'items' key containing the user's existing pieces
- **Output:** A non-empty string with 1-2 outfit suggestions naming specific wardrobe pieces, describing the overall vibe, and including a styling tip.
- **Purpose:** Uses the LLM to suggest outfit combinations based on the found item and the user's wardrobe.

### create_fit_card(outfit, new_item)
- **Input:** outfit (str) — the outfit suggestion string from suggest_outfit; new_item (dict) — the listing dict for the thrifted item
- **Output:** A 2-4 sentence Instagram/TikTok-style caption mentioning the item name, price, and platform naturally.
- **Purpose:** Uses the LLM to generate a casual, shareable outfit caption for the thrifted find.

---

## How the Planning Loop Works

1. Parse the user's query using regex to extract description, size, and max_price.
2. Call `search_listings(description, size, max_price)`. If results is empty, set an error message in the session and return early — do NOT call the next tool.
3. If results is not empty, set `session["selected_item"] = results[0]` and call `suggest_outfit(selected_item, wardrobe)`.
4. Store the outfit suggestion and call `create_fit_card(outfit_suggestion, selected_item)`.
5. Store the fit card and return the full session to the UI.

The agent's behavior changes based on what `search_listings` returns — if nothing matches, it stops and tells the user what to try differently instead of cascading with empty input.

---

## State Management

The agent uses a `session` dict to pass information between tools within one interaction:

- `session["selected_item"]` — top listing dict from `search_listings`, passed into `suggest_outfit`
- `session["outfit_suggestion"]` — outfit string from `suggest_outfit`, passed into `create_fit_card`
- `session["fit_card"]` — final caption string from `create_fit_card`, shown in the UI
- `session["error"]` — set if `search_listings` returns nothing, stops the agent early

No data is re-entered by the user between steps — everything flows through the session dict.

---

## Error Handling

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Sets session["error"] = "No listings found. Try different keywords, a higher price, or remove the size filter." and stops — does not call suggest_outfit. |
| suggest_outfit | Wardrobe is empty | Returns general styling advice for the item (what bottoms, shoes, or accessories would pair well) instead of crashing or returning empty. |
| create_fit_card | Outfit input is empty or missing | Returns "Error: no outfit suggestion provided — cannot generate a fit card." instead of raising an exception. |

**Concrete example:** Running `search_listings("designer ballgown", size="XXS", max_price=5)` returns `[]`. The agent sets the error message and returns early — the UI shows the error in the first panel and leaves the outfit and fit card panels empty.

---

## Spec Reflection

**One way the spec helped:** Writing the planning loop in `planning.md` before touching `agent.py` made the conditional logic clear — especially the early return when `search_listings` returns nothing. Without the spec, it would have been easy to accidentally cascade with empty input.

**One way implementation diverged:** The spec didn't specify how to parse the user's query into description, size, and max_price. I used regex to extract price (`\$\d+`) and size (`size \S+`) from the query string, then removed those from the description. This worked well but wasn't planned upfront.

---

## AI Usage

**Instance 1 — search_listings implementation:**
I gave Claude the Tool 1 section from planning.md (inputs, return value, failure mode) and asked it to implement the filtering and scoring logic. I verified the generated code filtered by all three parameters and handled the empty-results case before using it, then tested it with 3 queries in the terminal.

**Instance 2 — planning loop implementation:**
I gave Claude the Planning Loop, State Management, and Architecture sections from planning.md including the ASCII diagram, and asked it to implement `run_agent()` in agent.py. I verified the generated code branched on the search_listings result, stored values in the session dict, and did not call all three tools unconditionally.
