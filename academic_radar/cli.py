import argparse
import json
import os

from .config import DEFAULT_CONFIG, apply_overrides, load_config
from .emailer import send_email
from .pipeline import collect_items
from .render import render_email, serializable_items
from .state import filter_new_items, save_seen_links


def write_output(path, body):
    out_dir = os.path.dirname(path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Run the Academic Radar digest.")
    parser.add_argument("--config", default=os.environ.get("RADAR_CONFIG", DEFAULT_CONFIG))
    parser.add_argument("--opml", help="Override the OPML path from the profile.")
    parser.add_argument("--watchlist", help="Override the Bluesky watchlist path from the profile.")
    parser.add_argument("--state", help="Override the seen-link state file path from the profile.")
    parser.add_argument("--max-items", type=int, help="Override max email/output items.")
    parser.add_argument("--output-html", help="Write rendered digest HTML to this path.")
    parser.add_argument("--output-json", help="Write selected items as JSON to this path.")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and render without sending email or writing state.")
    parser.add_argument("--no-email", action="store_true", help="Do not send email.")
    parser.add_argument("--no-state", action="store_true", help="Do not write seen-link state.")
    parser.add_argument("--include-seen", action="store_true", help="Render all matching items, including seen links.")
    parser.add_argument("--skip-rss", action="store_true", help="Skip RSS fetching.")
    parser.add_argument("--skip-bsky", action="store_true", help="Skip Bluesky fetching.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    config = load_config(args.config)
    apply_overrides(config, opml=args.opml, watchlist=args.watchlist, state=args.state, max_items=args.max_items)

    items = collect_items(config, skip_rss=args.skip_rss, skip_bsky=args.skip_bsky)
    selected_items = items if args.include_seen else filter_new_items(items, config.state_file)
    digest_items = selected_items[: config.max_email_items]
    print(f"Rendered items: {len(digest_items)}")

    body = render_email(digest_items, config.max_email_items)

    if args.output_html:
        write_output(args.output_html, body)
        print(f"Wrote digest HTML: {args.output_html}")
    if args.output_json:
        write_output(args.output_json, json.dumps(serializable_items(digest_items), ensure_ascii=False, indent=2))
        print(f"Wrote digest JSON: {args.output_json}")

    if args.dry_run or args.no_email:
        print("Email skipped.")
    else:
        send_email(digest_items, config.max_email_items)
        print("Email sent.")

    if args.dry_run or args.no_state:
        print("State update skipped.")
    else:
        save_seen_links(items, config.state_file)
        print(f"State updated: {config.state_file}")
