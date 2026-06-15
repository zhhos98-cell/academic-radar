(function () {
  const LF = String.fromCharCode(10);
  const BACKSLASH = String.fromCharCode(92);

  const text = {
    en: {
      kicker: "Reuse",
      heading: "Import & Check",
      body: "Bring existing files back into the builder and check the setup before download.",
      profile: "JSON profile",
      watchlist: "Watchlist",
      opml: "OPML",
      refresh: "Refresh checks",
      health: "Configuration checks",
      ready: "Ready to import existing files.",
      profileImported: "JSON profile imported.",
      watchlistImported: "Watchlist imported.",
      opmlImported: "OPML imported.",
      importError: "Could not import this file.",
      coreOk: (count) => `Core vocabulary: ${count} term(s).`,
      coreWarn: "Add at least 3 core field terms.",
      rssOk: (count) => `RSS feeds: ${count}.`,
      rssWarn: (count) => `${count} RSS line(s) do not look like feed URLs.`,
      blueskyOk: (queries, handles) => `Bluesky inputs: ${queries} query/queries and ${handles} handle(s).`,
      bskyHandleOk: "Bluesky handles look consistent.",
      bskyHandleWarn: (count) => `${count} Bluesky handle(s) may need review.`,
      stateOk: "State file path looks local/ignored.",
      stateWarn: "State file should usually live under .radar/ or another ignored folder.",
      overlapOk: "No overlap between core and negative terms.",
      overlapWarn: (terms) => `Negative terms overlap core terms: ${terms}.`,
      privacyInfo: "Watchlists and feed selections can reveal research interests; keep downloaded files private.",
    },
    zh: {
      kicker: "Reuse",
      heading: "导入与检查",
      body: "把已有文件放回 builder，下载前检查配置。",
      profile: "JSON profile",
      watchlist: "Watchlist",
      opml: "OPML",
      refresh: "刷新检查",
      health: "配置检查",
      ready: "可以导入已有文件。",
      profileImported: "JSON profile 已导入。",
      watchlistImported: "Watchlist 已导入。",
      opmlImported: "OPML 已导入。",
      importError: "无法导入这个文件。",
      coreOk: (count) => `核心词：${count} 个。`,
      coreWarn: "建议至少填 3 个核心领域词。",
      rssOk: (count) => `RSS 源：${count} 个。`,
      rssWarn: (count) => `${count} 行 RSS 地址格式可能不对。`,
      blueskyOk: (queries, handles) => `Bluesky：${queries} 个检索式，${handles} 个账号。`,
      bskyHandleOk: "Bluesky 账号格式看起来正常。",
      bskyHandleWarn: (count) => `${count} 个 Bluesky 账号可能需要检查。`,
      stateOk: "State file 路径看起来是本地/忽略路径。",
      stateWarn: "State file 建议放在 .radar/ 或其他忽略目录下。",
      overlapOk: "核心词和排除词没有重叠。",
      overlapWarn: (terms) => `排除词和核心词重叠：${terms}。`,
      privacyInfo: "Watchlist 和 RSS 选择可能透露研究兴趣；下载文件建议保持私有。",
    },
  };

  let messageKey = "ready";
  let messageType = "info";
  let toolMessage;
  let healthList;

  function lang() {
    return document.documentElement.lang.toLowerCase().startsWith("zh") ? "zh" : "en";
  }

  function tx(key) {
    return text[lang()][key] || text.en[key] || key;
  }

  function fields() {
    return {
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
  }

  function cleanLines(value) {
    return String(value || "")
      .split(LF)
      .map((line) => line.trim())
      .filter(Boolean);
  }

  function unique(values) {
    return Array.from(new Set(values));
  }

  function setMultiline(field, values) {
    if (field) {
      field.value = unique(values.map((value) => String(value).trim()).filter(Boolean)).join(LF);
    }
  }

  function setNumber(field, value) {
    const parsed = Number.parseInt(value, 10);
    if (field && Number.isFinite(parsed)) {
      field.value = String(parsed);
    }
  }

  function isLikelyFeedUrl(value) {
    try {
      const url = new URL(value);
      return url.protocol === "http:" || url.protocol === "https:";
    } catch (_error) {
      return false;
    }
  }

  function isLikelyBskyHandle(value) {
    const handle = value.replace(/^@/, "").toLowerCase();
    const parts = handle.split(".");
    return parts.length >= 2 && parts.every((part) => part.length > 0 && part.length <= 63 && /^[a-z0-9-]+$/.test(part));
  }

  function isPrivateRuntimePath(value) {
    const normalized = String(value || "").split(BACKSLASH).join("/").toLowerCase();
    const basename = normalized.split("/").pop() || "";
    return (
      normalized.startsWith(".radar/") ||
      normalized.includes("/.radar/") ||
      normalized.startsWith("tmp/") ||
      basename === "sent_items.json" ||
      basename === "feedly_active.opml" ||
      basename === "bsky_watchlist_core.txt" ||
      basename.endsWith(".local.json") ||
      basename.endsWith("_sent.json")
    );
  }

  function checks() {
    const f = fields();
    const coreTerms = cleanLines(f.coreTerms?.value);
    const negativeTerms = cleanLines(f.negativeTerms?.value).map((term) => term.toLowerCase());
    const bskyQueries = cleanLines(f.bskyQueries?.value);
    const watchlist = cleanLines(f.watchlist?.value);
    const rssFeeds = cleanLines(f.rssFeeds?.value);
    const invalidFeeds = rssFeeds.filter((url) => !isLikelyFeedUrl(url));
    const invalidHandles = watchlist.filter((handle) => !isLikelyBskyHandle(handle));
    const overlap = coreTerms.filter((term) => negativeTerms.includes(term.toLowerCase()));
    const stateFile = f.stateFile?.value?.trim() || "sent_items.json";

    return [
      {
        level: coreTerms.length >= 3 ? "ok" : "warn",
        body: coreTerms.length >= 3 ? tx("coreOk")(coreTerms.length) : tx("coreWarn"),
      },
      {
        level: rssFeeds.length > 0 && invalidFeeds.length === 0 ? "ok" : "warn",
        body: invalidFeeds.length ? tx("rssWarn")(invalidFeeds.length) : tx("rssOk")(rssFeeds.length),
      },
      {
        level: bskyQueries.length > 0 || watchlist.length > 0 ? "ok" : "warn",
        body: tx("blueskyOk")(bskyQueries.length, watchlist.length),
      },
      {
        level: invalidHandles.length === 0 ? "ok" : "warn",
        body: invalidHandles.length ? tx("bskyHandleWarn")(invalidHandles.length) : tx("bskyHandleOk"),
      },
      {
        level: isPrivateRuntimePath(stateFile) ? "ok" : "warn",
        body: isPrivateRuntimePath(stateFile) ? tx("stateOk") : tx("stateWarn"),
      },
      {
        level: overlap.length === 0 ? "ok" : "warn",
        body: overlap.length ? tx("overlapWarn")(overlap.join(", ")) : tx("overlapOk"),
      },
      {
        level: "info",
        body: tx("privacyInfo"),
      },
    ];
  }

  function renderHealth() {
    if (!healthList) {
      return;
    }

    healthList.replaceChildren();
    checks().forEach((check) => {
      const item = document.createElement("li");
      const badge = document.createElement("span");
      const body = document.createElement("p");
      item.className = `health-item ${check.level}`;
      badge.textContent = check.level.toUpperCase();
      body.textContent = check.body;
      item.append(badge, body);
      healthList.append(item);
    });
  }

  function renderText() {
    document.querySelectorAll("[data-enhance-i18n]").forEach((node) => {
      node.textContent = tx(node.dataset.enhanceI18n);
    });
    if (toolMessage) {
      toolMessage.textContent = tx(messageKey);
      toolMessage.dataset.type = messageType;
    }
    renderHealth();
  }

  function setMessage(key, type) {
    messageKey = key;
    messageType = type || "info";
    renderText();
  }

  function rerender() {
    if (typeof render === "function") {
      render();
    } else {
      document.querySelector("#profileName")?.dispatchEvent(new Event("input", { bubbles: true }));
    }
    renderHealth();
  }

  function applyProfile(profile) {
    const f = fields();
    const files = profile.files || {};
    const settings = profile.settings || {};
    const scoring = profile.scoring || {};
    const bluesky = profile.bluesky || {};

    if (typeof profile.name === "string" && f.profileName) {
      f.profileName.value = profile.name;
    }
    if (typeof files.state === "string" && f.stateFile) {
      f.stateFile.value = files.state;
    }
    if (Array.isArray(scoring.core_field_terms)) {
      setMultiline(f.coreTerms, scoring.core_field_terms);
    }
    if (Array.isArray(scoring.negative_terms)) {
      setMultiline(f.negativeTerms, scoring.negative_terms);
    }
    if (Array.isArray(bluesky.queries)) {
      setMultiline(f.bskyQueries, bluesky.queries);
    }

    setNumber(f.rssDays, settings.rss_max_age_days);
    setNumber(f.bskyDays, settings.bsky_max_age_days);
    setNumber(f.maxItems, settings.max_email_items);
  }

  function importOpml(value) {
    const doc = new DOMParser().parseFromString(value, "application/xml");
    if (doc.querySelector("parsererror")) {
      throw new Error("Invalid OPML/XML.");
    }

    const urls = Array.from(doc.querySelectorAll("outline"))
      .map((outline) => outline.getAttribute("xmlUrl") || outline.getAttribute("xmlurl") || outline.getAttribute("XMLURL"))
      .filter(Boolean);

    if (!urls.length) {
      throw new Error("No OPML xmlUrl entries found.");
    }

    setMultiline(fields().rssFeeds, urls);
  }

  async function handleImport(event, kind) {
    const [file] = event.target.files;
    if (!file) {
      return;
    }

    try {
      const value = await file.text();
      if (kind === "profile") {
        applyProfile(JSON.parse(value));
        setMessage("profileImported", "ok");
      } else if (kind === "watchlist") {
        setMultiline(fields().watchlist, cleanLines(value));
        setMessage("watchlistImported", "ok");
      } else {
        importOpml(value);
        setMessage("opmlImported", "ok");
      }
      rerender();
    } catch (error) {
      console.error(error);
      setMessage("importError", "warn");
    } finally {
      event.target.value = "";
    }
  }

  function injectStyles() {
    if (document.querySelector("#builderEnhancementStyles")) {
      return;
    }

    const style = document.createElement("style");
    style.id = "builderEnhancementStyles";
    style.textContent = `
      .builder-tools {
        display: grid;
        gap: 16px;
        padding: 18px 0 20px;
        border-top: 1px solid rgba(214, 185, 159, 0.8);
        border-bottom: 1px solid rgba(214, 185, 159, 0.72);
      }

      .builder-tools-head {
        display: grid;
        grid-template-columns: minmax(150px, 0.34fr) minmax(0, 1fr);
        gap: 24px;
        align-items: end;
      }

      .builder-tools-head h3,
      .health-head h3 {
        margin: 0;
        color: var(--lacquer);
        font-family: var(--font-title);
        font-size: clamp(1.22rem, 2vw, 1.6rem);
        font-weight: 400;
        line-height: 1.05;
      }

      .builder-tools-head p {
        margin: 0;
        max-width: 54ch;
        font-size: 0.95rem;
      }

      .import-controls {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
      }

      .file-picker {
        gap: 8px;
      }

      .file-picker input[type="file"] {
        min-height: 48px;
        cursor: pointer;
      }

      .file-picker input[type="file"]::file-selector-button {
        border: 1px solid var(--lacquer);
        border-radius: 999px;
        background: var(--rubin-red-dark);
        color: var(--paper-pale);
        margin-right: 10px;
        padding: 8px 12px;
        font: inherit;
        font-size: 0.84rem;
        font-weight: 800;
        cursor: pointer;
      }

      .tool-message {
        border: 1px solid rgba(90, 27, 34, 0.16);
        border-radius: 12px;
        background: rgba(255, 244, 223, 0.52);
        color: var(--muted);
        padding: 10px 12px;
        font-size: 0.94rem;
        font-weight: 700;
      }

      .tool-message[data-type="ok"] {
        border-color: rgba(31, 79, 100, 0.36);
        color: var(--lapis);
      }

      .tool-message[data-type="warn"] {
        border-color: rgba(155, 31, 46, 0.38);
        color: var(--rubin-red-dark);
      }

      .health-panel {
        display: grid;
        gap: 12px;
      }

      .health-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        border-top: 1px solid rgba(214, 185, 159, 0.58);
        padding-top: 14px;
      }

      .health-head button {
        border: 1px solid var(--lacquer);
        border-radius: 999px;
        background: transparent;
        color: var(--lacquer);
        cursor: pointer;
        font-size: 0.88rem;
        font-weight: 800;
        padding: 8px 12px;
        white-space: nowrap;
      }

      .health-head button:hover,
      .health-head button:focus-visible {
        background: var(--rubin-red-dark);
        color: var(--paper-pale);
        outline: none;
      }

      .health-list {
        display: grid;
        gap: 8px;
        margin: 0;
        padding: 0;
        list-style: none;
      }

      .health-item {
        display: grid;
        grid-template-columns: 64px minmax(0, 1fr);
        gap: 10px;
        align-items: start;
        border: 1px solid rgba(90, 27, 34, 0.12);
        border-radius: 12px;
        background: rgba(255, 244, 223, 0.44);
        padding: 10px 12px;
      }

      .health-item span {
        border-radius: 999px;
        background: rgba(31, 79, 100, 0.12);
        color: var(--lapis);
        padding: 3px 7px;
        text-align: center;
        font-size: 0.68rem;
        font-weight: 900;
        letter-spacing: 0.08em;
      }

      .health-item.warn span {
        background: rgba(155, 31, 46, 0.12);
        color: var(--rubin-red-dark);
      }

      .health-item.info span {
        background: rgba(226, 166, 31, 0.18);
        color: var(--smoke);
      }

      .health-item p {
        margin: 0;
        color: var(--muted);
        font-size: 0.94rem;
        line-height: 1.42;
      }

      @media (max-width: 920px) {
        .builder-tools-head,
        .import-controls {
          grid-template-columns: 1fr;
        }

        .health-head {
          align-items: stretch;
          flex-direction: column;
        }
      }
    `;
    document.head.append(style);
  }

  function buildPanel() {
    const builder = document.querySelector(".builder");
    if (!builder || document.querySelector("#builderTools")) {
      return;
    }

    injectStyles();
    const panel = document.createElement("section");
    panel.className = "builder-tools";
    panel.id = "builderTools";
    panel.setAttribute("aria-label", "Import and configuration checks");
    panel.innerHTML = `
      <div class="builder-tools-head">
        <div>
          <p class="kicker" data-enhance-i18n="kicker">Reuse</p>
          <h3 data-enhance-i18n="heading">Import & Check</h3>
        </div>
        <p data-enhance-i18n="body">Bring existing files back into the builder and check the setup before download.</p>
      </div>
      <div class="import-controls">
        <label class="file-picker">
          <span data-enhance-i18n="profile">JSON profile</span>
          <input id="importProfile" type="file" accept=".json,application/json" />
        </label>
        <label class="file-picker">
          <span data-enhance-i18n="watchlist">Watchlist</span>
          <input id="importWatchlist" type="file" accept=".txt,text/plain" />
        </label>
        <label class="file-picker">
          <span data-enhance-i18n="opml">OPML</span>
          <input id="importOpml" type="file" accept=".opml,.xml,text/xml,application/xml" />
        </label>
      </div>
      <div class="tool-message" id="toolMessage" role="status"></div>
      <div class="health-panel">
        <div class="health-head">
          <h3 data-enhance-i18n="health">Configuration checks</h3>
          <button id="runChecks" data-enhance-i18n="refresh" type="button">Refresh checks</button>
        </div>
        <ul class="health-list" id="healthList"></ul>
      </div>
    `;

    const heading = builder.querySelector(".section-heading");
    if (heading) {
      heading.after(panel);
    } else {
      builder.prepend(panel);
    }

    toolMessage = panel.querySelector("#toolMessage");
    healthList = panel.querySelector("#healthList");
    panel.querySelector("#importProfile").addEventListener("change", (event) => handleImport(event, "profile"));
    panel.querySelector("#importWatchlist").addEventListener("change", (event) => handleImport(event, "watchlist"));
    panel.querySelector("#importOpml").addEventListener("change", (event) => handleImport(event, "opml"));
    panel.querySelector("#runChecks").addEventListener("click", () => {
      setMessage("ready", "info");
      rerender();
    });

    Object.values(fields()).forEach((field) => {
      field?.addEventListener("input", renderHealth);
    });

    document.querySelectorAll("[data-lang-choice]").forEach((button) => {
      button.addEventListener("click", () => setTimeout(renderText, 0));
    });

    renderText();
  }

  function updateLocalRunCommand() {
    const localRun = document.querySelector(".next pre");
    if (!localRun) {
      return;
    }

    localRun.textContent = [
      "academic-radar --config .radar/profiles/local.json --summary",
      "academic-radar --config .radar/profiles/local.json --doctor",
      "academic-radar --config .radar/profiles/local.json --privacy-report",
      "academic-radar --config .radar/profiles/local.json --dry-run",
    ].join(LF);
  }

  function boot() {
    buildPanel();
    updateLocalRunCommand();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})();
