"""Small desktop GUI for running Academic Radar without a terminal."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
import io
import json
import threading
import traceback
import webbrowser
import xml.sax.saxutils as xml_utils

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .config import apply_overrides, config_from_profile
from .diagnostics import diagnose_config, diagnostics_exit_code, format_diagnostics
from .pipeline import collect_items
from .render import render_email, serializable_items
from .state import filter_new_items
from .summary import summarize_config

DEFAULT_CORE_TERMS = """history of science
book history
history of medicine
history of technology
philosophy of science
STS"""

DEFAULT_NEGATIVE_TERMS = """marketing
crypto
undergraduate
celebrity
sports"""

DEFAULT_BSKY_QUERIES = """"call for papers" "history of science"
"special issue" "history of science"
"fellowship" "history of science""""

DEFAULT_WATCHLIST = """hssonline.bsky.social
isisjournal.bsky.social
whipplemuseum.bsky.social"""

DEFAULT_RSS_FEEDS = """https://networks.h-net.org/node/73374/announcements/feed
https://publicdomainreview.org/rss.xml"""

DEFAULT_EVENT_TERMS = [
    "call for papers",
    "cfp",
    "call for chapters",
    "special issue",
    "conference",
    "workshop",
    "symposium",
    "seminar",
    "fellowship",
    "grant",
    "deadline",
]


class ScrollFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)
        self.inner.bind(
            "<Configure>",
            lambda _event: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind("<Configure>", self._fit_inner_width)

    def _fit_inner_width(self, event):
        self.canvas.itemconfigure(self.window, width=event.width)


class AcademicRadarApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Academic Radar")
        self.geometry("1180x760")
        self.minsize(980, 640)

        default_workspace = Path.home() / "Documents" / "Academic Radar Run"
        self.workspace_var = tk.StringVar(value=str(default_workspace))
        self.profile_name_var = tk.StringVar(value="My Academic Radar")
        self.rss_days_var = tk.StringVar(value="35")
        self.bsky_days_var = tk.StringVar(value="10")
        self.max_items_var = tk.StringVar(value="20")
        self.skip_rss_var = tk.BooleanVar(value=False)
        self.skip_bsky_var = tk.BooleanVar(value=False)
        self.include_seen_var = tk.BooleanVar(value=False)

        self._build_ui()
        self._log("Ready. Fill the form, choose a workspace, then click Save files or Dry run.")

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, padding=(16, 14, 16, 8))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        ttk.Label(header, text="Academic Radar", font=("Georgia", 18, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Desktop runner: fill the form, create local files, run a dry preview, open the HTML result.",
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 0))

        body = ttk.PanedWindow(self, orient="horizontal")
        body.grid(row=1, column=0, sticky="nsew", padx=14, pady=10)

        left = ScrollFrame(body)
        right = ttk.Frame(body, padding=8)
        body.add(left, weight=3)
        body.add(right, weight=2)

        form = left.inner
        for column in range(2):
            form.columnconfigure(column, weight=1)

        workspace = ttk.LabelFrame(form, text="Workspace", padding=12)
        workspace.grid(row=0, column=0, columnspan=2, sticky="ew", padx=4, pady=6)
        workspace.columnconfigure(0, weight=1)
        ttk.Entry(workspace, textvariable=self.workspace_var).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(workspace, text="Choose folder", command=self.choose_workspace).grid(row=0, column=1, sticky="e")
        ttk.Label(
            workspace,
            text="Files are written under this folder. Real runtime files stay local unless you copy them elsewhere.",
            foreground="#555555",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

        basic = ttk.LabelFrame(form, text="Basic settings", padding=12)
        basic.grid(row=1, column=0, columnspan=2, sticky="ew", padx=4, pady=6)
        for column in range(4):
            basic.columnconfigure(column, weight=1)
        ttk.Label(basic, text="Profile name").grid(row=0, column=0, sticky="w")
        ttk.Entry(basic, textvariable=self.profile_name_var).grid(row=1, column=0, sticky="ew", padx=(0, 8))
        ttk.Label(basic, text="RSS days").grid(row=0, column=1, sticky="w")
        ttk.Entry(basic, textvariable=self.rss_days_var, width=8).grid(row=1, column=1, sticky="ew", padx=(0, 8))
        ttk.Label(basic, text="Bluesky days").grid(row=0, column=2, sticky="w")
        ttk.Entry(basic, textvariable=self.bsky_days_var, width=8).grid(row=1, column=2, sticky="ew", padx=(0, 8))
        ttk.Label(basic, text="Max items").grid(row=0, column=3, sticky="w")
        ttk.Entry(basic, textvariable=self.max_items_var, width=8).grid(row=1, column=3, sticky="ew")

        self.core_terms = self._text_group(form, 2, 0, "Core field terms", DEFAULT_CORE_TERMS)
        self.negative_terms = self._text_group(form, 2, 1, "Negative terms", DEFAULT_NEGATIVE_TERMS)
        self.bsky_queries = self._text_group(form, 3, 0, "Bluesky public search queries", DEFAULT_BSKY_QUERIES)
        self.watchlist = self._text_group(form, 3, 1, "Bluesky watchlist handles", DEFAULT_WATCHLIST)
        self.rss_feeds = self._text_group(form, 4, 0, "RSS feeds, one URL or TITLE=URL per line", DEFAULT_RSS_FEEDS, columnspan=2, height=6)

        options = ttk.LabelFrame(form, text="Run options", padding=12)
        options.grid(row=5, column=0, columnspan=2, sticky="ew", padx=4, pady=6)
        ttk.Checkbutton(options, text="Skip RSS", variable=self.skip_rss_var).grid(row=0, column=0, sticky="w", padx=(0, 14))
        ttk.Checkbutton(options, text="Skip Bluesky", variable=self.skip_bsky_var).grid(row=0, column=1, sticky="w", padx=(0, 14))
        ttk.Checkbutton(options, text="Include already-seen links", variable=self.include_seen_var).grid(row=0, column=2, sticky="w")

        buttons = ttk.Frame(form, padding=(4, 8))
        buttons.grid(row=6, column=0, columnspan=2, sticky="ew")
        for column in range(5):
            buttons.columnconfigure(column, weight=1)
        ttk.Button(buttons, text="Save files", command=self.save_files).grid(row=0, column=0, sticky="ew", padx=4)
        ttk.Button(buttons, text="Summary", command=self.show_summary).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(buttons, text="Doctor", command=self.show_doctor).grid(row=0, column=2, sticky="ew", padx=4)
        ttk.Button(buttons, text="Dry run", command=self.run_dry_preview).grid(row=0, column=3, sticky="ew", padx=4)
        ttk.Button(buttons, text="Open folder", command=self.open_workspace).grid(row=0, column=4, sticky="ew", padx=4)

        ttk.Label(right, text="Log", font=("Georgia", 14, "bold")).pack(anchor="w")
        self.log = tk.Text(right, wrap="word", height=28)
        self.log.pack(fill="both", expand=True, pady=(8, 8))
        self.log.configure(state="disabled")

        ttk.Button(right, text="Open latest HTML preview", command=self.open_latest_html).pack(fill="x", pady=(0, 8))
        ttk.Button(right, text="Clear log", command=self.clear_log).pack(fill="x")

    def _text_group(self, parent, row, column, title, default, columnspan=1, height=8):
        group = ttk.LabelFrame(parent, text=title, padding=12)
        group.grid(row=row, column=column, columnspan=columnspan, sticky="nsew", padx=4, pady=6)
        group.columnconfigure(0, weight=1)
        widget = tk.Text(group, height=height, wrap="word")
        widget.insert("1.0", default)
        widget.grid(row=0, column=0, sticky="nsew")
        return widget

    def choose_workspace(self):
        folder = filedialog.askdirectory(initialdir=self.workspace_var.get() or str(Path.home()))
        if folder:
            self.workspace_var.set(folder)

    def workspace(self) -> Path:
        return Path(self.workspace_var.get()).expanduser().resolve()

    def paths(self):
        root = self.workspace()
        radar = root / ".radar"
        tmp = root / "tmp"
        return {
            "root": root,
            "radar": radar,
            "tmp": tmp,
            "profile": radar / "profiles" / "local.json",
            "opml": radar / "feedly_active.opml",
            "watchlist": radar / "bsky_watchlist_core.txt",
            "state": radar / "sent_items.json",
            "html": tmp / "radar_digest.html",
            "json": tmp / "radar_items.json",
        }

    def text_lines(self, widget):
        return [line.strip() for line in widget.get("1.0", "end").splitlines() if line.strip()]

    def int_value(self, variable, fallback):
        try:
            value = int(variable.get())
            return value if value > 0 else fallback
        except ValueError:
            return fallback

    def build_profile(self):
        paths = self.paths()
        return {
            "name": self.profile_name_var.get().strip() or "My Academic Radar",
            "files": {
                "opml": paths["opml"].as_posix(),
                "bsky_watchlist": paths["watchlist"].as_posix(),
                "state": paths["state"].as_posix(),
            },
            "settings": {
                "rss_max_age_days": self.int_value(self.rss_days_var, 35),
                "bsky_max_age_days": self.int_value(self.bsky_days_var, 10),
                "max_email_items": self.int_value(self.max_items_var, 20),
                "max_rss_per_feed": 12,
                "max_bsky_per_query": 15,
                "max_bsky_per_account": 8,
            },
            "scoring": {
                "event_terms": list(DEFAULT_EVENT_TERMS),
                "core_field_terms": self.text_lines(self.core_terms),
                "prestige_or_core_sources": [],
                "negative_terms": self.text_lines(self.negative_terms),
            },
            "bluesky": {
                "queries": self.text_lines(self.bsky_queries),
            },
        }

    def build_opml(self):
        outlines = []
        for row in self.text_lines(self.rss_feeds):
            if "=" in row:
                title, url = row.split("=", 1)
                title = title.strip() or url.strip()
                url = url.strip()
            else:
                title = row
                url = row
            if not url:
                continue
            outlines.append(
                f'    <outline text="{xml_utils.escape(title)}" title="{xml_utils.escape(title)}" type="rss" xmlUrl="{xml_utils.escape(url)}" />'
            )
        body = "\n".join(outlines)
        return f'<?xml version="1.0" encoding="UTF-8"?>\n<opml version="2.0">\n  <head>\n    <title>Academic Radar feeds</title>\n  </head>\n  <body>\n{body}\n  </body>\n</opml>\n'

    def write_local_files(self):
        paths = self.paths()
        paths["profile"].parent.mkdir(parents=True, exist_ok=True)
        paths["tmp"].mkdir(parents=True, exist_ok=True)
        profile = self.build_profile()
        paths["profile"].write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        paths["opml"].write_text(self.build_opml(), encoding="utf-8")
        paths["watchlist"].write_text("\n".join(self.text_lines(self.watchlist)) + "\n", encoding="utf-8")
        return profile, paths

    def config(self):
        profile, paths = self.write_local_files()
        config = config_from_profile(profile)
        apply_overrides(config, max_items=self.int_value(self.max_items_var, 20))
        return config, paths

    def save_files(self):
        try:
            _profile, paths = self.write_local_files()
            self._log(f"Saved profile: {paths['profile']}")
            self._log(f"Saved OPML: {paths['opml']}")
            self._log(f"Saved watchlist: {paths['watchlist']}")
        except Exception as exc:
            self._show_error(exc)

    def show_summary(self):
        try:
            config, paths = self.config()
            self._log(f"\nSummary for {paths['profile']}\n" + summarize_config(config))
        except Exception as exc:
            self._show_error(exc)

    def show_doctor(self):
        try:
            config, _paths = self.config()
            diagnostics = diagnose_config(config)
            self._log("\nDiagnostics\n" + format_diagnostics(diagnostics))
            if diagnostics_exit_code(diagnostics):
                messagebox.showwarning("Academic Radar", "Diagnostics found errors. See the log for details.")
        except Exception as exc:
            self._show_error(exc)

    def run_dry_preview(self):
        thread = threading.Thread(target=self._run_dry_preview_worker, daemon=True)
        thread.start()

    def _run_dry_preview_worker(self):
        try:
            self._log("\nDry run started. This may take a little while if RSS or Bluesky sources are slow.")
            config, paths = self.config()
            buffer = io.StringIO()
            with redirect_stdout(buffer), redirect_stderr(buffer):
                items = collect_items(
                    config,
                    skip_rss=self.skip_rss_var.get(),
                    skip_bsky=self.skip_bsky_var.get(),
                )
                selected_items = items if self.include_seen_var.get() else filter_new_items(items, config.state_file)
                digest_items = selected_items[: config.max_email_items]
                html = render_email(digest_items, config.max_email_items)
                paths["html"].write_text(html, encoding="utf-8")
                paths["json"].write_text(
                    json.dumps(serializable_items(digest_items), ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
            captured = buffer.getvalue().strip()
            if captured:
                self._log(captured)
            self._log(f"Rendered items: {len(digest_items)}")
            self._log(f"Wrote HTML preview: {paths['html']}")
            self._log(f"Wrote JSON preview: {paths['json']}")
            self.after(0, lambda: webbrowser.open(paths["html"].as_uri()))
        except Exception as exc:
            self._show_error(exc)

    def open_latest_html(self):
        path = self.paths()["html"]
        if path.exists():
            webbrowser.open(path.as_uri())
        else:
            messagebox.showinfo("Academic Radar", "No HTML preview exists yet. Run Dry run first.")

    def open_workspace(self):
        folder = self.workspace()
        folder.mkdir(parents=True, exist_ok=True)
        webbrowser.open(folder.as_uri())

    def clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def _log(self, message):
        def write():
            self.log.configure(state="normal")
            self.log.insert("end", message.rstrip() + "\n")
            self.log.see("end")
            self.log.configure(state="disabled")
        self.after(0, write)

    def _show_error(self, exc):
        details = "".join(traceback.format_exception(exc)).strip()
        self._log("\nERROR\n" + details)
        self.after(0, lambda: messagebox.showerror("Academic Radar", str(exc)))


def main():
    app = AcademicRadarApp()
    app.mainloop()


if __name__ == "__main__":
    main()
