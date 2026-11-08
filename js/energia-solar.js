/* Calculadoras — Energía solar fotovoltaica */
(function () {
  "use strict";
  var W = window.Wiki;

  /* La lista de ciudades rellena el campo HSP; si el usuario lo edita, vuelve a "Personalizado". */
  var ciudad = document.getElementById("fv-ciudad");
  var hsp = document.getElementById("fv-hsp");
  ciudad.addEventListener("change", function () { if (ciudad.value) hsp.value = ciudad.value; });
  hsp.addEventListener("input", function () { ciudad.value = ""; });

  /* A. Número de paneles */
  function paneles() {
    var eMes = W.num("fv-e");
    var cob = W.num("fv-cob") / 100;
    var h = W.num("fv-hsp");
    var pr = W.num("fv-pr");
    var pmod = W.num("fv-pmod") / 1000; // Wp → kWp
    var area = W.num("fv-area");
    if (!(eMes > 0 && cob > 0 && h > 0 && pr > 0 && pmod > 0 && area > 0)) {
      ["fv-n", "fv-pp", "fv-pinst", "fv-gen", "fv-a", "fv-inv"].forEach(function (id) { W.out(id, "—"); });
      W.status("fv-status", "bad", "Revise los datos: todos deben ser positivos.");
      return;
    }
    var ed = eMes * cob / 30;            // kWh/día a cubrir
    var pp = ed / (h * pr);              // kWp requeridos
    var n = Math.ceil(pp / pmod);        // módulos
    var pinst = n * pmod;                // kWp instalados
    var gen = pinst * h * pr * 30;       // kWh/mes
    var a = n * area * 1.2;              // m² con pasillos

    W.out("fv-n", n + " módulos");
    W.out("fv-pp", W.fmt(pp, 2) + " kWp");
    W.out("fv-pinst", W.fmt(pinst, 2) + " kWp");
    W.out("fv-gen", W.fmt(gen, 0) + " kWh/mes");
    W.out("fv-a", W.fmt(a, 1) + " m²");
    W.out("fv-inv", "≈ " + W.fmt(pinst / 1.1, 1) + " kW");

    var pct = gen / eMes * 100;
    if (pinst > 1000) {
      W.status("fv-status", "info", "Más de 1 MW: ya no es autogeneración a pequeña escala (AGPE).");
    } else if (pinst > 100) {
      W.status("fv-status", "info", "Cubre ≈ " + W.fmt(pct, 0) + " % del consumo. AGPE mayor a 100 kW: revise las reglas de excedentes de la CREG 174.");
    } else {
      W.status("fv-status", "ok", "Cubre ≈ " + W.fmt(pct, 0) + " % del consumo. AGPE de hasta 100 kW (CREG 174).");
    }
  }

  /* B. Módulos en serie por string */
  function strings() {
    var voc = W.num("st-voc");
    var beta = W.num("st-beta");
    var tmin = W.num("st-tmin");
    var vmax = W.num("st-vmax");
    if (!(voc > 0 && vmax > 0) || !isFinite(beta) || !isFinite(tmin)) {
      ["st-n", "st-vc", "st-vs"].forEach(function (id) { W.out(id, "—"); });
      W.status("st-status", "bad", "Revise los datos.");
      return;
    }
    if (beta > 0) {
      W.status("st-status", "bad", "β de Voc normalmente es negativo (por ejemplo −0,27 %/°C).");
    }
    var vc = voc * (1 + beta / 100 * (tmin - 25));
    var n = Math.floor(vmax / vc);
    W.out("st-n", n + " módulos");
    W.out("st-vc", W.fmt(vc, 1) + " V");
    W.out("st-vs", W.fmt(n * vc, 0) + " V");
    if (beta <= 0) {
      if (n < 1) W.status("st-status", "bad", "Ni un módulo cabe: revise la tensión del inversor.");
      else W.status("st-status", "ok", "✓ " + n + " módulos dan " + W.fmt(n * vc, 0) + " V ≤ " + W.fmt(vmax, 0) + " V del inversor.");
    }
  }

  W.bind("form-fv", paneles);
  W.bind("form-string", strings);
})();
