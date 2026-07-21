# eGain Laptop Advisor Chatbot

A command-line customer service chatbot that helps a customer choose the right laptop.
Instead of rigid menus, it uses **MiniLM sentence embeddings** (`all-MiniLM-L6-v2`) so the
customer can answer in natural language ("I need something for my CS classes") and the bot
maps it to an intent by cosine similarity.

## Setup

```bash
pip install -r requirements.txt
python chatbot.py
```

The first run downloads the MiniLM model (~90 MB).

## Conversation flow (decision tree)

```
Start
 └─ Q1: What will you use it for?  ── MiniLM intent match
     ├─ unrecognized ──> clarify & re-ask (2 retries, then default to "everyday")
     └─ school / gaming / work / creative / everyday
         └─ Q2: Budget?
             ├─ not a number ──> re-ask with example format
             ├─ < $200 ──> explain minimum & re-ask
             └─ valid
                 └─ Q3: Portability needed?  ── MiniLM yes/no match
                     └─ Recommend top 2 in budget (+ optional "stretch" pick)
                         └─ Show Amazon search links
                             └─ Search again?  ──> restart or exit
```

## Error handling examples

1. **Unrecognized free text** — if MiniLM's best similarity score is below a
   threshold, the bot doesn't guess; it re-asks with example phrasings, and
   after 2 retries falls back to a safe default.
2. **Invalid budget** — accepts `$1,200`, `800`, `1000 usd`; rejects
   non-numbers and unrealistically low values with a helpful message.
3. Typing `quit` / `exit` at any prompt ends the chat gracefully.
4. Three consecutive irrelevant answers at one question close the chat
   gracefully; four consecutive blank replies do the same.

## Approach

- `chatbot.py` — conversation flow / decision tree
- `nlu.py` — MiniLM embedding + cosine-similarity intent classification
- `catalog.py` — small in-memory laptop catalog + recommendation logic

The links are Amazon search queries generated from each laptop name, rather
than fixed product pages, so they remain useful when listings change.
