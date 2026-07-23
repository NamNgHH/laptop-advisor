# Laptop Advisor Chatbot

A Python command-line customer service chatbot that helps customers choose the right laptop.
Customers can answer in natural language (e.g. "I need something for my CS classes") instead of picking from rigid menus.

## a. Setup / Installation

### Requirements
- Python 3.10+ recommended
- Internet connection on the **first run only** (to download the MiniLM model, ~90 MB)

### Install

```bash
# 1. Clone the repo
git clone https://github.com/NamNgHH/laptop-advisor.git
cd laptop-advisor

# 2. (Optional but recommended) create a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Run

```bash
python chatbot.py
```

Type answers at each prompt. You can type `quit`, `exit`, or `bye` anytime to leave.

**Note:** The first launch loads `all-MiniLM-L6-v2` from Hugging Face into a local cache. Later runs use the cache and work offline.

## b. Approach

This chatbot is a small conversation decision tree with lightweight natural language understanding (NLU) on top.

### Conversation design
The bot asks three questions in order:

1. **Use case** — school, gaming, work, creative, or everyday
2. **Budget** — a dollar amount or vague wording like "something cheap"
3. **Portability** — whether the laptop needs to travel

It then recommends up to two matching laptops from a small in-memory catalog, optionally suggests a stretch pick slightly over budget, and prints Amazon search links for each recommendation.

### How natural language is handled
Instead of keyword menus, free-text answers are classified with **MiniLM** (`all-MiniLM-L6-v2` via `sentence-transformers`):

1. Embed the user's reply
2. Compare it to example phrases for each intent using **cosine similarity**
3. Accept the best match only if it clears a confidence threshold; otherwise re-ask

This lets the bot understand phrasing like "I want to carry it around" (portable = yes) or "money is no object" (premium budget tier) without forcing exact menu choices.

Budget numbers are handled differently: regex extracts values like `$1,200`, `1.5k`, or `2 grand`. MiniLM is only used for vague budget language with no number. Numbers are a better fit for deterministic parsing than embeddings.

### Error handling
- Low-confidence / irrelevant answers are re-asked; **3 consecutive irrelevant replies** close the chat
- Empty Enter spam is nudged; **4 consecutive blanks** close the chat
- Unrealistic budgets under $200 are rejected with a clear minimum
- `quit` / `exit` / `bye` end the session at any prompt

### Project structure

| File | Role |
|------|------|
| `chatbot.py` | Conversation flow / decision tree and CLI |
| `nlu.py` | MiniLM embedding + cosine-similarity intent matching |
| `catalog.py` | Laptop catalog + recommendation logic |
| `requirements.txt` | Python dependencies |

### Conversation flow

```
Start
 └─ Q1: What will you use it for?  ── MiniLM intent match
     ├─ unrecognized ──> clarify & re-ask (closes after 3 irrelevant)
     └─ school / gaming / work / creative / everyday
         └─ Q2: Budget?
             ├─ number in text ──> parse ($1,200 / 1.5k / etc.)
             ├─ vague wording ──> MiniLM tier (cheap / mid / premium)
             ├─ invalid / too low ──> re-ask
             └─ valid
                 └─ Q3: Portability?  ── MiniLM yes/no (portability phrases)
                     └─ Recommend top 2 (+ optional stretch pick)
                         └─ Amazon search links
                             └─ Search again?  ──> restart or exit
```
