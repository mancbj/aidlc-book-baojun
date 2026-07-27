(() => {
  const TOC = {
    zh: [
      { id: "part-00", label: "Part 00 · 鸟瞰", hash: "#part-00-鸟瞰-ai-dlc" },
      { id: "ch01", label: "CH-01 · AI-native SDLC", hash: "#chapter-1" },
      { id: "ch02", label: "CH-02 · 人的判断", hash: "#chapter-2" },
      { id: "ch03", label: "CH-03 · Inception", hash: "#chapter-3" },
      { id: "ch04", label: "CH-04 · Memory Bank", hash: "#chapter-4" },
      { id: "ch05", label: "CH-05 · Bolts", hash: "#chapter-5" },
      { id: "ch06", label: "CH-06 · Exsecutio", hash: "#chapter-6" },
      { id: "ch07", label: "CH-07 · Verification", hash: "#chapter-7" },
      { id: "ch08", label: "CH-08 · Operations", hash: "#chapter-8" },
      { id: "ch09", label: "CH-09 · Adaptive", hash: "#chapter-9" },
      { id: "ch10", label: "CH-10 · Organization", hash: "#chapter-10" },
    ],
    en: [
      { id: "part-00", label: "Part 00 · Overview", hash: "#part-00" },
      { id: "ch01", label: "CH-01 · AI-native SDLC", hash: "#chapter-1" },
      { id: "ch02", label: "CH-02 · Human judgment", hash: "#chapter-2" },
      { id: "ch03", label: "CH-03 · Inception", hash: "#chapter-3" },
      { id: "ch04", label: "CH-04 · Memory Bank", hash: "#chapter-4" },
      { id: "ch05", label: "CH-05 · Bolts", hash: "#chapter-5" },
      { id: "ch06", label: "CH-06 · Exsecutio", hash: "#chapter-6" },
      { id: "ch07", label: "CH-07 · Verification", hash: "#chapter-7" },
      { id: "ch08", label: "CH-08 · Operations", hash: "#chapter-8" },
      { id: "ch09", label: "CH-09 · Adaptive", hash: "#chapter-9" },
      { id: "ch10", label: "CH-10 · Organization", hash: "#chapter-10" },
    ],
  };

  const params = new URLSearchParams(location.search);
  let locale = params.get("locale") || localStorage.getItem("aidlc-book-locale") || "zh";
  if (locale !== "en") locale = "zh";

  const frame = document.getElementById("book-frame");
  const tocList = document.getElementById("toc-list");
  const title = document.getElementById("reader-title");
  const bookUrl = `assets/${locale}/book.html`;

  function renderToc() {
    tocList.innerHTML = "";
    (TOC[locale] || TOC.zh).forEach((item, index) => {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.href = `${bookUrl}${item.hash}`;
      a.textContent = item.label;
      a.dataset.index = String(index);
      a.addEventListener("click", (event) => {
        event.preventDefault();
        navigate(index);
      });
      li.appendChild(a);
      tocList.appendChild(li);
    });
  }

  let current = 0;

  function navigate(index) {
    const items = TOC[locale] || TOC.zh;
    current = Math.max(0, Math.min(items.length - 1, index));
    const target = `${bookUrl}${items[current].hash}`;
    frame.src = target;
    document.querySelectorAll(".side-nav a").forEach((node) => {
      node.setAttribute("aria-current", node.dataset.index === String(current) ? "true" : "false");
    });
  }

  function setLocale(next) {
    locale = next === "en" ? "en" : "zh";
    localStorage.setItem("aidlc-book-locale", locale);
    document.documentElement.lang = locale === "zh" ? "zh-CN" : "en";
    title.textContent = locale === "zh" ? "深入理解 AI-DLC" : "Deep Understanding AI-DLC";
    document.querySelectorAll(".lang-switch button").forEach((btn) => {
      btn.setAttribute("aria-pressed", btn.dataset.locale === locale ? "true" : "false");
    });
    renderToc();
    navigate(0);
  }

  document.querySelectorAll(".lang-switch button").forEach((btn) => {
    btn.addEventListener("click", () => setLocale(btn.dataset.locale));
  });
  document.getElementById("prev-chapter").addEventListener("click", () => navigate(current - 1));
  document.getElementById("next-chapter").addEventListener("click", () => navigate(current + 1));

  setLocale(locale);
})();
