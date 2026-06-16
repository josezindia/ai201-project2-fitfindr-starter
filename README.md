# FitFindr 🛍️

FitFindr is a multi-tool AI agent that helps you find secondhand clothing and figure out how to wear it. Type what you're looking for, and the agent searches thrift listings, suggests outfits using your wardrobe, and writes you a shareable caption — all in one query.

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
Replace `your_key_here` with your actual key from [console.groq.com](https://console.groq.com). No credit card required. This file is already in `.gitignore` — never commit it.

3. Run the app:
```bash
python app.py
```

Open the URL shown in your terminal.

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
│   └── data_loader.py         # load_listings(), get_example_wardrobe(), get_empty_wardrobe()
│
├── tests/
│   └── test_tools.py          # Pytest tests for all three tools (7 tests)
│
├── tools.py                   # The 3 tools: search_listings, suggest_outfit, create_fit_card
├── agent.py                   # Planning loop: run_agent()
├── app.py                     # Gradio UI: handle_query()
├── planning.md                # Spec written before implementation
├── requirements.txt           # Python dependencies
└── .env                       # Groq API key 
```

---

## Tool Inventory

### `search_listings(description, size, max_price)`
- **description** (str): Keywords describing what the user wants, e.g. "vintage graphic tee"
- **size** (str | None): Size filter, e.g. "M" — or None to skip
- **max_price** (float | None): Price ceiling — or None to skip
- **Returns:** A list of matching listing dicts sorted by keyword relevance. Each dict has: id, title, description, category, style_tags, size, condition, price, colors, brand, platform. Returns an empty list if nothing matches.

### `suggest_outfit(new_item, wardrobe)`
- **new_item** (dict): The top listing dict from search_listings
- **wardrobe** (dict): A wardrobe dict with an `items` key containing the user's existing pieces
- **Returns:** A string with 1-2 outfit combinations naming specific wardrobe pieces, the overall vibe, and a styling tip. If the wardrobe is empty, returns general styling advice instead.

### `create_fit_card(outfit, new_item)`
- **outfit** (str): The outfit suggestion string from suggest_outfit
- **new_item** (dict): The listing dict for the thrifted item
- **Returns:** A 2-4 sentence Instagram/TikTok-style caption — casual, authentic, mentioning the item name, price, and platform once each.

---

## How the Planning Loop Works

When the user submits a query, the agent runs these steps in order:

1. Parse the query using regex to extract a description, size, and max_price.
2. Call `search_listings` with those values. If the result is empty, store an error message in `session["error"]` and return early — `suggest_outfit` is never called with empty input.
3. If results exist, store the top result in `session["selected_item"]` and call `suggest_outfit`.
4. Store the outfit suggestion in `session["outfit_suggestion"]` and call `create_fit_card`.
5. Store the caption in `session["fit_card"]` and return the session to the UI.

The agent only moves to the next tool if the previous one returned something useful. The branch at step 2 is the only conditional — everything else is a straight pipeline.

---

## State Management

The agent uses a `session` dict as its single source of truth. Each tool reads from and writes to this dict:

- `session["selected_item"]` — set after search_listings, passed into suggest_outfit
- `session["outfit_suggestion"]` — set after suggest_outfit, passed into create_fit_card
- `session["fit_card"]` — set after create_fit_card, displayed in the third UI panel
- `session["error"]` — set if search_listings returns nothing, causes early return

The user never has to re-enter information between steps — it all flows through the session.

---

## Error Handling

| Tool | Failure mode | What happens |
|------|-------------|--------------|
| search_listings | No results match the query | Sets `session["error"]` and returns early. The UI shows the error in panel 1; panels 2 and 3 stay empty. |
| suggest_outfit | Wardrobe is empty | Returns general styling advice (e.g. what types of bottoms or shoes pair well) instead of crashing. |
| create_fit_card | Outfit string is empty or missing | Returns `"Error: no outfit suggestion provided — cannot generate a fit card."` instead of raising an exception. |

**Example from testing:** Querying "designer ballgown size XXS under $5" returns an empty list from search_listings. The agent sets the error message, skips suggest_outfit and create_fit_card entirely, and the UI displays: *"No listings found. Try different keywords, a higher price, or remove the size filter."*

---

## Spec Reflection

**One way the spec helped:** Writing the planning loop in `planning.md` before touching `agent.py` made the early-return logic clear upfront. Without it, it would have been easy to accidentally call suggest_outfit with an empty item and get a confusing LLM response instead of a useful error.

**One way implementation diverged:** The spec didn't define how to parse the user's natural language query into structured parameters. I ended up using regex to extract price (`\$\d+`) and size (`size \S+`) from the query string and stripping those from the description. It works well but wasn't planned — it was a decision made during implementation.

---

## AI Usage

**Instance 1 — search_listings implementation:**
I gave Claude the Tool 1 section from planning.md (inputs, return value, failure mode) and asked it to generate the filtering and scoring logic. I verified the output matched my spec — filtering by all three parameters, handling empty results — before running it, then tested it with 3 queries in the terminal.

**Instance 2 — suggest_outfit and create_fit_card implementation:**
I gave Claude the Tool 2 and Tool 3 sections from planning.md and asked it to generate the LLM prompt logic for both tools. I checked each handled its failure mode (empty wardrobe, empty outfit string) before using it, then tested each independently in the terminal.

**Instance 3 — planning loop implementation:**
I gave Claude the Planning Loop, State Management, and Architecture sections from planning.md including the ASCII diagram, and asked it to generate `run_agent()` in agent.py. I verified the output branched on the search_listings result, stored values in the session dict correctly, and did not call all three tools unconditionally.

**Instance 4 — pytest tests:**
I gave Claude the three tool specs and asked it to generate pytest tests covering each failure mode. I ran all 7 tests with `pytest tests/` and confirmed they passed before submitting.