"""eGain take-home: laptop recommendation chatbot (CLI).

Decision flow:
  1. What will you use the laptop for?  (MiniLM free-text intent detection)
  2. What's your budget?                (number parsing with error handling)
  3. Do you need it portable?           (MiniLM yes/no detection)
  -> Recommend from catalog, offer to restart.

Error handling examples:
  - Free-text answers that MiniLM can't confidently match are re-asked
    with a hint (instead of guessing wrong).
  - Budget input strips $ and commas, rejects non-numbers and
    unrealistically low amounts.
"""

import re
from urllib.parse import quote_plus

from catalog import recommend
from nlu import YES_NO_PORTABILITY, detect_budget_tier, detect_use_case, detect_yes_no

# Dollar amounts used when the user gives a vague budget instead of a number
BUDGET_TIERS = {"budget": 600, "mid": 1100, "premium": 2500}

BOT = "Bot:"
MAX_BLANKS = 4
MAX_IRRELEVANT = 3


def close_for_irrelevant_answers():
    print(f"{BOT} I'm having trouble understanding your answers, so I'll close the chat for now. "
          "Please come back when you're ready!")
    raise SystemExit


def ask(prompt: str) -> str:
    """Prompt the user and always return a non-empty reply.

    Error handling: blank replies get a nudge instead of being sent to
    the NLU; after MAX_BLANKS blanks in a row we assume the user left
    and end the chat gracefully.
    """
    print(f"{BOT} {prompt}")
    blanks = 0
    while True:
        reply = input("You: ").strip()
        if reply.lower() in ("quit", "exit", "bye"):
            print(f"{BOT} Thanks for stopping by. Goodbye!")
            raise SystemExit
        if reply:
            return reply
        blanks += 1
        if blanks >= MAX_BLANKS:
            print(f"{BOT} Looks like you stepped away — ending the chat for now. Come back anytime!")
            raise SystemExit
        if blanks < 3:
            print(f"{BOT} I didn't catch anything — please type a reply.")
        else:
            print(f"{BOT} Still there? Last chance — type an answer or I'll close the chat.")


def ask_use_case() -> str:
    reply = ask("What will you mainly use the laptop for? (e.g. school, gaming, work, video editing, everyday stuff)")
    irrelevant = 0
    while True:
        intent, score = detect_use_case(reply)
        if intent:
            return intent
        irrelevant += 1
        if irrelevant >= MAX_IRRELEVANT:
            close_for_irrelevant_answers()
        reply = ask("Hmm, I didn't quite catch that. Could you describe it differently? "
                    "For example: 'classes and homework', 'playing games', or 'editing videos'.")


def ask_budget() -> float:
    reply = ask("Got it! What's your budget in USD? (e.g. 800, $1,200, or 'something cheap')")
    irrelevant = 0
    while True:
        budget = parse_budget(reply)

        if budget is None:
            # No number in the reply -> try vague wording ("something cheap")
            tier, _ = detect_budget_tier(reply)
            if tier:
                budget = BUDGET_TIERS[tier]
                print(f"{BOT} Okay, I'll aim for around ${budget:,.0f}.")

        if budget is None:
            irrelevant += 1
            if irrelevant >= MAX_IRRELEVANT:
                close_for_irrelevant_answers()
            reply = ask("Sorry, I didn't get a budget from that — try a number like 800 or $1,200, "
                        "or say something like 'cheap' or 'money is no object'.")
        elif budget < 200:
            # Error handling #2: valid number but unrealistic
            reply = ask("Laptops in our catalog start around $200. Could you give a budget of at least $200?")
        else:
            return budget


def ask_portability() -> bool:
    reply = ask("Do you need it to be light and portable, or will it mostly stay in one place?")
    irrelevant = 0
    while True:
        answer, score = detect_yes_no(reply, YES_NO_PORTABILITY)
        if answer:
            return answer == "yes"
        irrelevant += 1
        if irrelevant >= MAX_IRRELEVANT:
            close_for_irrelevant_answers()
        reply = ask("Sorry — just to confirm, is portability important to you? (yes/no)")


def ask_search_again() -> bool:
    reply = ask("Would you like to search again with different answers?")
    irrelevant = 0
    while True:
        answer, _ = detect_yes_no(reply)
        if answer:
            return answer == "yes"
        irrelevant += 1
        if irrelevant >= MAX_IRRELEVANT:
            close_for_irrelevant_answers()
        reply = ask("Sorry, would you like to search again? Please answer yes or no.")


def present_results(use_case: str, budget: float, portable: bool):
    picks, stretch = recommend(use_case, budget, portable)

    if not picks and not stretch:
        print(f"{BOT} I couldn't find a {use_case} laptop under ${budget:,.0f}. "
              "You may want to raise the budget a bit — try me again!")
        return

    if picks:
        print(f"{BOT} Based on {use_case} use and a ${budget:,.0f} budget, here's what I'd recommend:\n")
        for i, l in enumerate(picks, 1):
            tag = "portable" if l["portable"] else "less portable"
            print(f"  {i}. {l['name']} — ${l['price']} ({tag})")
            print(f"     {l['blurb']}\n")

    if stretch:
        print(f"{BOT} If you can stretch a little: {stretch['name']} at ${stretch['price']} — {stretch['blurb']}")

    products = picks + ([stretch] if stretch else [])
    print(f"\n{BOT} Amazon search links:")
    for laptop in products:
        query = quote_plus(f"{laptop['name']} laptop")
        print(f"  {laptop['name']}: https://www.amazon.com/s?k={query}")


def parse_budget(text: str):
    text = text.lower().replace(",", "")
    m = re.search(r"\$?\s*(\d+(?:\.\d+)?)\s*(k|grand)?", text)
    if not m:
        return None
    value = float(m.group(1))
    if m.group(2):          # "1.5k" or "2 grand"
        value *= 1000
    return value

def main():
    print("=" * 60)
    print("  eGain Laptop Advisor  (type 'quit' anytime to exit)")
    print("=" * 60)
    print(f"{BOT} Hi! I'm here to help you find the right laptop.")

    while True:
        use_case = ask_use_case()
        print(f"{BOT} Nice — sounds like a {use_case} laptop.")
        budget = ask_budget()
        portable = ask_portability()
        present_results(use_case, budget, portable)

        if not ask_search_again():
            print(f"{BOT} Happy laptop hunting. Goodbye!")
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nBot: Goodbye!")
