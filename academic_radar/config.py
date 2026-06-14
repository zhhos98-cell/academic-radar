from dataclasses import dataclass, field
import json
import os


DEFAULT_CONFIG = "config/profiles/hps.json"

DEFAULT_EVENT_TERMS = [
    "call for papers",
    "cfp",
    "call for chapters",
    "special issue",
    "conference",
    "workshop",
    "symposium",
    "seminar",
    "new book",
    "forthcoming",
    "book launch",
    "review copy",
    "fellowship",
    "grant",
    "bursary",
    "studentship",
    "research assistant",
    "ra position",
    "library assistant",
    "assistant librarian",
    "archivist",
    "curator",
    "deadline",
    "open access",
    "new issue",
]

DEFAULT_CORE_FIELD_TERMS = [
    "history of science",
    "histstm",
    "hstm",
    "history of knowledge",
    "history of humanities",
    "book history",
    "material culture",
    "intellectual history",
    "history of medicine",
    "history of technology",
    "philosophy of science",
    "hps",
    "sts",
    "early modern",
    "eighteenth century",
    "18th century",
    "manuscript",
    "bibliography",
    "rare books",
    "scientific instrument",
    "natural history",
]

DEFAULT_PRESTIGE_OR_CORE_SOURCES = [
    "bshs",
    "hstm",
    "hopos",
    "isis",
    "history of science",
    "jhi",
    "journal of the history of ideas",
    "isih",
    "history of humanities",
    "mpi",
    "mpiwg",
    "royal historical society",
    "royal society",
    "royal astronomical society",
    "society for renaissance studies",
    "bsecs",
    "bars",
    "warburg",
    "whipple",
    "cambridge",
    "oxford",
    "bodleian",
    "british library",
    "wellcome",
    "ihr",
    "crassh",
]

DEFAULT_NEGATIVE_TERMS = [
    "contemporary",
    "postdoc",
    "postdoctoral",
    "lecturer",
    "assistant professor",
    "associate professor",
    "professor",
    "tenure",
    "tenure-track",
    "faculty position",
    "undergraduate",
    "high school",
    "marketing",
    "seo",
]

DEFAULT_BLUESKY_QUERIES = [
    '"call for papers" "history of science"',
    'cfp "history of science"',
    '"special issue" "history of science"',
    '"new book" "history of science"',
    '"call for papers" "history of knowledge"',
    '"special issue" "history of knowledge"',
    '"new book" "history of knowledge"',
    '"call for papers" "book history"',
    '"special issue" "book history"',
    '"new book" "book history"',
    '"call for papers" "history of humanities"',
    '"special issue" "history of humanities"',
    '"fellowship" "history of science"',
    '"bursary" "history of science"',
    '"scientific instruments" "call for papers"',
    '"premodern mediterranean" "history of medicine"',
    '"research assistant" "history of science"',
    '"archivist" "history of science"',
    '"curator" "history of science"',
]


@dataclass
class RadarConfig:
    opml_file: str = "feedly_active.opml"
    bsky_watchlist_file: str = "bsky_watchlist_core.txt"
    state_file: str = "sent_items.json"
    rss_max_age_days: int = 35
    bsky_max_age_days: int = 10
    max_email_items: int = 20
    max_rss_per_feed: int = 12
    max_bsky_per_query: int = 15
    max_bsky_per_account: int = 8
    event_terms: list[str] = field(default_factory=lambda: list(DEFAULT_EVENT_TERMS))
    core_field_terms: list[str] = field(default_factory=lambda: list(DEFAULT_CORE_FIELD_TERMS))
    prestige_or_core_sources: list[str] = field(default_factory=lambda: list(DEFAULT_PRESTIGE_OR_CORE_SOURCES))
    negative_terms: list[str] = field(default_factory=lambda: list(DEFAULT_NEGATIVE_TERMS))
    bluesky_queries: list[str] = field(default_factory=lambda: list(DEFAULT_BLUESKY_QUERIES))


def load_profile(path=None):
    path = path or os.environ.get("RADAR_CONFIG", DEFAULT_CONFIG)
    if not path or not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def config_from_profile(profile):
    config = RadarConfig()
    files = profile.get("files", {})
    settings = profile.get("settings", {})
    scoring = profile.get("scoring", {})
    bluesky = profile.get("bluesky", {})

    config.opml_file = files.get("opml", config.opml_file)
    config.bsky_watchlist_file = files.get("bsky_watchlist", config.bsky_watchlist_file)
    config.state_file = files.get("state", config.state_file)

    config.rss_max_age_days = int(settings.get("rss_max_age_days", config.rss_max_age_days))
    config.bsky_max_age_days = int(settings.get("bsky_max_age_days", config.bsky_max_age_days))
    config.max_email_items = int(settings.get("max_email_items", config.max_email_items))
    config.max_rss_per_feed = int(settings.get("max_rss_per_feed", config.max_rss_per_feed))
    config.max_bsky_per_query = int(settings.get("max_bsky_per_query", config.max_bsky_per_query))
    config.max_bsky_per_account = int(settings.get("max_bsky_per_account", config.max_bsky_per_account))

    config.event_terms = scoring.get("event_terms", config.event_terms)
    config.core_field_terms = scoring.get("core_field_terms", config.core_field_terms)
    config.prestige_or_core_sources = scoring.get("prestige_or_core_sources", config.prestige_or_core_sources)
    config.negative_terms = scoring.get("negative_terms", config.negative_terms)
    config.bluesky_queries = bluesky.get("queries", config.bluesky_queries)

    return config


def load_config(path=None):
    return config_from_profile(load_profile(path))


def apply_overrides(config, opml=None, watchlist=None, state=None, max_items=None):
    if opml:
        config.opml_file = opml
    if watchlist:
        config.bsky_watchlist_file = watchlist
    if state:
        config.state_file = state
    if max_items is not None:
        config.max_email_items = max_items
    return config
