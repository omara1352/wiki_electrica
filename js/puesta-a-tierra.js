/* Calculadoras — Puesta a tierra */
(function () {
  "use strict";
  var W = window.Wiki;

  /* A. Resistividad por Wenner: ρ = 2·π·a·R */
  var lastRho = NaN;
  function wenner() {
    var a = W.num("w-a");
    var R = W.num("w-r");
    if (!(a > 0) || !(R >= 0)) {
      W.out("w-rho", "—");
      W.status("w-status", "bad", "Ingrese valores positivos.");
      return;
    }
    lastRho = 2 * Math.PI * a * R;
    W.out("w-rho", W.fmt(lastRho, 1) + " Ω·m");
    var tipo;
    if (lastRho < 100) tipo = "Resistividad baja: terreno favorable (arcillas, suelos húmedos).";
    else if (lastRho < 1000) tipo = "Resistividad media: típica de suelos arenosos o mezclados.";
    else tipo = "Resistividad alta: roca o suelo seco. Considere malla, más electrodos o mejoramiento del terreno.";
    W.status("w-status", "info", tipo);
  }

  /* B. Resistencia de una varilla (Dwight): R = ρ/(2πL)·[ln(4L/r) − 1] */
  function varilla() {
    var rho = W.num("v-rho");
    var L = W.num("v-l");
    var r = W.num("v-d") / 2000; // mm de diámetro → m de radio
    var lim = W.num("v-lim");
    if (!(rho > 0) || !(L > 0) || !(r > 0)) {
      W.out("v-r", "—");
      W.out("v-n", "—");
      W.status("v-status", "bad", "Ingrese valores positivos.");
      return;
    }
    var R = rho / (2 * Math.PI * L) * (Math.log(4 * L / r) - 1);
    W.out("v-r", W.fmt(R, 2) + " Ω");

    // Estimación sencilla: Rn ≈ 1,2 · R1 / n
    var n = R <= lim ? 1 : Math.ceil(1.2 * R / lim);
    W.out("v-n", n > 20 ? "> 20" : String(n));

    if (L < 2.4) {
      W.status("v-status", "bad", "La longitud es menor que el mínimo de 2,4 m del RETIE.");
    } else if (R <= lim) {
      W.status("v-status", "ok", "✓ Cumple el valor de referencia de " + W.fmt(lim, 0) + " Ω con una sola varilla.");
    } else if (n > 20) {
      W.status("v-status", "bad", "✗ Supera ampliamente " + W.fmt(lim, 0) + " Ω. Se requiere una malla o mejorar el terreno.");
    } else {
      W.status("v-status", "bad", "✗ Supera " + W.fmt(lim, 0) + " Ω. Añada varillas, use un anillo/malla o mejore el terreno.");
    }
  }

  W.bind("form-wenner", wenner);
  W.bind("form-varilla", varilla);

  var useBtn = document.getElementById("w-use");
  if (useBtn) {
    useBtn.addEventListener("click", function () {
      if (!isFinite(lastRho)) return;
      document.getElementById("v-rho").value = lastRho.toFixed(1);
      varilla();
      document.getElementById("form-varilla").scrollIntoView({ behavior: "smooth", block: "center" });
    });
  }
})();
