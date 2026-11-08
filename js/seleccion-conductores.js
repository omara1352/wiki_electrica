/* Calculadora — Selección de conductores
   Para actualizar la tabla de ampacidades, edite el objeto TABLA. */
(function () {
  "use strict";
  var W = window.Wiki;

  var CALIBRES = ["14 AWG", "12 AWG", "10 AWG", "8 AWG", "6 AWG", "4 AWG", "3 AWG", "2 AWG", "1 AWG",
    "1/0 AWG", "2/0 AWG", "3/0 AWG", "4/0 AWG", "250 kcmil", "300 kcmil", "350 kcmil", "400 kcmil", "500 kcmil"];

  // Sección en mm²
  var AREA = [2.08, 3.31, 5.26, 8.37, 13.3, 21.2, 26.7, 33.6, 42.4, 53.5, 67.4, 85.0, 107.2, 127, 152, 177, 203, 253];

  // Ampacidad [A] — máx. 3 conductores portadores en canalización, 30 °C ambiente
  // (valores de referencia de la tabla 310-16 / 310.15(B)(16) de la NTC 2050).
  var TABLA = {
    cu: {
      60: [15, 20, 30, 40, 55, 70, 85, 95, 110, 125, 145, 165, 195, 215, 240, 260, 280, 320],
      75: [20, 25, 35, 50, 65, 85, 100, 115, 130, 150, 175, 200, 230, 255, 285, 310, 335, 380],
      90: [25, 30, 40, 55, 75, 95, 115, 130, 145, 170, 195, 225, 260, 290, 320, 350, 380, 430]
    },
    al: {
      60: [null, 15, 25, 35, 40, 55, 65, 75, 85, 100, 115, 130, 150, 170, 195, 210, 225, 260],
      75: [null, 20, 30, 40, 50, 65, 75, 90, 100, 120, 135, 155, 180, 205, 230, 250, 270, 310],
      90: [null, 25, 35, 45, 55, 75, 85, 100, 115, 135, 150, 175, 205, 230, 260, 280, 305, 350]
    }
  };

  // Límite de la protección para conductores pequeños (14, 12, 10 AWG)
  var LIMITE = { cu: [15, 20, 30], al: [null, 15, 25] };

  // Resistividad a 75 °C [Ω·mm²/m]
  var RHO = { cu: 0.0210, al: 0.0345 };

  function ampacidad(mat, temp, i) {
    var a = TABLA[mat][temp][i];
    if (a == null) return null;
    var lim = LIMITE[mat][i];
    return lim != null ? Math.min(a, lim) : a;
  }

  function calcular() {
    var fases = W.num("c-sis");
    var V = W.num("c-v");
    var P = W.num("c-p") * 1000;
    var fp = W.num("c-fp");
    var L = W.num("c-l");
    var dvMax = W.num("c-dv");
    var mat = document.getElementById("c-mat").value;
    var temp = document.getElementById("c-t").value;
    var ft = W.num("c-ft");
    var fa = W.num("c-fa");
    var cont = document.getElementById("c-cont").checked;

    var ids = ["c-i", "c-id", "c-amp", "c-cdt", "c-rec", "c-iz", "c-dvr"];
    if (!(V > 0 && P > 0 && fp > 0 && fp <= 1 && L > 0 && dvMax > 0 && ft > 0 && fa > 0)) {
      ids.forEach(function (id) { W.out(id, "—"); });
      W.status("c-status", "bad", "Revise los datos: todos deben ser positivos y fp ≤ 1.");
      return;
    }

    var k = fases === 3 ? Math.sqrt(3) : 1;
    var I = P / (k * V * fp);
    var Id = cont ? 1.25 * I : I;

    // 1) Por ampacidad
    var iAmp = -1;
    for (var i = 0; i < CALIBRES.length; i++) {
      var a = ampacidad(mat, temp, i);
      if (a != null && a * ft * fa >= Id) { iAmp = i; break; }
    }

    // 2) Por caída de tensión (sección mínima)
    var factor = fases === 3 ? 100 * Math.sqrt(3) : 200;
    var Smin = factor * RHO[mat] * L * I / (dvMax * V);
    var iCdt = -1;
    for (var j = 0; j < AREA.length; j++) {
      if (AREA[j] >= Smin && TABLA[mat][temp][j] != null) { iCdt = j; break; }
    }

    W.out("c-i", W.fmt(I, 1) + " A");
    W.out("c-id", W.fmt(Id, 1) + " A");
    W.out("c-amp", iAmp >= 0 ? CALIBRES[iAmp] : "> 500 kcmil");
    W.out("c-cdt", iCdt >= 0 ? CALIBRES[iCdt] + " (≥ " + W.fmt(Smin, 1) + " mm²)" : "> 500 kcmil");

    if (iAmp < 0 || iCdt < 0) {
      W.out("c-rec", "Paralelo");
      W.out("c-iz", "—");
      W.out("c-dvr", "—");
      W.status("c-status", "bad", "Supera 500 kcmil: considere conductores en paralelo, mayor tensión o reducir la longitud.");
      return;
    }

    var iRec = Math.max(iAmp, iCdt);
    var Iz = ampacidad(mat, temp, iRec) * ft * fa;
    var dvReal = factor * RHO[mat] * L * I / (AREA[iRec] * V);

    W.out("c-rec", CALIBRES[iRec]);
    W.out("c-iz", W.fmt(Iz, 1) + " A");
    W.out("c-dvr", W.fmt(dvReal, 2) + " %");

    var manda = iCdt > iAmp ? "Manda la caída de tensión." : (iAmp > iCdt ? "Manda la ampacidad." : "Ambos criterios coinciden.");
    var nota = "";
    if (temp === "90") nota = " Recuerde: la columna de 90 °C solo es válida si todos los terminales lo permiten.";
    else if (temp === "75" && Id <= 100) nota = " Para ≤ 100 A verifique que los terminales sean de 75 °C (si no, use 60 °C).";
    W.status("c-status", "ok", "✓ " + CALIBRES[iRec] + " (" + W.fmt(AREA[iRec], 1) + " mm²). " + manda + nota);
  }

  W.bind("form-cond", calcular);
})();
