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

  /* =========================================================
     C. Diseño de malla de puesta a tierra — IEEE Std 80
     Método simplificado de IEEE Std 80 (edición 2000, que la edición 2013
     conserva) para una malla rectangular de retícula uniforme en suelo
     homogéneo. Cláusulas: 11.3 (calibre), 7.4 (Cs), 8 (tensiones
     tolerables), 14.2 (Rg, Sverak), 15.10 (Df), 16.5.1 (Em) y 16.5.2 (Es).
     Validada con los ejemplos B.1 a B.3 del Anexo B de la misma guía.
     ========================================================= */

  var F_HZ = 60;   // frecuencia del sistema en Colombia [Hz]
  var H0 = 1;      // profundidad de referencia de la malla h0 [m]

  // Calibres comerciales de cobre desnudo cableado: sección [mm²] y diámetro
  // aproximado [mm] (valores nominales de cable clase B, ASTM B8; 2/0 AWG
  // según el Anexo B de IEEE Std 80: 0,0105 m). Confirme con el fabricante.
  var CAL_MALLA = [
    { n: "4 AWG", s: 21.15, d: 5.9 }, { n: "2 AWG", s: 33.62, d: 7.4 },
    { n: "1/0 AWG", s: 53.49, d: 9.5 }, { n: "2/0 AWG", s: 67.43, d: 10.5 },
    { n: "3/0 AWG", s: 85.01, d: 11.9 }, { n: "4/0 AWG", s: 107.2, d: 13.4 },
    { n: "250 kcmil", s: 126.7, d: 14.6 }, { n: "300 kcmil", s: 152.0, d: 16.0 },
    { n: "350 kcmil", s: 177.3, d: 17.3 }, { n: "400 kcmil", s: 202.7, d: 18.5 },
    { n: "500 kcmil", s: 253.4, d: 20.7 }
  ];
  var S_MIN_MEC = 67.43; // 2/0 AWG: mínimo práctico por resistencia mecánica (IEEE Std 80, Anexo B)

  // Datos de los ejemplos del Anexo B de IEEE Std 80 (ρ = 400 Ω·m, gravilla de
  // 2 500 Ω·m y 0,102 m, 3I0 = 3 180 A en 115 kV, Sf = 0,6, tf = 0,5 s, 70 kg,
  // Df ≈ 1,0, conductor dimensionado con 6 814 A de la barra de 13 kV, d = 0,01 m).
  var BASE_B = { "m-rho": 400, "m-rhos": 2500, "m-hs": 0.102, "m-if": 3180, "m-sf": 0.6,
    "m-xr": 3.33, "m-df": 1, "m-tf": 0.5, "m-peso": 70, "m-d": 7, "m-h": 0.5,
    "m-mat": 7.06, "m-dc": 10, "m-ic": 6814 };
  var EJEMPLOS = {
    b1: { "m-lx": 70, "m-ly": 70, "m-nr": 0, "m-lr": 7.5, "m-ubic": "perimetro" },
    b2: { "m-lx": 70, "m-ly": 70, "m-nr": 20, "m-lr": 7.5, "m-ubic": "perimetro" },
    b3: { "m-lx": 84, "m-ly": 63, "m-nr": 38, "m-lr": 10, "m-ubic": "perimetro" }
  };

  var M_IDS = ["m-geo", "m-em-r", "m-es-r", "m-ifc", "m-kf", "m-amin", "m-cal", "m-cs", "m-k",
    "m-estep", "m-etouch", "m-area", "m-lt", "m-rg", "m-dfr", "m-ig", "m-gpr", "m-n", "m-kii",
    "m-kh", "m-km", "m-ki", "m-lm", "m-em", "m-ks", "m-ls", "m-es", "m-cmp-em", "m-cmp-es", "m-cmp-gpr"];

  /** Número con formato colombiano y hasta "dec" decimales (sin ceros de relleno). */
  function fnum(n, dec) {
    if (!isFinite(n)) return "—";
    return n.toLocaleString("es-CO", { maximumFractionDigits: dec == null ? 2 : dec });
  }

  /** Calcula todo el diseño. Recibe los datos en unidades SI (A, m, s, Ω·m). */
  function evaluarMalla(p) {
    var r = {};

    // --- Geometría: retícula uniforme de vanos enteros ---
    r.vx = Math.max(1, Math.round(p.Lx / p.D));   // vanos a lo largo de Lx
    r.vy = Math.max(1, Math.round(p.Ly / p.D));   // vanos a lo largo de Ly
    r.Dx = p.Lx / r.vx;
    r.Dy = p.Ly / r.vy;
    r.Dm = Math.max(r.Dx, r.Dy);                  // espaciamiento mayor → Km (lado seguro)
    r.Ds = Math.min(r.Dx, r.Dy);                  // espaciamiento menor → Ks (lado seguro)
    r.LC = (r.vx + 1) * p.Ly + (r.vy + 1) * p.Lx; // longitud de conductor horizontal [m]
    r.LR = p.nr * p.Lr;                           // longitud total de varillas [m]
    r.LT = r.LC + r.LR;
    r.A = p.Lx * p.Ly;
    r.Lp = 2 * (p.Lx + p.Ly);
    r.perim = p.nr > 0 && p.ubic === "perimetro"; // varillas en esquinas o perímetro

    // --- Factor de decremento (IEEE 80, 15.10): Df = √(1 + (Ta/tf)·(1 − e^(−2·tf/Ta))), Ta = (X/R)/(2πf) ---
    if (isFinite(p.Df)) {
      r.Df = p.Df;
      r.dfManual = true;
    } else {
      var Ta = p.XR / (2 * Math.PI * F_HZ);
      r.Df = Ta > 0 ? Math.sqrt(1 + Ta / p.tf * (1 - Math.exp(-2 * p.tf / Ta))) : 1;
      r.dfManual = false;
    }

    // --- 1. Calibre mínimo (IEEE 80, 11.3, ecuación simplificada con Kf de la tabla 2):
    //        A[kcmil] = I[kA]·Kf·√tc ; A[mm²] = A[kcmil]/1,9737 ---
    r.Ifc = (isFinite(p.Ic) ? p.Ic : p.If) * r.Df / 1000; // corriente asimétrica en el conductor [kA]
    r.Akcmil = r.Ifc * p.Kf * Math.sqrt(p.tf);
    r.Amm2 = r.Akcmil / 1.9737;
    r.cal = null;
    for (var i = 0; i < CAL_MALLA.length; i++) {
      if (CAL_MALLA[i].s >= Math.max(r.Amm2, S_MIN_MEC)) { r.cal = CAL_MALLA[i]; break; }
    }

    // --- 2. Factor de la capa superficial (IEEE 80, 7.4): Cs = 1 − 0,09·(1 − ρ/ρs)/(2·hs + 0,09) ---
    if (p.hs > 0) {
      r.rhoSup = p.rhos;
      r.Cs = 1 - 0.09 * (1 - p.rho / p.rhos) / (2 * p.hs + 0.09);
    } else {
      r.rhoSup = p.rho;   // sin capa superficial: Cs = 1 y ρs = ρ
      r.Cs = 1;
    }

    // --- 3. Tensiones tolerables (IEEE 80, cláusula 8): E = (1000 + c·Cs·ρs)·k/√ts,
    //        c = 6 (paso) o 1,5 (contacto); k = 0,116 (50 kg) o 0,157 (70 kg) ---
    r.k = p.peso === 70 ? 0.157 : 0.116;
    r.Estep = (1000 + 6 * r.Cs * r.rhoSup) * r.k / Math.sqrt(p.tf);
    r.Etouch = (1000 + 1.5 * r.Cs * r.rhoSup) * r.k / Math.sqrt(p.tf);

    // --- 4. Resistencia de la malla (Sverak; IEEE 80, 14.2):
    //        Rg = ρ·[1/LT + 1/√(20A)·(1 + 1/(1 + h·√(20/A)))] ---
    r.Rg = p.rho * (1 / r.LT + 1 / Math.sqrt(20 * r.A) * (1 + 1 / (1 + p.h * Math.sqrt(20 / r.A))));

    // --- 5. Corriente máxima de malla y GPR (IEEE 80, cláusula 15): IG = Df·Sf·If ; GPR = IG·Rg ---
    r.IG = r.Df * p.Sf * p.If;
    r.GPR = r.IG * r.Rg;

    // --- 6. Tensión de malla (IEEE 80, 16.5.1): Em = ρ·Km·Ki·IG/LM ---
    r.na = 2 * r.LC / r.Lp;
    r.nb = Math.sqrt(r.Lp / (4 * Math.sqrt(r.A)));
    r.n = r.na * r.nb;                             // nc = nd = 1 en mallas rectangulares
    r.Kii = r.perim ? 1 : 1 / Math.pow(2 * r.n, 2 / r.n);
    r.Kh = Math.sqrt(1 + p.h / H0);
    r.arg = r.Dm * r.Dm / (16 * p.h * p.d) + Math.pow(r.Dm + 2 * p.h, 2) / (8 * r.Dm * p.d) - p.h / (4 * p.d);
    r.Km = (Math.log(r.arg) + r.Kii / r.Kh * Math.log(8 / (Math.PI * (2 * r.n - 1)))) / (2 * Math.PI);
    r.Ki = 0.644 + 0.148 * r.n;
    r.LM = r.perim
      ? r.LC + (1.55 + 1.22 * p.Lr / Math.sqrt(p.Lx * p.Lx + p.Ly * p.Ly)) * r.LR
      : r.LC + r.LR;
    r.Em = p.rho * r.Km * r.Ki * r.IG / r.LM;

    // --- 7. Tensión de paso (IEEE 80, 16.5.2): Es = ρ·Ks·Ki·IG/LS ;
    //        Ks = (1/π)·[1/(2h) + 1/(D + h) + (1/D)·(1 − 0,5^(n−2))] ; LS = 0,75·LC + 0,85·LR ---
    r.Ks = (1 / (2 * p.h) + 1 / (r.Ds + p.h) + (1 - Math.pow(0.5, r.n - 2)) / r.Ds) / Math.PI;
    r.LS = 0.75 * r.LC + 0.85 * r.LR;
    r.Es = p.rho * r.Ks * r.Ki * r.IG / r.LS;

    // --- 8. Veredicto ---
    r.okEm = r.Em <= r.Etouch;
    r.okEs = r.Es <= r.Estep;
    r.okGpr = r.GPR <= r.Etouch;   // si se cumple, no hace falta más análisis (paso 7 del procedimiento)
    r.valido = isFinite(r.Em) && isFinite(r.Es) && r.arg > 0 && r.Km > 0 && r.Ks > 0;
    return r;
  }

  /** Busca el mayor espaciamiento (≥ 2,5 m) con el que la malla cumpliría, sin cambiar lo demás. */
  function espaciamientoQueCumple(p, r) {
    var lado = Math.min(p.Lx, p.Ly);
    var q = {};
    for (var key in p) { if (Object.prototype.hasOwnProperty.call(p, key)) q[key] = p[key]; }
    for (var v = Math.round(lado / r.Dm) + 1; v <= 400 && lado / v >= 2.5; v++) {
      q.D = lado / v;
      var t = evaluarMalla(q);
      if (t.valido && t.okEm && t.okEs) return { D: Math.max(t.Dx, t.Dy), nx: t.vx + 1, ny: t.vy + 1 };
    }
    return null;
  }

  /* ---------- Diagrama SVG de la malla ---------- */
  var firmaSvg = "";
  function dibujarMalla(p, r) {
    var svg = document.getElementById("m-svg");
    if (!svg) return;
    var firma = [p.Lx, p.Ly, r.vx, r.vy, p.nr, p.Lr, r.perim].join("|");
    if (firma !== firmaSvg) {
      firmaSvg = firma;
      var esc = Math.min(340 / p.Lx, 180 / p.Ly);
      var w = Math.max(p.Lx * esc, 40), hh = Math.max(p.Ly * esc, 40);
      var aEscala = p.Lx * esc >= 40 && p.Ly * esc >= 40;
      var x0 = 240 - w / 2, y0 = 138 - hh / 2, x1 = x0 + w, y1 = y0 + hh;
      var maxV = Math.max(r.vx, r.vy);
      var sw = maxV > 40 ? 1 : (maxV > 20 ? 1.6 : 2.6);
      var px = Math.ceil((r.vx + 1) / 120), py = Math.ceil((r.vy + 1) / 120); // en mallas muy densas se dibuja 1 de cada px
      var paso = Math.min(0.08, 0.9 / (r.vx + r.vy + 2));
      var k = 0, i, s = "";

      s += '<rect x="' + x0.toFixed(1) + '" y="' + y0.toFixed(1) + '" width="' + w.toFixed(1) + '" height="' + hh.toFixed(1) + '" fill="rgba(255,214,10,.04)"/>';
      // Malla más exigente para Em: la de la esquina
      s += '<rect id="m-svg-em" class="pulse" x="' + x0.toFixed(1) + '" y="' + y0.toFixed(1) + '" width="' + (w / r.vx).toFixed(1) + '" height="' + (hh / r.vy).toFixed(1) + '" fill="#52d17c" opacity=".45"/>';

      // Conductores
      s += '<g stroke="#c98a4b" stroke-width="' + sw + '" fill="none" stroke-linecap="round">';
      for (i = 0; i <= r.vy; i += py) {
        var y = y0 + i * hh / r.vy;
        s += '<path class="draw" style="--len:' + Math.ceil(w) + ';--d:' + (k++ * paso).toFixed(2) + 's" d="M' + x0.toFixed(1) + " " + y.toFixed(1) + " H" + x1.toFixed(1) + '"/>';
      }
      for (i = 0; i <= r.vx; i += px) {
        var x = x0 + i * w / r.vx;
        s += '<path class="draw" style="--len:' + Math.ceil(hh) + ';--d:' + (k++ * paso).toFixed(2) + 's" d="M' + x.toFixed(1) + " " + y0.toFixed(1) + " V" + y1.toFixed(1) + '"/>';
      }
      s += "</g>";

      // Varillas (ubicación esquemática)
      var nDib = Math.min(p.nr, 200), rr = nDib > 60 ? 2.5 : (nDib > 30 ? 3.5 : 5);
      var t0 = k * paso + 0.3;
      s += '<g fill="#ffd60a">';
      for (i = 0; i < nDib; i++) {
        var cx, cy;
        if (r.perim) {
          var u = i / nDib * 2 * (w + hh); // distancia recorrida por el perímetro desde la esquina
          if (u < w) { cx = x0 + u; cy = y0; }
          else if (u < w + hh) { cx = x1; cy = y0 + (u - w); }
          else if (u < 2 * w + hh) { cx = x1 - (u - w - hh); cy = y1; }
          else { cx = x0; cy = y1 - (u - 2 * w - hh); }
        } else {
          var cols = Math.ceil(Math.sqrt(nDib * w / hh)), filas = Math.ceil(nDib / cols);
          cx = x0 + ((i % cols) + 0.5) * w / cols;
          cy = y0 + (Math.floor(i / cols) + 0.5) * hh / filas;
        }
        s += '<circle class="pop" style="--d:' + (t0 + i * Math.min(0.05, 0.8 / nDib)).toFixed(2) + 's" cx="' + cx.toFixed(1) + '" cy="' + cy.toFixed(1) + '" r="' + rr + '"/>';
      }
      s += "</g>";

      // Punto más exigente para Es: fuera de la esquina, sobre la diagonal
      s += '<circle id="m-svg-es" class="pulse" cx="' + (x1 + 9).toFixed(1) + '" cy="' + (y1 + 9).toFixed(1) + '" r="5" fill="#52d17c"/>';

      // Cotas y rótulos
      var td = (t0 + 0.5).toFixed(2);
      s += '<g class="fade" style="--d:' + td + 's">';
      s += '<text x="' + x0.toFixed(1) + '" y="' + (y0 - 9).toFixed(1) + '" class="hl">Em</text>';
      s += '<text x="' + (x1 + 18).toFixed(1) + '" y="' + (y1 + 13).toFixed(1) + '" class="hl">Es</text>';
      s += '<text x="' + x1.toFixed(1) + '" y="' + (y0 - 9).toFixed(1) + '" text-anchor="end" class="lbl">D = ' + fnum(r.Dm, 2) + (Math.abs(r.Dx - r.Dy) > 0.005 ? " / " + fnum(r.Ds, 2) : "") + " m</text>";
      s += '<line x1="' + x0.toFixed(1) + '" y1="' + (y1 + 12).toFixed(1) + '" x2="' + x1.toFixed(1) + '" y2="' + (y1 + 12).toFixed(1) + '" stroke="#9aa3b8"/>';
      s += '<text x="240" y="' + (y1 + 28).toFixed(1) + '" text-anchor="middle" class="lbl">Lx = ' + fnum(p.Lx, 2) + " m</text>";
      s += '<line x1="' + (x0 - 12).toFixed(1) + '" y1="' + y0.toFixed(1) + '" x2="' + (x0 - 12).toFixed(1) + '" y2="' + y1.toFixed(1) + '" stroke="#9aa3b8"/>';
      s += '<text transform="rotate(-90 ' + (x0 - 18).toFixed(1) + ' 138)" x="' + (x0 - 18).toFixed(1) + '" y="138" text-anchor="middle" class="lbl">Ly = ' + fnum(p.Ly, 2) + " m</text>";
      s += '<line x1="20" y1="286" x2="40" y2="286" stroke="#c98a4b" stroke-width="2.6"/>';
      s += '<text x="46" y="290" class="lbl">' + (r.vx + 1) + " × " + (r.vy + 1) + " conductores" + (aEscala ? "" : " (no a escala)") + "</text>";
      if (p.nr > 0) {
        s += '<circle cx="262" cy="286" r="5" fill="#ffd60a"/>';
        s += '<text x="272" y="290" class="lbl">' + p.nr + " varillas de " + fnum(p.Lr, 2) + " m" + (r.perim ? " (perímetro)" : " (interior)") + "</text>";
      }
      s += "</g>";

      svg.innerHTML = s;
      svg.setAttribute("aria-label", "Vista en planta de la malla: " + fnum(p.Lx, 2) + " m por " + fnum(p.Ly, 2) + " m, " +
        (r.vx + 1) + " por " + (r.vy + 1) + " conductores y " + p.nr + " varillas");
    }
    // Colores del veredicto (verde cumple, rojo no cumple)
    var em = document.getElementById("m-svg-em"), es = document.getElementById("m-svg-es");
    if (em) em.setAttribute("fill", r.okEm ? "#52d17c" : "#ff5d73");
    if (es) es.setAttribute("fill", r.okEs ? "#52d17c" : "#ff5d73");
  }

  function limpiarMalla(msg) {
    M_IDS.forEach(function (id) { W.out(id, "—"); });
    W.status("m-status", "bad", msg);
    W.status("m-st-em", "info", "—");
    W.status("m-st-es", "info", "—");
    var sug = document.getElementById("m-sug"), av = document.getElementById("m-avisos");
    if (sug) sug.hidden = true;
    if (av) av.hidden = true;
  }

  function malla() {
    var p = {
      rho: W.num("m-rho"), rhos: W.num("m-rhos"), hs: W.num("m-hs"),
      If: W.num("m-if"), Sf: W.num("m-sf"), XR: W.num("m-xr"), Df: W.num("m-df"),
      tf: W.num("m-tf"), peso: W.num("m-peso"),
      Lx: W.num("m-lx"), Ly: W.num("m-ly"), D: W.num("m-d"), h: W.num("m-h"),
      nr: W.num("m-nr"), Lr: W.num("m-lr"), ubic: document.getElementById("m-ubic").value,
      Kf: W.num("m-mat"), d: W.num("m-dc") / 1000, Ic: W.num("m-ic")
    };
    if (isNaN(p.hs)) p.hs = 0;
    if (isNaN(p.nr)) p.nr = 0;
    if (p.nr === 0 && !(p.Lr > 0)) p.Lr = 0;

    // Validación de entradas
    var err = "";
    if (!(p.rho > 0)) err = "La resistividad del suelo debe ser positiva.";
    else if (!(p.hs >= 0) || (p.hs > 0 && !(p.rhos > 0))) err = "Revise la capa superficial: espesor ≥ 0 y resistividad positiva.";
    else if (!(p.If > 0)) err = "La corriente de falla debe ser positiva.";
    else if (!(p.Sf > 0 && p.Sf <= 1)) err = "El factor de división de corriente Sf debe estar entre 0 y 1.";
    else if (isNaN(p.Df) && !(p.XR >= 0)) err = "Ingrese la relación X/R (≥ 0) o el factor de decremento Df.";
    else if (!isNaN(p.Df) && !(p.Df >= 1)) err = "El factor de decremento Df no puede ser menor que 1.";
    else if (!(p.tf > 0)) err = "El tiempo de despeje debe ser positivo.";
    else if (!(p.Lx > 0 && p.Ly > 0)) err = "El largo y el ancho de la malla deben ser positivos.";
    else if (!(p.D > 0) || p.D > Math.min(p.Lx, p.Ly)) err = "El espaciamiento debe ser positivo y no mayor que el lado menor de la malla.";
    else if (!(p.h > 0)) err = "La profundidad de la malla debe ser positiva.";
    else if (!(p.nr >= 0) || p.nr !== Math.floor(p.nr)) err = "El número de varillas debe ser un entero ≥ 0.";
    else if (p.nr > 0 && !(p.Lr > 0)) err = "La longitud de las varillas debe ser positiva.";
    else if (!(p.d > 0)) err = "El diámetro del conductor debe ser positivo.";
    else if (!isNaN(p.Ic) && !(p.Ic > 0)) err = "La corriente para el calibre debe ser positiva (o deje el campo vacío).";
    if (err) { limpiarMalla(err); return; }

    var r = evaluarMalla(p);
    if (!r.valido) {
      limpiarMalla("Con estos datos las ecuaciones simplificadas de IEEE 80 no dan un resultado válido. Revise el espaciamiento, la profundidad y el diámetro del conductor.");
      return;
    }

    dibujarMalla(p, r);

    // Resumen
    W.out("m-geo", (r.vx + 1) + " × " + (r.vy + 1) + " · LC = " + fnum(r.LC, 1) + " m");
    W.out("m-em-r", W.fmt(r.Em, 1) + " V");
    W.out("m-es-r", W.fmt(r.Es, 1) + " V");

    // 1. Calibre
    W.out("m-ifc", W.fmt(r.Ifc, 3) + " kA");
    W.out("m-kf", W.fmt(p.Kf, 2));
    W.out("m-amin", W.fmt(r.Amm2, 1) + " mm² (" + W.fmt(r.Akcmil, 1) + " kcmil)");
    W.out("m-cal", r.cal ? r.cal.n + " (" + fnum(r.cal.s, 1) + " mm²; d ≈ " + fnum(r.cal.d, 1) + " mm)" : "> 500 kcmil");
    // 2. Cs
    W.out("m-cs", W.fmt(r.Cs, 3));
    // 3. Tolerables
    W.out("m-k", W.fmt(r.k, 3) + " (" + p.peso + " kg)");
    W.out("m-estep", W.fmt(r.Estep, 1) + " V");
    W.out("m-etouch", W.fmt(r.Etouch, 1) + " V");
    // 4. Rg
    W.out("m-area", fnum(r.A, 1) + " m²");
    W.out("m-lt", fnum(r.LC, 1) + " + " + fnum(r.LR, 1) + " = " + fnum(r.LT, 1) + " m");
    W.out("m-rg", W.fmt(r.Rg, 3) + " Ω");
    // 5. IG y GPR
    W.out("m-dfr", W.fmt(r.Df, 3) + (r.dfManual ? " (ingresado)" : " (con X/R)"));
    W.out("m-ig", W.fmt(r.IG, 1) + " A");
    W.out("m-gpr", W.fmt(r.GPR, 0) + " V");
    // 6. Em
    W.out("m-n", W.fmt(r.na, 3) + " × " + W.fmt(r.nb, 3) + " = " + W.fmt(r.n, 3));
    W.out("m-kii", W.fmt(r.Kii, 3) + (r.perim ? " (varillas en perímetro)" : ""));
    W.out("m-kh", W.fmt(r.Kh, 3));
    W.out("m-km", W.fmt(r.Km, 3));
    W.out("m-ki", W.fmt(r.Ki, 3));
    W.out("m-lm", fnum(r.LM, 1) + " m");
    W.out("m-em", W.fmt(r.Em, 1) + " V");
    // 7. Es
    W.out("m-ks", W.fmt(r.Ks, 3));
    W.out("m-ls", fnum(r.LS, 1) + " m");
    W.out("m-es", W.fmt(r.Es, 1) + " V");
    // 8. Veredicto
    var pEm = r.Em / r.Etouch * 100, pEs = r.Es / r.Estep * 100;
    W.out("m-cmp-em", W.fmt(r.Em, 1) + " V " + (r.okEm ? "≤" : ">") + " " + W.fmt(r.Etouch, 1) + " V");
    W.out("m-cmp-es", W.fmt(r.Es, 1) + " V " + (r.okEs ? "≤" : ">") + " " + W.fmt(r.Estep, 1) + " V");
    W.out("m-cmp-gpr", W.fmt(r.GPR, 0) + " V " + (r.okGpr ? "≤" : ">") + " " + W.fmt(r.Etouch, 1) + " V");
    W.status("m-st-em", r.okEm ? "ok" : "bad", (r.okEm ? "✓ Contacto: Em es el " : "✗ Contacto: Em es el ") + W.fmt(pEm, 0) + " % de la tensión de contacto tolerable.");
    W.status("m-st-es", r.okEs ? "ok" : "bad", (r.okEs ? "✓ Paso: Es es el " : "✗ Paso: Es es el ") + W.fmt(pEs, 0) + " % de la tensión de paso tolerable.");

    if (r.okEm && r.okEs) {
      W.status("m-status", "ok", r.okGpr
        ? "✓ Cumple: el GPR ya es menor que la tensión de contacto tolerable."
        : "✓ Cumple: las tensiones de malla y de paso son menores que las tolerables.");
    } else {
      W.status("m-status", "bad", "✗ No cumple: " + (!r.okEm && !r.okEs ? "las tensiones de malla y de paso superan" : (!r.okEm ? "la tensión de malla supera" : "la tensión de paso supera")) + " el valor tolerable. Modifique el diseño.");
    }

    // Sugerencias cuando no cumple
    var sug = document.getElementById("m-sug");
    if (sug) {
      var items = [];
      if (!r.okEm || !r.okEs) {
        var alt = espaciamientoQueCumple(p, r);
        items.push(alt
          ? "Reduzca el espaciamiento: con D ≈ " + fnum(alt.D, 2) + " m (" + alt.nx + " × " + alt.ny + " conductores) y lo demás igual, cumpliría."
          : "Reduzca el espaciamiento; aun con D = 2,5 m no alcanza por sí solo, así que combínelo con las medidas siguientes.");
        if (!r.perim) items.push("Agregue varillas en las esquinas y el perímetro: bajan la tensión de malla (Kii = 1 y mayor longitud efectiva LM).");
        else items.push("Agregue más varillas, o más largas, en el perímetro y las esquinas.");
        if (!(p.hs > 0)) items.push("Agregue una capa superficial de gravilla de 0,08 m a 0,15 m: su alta resistividad eleva las tensiones tolerables.");
        else items.push("Aumente el espesor o la resistividad de la capa de gravilla (suben las tensiones tolerables).");
        items.push("Reduzca el tiempo de despeje o la corriente que entra a la malla (Sf), o amplíe el área de la malla para bajar el GPR.");
      }
      sug.innerHTML = "";
      items.forEach(function (t) {
        var li = document.createElement("li");
        li.textContent = t;
        sug.appendChild(li);
      });
      sug.hidden = items.length === 0;
    }

    // Avisos sobre los límites del método
    var avisos = [];
    if (Math.abs(r.Dx - p.D) > 0.005 || Math.abs(r.Dy - p.D) > 0.005) {
      avisos.push("El espaciamiento se ajustó a vanos enteros: " + fnum(r.Dx, 2) + " m a lo largo de Lx y " + fnum(r.Dy, 2) + " m a lo largo de Ly.");
    }
    if (p.h < 0.25 || p.h > 2.5) avisos.push("Las ecuaciones simplificadas suponen profundidades entre 0,25 m y 2,5 m.");
    if (r.Dm < 2.5) avisos.push("Espaciamiento menor que 2,5 m: fuera del rango usual de las ecuaciones simplificadas.");
    if (p.d >= 0.25 * p.h) avisos.push("El diámetro del conductor debería ser menor que 0,25·h.");
    if (r.n > 25) avisos.push("n > 25: fuera del rango usual de las ecuaciones simplificadas.");
    if (p.tf < 0.03 || p.tf > 3) avisos.push("Los límites de corriente tolerable (Dalziel) aplican para duraciones entre 0,03 s y 3 s.");
    if (r.cal && p.d * 1000 < r.cal.d - 0.6) avisos.push("El diámetro ingresado es menor que el del calibre sugerido (" + r.cal.n + ", ≈ " + fnum(r.cal.d, 1) + " mm).");
    if (!r.cal) avisos.push("La sección mínima supera 500 kcmil: revise la corriente, el tiempo de despeje o el material.");
    var av = document.getElementById("m-avisos");
    if (av) {
      av.textContent = avisos.length ? "Avisos: " + avisos.join(" ") : "";
      av.hidden = avisos.length === 0;
    }
  }

  W.bind("form-malla", malla);

  // Botones que cargan los ejemplos del Anexo B de IEEE Std 80
  Array.prototype.forEach.call(document.querySelectorAll("[data-ejemplo]"), function (btn) {
    btn.addEventListener("click", function () {
      var ej = EJEMPLOS[btn.getAttribute("data-ejemplo")];
      if (!ej) return;
      [BASE_B, ej].forEach(function (datos) {
        for (var id in datos) {
          if (!Object.prototype.hasOwnProperty.call(datos, id)) continue;
          var el = document.getElementById(id);
          if (el) el.value = String(datos[id]);
        }
      });
      malla();
    });
  });
})();
