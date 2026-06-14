import argparse
import json
import os

from .config import DEFAULT_CONFIG, apply_overrides, load_config
from .diagnostics import diagnose_config, diagnostics_exit_code, format_diagnostics
from .emailer import send_email
from .pipeline import collect_items
from .presets import describe_presets
from .render import render_email, serializable_items
from .setup import DEFAULT_LOCAL_PROFILE, write_first_run_files
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
    parser.add_argument("--doctor", action="store_true", help="Run no-network diagnostics for the selected profile and exit.")
    parser.add_argument("--no-email", action="store_true", help="Do not send email.")
    parser.add_argument("--no-state", action="store_true", help="Do not write seen-link state.")
    parser.add_argument("--include-seen", action="store_true", help="Render all matching items, including seen links.")
    parser.add_argument("--skip-rss", action="store_true", help="Skip RSS fetching.")
    parser.add_argument("--skip-bsky", action="store_true", help="Skip Bluesky fetching.")

    setup_group = parser.add_argument_group("first-run setup")
    setup_group.add_argument(
        "--init",
        action="store_true",
        help="Create a local private profile, OPML file, and Bluesky watchlist, then exit.",
    )
    setup_group.add_argument("--list-presets", action="store_true", help="List built-in first-run profile presets and exit.")
    setup_group.add_argument("--init-profile", default=DEFAULT_LOCAL_PROFILE, help="Path for the generated local profile.")
    setup_group.add_argument("--profile-name", default="Local Academic Radar", help="Name stored in the generated profile.")
    setup_group.add_argument(
        "--preset",
        action="append",
        default=[],
        help="Built-in preset to merge into the generated profile. Repeat or pass comma-separated names.",
    )
    setup_group.add_argument("--field-term", action="append", default=[], help="Extra field term to score and query.")
    setup_group.add_argument("--negative-term", action="append", default=[], help="Extra term to suppress.")
    setup_group.add_argument("--bsky-query", action="append", default=[], help="Extra public Bluesky search query.")
    setup_group.add_argument("--bsky-handle", action="append", default=[], help="Bluesky handle to add to the local watchlist.")
    setup_group.add_argument("--rss-feed", action="append", default=[], help="RSS feed as TITLE=URL or URL.")
    setup_group.add_argument("--overwrite", action="store_true", help="Replace generated first-run files if they exist.")

    return parser.parse_args(argv)


def print_first_run_result(result):
    print("Created local Academic Radar files:")
    print(f"  Profile: {result['profile']}")
    print(f"  OPML: {result['opml']}")
    print(f"  Bluesky watchlist: {result['watchlist']}")
    print(f"  Seen-link state: {result['state']}")
    print("")
    print(f"Run diagnostics with: academic-radar --config {result['profile']} --doctor")
    print(f"Run a preview with: academic-radar --config {result['profile']} --dry-run")


def print_presets():
    print("Available Academic Radar presets:")
    for name, description in describe_presets():
        print(f"  {name}: {description}")


def main(argv=None):
    args = parse_args(argv)

    if args.list_presets:
        print_presets()
        return 0

    if args.init:
        result = write_first_run_files(
            profile_path=args.init_profile,
            profile_name=args.profile_name,
            field_terms=args.field_term,
            negative_terms=args.negative_term,
            bsky_queries=args.bsky_query,
            bsky_handles=args.bsky_handle,
            rss_feeds=args.rss_feed,
            presets=args.preset,
            overwrite=args.overwrite,
        )
        print_first_run_result(result)
        return 0

    config = load_config(args.config)
    apply_overrides(config, opml=args.opml, watchlist=args.watchlist, state=args.state, max_items=args.max_items)

    if args.doctor:
        diagnostics = diagnose_config(config)
        print(format_diagnostics(diagnostics))
        return diagnostics_exit_code(diagnostics)

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

    return 0
