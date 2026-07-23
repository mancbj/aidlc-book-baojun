(() => {
  "use strict";

  const filters = Array.from(document.querySelectorAll("[data-filter]"));
  const actions = Array.from(document.querySelectorAll("#next-actions [data-priority]"));

  filters.forEach((button) => {
    button.addEventListener("click", () => {
      const selected = button.dataset.filter;
      filters.forEach((item) => {
        const active = item === button;
        item.classList.toggle("is-active", active);
        item.setAttribute("aria-pressed", String(active));
      });
      actions.forEach((action) => {
        action.hidden = selected !== "all" && action.dataset.priority !== selected;
      });
    });
  });
})();
