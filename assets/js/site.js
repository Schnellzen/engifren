(function () {
  var root = document.documentElement;

  /* ---------- language ---------- */
  function setLang(l, save) {
    root.dataset.lang = l;
    root.lang = l;
    document.querySelectorAll("[data-set-lang]").forEach(function (b) {
      b.setAttribute("aria-pressed", b.dataset.setLang === l ? "true" : "false");
    });
    document.querySelectorAll("[data-wa-" + l + "]").forEach(function (a) {
      a.href = a.getAttribute("data-wa-" + l);
    });
    if (save) { try { localStorage.setItem("engifren-lang", l); } catch (e) {} }
  }
  document.querySelectorAll("[data-set-lang]").forEach(function (b) {
    b.addEventListener("click", function () { setLang(b.dataset.setLang, true); });
  });
  setLang(root.dataset.lang || "id", false);

  /* ---------- project filter ---------- */
  var filters = document.querySelectorAll("[data-filter]");
  var cards = document.querySelectorAll(".projects .pcard[data-disc]");
  var empty = document.querySelector(".projects__empty");
  filters.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var f = btn.dataset.filter, shown = 0;
      filters.forEach(function (b) {
        var on = b === btn;
        b.classList.toggle("is-active", on);
        b.setAttribute("aria-pressed", on ? "true" : "false");
      });
      cards.forEach(function (c) {
        var show = f === "all" || c.dataset.disc.split(" ").indexOf(f) !== -1;
        c.hidden = !show;
        if (show) shown++;
      });
      if (empty) empty.hidden = shown > 0;
    });
  });

  /* ---------- gallery lightbox ---------- */
  var box = document.querySelector(".lightbox");
  if (box && box.showModal) {
    var img = box.querySelector("img"), cap = box.querySelector(".lightbox__cap");
    document.querySelectorAll(".gallery__item").forEach(function (item) {
      item.addEventListener("click", function () {
        img.src = item.dataset.full;
        var text = item.getAttribute("data-cap-" + root.dataset.lang) || "";
        img.alt = text;
        cap.textContent = text;
        box.showModal();
      });
    });
    box.addEventListener("click", function (e) { if (e.target === box) box.close(); });
  }
})();
