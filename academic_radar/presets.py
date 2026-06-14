PRESETS = {
    "hps": {
        "description": "History and philosophy of science / HSTM baseline.",
        "field_terms": [
            "history of science",
            "history and philosophy of science",
            "hps",
            "hstm",
            "history of medicine",
            "history of technology",
            "philosophy of science",
            "science and technology studies",
        ],
        "bsky_queries": [
            '"call for papers" "history of science"',
            '"special issue" "history of science"',
            '"workshop" "history of science"',
            '"fellowship" "history of science"',
        ],
    },
    "history-of-knowledge": {
        "description": "History of knowledge, practices, records, and institutions.",
        "field_terms": [
            "history of knowledge",
            "knowledge practices",
            "knowledge production",
            "epistemic practices",
            "archives",
            "record keeping",
            "paperwork",
            "bureaucracy",
        ],
        "bsky_queries": [
            '"call for papers" "history of knowledge"',
            '"special issue" "history of knowledge"',
            '"workshop" "knowledge practices"',
            '"new book" "history of knowledge"',
        ],
    },
    "scientific-instruments": {
        "description": "Scientific instruments, measurement, precision, calibration, and observatory practices.",
        "field_terms": [
            "scientific instrument",
            "scientific instruments",
            "measurement",
            "calibration",
            "precision",
            "instrument making",
            "observatory",
            "navigation",
            "longitude",
            "astronomical instruments",
        ],
        "bsky_queries": [
            '"scientific instruments" "call for papers"',
            '"measurement" "history of science" "call for papers"',
            '"calibration" "history of science"',
            '"observatory" "history of science"',
        ],
    },
    "photography-history": {
        "description": "History of photography, photographic science, tacit knowledge, and visual/material practices.",
        "field_terms": [
            "history of photography",
            "photographic history",
            "photographic science",
            "photography studies",
            "visual culture",
            "camera obscura",
            "photochemistry",
            "tacit knowledge",
            "material practice",
        ],
        "bsky_queries": [
            '"call for papers" "history of photography"',
            '"special issue" "photography studies"',
            '"photographic history" "conference"',
            '"photographic science" "history of science"',
        ],
    },
    "romantic-science": {
        "description": "Romantic-era science, literature and science, geology, chemistry, optics, and material culture.",
        "field_terms": [
            "romantic science",
            "romanticism and science",
            "literature and science",
            "history of geology",
            "history of chemistry",
            "history of optics",
            "eighteenth century",
            "nineteenth century",
            "material culture",
        ],
        "bsky_queries": [
            '"romanticism" "history of science"',
            '"literature and science" "call for papers"',
            '"history of geology" "call for papers"',
            '"history of optics" "conference"',
        ],
    },
    "book-history": {
        "description": "Book history, bibliography, manuscripts, print culture, and archives.",
        "field_terms": [
            "book history",
            "bibliography",
            "manuscript studies",
            "print culture",
            "history of reading",
            "archive studies",
            "special collections",
            "rare books",
        ],
        "bsky_queries": [
            '"call for papers" "book history"',
            '"special issue" "book history"',
            '"manuscript studies" "conference"',
            '"rare books" "fellowship"',
        ],
    },
}


def normalize_preset_names(values):
    names = []
    for value in values or []:
        for name in str(value).split(","):
            normalized = name.strip().lower()
            if normalized:
                names.append(normalized)
    return names


def available_presets():
    return sorted(PRESETS)


def describe_presets():
    return [(name, PRESETS[name]["description"]) for name in available_presets()]


def merge_presets(names):
    merged = {
        "field_terms": [],
        "negative_terms": [],
        "bsky_queries": [],
    }
    unknown = []
    for name in normalize_preset_names(names):
        preset = PRESETS.get(name)
        if preset is None:
            unknown.append(name)
            continue
        for key in merged:
            merged[key].extend(preset.get(key, []))
    if unknown:
        valid = ", ".join(available_presets())
        raise ValueError(f"Unknown preset(s): {', '.join(unknown)}. Available presets: {valid}")
    return merged
