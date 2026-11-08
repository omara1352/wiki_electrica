/* =========================================================
   Wiki Eléctrica Colombia — comportamiento compartido
   - Menú en celular
   - Aparición suave al hacer scroll (.reveal)
   - Brillo que sigue al cursor en las tarjetas (.card.live)
   - Paso a paso animado (.stepper)
   - Render de fórmulas con KaTeX (si está cargado)
   ========================================================= */

(function () {
  "use strict";

  /* ---------- Menú móvil ---------- */
  var menuBtn = document.querySelector(".menu-btn");
  var nav = document.querySelector(".nav");
  if (menuBtn && nav) {
    menuBtn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* ---------- Aparición al hacer scroll ---------- */
  var revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("visible"); });
  }

  /* ---------- Brillo de tarjetas ---------- */
  document.querySelectorAll(".card.live").forEach(function (card) {
    card.addEventListener("pointermove", function (e) {
      var r = card.getBoundingClientRect();
      card.style.setProperty("--mx", (e.clientX - r.left) + "px");
      card.style.setProperty("--my", (e.clientY - r.top) + "px");
    });
  });

  /* ---------- Paso a paso ---------- */
  document.querySelectorAll(".stepper").forEach(function (stepper) {
    var buttons = Array.prototype.slice.call(stepper.querySelectorAll(".step-list button"));
    var panels = Array.prototype.slice.call(stepper.querySelectorAll(".step-panel"));
    var prev = stepper.querySelector("[data-prev]");
    var next = stepper.querySelector("[data-next]");
    var play = stepper.querySelector("[data-play]");
    var bar = stepper.querySelector(".progress span");
    var current = 0;
    var timer = null;

    function show(i) {
      current = Math.max(0, Math.min(panels.length - 1, i));
      panels.forEach(function (p, k) {
        p.classList.remove("active");
        if (k === current) {
          void p.offsetWidth; // fuerza reinicio de las animaciones
          p.classList.add("active");
        }
      });
      buttons.forEach(function (b, k) {
        b.setAttribute("aria-selected", k === current ? "true" : "false");
        b.classList.toggle("done", k < current);
      });
      if (buttons[current] && window.innerWidth < 900) {
        var list = buttons[current].closest(".step-list");
        var li = buttons[current].parentElement;
        list.scrollTo({ left: li.offsetLeft - 16, behavior: "smooth" });
      }
      if (prev) prev.disabled = current === 0;
      if (next) next.disabled = current === panels.length - 1;
      if (bar) bar.style.width = ((current + 1) / panels.length * 100) + "%";
    }

    function stop() {
      clearInterval(timer);
      timer = null;
      if (play) play.innerHTML = "▶ Reproducir";
    }

    buttons.forEach(function (b, k) { b.addEventListener("click", function () { stop(); show(k); }); });
    if (prev) prev.addEventListener("click", function () { stop(); show(current - 1); });
    if (next) next.addEventListener("click", function () { stop(); show(current + 1); });
    if (play) play.addEventListener("click", function () {
      if (timer) { stop(); return; }
      if (current === panels.length - 1) show(0);
      play.innerHTML = "❚❚ Pausar";
      timer = setInterval(function () {
        if (current >= panels.length - 1) { stop(); return; }
        show(current + 1);
      }, 5000);
    });

    show(0);
  });

  /* ---------- Fórmulas con KaTeX ---------- */
  function renderMath() {
    if (window.renderMathInElement) {
      window.renderMathInElement(document.body, {
        delimiters: [
          { left: "$$", right: "$$", display: true },
          { left: "\\(", right: "\\)", display: false }
        ],
        throwOnError: false
      });
    }
  }
  if (document.readyState === "complete") renderMath();
  else window.addEventListener("load", renderMath);

  /* ---------- Año en el pie ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();

/* ---------- Utilidades para las calculadoras ---------- */
window.Wiki = {
  /** Lee un número de un input por id (acepta coma decimal). */
  num: function (id) {
    var el = document.getElementById(id);
    if (!el) return NaN;
    return parseFloat(String(el.value).replace(",", "."));
  },
  /** Formatea con separadores colombianos. */
  fmt: function (n, dec) {
    if (!isFinite(n)) return "—";
    return n.toLocaleString("es-CO", { minimumFractionDigits: dec || 0, maximumFractionDigits: dec || 0 });
  },
  /** Escribe un valor en un elemento y lo resalta brevemente. */
  out: function (id, text) {
    var el = document.getElementById(id);
    if (!el) return;
    if (el.textContent !== text) {
      el.textContent = text;
      el.classList.remove("flash");
      void el.offsetWidth;
      el.classList.add("flash");
    }
  },
  /** Muestra un mensaje de estado (ok | bad | info). */
  status: function (id, type, text) {
    var el = document.getElementById(id);
    if (!el) return;
    el.className = "status " + type;
    el.textContent = text;
  },
  /** Recalcula cada vez que cambie un campo dentro del formulario. */
  bind: function (formId, fn) {
    var form = document.getElementById(formId);
    if (!form) return;
    form.addEventListener("input", fn);
    form.addEventListener("change", fn);
    form.addEventListener("submit", function (e) { e.preventDefault(); fn(); });
    fn();
  }
};
