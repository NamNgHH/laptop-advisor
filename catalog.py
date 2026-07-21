"""Small in-memory laptop catalog used for recommendations."""

LAPTOPS = [
    {
        "name": "Acer Aspire 5",
        "price": 550,
        "use_cases": ["school", "everyday"],
        "portable": True,
        "blurb": "Reliable budget all-rounder for classes, browsing, and docs.",
    },
    {
        "name": "MacBook Air M3",
        "price": 1099,
        "use_cases": ["school", "everyday", "work"],
        "portable": True,
        "blurb": "Ultra-light with all-day battery. Great for students and professionals.",
    },
    {
        "name": "Lenovo ThinkPad T14",
        "price": 1200,
        "use_cases": ["work"],
        "portable": True,
        "blurb": "Business workhorse with a famously good keyboard and durability.",
    },
    {
        "name": "ASUS TUF Gaming A15",
        "price": 900,
        "use_cases": ["gaming"],
        "portable": False,
        "blurb": "Budget gaming with a dedicated GPU that handles most modern titles.",
    },
    {
        "name": "Razer Blade 14",
        "price": 2200,
        "use_cases": ["gaming", "creative"],
        "portable": True,
        "blurb": "Premium thin-and-light gaming laptop, strong enough for creative work too.",
    },
    {
        "name": "MacBook Pro 14 M3 Pro",
        "price": 1999,
        "use_cases": ["creative", "work"],
        "portable": True,
        "blurb": "Top-tier display and performance for video/photo editing and dev work.",
    },
    {
        "name": "HP Victus 15",
        "price": 700,
        "use_cases": ["gaming", "everyday"],
        "portable": False,
        "blurb": "Entry-level gaming laptop that doubles as an everyday machine.",
    },
]


def recommend(use_case: str, budget: float, wants_portable: bool):
    """Return (best_matches, stretch_pick).

    best_matches: laptops matching use case within budget, sorted by fit.
    stretch_pick: best laptop for the use case slightly above budget (or None).
    """
    matches = [l for l in LAPTOPS if use_case in l["use_cases"]]

    in_budget = [l for l in matches if l["price"] <= budget]
    # Prefer portability match, then higher price (better machine) within budget
    in_budget.sort(key=lambda l: (l["portable"] == wants_portable, l["price"]), reverse=True)

    stretch = None
    over = [l for l in matches if budget < l["price"] <= budget * 1.25]
    if over:
        stretch = min(over, key=lambda l: l["price"])

    return in_budget[:2], stretch
