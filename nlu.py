"""MiniLM-based intent matching.

Embeds the user's free-text answer and compares it (cosine similarity)
against example phrases for each intent. If nothing is similar enough,
returns None so the chatbot can ask again instead of guessing.
"""
import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

from sentence_transformers import SentenceTransformer, util

# Example phrases per use-case intent. MiniLM lets users answer naturally
# ("i need something for my CS classes") instead of picking from a menu.
INTENT_EXAMPLES = {
    "school": [
        "school and studying",
        "a laptop for college classes and homework",
        "I need a laptop for my university courses",
        "I'm a student and need it for note taking and essays",
    ],
    "gaming": [
        "gaming",
        "a laptop for playing video games",
        "I want to run AAA games like fortnite and valorant",
        "a gaming laptop for gaming and streaming",
    ],
    "work": [
        "work and business",
        "a laptop for office work, emails and spreadsheets",
        "I need it for programming and software development",
        "business laptop for remote work and meetings",
    ],
    "creative": [
        "video editing",
        "a laptop for photoshop and graphic design",
        "I need it for music production and creative projects",
        "editing videos and 3d modeling",
    ],
    "everyday": [
        "everyday use",
        "just browsing the web and checking email",
        "a laptop for watching netflix and youtube",
        "general everyday light use at home",
    ],
}
# Generic yes/no for questions like "search again?"
YES_NO_EXAMPLES = {
    "yes": ["yes", "yeah sure", "definitely", "yep let's do it", "okay one more time"],
    "no": ["no", "nope", "not really", "no thanks I'm done", "that's all I needed"],
}

# Portability-specific: implicit answers phrased about carrying/desk use
YES_NO_PORTABILITY = {
    "yes": ["yes", "yeah sure", "definitely", "yep that works", "I travel a lot so yes","I want to carry it around", "I'll take it with me everywhere", "needs to be light and easy to move","I'll be using it on the go"],
    "no": ["no", "nope", "not really", "it stays on my desk", "I don't care about that","it will sit on my desk all day", "I won't be moving it", "I need a laptop that's heavy and bulky","I'll be using it at home"],
}

BUDGET_TIER_EXAMPLES = {
    "budget":  ["something cheap", "as affordable as possible", "low cost"],
    "mid":     ["mid-range", "something reasonable, not too expensive"],
    "premium": ["money is no object", "I want the best, price doesn't matter","expensive is good"],
}

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _classify(text: str, examples: dict, threshold: float):
    """Return (best_intent, score) or (None, score) if below threshold."""
    model = _get_model()
    query = model.encode(text, convert_to_tensor=True)

    best_intent, best_score = None, 0.0
    for intent, phrases in examples.items():
        emb = model.encode(phrases, convert_to_tensor=True)
        score = util.cos_sim(query, emb).max().item()
        if score > best_score:
            best_intent, best_score = intent, score

    if best_score < threshold:
        return None, best_score
    return best_intent, best_score


def detect_use_case(text: str):
    return _classify(text, INTENT_EXAMPLES, threshold=0.4)


def detect_yes_no(text: str, examples: dict = YES_NO_EXAMPLES):
    return _classify(text, examples, threshold=0.45)


def detect_budget_tier(text: str):
    return _classify(text, BUDGET_TIER_EXAMPLES, threshold=0.45)
