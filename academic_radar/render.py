import html


def render_details(details):
    rows = []
    if details.get("deadline"):
        rows.append(f"<b>Deadline:</b> {html.escape(details['deadline'])}")
    if details.get("event_date"):
        rows.append(f"<b>Date:</b> {html.escape(details['event_date'])}")
    if details.get("location"):
        rows.append(f"<b>Place:</b> {html.escape(details['location'])}")
    if details.get("format"):
        rows.append(f"<b>Format:</b> {html.escape(details['format'])}")
    if details.get("funding"):
        rows.append(f"<b>Funding:</b> {html.escape(details['funding'])}")

    if not rows:
        return ""
    return "<p>" + " | ".join(rows) + "</p>"


def render_score_reasons(item):
    reasons = item.get("score_reasons") or []
    if not reasons:
        return ""
    body = "; ".join(str(reason) for reason in reasons[:4])
    return f"<p><b>Why:</b> {html.escape(body)}</p>"


def render_email(items, max_items):
    from datetime import datetime, timezone

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if not items:
        return f"No new relevant items found today ({today})."

    categories = [
        "CFP / Calls",
        "Special Issues / Journals",
        "New Books",
        "Fellowships / Grants",
        "RA / Library / Archive Jobs",
        "Events / Seminars",
        "Other Signals",
    ]

    parts = [
        f"<h2>Daily Academic Radar - {html.escape(today)}</h2>",
        "<p>Only new links are shown. Scoring and categories are rule-based.</p>",
    ]
    count = 0

    for category in categories:
        category_items = [item for item in items if item["category"] == category]
        if not category_items:
            continue

        parts.append(f"<h2>{html.escape(category)}</h2>")
        for item in category_items:
            if count >= max_items:
                break

            count += 1
            source_line = item["source"]
            if item["source_name"]:
                source_line += f" | {item['source_name']}"

            parts.append(
                f"<div style='margin-bottom:18px;'>"
                f"<h3>[{html.escape(item['tag'])}] {html.escape(item['title'])}</h3>"
                f"{render_details(item['details'])}"
                f"<p><b>Source:</b> {html.escape(source_line)} | "
                f"<b>Score:</b> {item['score']}</p>"
                f"{render_score_reasons(item)}"
                f"<p>{html.escape(item['summary'])}</p>"
                f"<p><a href='{html.escape(item['link'])}'>{html.escape(item['link'])}</a></p>"
                f"</div>"
            )

        if count >= max_items:
            break

    return "\n".join(parts)


def serializable_items(items):
    output = []
    for item in items:
        row = dict(item)
        if row.get("dt"):
            row["dt"] = row["dt"].isoformat()
        output.append(row)
    return output
