(() => {
  const PAGE = 24;
  const PLAT_LABEL = { pc: "PC", console: "Console", mobile: "Mobile", general: "عام" };
  const state = { items: [], platform: "all", source: "all", q: "", shown: PAGE };
  const $ = (id) => document.getElementById(id);

  const timeAgo = (iso) => {
    const s = Math.max(1, (Date.now() - new Date(iso)) / 1000);
    if (s < 3600) return `قبل ${Math.round(s / 60)} دقيقة`;
    if (s < 86400) return `قبل ${Math.round(s / 3600)} ساعة`;
    return `قبل ${Math.round(s / 86400)} يوم`;
  };

  function filtered() {
    const q = state.q.trim().toLowerCase();
    return state.items.filter((i) =>
      (state.platform === "all" || i.platforms.includes(state.platform)) &&
      (state.source === "all" || i.source === state.source) &&
      (!q || (i.title + " " + i.excerpt).toLowerCase().includes(q))
    );
  }

  function render() {
    const list = filtered();
    const grid = $("grid");
    grid.textContent = "";
    list.slice(0, state.shown).forEach((i) => {
      const a = document.createElement("a");
      a.className = "card";
      a.href = i.link;
      a.target = "_blank";
      a.rel = "noopener noreferrer";

      const th = document.createElement("div");
      th.className = "thumb";
      if (i.image) th.style.backgroundImage = `url("${i.image.replace(/"/g, "%22")}")`;

      const body = document.createElement("div");
      body.className = "body";

      const tags = document.createElement("div");
      tags.className = "tags";
      const src = document.createElement("span");
      src.className = "tag src";
      src.textContent = i.source;
      tags.appendChild(src);
      i.platforms.forEach((p) => {
        const t = document.createElement("span");
        t.className = "tag";
        t.textContent = PLAT_LABEL[p] || p;
        tags.appendChild(t);
      });

      const h = document.createElement("h3");
      h.textContent = i.title;
      const p = document.createElement("p");
      p.textContent = i.excerpt;
      const d = document.createElement("span");
      d.className = "date";
      d.textContent = timeAgo(i.date);

      body.append(tags, h, p, d);
      a.append(th, body);
      grid.appendChild(a);
    });
    $("empty").hidden = list.length > 0;
    $("more").hidden = list.length <= state.shown;
  }

  function buildSources() {
    const names = [...new Set(state.items.map((i) => i.source))].sort();
    const box = $("sources");
    box.textContent = "";
    ["all", ...names].forEach((n) => {
      const b = document.createElement("button");
      b.className = "chip" + (n === state.source ? " on" : "");
      b.dataset.s = n;
      b.textContent = n === "all" ? "كل المصادر" : n;
      box.appendChild(b);
    });
  }

  async function load() {
    try {
      const r = await fetch("data/news.json?t=" + Date.now(), { cache: "no-store" });
      const data = await r.json();
      state.items = data.items || [];
      $("updated").textContent = new Date(data.updated).toLocaleString("ar-TN");
      buildSources();
      render();
    } catch (e) {
      $("updated").textContent = "تعذر تحميل الأخبار";
    }
  }

  document.querySelector(".filters").addEventListener("click", (e) => {
    const b = e.target.closest("[data-p]");
    if (!b) return;
    document.querySelectorAll("[data-p]").forEach((x) => x.classList.toggle("on", x === b));
    state.platform = b.dataset.p;
    state.shown = PAGE;
    render();
  });
  $("sources").addEventListener("click", (e) => {
    const b = e.target.closest("[data-s]");
    if (!b) return;
    state.source = b.dataset.s;
    state.shown = PAGE;
    buildSources();
    render();
  });
  let t;
  $("q").addEventListener("input", (e) => {
    clearTimeout(t);
    t = setTimeout(() => { state.q = e.target.value; state.shown = PAGE; render(); }, 200);
  });
  $("more").addEventListener("click", () => { state.shown += PAGE; render(); });

  load();
  setInterval(load, 10 * 60 * 1000); // يعيد تحميل البيانات كل 10 دقائق للزائر المفتوح
})();
