const fields = {
  profileName: document.querySelector("#profileName"),
  stateFile: document.querySelector("#stateFile"),
  coreTerms: document.querySelector("#coreTerms"),
  negativeTerms: document.querySelector("#negativeTerms"),
  bskyQueries: document.querySelector("#bskyQueries"),
  watchlist: document.querySelector("#watchlist"),
  rssFeeds: document.querySelector("#rssFeeds"),
  rssDays: document.querySelector("#rssDays"),
  bskyDays: document.querySelector("#bskyDays"),
  maxItems: document.querySelector("#maxItems"),
};

const preview = document.querySelector("#preview");
const statusText = document.querySelector("#statusText");
let activePreview = "json";

function lines(value) {
  return value
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
}

function numberValue(input, fallback) {
  const value = Number.parseInt(input.value, 10);
  return Number.isFinite(value) ? value : fallback;
}

function buildConfig() {
  return {
    name: fields.profileName.value.trim() || "My Academic Radar",
    files: {
      opml: "feedly_active.opml",
      bsky_watchlist: "bsky_watchlist_core.txt",
      state: fields.stateFile.value.trim() || "sent_items.json",
    },
    settings: {
      rss_max_age_days: numberValue(fields.rssDays, 35),
      bsky_max_age_days: numberValue(fields.bskyDays, 10),
      max_email_items: numberValue(fields.maxItems, 20),
      max_rss_per_feed: 12,
      max_bsky_per_query: 15,
      max_bsky_per_account: 8,
    },
    scoring: {
      event_terms: [
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
      ],
      core_field_terms: lines(fields.coreTerms.value),
      prestige_or_core_sources: [],
      negative_terms: lines(fields.negativeTerms.value),
    },
    bluesky: {
      queries: lines(fields.bskyQueries.value),
    },
  };
}

function escapeXml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function buildOpml() {
  const outlines = lines(fields.rssFeeds.value)
    .map((url) => {
      const safe = escapeXml(url);
      return `    <outline text="${safe}" title="${safe}" type="rss" xmlUrl="${safe}" />`;
    })
    .join("\n");

  return `<?xml version="1.0" encoding="UTF-8"?>\n<opml version="2.0">\n  <head>\n    <title>Academic Radar feeds</title>\n  </head>\n  <body>\n${outlines}\n  </body>\n</opml>\n`;
}

function fileText(kind) {
  if (kind === "json") {
    return JSON.stringify(buildConfig(), null, 2) + "\n";
  }

  if (kind === "watchlist") {
    return lines(fields.watchlist.value).join("\n") + "\n";
  }

  return buildOpml();
}

function render() {
  preview.textContent = fileText(activePreview);
  statusText.textContent = `${lines(fields.coreTerms.value).length} terms · ${lines(fields.bskyQueries.value).length} queries`;
}

function download(filename, text) {
  const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

document.querySelectorAll(".tab").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((tab) => tab.classList.remove("active"));
    button.classList.add("active");
    activePreview = button.dataset.preview;
    render();
  });
});

Object.values(fields).forEach((field) => field.addEventListener("input", render));

document.querySelector("#downloadJson").addEventListener("click", () => {
  download("academic-radar-profile.json", fileText("json"));
});

document.querySelector("#downloadWatchlist").addEventListener("click", () => {
  download("bsky_watchlist_core.txt", fileText("watchlist"));
});

document.querySelector("#downloadOpml").addEventListener("click", () => {
  download("feedly_active.opml", fileText("opml"));
});

render();
