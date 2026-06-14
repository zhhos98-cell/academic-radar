const translations = {
  en: {
    "page.title": "Academic Radar Web Builder",
    title: "Web Builder",
    "hero.heading": "Build a private radar profile in your browser.",
    "hero.body": "Fill in your fields, feeds, and Bluesky sources. This page generates three plain-text files you can download and use with the local academic-radar command-line tool.",
    "privacy.label": "Privacy posture:",
    "privacy.body": "this builder is static and client-side only. It has no analytics, cookies, accounts, uploads, backend API calls, or server-side storage.",
    "process.kicker": "Workflow",
    "compliance.kicker": "Responsible use",
    "compliance.heading": "Check sources and obligations before automation.",
    "compliance.body": "This builder only prepares local configuration files. Before running collection, review source terms, platform rules, institutional policies, and any data-protection duties that apply to your use case.",
    "compliance.item1": "Keep private watchlists, feed exports, state files, and delivery settings out of public repositories.",
    "compliance.item2": "Use dry runs and diagnostics before enabling email delivery or persistent state.",
    "compliance.item3": "Do not use this project to collect or republish information you are not permitted to process.",
    "step1.heading": "Fill the form",
    "step1.body": "Add field terms, negative filters, RSS feeds, Bluesky queries, and watched accounts.",
    "step2.heading": "Preview files",
    "step2.body": "Switch between JSON, Watchlist, and OPML to inspect exactly what will be downloaded.",
    "step3.heading": "Download and run",
    "step3.body": "Save the three files, then run --summary, --doctor, and a dry preview locally.",
    "inputs.kicker": "Configure",
    "inputs.heading": "Build Profile",
    "inputs.body": "Start with the defaults, then replace the examples with your own sources.",
    "group.profile.heading": "Profile",
    "group.profile.body": "Name the local profile and choose the state file used to avoid repeat items.",
    "group.vocabulary.heading": "Vocabulary",
    "group.vocabulary.body": "Define what counts as field-relevant, and what should be pushed down or ignored.",
    "group.bsky.heading": "Bluesky",
    "group.bsky.body": "Combine public search queries with a small watchlist of relevant accounts.",
    "group.rss.heading": "RSS & limits",
    "group.rss.body": "Add feed URLs and set the look-back window for local dry previews.",
    "label.profileName": "Profile name",
    "label.stateFile": "State file",
    "label.coreTerms": "Core field terms",
    "label.negativeTerms": "Negative terms",
    "label.bskyQueries": "Bluesky queries",
    "label.watchlist": "Bluesky watchlist",
    "label.rssFeeds": "RSS feed URLs",
    "label.rssDays": "RSS days",
    "label.bskyDays": "Bluesky days",
    "label.maxItems": "Max email items",
    "output.kicker": "Generated files",
    "output.heading": "Review Files",
    "output.body": "Download all three files. Keep real runtime files private unless you intentionally want them public.",
    "tab.json": "JSON profile",
    "tab.watchlist": "Watchlist",
    "tab.opml": "OPML",
    "button.json": "Download JSON",
    "button.watchlist": "Download Watchlist",
    "button.opml": "Download OPML",
    "after.kicker": "Local run",
    "after.heading": "Run Locally",
    "after.body": "Put the files where your JSON profile points, then inspect the setup before fetching live data.",
    "link.repo": "GitHub repository",
    "link.guide": "Local first-run guide",
    "link.releases": "Releases",
    "footer.privacy": "Runs in your browser. No analytics, cookies, uploads, accounts, backend API calls, or server-side storage.",
  },
  zh: {
    "page.title": "Academic Radar Web Builder",
    title: "Web Builder",
    "hero.heading": "Build a private radar profile.",
    "hero.body": "填写研究领域、RSS 源和 Bluesky 来源；页面会在本地生成三个纯文本文件，供 academic-radar 使用。",
    "privacy.label": "Privacy:",
    "privacy.body": "静态页面，只在浏览器端运行；没有分析代码、cookies、账号、上传、后端 API 调用或服务器端存储。",
    "process.kicker": "Workflow",
    "compliance.kicker": "Responsible use",
    "compliance.heading": "Check sources before automation.",
    "compliance.body": "本页只准备本地配置文件。正式抓取前，请核对信息源条款、平台规则、机构政策，以及你的使用场景中可能涉及的数据保护义务。",
    "compliance.item1": "私人 watchlists、RSS exports、state files 和 delivery settings 不应提交到公开仓库。",
    "compliance.item2": "启用邮件投递或持久化状态之前，先运行 dry-run 和 diagnostics。",
    "compliance.item3": "不要用本项目收集或再发布你无权处理的信息。",
    "step1.heading": "Fill the form",
    "step1.body": "加入领域词、排除词、RSS 源、Bluesky 检索式和关注账号。",
    "step2.heading": "Preview files",
    "step2.body": "在 JSON、Watchlist 和 OPML 之间切换，确认即将下载的内容。",
    "step3.heading": "Download and run",
    "step3.body": "保存三个文件，然后在本地运行 --summary、--doctor 和 dry-run。",
    "inputs.kicker": "Configure",
    "inputs.heading": "Build Profile",
    "inputs.body": "先使用默认值，再把示例替换成你的研究方向和信息源。",
    "group.profile.heading": "Profile",
    "group.profile.body": "命名本地配置，并选择用于避免重复条目的 state file。",
    "group.vocabulary.heading": "Vocabulary",
    "group.vocabulary.body": "定义哪些内容属于你的领域，哪些内容应降低权重或排除。",
    "group.bsky.heading": "Bluesky",
    "group.bsky.body": "把公共检索式和少量相关账号 watchlist 结合起来。",
    "group.rss.heading": "RSS & limits",
    "group.rss.body": "加入 RSS 源地址，并设置本地 dry-run 的回溯窗口。",
    "label.profileName": "Profile name",
    "label.stateFile": "State file",
    "label.coreTerms": "Core field terms",
    "label.negativeTerms": "Negative terms",
    "label.bskyQueries": "Bluesky queries",
    "label.watchlist": "Bluesky watchlist",
    "label.rssFeeds": "RSS feed URLs",
    "label.rssDays": "RSS days",
    "label.bskyDays": "Bluesky days",
    "label.maxItems": "Max email items",
    "output.kicker": "Generated files",
    "output.heading": "Review Files",
    "output.body": "下载全部三个文件。真实运行文件默认保持私有，除非你明确希望公开。",
    "tab.json": "JSON profile",
    "tab.watchlist": "Watchlist",
    "tab.opml": "OPML",
    "button.json": "Download JSON",
    "button.watchlist": "Download Watchlist",
    "button.opml": "Download OPML",
    "after.kicker": "Local run",
    "after.heading": "Run Locally",
    "after.body": "把文件放到 JSON 配置指向的位置，然后先检查配置，再抓取实时数据。",
    "link.repo": "GitHub repository",
    "link.guide": "Local first-run guide",
    "link.releases": "Releases",
    "footer.privacy": "Runs in your browser. 无分析代码、cookies、上传、账号、后端 API 调用或服务器端存储。",
  },
};

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
const languageButtons = document.querySelectorAll("[data-lang-choice]");
let activePreview = "json";
let currentLanguage = navigator.language.toLowerCase().startsWith("zh") ? "zh" : "en";

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

function renderStatus() {
  const termCount = lines(fields.coreTerms.value).length;
  const queryCount = lines(fields.bskyQueries.value).length;
  statusText.textContent = currentLanguage === "zh"
    ? `${termCount} terms · ${queryCount} queries`
    : `${termCount} terms · ${queryCount} queries`;
}

function render() {
  preview.textContent = fileText(activePreview);
  renderStatus();
}

function applyLanguage(language) {
  currentLanguage = translations[language] ? language : "en";
  const dictionary = translations[currentLanguage];
  document.documentElement.lang = currentLanguage === "zh" ? "zh-Hans" : "en";
  document.body.classList.toggle("lang-zh", currentLanguage === "zh");
  document.title = dictionary["page.title"];

  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const key = element.dataset.i18n;
    if (dictionary[key]) {
      element.textContent = dictionary[key];
    }
  });

  languageButtons.forEach((button) => {
    const isActive = button.dataset.langChoice === currentLanguage;
    button.classList.toggle("active", isActive);
    button.setAttribute("aria-pressed", isActive ? "true" : "false");
  });

  renderStatus();
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

languageButtons.forEach((button) => {
  button.addEventListener("click", () => applyLanguage(button.dataset.langChoice));
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

applyLanguage(currentLanguage);
render();
