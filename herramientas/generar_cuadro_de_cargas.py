#!/usr/bin/env python3
"""Genera herramientas/cuadro_de_cargas.xlsx (Wiki Eléctrica CO).

Uso:  python3 herramientas/generar_cuadro_de_cargas.py [salida.xlsx]

Requiere openpyxl. Todas las celdas calculadas son fórmulas de Excel; después de
generar el archivo conviene abrirlo y guardarlo con Excel o LibreOffice para que
queden guardados los valores calculados (así se ve bien en visores sin motor de cálculo).

Fuentes de los valores (verificar siempre la versión vigente):
- Ampacidades: NTC 2050, Tabla 310.16 (segunda actualización) / 310-16 (primera act.).
- Protección máxima de 14, 12 y 10 AWG: NTC 2050, 240.4(D).
- Corrientes nominales de interruptores: NTC 2050, 240.6(A) (subconjunto comercial).
- Factores de demanda: NTC 2050, Tabla 220.42, 220.52, 220.53, 220.54, Tabla 220.55, 430.24.
"""
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation

SALIDA = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("cuadro_de_cargas.xlsx")

# ---------- Estilos ----------
FUENTE = "Arial"
AMARILLO = PatternFill("solid", fgColor="FFF200")      # celdas de entrada
OSCURO = PatternFill("solid", fgColor="0A0D14")        # títulos
ENCAB = PatternFill("solid", fgColor="1C2233")         # encabezados de tabla
GRIS = PatternFill("solid", fgColor="EEF0F4")          # cálculo auxiliar
SUAVE = PatternFill("solid", fgColor="F7F8FA")         # totales
ROJO = PatternFill("solid", bgColor="FF5D73", fgColor="FF5D73")
VERDE = PatternFill("solid", bgColor="C8F0D4", fgColor="C8F0D4")
LINEA = Side(style="thin", color="B5BBC9")
BORDE = Border(left=LINEA, right=LINEA, top=LINEA, bottom=LINEA)

F_NORMAL = Font(name=FUENTE, size=10)
F_NEGRITA = Font(name=FUENTE, size=10, bold=True)
F_TITULO = Font(name=FUENTE, size=14, bold=True, color="FFD60A")
F_ENCAB = Font(name=FUENTE, size=10, bold=True, color="FFFFFF")
F_SECCION = Font(name=FUENTE, size=11, bold=True, color="FFD60A")
F_NOTA = Font(name=FUENTE, size=9, italic=True, color="555B6B")
F_AUX = Font(name=FUENTE, size=9, color="555B6B")

CENTRO = Alignment(horizontal="center", vertical="center", wrap_text=True)
IZQ = Alignment(horizontal="left", vertical="center", wrap_text=True)
ARRIBA = Alignment(horizontal="left", vertical="top", wrap_text=True)

FMT_W = "#,##0;-#,##0;;@"        # oculta los ceros
FMT_A = "0.0;-0.0;;@"
FMT_PCT = "0.0%"


def celda(ws, ref, valor=None, fuente=F_NORMAL, relleno=None, alin=None, fmt=None, borde=True):
    c = ws[ref]
    if valor is not None:
        c.value = valor
    c.font = fuente
    if relleno is not None:
        c.fill = relleno
    if alin is not None:
        c.alignment = alin
    if fmt is not None:
        c.number_format = fmt
    if borde:
        c.border = BORDE
    return c


def titulo(ws, texto, hasta_col, fila=1):
    ws.merge_cells(start_row=fila, start_column=1, end_row=fila, end_column=hasta_col)
    for col in range(1, hasta_col + 1):
        ws.cell(fila, col).fill = OSCURO
    celda(ws, f"A{fila}", texto, F_TITULO, OSCURO, Alignment(horizontal="left", vertical="center"), borde=False)
    ws.row_dimensions[fila].height = 30


def seccion(ws, fila, texto, hasta_col):
    ws.merge_cells(start_row=fila, start_column=1, end_row=fila, end_column=hasta_col)
    for col in range(1, hasta_col + 1):
        ws.cell(fila, col).fill = ENCAB
    celda(ws, f"A{fila}", texto, F_SECCION, ENCAB, Alignment(horizontal="left", vertical="center"), borde=False)
    ws.row_dimensions[fila].height = 22


def encabezados(ws, fila, textos, col_ini=1, alto=42):
    for i, t in enumerate(textos):
        celda(ws, f"{L(col_ini + i)}{fila}", t, F_ENCAB, ENCAB, CENTRO)
    ws.row_dimensions[fila].height = alto


def nota(ws, fila, texto, hasta_col, alto=None, col_ini=1):
    ws.merge_cells(start_row=fila, start_column=col_ini, end_row=fila, end_column=hasta_col)
    celda(ws, f"{L(col_ini)}{fila}", texto, F_NOTA, None, ARRIBA, borde=False)
    if alto:
        ws.row_dimensions[fila].height = alto


wb = Workbook()
ws_i = wb.active
ws_i.title = "Instrucciones"
ws_d = wb.create_sheet("Datos")
ws_c = wb.create_sheet("Cuadro de cargas")
ws_a = wb.create_sheet("Acometida")
ws_x = wb.create_sheet("Auxiliar")
M = 6                       # circuitos monofásicos pequeños que se reparten probando todas las combinaciones
AX0 = 15                    # primera fila de combinaciones en la hoja Auxiliar
AX1 = AX0 + 3 ** M - 1
CC = "'Cuadro de cargas'!"

# =====================================================================
# Hoja "Datos"
# =====================================================================
ws = ws_d
titulo(ws, "Datos del sistema y tablas de referencia", 7)
celda(ws, "A2", "Celdas amarillas = datos de entrada (editables). Las demás celdas tienen fórmulas o valores de norma.",
      F_NOTA, borde=False)
celda(ws, "F2", "Entrada", F_NEGRITA, AMARILLO, CENTRO)

seccion(ws, 4, "1. Sistema eléctrico", 7)
encabezados(ws, 5, ["Parámetro", "Valor", "Unidad", "Nota / fuente"], alto=22)
ws.merge_cells("D5:G5")
sistema = [
    (6, "Tensión fase-neutro", 120, "V", True, "0",
     "Dato de entrada. Sistemas usuales en Colombia: 120 V (120/208 V) o 127 V (127/220 V)."),
    (7, "Tensión fase-fase", "=ROUND(B6*SQRT(3),0)", "V", False, "0",
     "Fórmula: tensión fase-neutro × √3, redondeada (120 → 208 V; 127 → 220 V)."),
    (8, "Sistema", '="Trifásico, 4 hilos, "&B6&"/"&B7&" V"', "", False, None,
     "El libro está hecho para sistemas trifásicos en estrella con neutro (fases R, S y T)."),
    (9, "Factor de potencia", 0.95, "", True, "0.00",
     "Supuesto de diseño (un solo valor para todas las cargas). Convierte W en VA: S = P / FP."),
    (10, "Límite de desbalance entre fases", 0.05, "%", True, "0.0%",
     "Criterio de diseño (5 %). No es un valor tomado del RETIE ni de la NTC 2050: confirme el límite que pida el operador de red."),
    (11, "Columna de temperatura para circuitos ramales", 60, "°C", True, "0",
     "60 o 75. NTC 2050, 110.14(C): hasta 100 A se usa la columna de 60 °C, salvo que los terminales estén marcados para 75 °C."),
    (12, "Columna de temperatura para la acometida", 75, "°C", True, "0",
     "60 o 75. Use 75 °C solo si los terminales del breaker principal y del medidor están marcados para 75 °C; si no, use 60."),
]
for fila, nombre, valor, unidad, entrada, fmt, texto in sistema:
    celda(ws, f"A{fila}", nombre, F_NORMAL, alin=IZQ)
    celda(ws, f"B{fila}", valor, F_NEGRITA, AMARILLO if entrada else None, CENTRO, fmt)
    celda(ws, f"C{fila}", unidad, F_NORMAL, alin=CENTRO)
    ws.merge_cells(f"D{fila}:G{fila}")
    celda(ws, f"D{fila}", texto, F_NOTA, alin=IZQ)
    for col in "EFG":
        ws[f"{col}{fila}"].border = BORDE
    ws.row_dimensions[fila].height = 28
ws.merge_cells("B8:C8")
dv_temp = DataValidation(type="list", formula1='"60,75"', allow_blank=False, showErrorMessage=True,
                         errorTitle="Valor no válido", error="Escriba 60 o 75.")
ws.add_data_validation(dv_temp)
dv_temp.add("B11:B12")

V_LN, V_LL, FP, LIM_DESB = "Datos!$B$6", "Datos!$B$7", "Datos!$B$9", "Datos!$B$10"

# ---- Tipos de carga y factores de demanda ----
seccion(ws, 14, "2. Tipos de carga y factores de demanda", 7)
encabezados(ws, 15, ["Tipo de carga", "Primer tramo: hasta (VA)", "Factor del primer tramo",
                     "Factor del resto", "Factor para la protección del circuito", "Fuente / nota"], alto=44)
ws.merge_cells("F15:G15")
T0, T1 = 16, 25   # filas de la tabla de tipos (10 filas, 2 libres)
tipos = [
    ("Alumbrado y tomas generales", 3000, 1.0, 0.35, 1.0,
     "NTC 2050, Tabla 220.42 (viviendas): primeros 3 000 VA al 100 %, de 3 001 a 120 000 VA al 35 %. "
     "Incluye los circuitos de pequeños artefactos y de lavandería de 1 500 VA cada uno (220.52). "
     "No se modela el tramo de más de 120 000 VA (25 %)."),
    ("Estufa o cocina eléctrica", None, 0.8, None, 1.0,
     "NTC 2050, Tabla 220.55: 80 % para un solo artefacto de menos de 8,75 kW. "
     "Para un artefacto de 8,75 a 12 kW la tabla fija 8 kW: ajuste el factor."),
    ("Secadora de ropa", None, 1.0, None, 1.0,
     "NTC 2050, 220.54: 5 000 W o la potencia de placa, la que sea mayor, al 100 % (hasta 4 secadoras)."),
    ("Calentador de agua", None, 1.0, None, 1.25,
     "Artefacto fijo al 100 % (220.53 permite 75 % si hay cuatro o más artefactos fijos). "
     "Circuito al 125 %: calentador de acumulación tratado como carga continua (422.13)."),
    ("Aire acondicionado", None, 1.0, None, 1.25,
     "100 % de la carga. Conductores y protección del circuito con el 125 % de la corriente nominal (sección 440)."),
    ("Motor o bomba", None, 1.0, None, 1.25,
     "100 % más el 25 % del motor mayor (430.24), que se suma aparte en el resumen de demanda. "
     "Conductores del circuito al 125 % (430.22)."),
    ("Otros artefactos fijos", None, 1.0, None, 1.0,
     "100 %. NTC 2050, 220.53 permite 75 % cuando hay cuatro o más artefactos fijos en una vivienda."),
    ("Reserva", None, 1.0, None, 1.0, "Circuitos de reserva (potencia 0 W) o cargas futuras al 100 %."),
    (None, None, None, None, None, "Fila libre para agregar otro tipo de carga."),
    (None, None, None, None, None, "Fila libre para agregar otro tipo de carga."),
]
for i, (nombre, lim, f1, f2, fprot, fuente) in enumerate(tipos):
    fila = T0 + i
    celda(ws, f"A{fila}", nombre, F_NORMAL, AMARILLO, IZQ)
    celda(ws, f"B{fila}", lim, F_NORMAL, AMARILLO, CENTRO, "#,##0")
    celda(ws, f"C{fila}", f1, F_NORMAL, AMARILLO, CENTRO, "0%")
    celda(ws, f"D{fila}", f2, F_NORMAL, AMARILLO, CENTRO, "0%")
    celda(ws, f"E{fila}", fprot, F_NORMAL, AMARILLO, CENTRO, "0.00")
    ws.merge_cells(f"F{fila}:G{fila}")
    celda(ws, f"F{fila}", fuente, F_NOTA, alin=IZQ)
    ws[f"G{fila}"].border = BORDE
    ws.row_dimensions[fila].height = 54 if i == 0 else (40 if len(fuente) > 105 else 28)
FILA_MOTOR = T0 + 5
nota(ws, T1 + 1,
     "Demanda de cada tipo = mín(S; primer tramo) × factor del primer tramo + máx(S − primer tramo; 0) × factor del resto, "
     "con S en VA. Si el primer tramo está vacío, todo el tipo lleva el factor del primer tramo. "
     "El factor para la protección multiplica la corriente del circuito antes de elegir el breaker (1,25 = carga continua o motor).",
     7, alto=40)
TIPOS = f"Datos!$A${T0}:$A${T1}"
T_FPROT = f"Datos!$E${T0}:$E${T1}"

# ---- Interruptores comerciales ----
B0 = 30
seccion(ws, B0 - 2, "3. Interruptores automáticos (breakers) comerciales", 7)
encabezados(ws, B0 - 1, ["Corriente nominal (A)"], alto=22)
breakers = [15, 20, 30, 40, 50, 60, 70, 80, 100, 125, 150, 175, 200, 225, 250, 300, 350, 400]
for i, b in enumerate(breakers):
    celda(ws, f"A{B0 + i}", b, F_NORMAL, alin=CENTRO, fmt="0")
B1 = B0 + len(breakers) - 1
ws.merge_cells(f"B{B0}:G{B0 + 3}")
celda(ws, f"B{B0}",
      "Corrientes nominales normalizadas de la NTC 2050, 240.6(A), limitadas a las que se consiguen "
      "normalmente en el comercio colombiano (se omiten 25, 35, 45, 90 y 110 A). Puede editar la lista, "
      "pero debe quedar en orden ascendente y sin celdas vacías.",
      F_NOTA, alin=ARRIBA, borde=False)
BRK = f"Datos!$A${B0}:$A${B1}"

# ---- Conductores ----
C0 = B1 + 4
seccion(ws, C0 - 2, "4. Conductores de cobre: ampacidad (NTC 2050, Tabla 310.16)", 7)
encabezados(ws, C0 - 1, ["Calibre", "Sección (mm²)", "Ampacidad 60 °C (A)", "Ampacidad 75 °C (A)",
                         "Protección máxima 240.4(D) (A)", "Ampacidad de diseño: ramales (A)",
                         "Ampacidad de diseño: acometida (A)"], alto=44)
calibres = ["14 AWG", "12 AWG", "10 AWG", "8 AWG", "6 AWG", "4 AWG", "3 AWG", "2 AWG", "1 AWG",
            "1/0 AWG", "2/0 AWG", "3/0 AWG", "4/0 AWG", "250 kcmil", "300 kcmil", "350 kcmil", "400 kcmil", "500 kcmil"]
area = [2.08, 3.31, 5.26, 8.37, 13.3, 21.2, 26.7, 33.6, 42.4, 53.5, 67.4, 85.0, 107.2, 127, 152, 177, 203, 253]
amp60 = [15, 20, 30, 40, 55, 70, 85, 95, 110, 125, 145, 165, 195, 215, 240, 260, 280, 320]
amp75 = [20, 25, 35, 50, 65, 85, 100, 115, 130, 150, 175, 200, 230, 255, 285, 310, 335, 380]
limite = [15, 20, 30]
for i, cal in enumerate(calibres):
    fila = C0 + i
    celda(ws, f"A{fila}", cal, F_NORMAL, alin=CENTRO)
    celda(ws, f"B{fila}", area[i], F_NORMAL, alin=CENTRO, fmt="0.0#")
    celda(ws, f"C{fila}", amp60[i], F_NORMAL, alin=CENTRO, fmt="0")
    celda(ws, f"D{fila}", amp75[i], F_NORMAL, alin=CENTRO, fmt="0")
    celda(ws, f"E{fila}", limite[i] if i < 3 else None, F_NORMAL, alin=CENTRO, fmt="0")
    # Ampacidad de diseño = ampacidad de la columna elegida, limitada por 240.4(D) en 14, 12 y 10 AWG
    for col, temp in (("F", "$B$11"), ("G", "$B$12")):
        celda(ws, f"{col}{fila}", f'=MIN(IF({temp}=75,D{fila},C{fila}),IF(E{fila}="",1E+9,E{fila}))',
              F_NORMAL, alin=CENTRO, fmt="0")
C1 = C0 + len(calibres) - 1
nota(ws, C1 + 1,
     "Ampacidades de la NTC 2050, Tabla 310.16 (Tabla 310-16 en la primera actualización): conductores de cobre aislados, "
     "máximo tres conductores portadores de corriente en canalización o cable, temperatura ambiente de 30 °C. "
     "No se aplican factores de corrección por temperatura ni por agrupamiento: si hay más de 30 °C o más de tres "
     "conductores portadores en el mismo ducto, corrija la ampacidad (vea el tema «Selección de conductores» de la wiki). "
     "Protección máxima de 14, 12 y 10 AWG según 240.4(D). Las ampacidades de diseño deben quedar en orden ascendente.",
     7, alto=66)
CAL = f"Datos!$A${C0}:$A${C1}"
MM2 = f"Datos!$B${C0}:$B${C1}"
AMP_R = f"Datos!$F${C0}:$F${C1}"
AMP_A = f"Datos!$G${C0}:$G${C1}"

for col, ancho in zip("ABCDEFG", (44, 15, 15, 15, 17, 26, 46)):
    ws.column_dimensions[col].width = ancho
ws.freeze_panes = "A4"

# =====================================================================
# Hoja "Cuadro de cargas"
# =====================================================================
ws = ws_c
N = 30                      # circuitos disponibles
R0 = 6                      # primera fila de circuitos
R1 = R0 + N - 1             # última fila de circuitos
RT = R1 + 1                 # fila de totales
ULT = 19                    # última columna de la tabla principal (S)

titulo(ws, "Cuadro de cargas", ULT)
ws.merge_cells("A2:J2")
celda(ws, "A2", f'="Sistema: "&Datos!B8&" · Factor de potencia: "&ROUND({FP},2)', F_NEGRITA, borde=False)
ws.merge_cells("A3:J3")
celda(ws, "A3", "Celdas amarillas = datos de entrada. No escriba en las demás: tienen fórmulas.", F_NOTA, borde=False)
celda(ws, "L3", "Entrada", F_NEGRITA, AMARILLO, CENTRO)
ws.merge_cells("L3:M3")

# Columnas de la tabla principal
(cN, cDesc, cTipo, cCant, cPu, cPt, cPol, cFija, cBmin, cFases, cR, cS, cT,
 cI, cId, cBrk, cCal, cMm, cObs) = [L(i) for i in range(1, 20)]
# Columnas del cálculo auxiliar
(xFija, xCarga, xCand, xCola, xG, xClave, xOrden, xIdx, xP, xPol, xFij, xAR, xAS, xAT, xFases, xR, xS, xT) = \
    [L(i) for i in range(21, 39)]

ws.merge_cells(f"A4:{cPt}4")
ws.merge_cells(f"{cPol}4:{cBmin}4")
ws.merge_cells(f"{cFases}4:{cT}4")
ws.merge_cells(f"{cI}4:{cObs}4")
for ref, texto in ((f"A4", "Circuito"), (f"{cPol}4", "Conexión"), (f"{cFases}4", "Reparto por fase"),
                   (f"{cI}4", "Protección y conductor")):
    celda(ws, ref, texto, F_ENCAB, OSCURO, CENTRO)
for col in range(1, ULT + 1):
    ws.cell(4, col).fill = OSCURO
    ws.cell(4, col).border = BORDE
encabezados(ws, 5, ["N.º", "Descripción", "Tipo de carga", "Cantidad", "Potencia unitaria (W)",
                    "Potencia total (W)", "Polos (1, 2 o 3)", "Fase fija (opcional)",
                    "Breaker mínimo (A) (opcional)", "Fases asignadas", "Carga fase R (W)",
                    "Carga fase S (W)", "Carga fase T (W)", "Corriente (A)", "Corriente de diseño (A)",
                    "Breaker sugerido (A)", "Calibre sugerido (Cu)", "Sección (mm²)", "Observación"], alto=44)

# Encabezados del cálculo auxiliar
ws.merge_cells(f"{xFija}4:{xT}4")
celda(ws, f"{xFija}4", "Cálculo auxiliar del reparto de fases (no editar)", F_AUX, GRIS, CENTRO)
aux_tit = ["Fase fija válida", "Carga activa (W)", "Candidato a combinaciones (W)", "N.º entre los 6 menores",
           "Carga para el reparto 1 (W)", "Clave de orden", "Orden", "Circuito en ese orden",
           "Carga (W)", "Polos", "Fase fija", "Acum. R (W)", "Acum. S (W)", "Acum. T (W)",
           "Fases", "A fase R (W)", "A fase S (W)", "A fase T (W)"]
for i, t in enumerate(aux_tit):
    celda(ws, f"{L(21 + i)}5", t, F_AUX, GRIS, CENTRO)

RNG = lambda col: f"${col}${R0}:${col}${R1}"
SQ3 = "SQRT(3)"

ejemplo = [
    ("Alumbrado zona social y cocina", 0, 10, 100, 1, None),
    ("Alumbrado habitaciones y baños", 0, 9, 100, 1, None),
    ("Tomas zona social", 0, 8, 180, 1, None),
    ("Tomas habitaciones", 0, 8, 180, 1, None),
    ("Tomas habitación principal y estudio", 0, 7, 180, 1, None),
    ("Pequeños artefactos de cocina 1", 0, 1, 1500, 1, 20),
    ("Pequeños artefactos de cocina 2", 0, 1, 1500, 1, 20),
    ("Lavandería y planchado", 0, 1, 1500, 1, 20),
    ("Estufa eléctrica de 4 puestos", 1, 1, 6000, 2, None),
    ("Calentador de agua de acumulación", 3, 1, 3500, 2, None),
    ("Aire acondicionado habitación principal", 4, 1, 2400, 2, None),
    ("Motobomba de agua", 5, 1, 900, 1, None),
]

for k in range(N):
    r = R0 + k
    ej = ejemplo[k] if k < len(ejemplo) else None
    celda(ws, f"{cN}{r}", k + 1, F_NORMAL, alin=CENTRO)
    celda(ws, f"{cDesc}{r}", ej[0] if ej else None, F_NORMAL, AMARILLO, IZQ)
    celda(ws, f"{cTipo}{r}", tipos[ej[1]][0] if ej else None, F_NORMAL, AMARILLO, IZQ)
    celda(ws, f"{cCant}{r}", ej[2] if ej else None, F_NORMAL, AMARILLO, CENTRO, "0.##")
    celda(ws, f"{cPu}{r}", ej[3] if ej else None, F_NORMAL, AMARILLO, CENTRO, "#,##0")
    celda(ws, f"{cPol}{r}", ej[4] if ej else None, F_NORMAL, AMARILLO, CENTRO, "0")
    celda(ws, f"{cFija}{r}", None, F_NORMAL, AMARILLO, CENTRO)
    celda(ws, f"{cBmin}{r}", ej[5] if ej else None, F_NORMAL, AMARILLO, CENTRO, "0")

    polos_ok = f"OR({cPol}{r}=1,{cPol}{r}=2,{cPol}{r}=3)"
    # Potencia total = cantidad × potencia unitaria
    celda(ws, f"{cPt}{r}", f"=IF(AND(ISNUMBER({cCant}{r}),ISNUMBER({cPu}{r})),{cCant}{r}*{cPu}{r},0)",
          F_NORMAL, alin=CENTRO, fmt=FMT_W)
    # Fases asignadas: las trae del cálculo auxiliar según el orden del circuito
    celda(ws, f"{cFases}{r}", f'=IF({xCarga}{r}<=0,"",IF({xCola}{r}>0,INDEX(Auxiliar!$B$9:${L(1 + M)}$9,{xCola}{r}),INDEX({RNG(xFases)},{xOrden}{r})))',
          F_NEGRITA, alin=CENTRO)
    # Carga por fase: la potencia se divide por igual entre las fases del circuito
    for col, letra in ((cR, "R"), (cS, "S"), (cT, "T")):
        celda(ws, f"{col}{r}", f'=IF(ISNUMBER(SEARCH("{letra}",{cFases}{r})),{cPt}{r}/LEN({cFases}{r}),0)',
              F_NORMAL, alin=CENTRO, fmt=FMT_W)
    # Corriente: 1 polo I = P/(Vfn·FP); 2 polos I = P/(Vff·FP); 3 polos I = P/(√3·Vff·FP)
    celda(ws, f"{cI}{r}",
          f"=IF({xCarga}{r}>0,{cPt}{r}/({FP}*IF({cPol}{r}=1,{V_LN},IF({cPol}{r}=2,{V_LL},{SQ3}*{V_LL}))),0)",
          F_NORMAL, alin=CENTRO, fmt=FMT_A)
    # Corriente de diseño = corriente × factor para la protección del tipo de carga (1 si no hay factor)
    fprot = f"INDEX({T_FPROT},MATCH({cTipo}{r},{TIPOS},0))"
    celda(ws, f"{cId}{r}", f"={cI}{r}*IFERROR(IF({fprot}>0,{fprot},1),1)", F_NORMAL, alin=CENTRO, fmt=FMT_A)
    # Breaker: primer valor comercial ≥ máx(corriente de diseño; breaker mínimo)
    celda(ws, f"{cBrk}{r}",
          f'=IF({cI}{r}>0,IFERROR(INDEX({BRK},SUMPRODUCT(--({BRK}<MAX({cId}{r},{cBmin}{r})))+1),"Fuera de tabla"),"")',
          F_NEGRITA, alin=CENTRO, fmt="0")
    # Calibre: primer conductor con ampacidad de diseño ≥ corriente nominal del breaker
    celda(ws, f"{cCal}{r}",
          f'=IF(ISNUMBER({cBrk}{r}),IFERROR(INDEX({CAL},SUMPRODUCT(--({AMP_R}<{cBrk}{r}))+1),"Fuera de tabla"),"")',
          F_NEGRITA, alin=CENTRO)
    celda(ws, f"{cMm}{r}", f'=IF(ISNUMBER({cBrk}{r}),IFERROR(INDEX({MM2},MATCH({cCal}{r},{CAL},0)),""),"")',
          F_NORMAL, alin=CENTRO, fmt="0.0#")
    celda(ws, f"{cObs}{r}",
          f'=IF({cPt}{r}<=0,"",IF(ISNA(MATCH({cTipo}{r},{TIPOS},0)),"Elija un tipo de carga de la lista",'
          f'IF(NOT({polos_ok}),"Polos debe ser 1, 2 o 3",'
          f'IF(AND({cFija}{r}<>"",LEN({cFija}{r})<>{cPol}{r}),"La fase fija no coincide con los polos: se asignó automáticamente",'
          f'IF(NOT(ISNUMBER({cBrk}{r})),"Corriente fuera de la tabla de breakers",'
          f'IF({cCal}{r}="Fuera de tabla","Breaker fuera de la tabla de conductores",""))))))',
          F_NOTA, alin=IZQ)

    # ---- Cálculo auxiliar: reparto de fases ----
    # Reparto 1: se ordenan los circuitos de mayor a menor carga (primero los de fase fija) y cada uno
    # se conecta a la fase (o par de fases) que lleve menos carga acumulada hasta ese momento.
    # Reparto 2: los M circuitos de 1 polo más pequeños (sin fase fija) se dejan por fuera y se
    # reparten en la hoja Auxiliar probando las 3^M combinaciones posibles.
    aux = {
        xFija: f'=IF(AND({cFija}{r}<>"",LEN({cFija}{r})={cPol}{r}),{cFija}{r},"")',
        xCarga: f"=IF(AND({cPt}{r}>0,{polos_ok}),{cPt}{r},0)",
        xCand: f'=IF(AND({xCarga}{r}>0,{cPol}{r}=1,{xFija}{r}=""),{xCarga}{r},0)',
        xCola: (f"=IF({xCand}{r}>0,IF(SUMPRODUCT(--({RNG(xCand)}>0),--({RNG(xCand)}+ROW({RNG(xCand)})*0.0001<{xCand}{r}+ROW()*0.0001))<{M},"
                f"SUMPRODUCT(--({RNG(xCand)}>0),--({RNG(xCand)}+ROW({RNG(xCand)})*0.0001<{xCand}{r}+ROW()*0.0001))+1,0),0)"),
        xG: f"=IF({xCola}{r}>0,0,{xCarga}{r})",
        xClave: f'={xG}{r}+IF(AND({xFija}{r}<>"",{xG}{r}>0),1E+9,0)-ROW()*0.0001',
        xOrden: f"=RANK({xClave}{r},{RNG(xClave)})",
        xIdx: f"=MATCH(ROW()-{R0 - 1},{RNG(xOrden)},0)",
        xP: f"=INDEX({RNG(xG)},{xIdx}{r})",
        xPol: f"=INDEX({RNG(cPol)},{xIdx}{r})",
        xFij: f"=INDEX({RNG(xFija)},{xIdx}{r})",
        xAR: f"=SUM({xR}${R0 - 1}:{xR}{r - 1})",
        xAS: f"=SUM({xS}${R0 - 1}:{xS}{r - 1})",
        xAT: f"=SUM({xT}${R0 - 1}:{xT}{r - 1})",
        xFases: (f'=IF({xP}{r}<=0,"",IF({xFij}{r}<>"",{xFij}{r},IF({xPol}{r}=3,"RST",IF({xPol}{r}=1,'
                 f'IF(AND({xAR}{r}<={xAS}{r},{xAR}{r}<={xAT}{r}),"R",IF({xAS}{r}<={xAT}{r},"S","T")),'
                 f'IF(AND({xAT}{r}>={xAR}{r},{xAT}{r}>={xAS}{r}),"RS",IF({xAR}{r}>={xAS}{r},"ST","TR"))))))'),
        xR: f'=IF(ISNUMBER(SEARCH("R",{xFases}{r})),{xP}{r}/LEN({xFases}{r}),0)',
        xS: f'=IF(ISNUMBER(SEARCH("S",{xFases}{r})),{xP}{r}/LEN({xFases}{r}),0)',
        xT: f'=IF(ISNUMBER(SEARCH("T",{xFases}{r})),{xP}{r}/LEN({xFases}{r}),0)',
    }
    for col, f in aux.items():
        celda(ws, f"{col}{r}", f, F_AUX, GRIS, CENTRO, "0.####" if col == xClave else "#,##0.##")

# ---- Fila de totales ----
ws.merge_cells(f"A{RT}:{cPu}{RT}")
celda(ws, f"A{RT}", "Totales", F_NEGRITA, SUAVE, Alignment(horizontal="right", vertical="center"))
for col in range(1, ULT + 1):
    ws.cell(RT, col).fill = SUAVE
    ws.cell(RT, col).border = BORDE
for col in (cPt, cR, cS, cT):
    celda(ws, f"{col}{RT}", f"=SUM({col}{R0}:{col}{R1})", F_NEGRITA, SUAVE, CENTRO, "#,##0")
ws.row_dimensions[RT].height = 20

# ---- Resumen ----
S0 = RT + 2
ws.merge_cells(f"A{S0}:{cT}{S0}")
for col in range(1, 14):
    ws.cell(S0, col).fill = ENCAB
celda(ws, f"A{S0}", "Totales del tablero", F_SECCION, ENCAB, Alignment(horizontal="left", vertical="center"), borde=False)
F_INST, F_KVA, F_DEM, F_IR, F_IS, F_IT, F_DESB = range(S0 + 1, S0 + 8)
# El resumen de demanda queda más abajo; se calcula su posición ahora para poder enlazarlo
D0 = F_DESB + 3            # fila de encabezados de la tabla de demanda
DT = D0 + 1 + len(tipos) + 1   # fila del total de demanda
resumen = [
    (F_INST, "Carga instalada", f"={cPt}{RT}", "W", "#,##0", "Suma de la potencia total de todos los circuitos."),
    (F_KVA, "Carga instalada", f"={cPt}{RT}/{FP}/1000", "kVA", "0.00", "Carga instalada ÷ factor de potencia."),
    (F_DEM, "Demanda con factores", f"=D{DT}/1000", "kVA", "0.00",
     "Total de la tabla «Demanda por tipo de carga» (factores de la hoja Datos)."),
    (F_IR, "Corriente fase R", f"={cR}{RT}/({FP}*{V_LN})", "A", "0.0", "Carga de la fase ÷ (FP × tensión fase-neutro), con la carga instalada."),
    (F_IS, "Corriente fase S", f"={cS}{RT}/({FP}*{V_LN})", "A", "0.0", "Ídem."),
    (F_IT, "Corriente fase T", f"={cT}{RT}/({FP}*{V_LN})", "A", "0.0", "Ídem."),
    (F_DESB, "Desbalance entre fases",
     f"=IF(MAX({cR}{RT}:{cT}{RT})=0,0,(MAX({cR}{RT}:{cT}{RT})-MIN({cR}{RT}:{cT}{RT}))/MAX({cR}{RT}:{cT}{RT}))",
     "%", FMT_PCT, None),
]
for fila, nombre, formula, unidad, fmt, texto in resumen:
    ws.merge_cells(f"A{fila}:B{fila}")
    celda(ws, f"A{fila}", nombre, F_NEGRITA, alin=IZQ)
    ws[f"B{fila}"].border = BORDE
    celda(ws, f"C{fila}", formula, F_NEGRITA, alin=CENTRO, fmt=fmt)
    celda(ws, f"D{fila}", unidad, F_NORMAL, alin=CENTRO)
    ws.merge_cells(f"E{fila}:{cT}{fila}")
    celda(ws, f"E{fila}", texto, F_NOTA, alin=IZQ, borde=False)
    ws.row_dimensions[fila].height = 20
celda(ws, f"E{F_DESB}",
      f'=IF(C{F_DESB}>{LIM_DESB},"Supera el límite de "&ROUND({LIM_DESB}*100,1)&" %: fije fases a mano o redistribuya cargas.",'
      f'"Dentro del límite de "&ROUND({LIM_DESB}*100,1)&" %.")&" Fórmula: (fase mayor − fase menor) ÷ fase mayor."',
      F_NOTA, alin=IZQ, borde=False)
# Desbalance en rojo si supera el límite de la hoja Datos (5 % por defecto)
ws.conditional_formatting.add(f"C{F_DESB}", CellIsRule(operator="greaterThan", formula=[LIM_DESB], fill=ROJO,
                                                        font=Font(name=FUENTE, bold=True, color="FFFFFF")))
ws.conditional_formatting.add(f"C{F_DESB}", CellIsRule(operator="lessThanOrEqual", formula=[LIM_DESB], fill=VERDE,
                                                        font=Font(name=FUENTE, bold=True, color="14532D")))

# ---- Demanda por tipo de carga ----
ws.merge_cells(f"A{D0 - 1}:{cT}{D0 - 1}")
for col in range(1, 14):
    ws.cell(D0 - 1, col).fill = ENCAB
celda(ws, f"A{D0 - 1}", "Demanda por tipo de carga (factores de la hoja Datos)", F_SECCION, ENCAB,
      Alignment(horizontal="left", vertical="center"), borde=False)
encabezados(ws, D0, ["Tipo de carga", "", "Carga instalada (W)", "Demanda (VA)", "Factor resultante", ""], alto=32)
ws.merge_cells(f"A{D0}:B{D0}")
ws.merge_cells(f"E{D0}:F{D0}")
ws[f"F{D0}"].border = BORDE
# Nota: en esta tabla C = carga instalada (W), D = demanda (VA), E = factor resultante
for i in range(len(tipos)):
    fila = D0 + 1 + i
    t = T0 + i
    ws.merge_cells(f"A{fila}:B{fila}")
    celda(ws, f"A{fila}", f'=IF(Datos!$A{t}="","",Datos!$A{t})', F_NORMAL, alin=IZQ)
    ws[f"B{fila}"].border = BORDE
    celda(ws, f"C{fila}", f'=IF(Datos!$A{t}="",0,SUMIF({RNG(cTipo)},Datos!$A{t},{RNG(cPt)}))',
          F_NORMAL, alin=CENTRO, fmt=FMT_W)
    # Demanda (VA) = mín(S; tramo)·f1 + máx(S − tramo; 0)·f2, con S = P/FP  (NTC 2050, Tabla 220.42)
    s = f"(C{fila}/{FP})"
    celda(ws, f"D{fila}",
          f'=IF(Datos!$B{t}="",{s}*Datos!$C{t},MIN({s},Datos!$B{t})*Datos!$C{t}+MAX({s}-Datos!$B{t},0)*Datos!$D{t})',
          F_NORMAL, alin=CENTRO, fmt=FMT_W)
    ws.merge_cells(f"E{fila}:F{fila}")
    celda(ws, f"E{fila}", f'=IF(C{fila}>0,D{fila}/(C{fila}/{FP}),"")', F_NORMAL, alin=CENTRO, fmt="0%")
    ws[f"F{fila}"].border = BORDE
FM = D0 + 1 + len(tipos)    # fila del 25 % del motor mayor
ws.merge_cells(f"A{FM}:B{FM}")
celda(ws, f"A{FM}", "25 % adicional del motor mayor (NTC 2050, 430.24)", F_NORMAL, alin=IZQ)
ws[f"B{FM}"].border = BORDE
celda(ws, f"C{FM}", f"=SUMPRODUCT(MAX(({RNG(cTipo)}=Datos!$A${FILA_MOTOR})*{RNG(cPt)}))", F_NORMAL, alin=CENTRO, fmt=FMT_W)
celda(ws, f"D{FM}", f"=0.25*C{FM}/{FP}", F_NORMAL, alin=CENTRO, fmt=FMT_W)
ws.merge_cells(f"E{FM}:F{FM}")
celda(ws, f"E{FM}", "Motor mayor (W)", F_NOTA, alin=CENTRO)
ws[f"F{FM}"].border = BORDE
assert DT == FM + 1
ws.merge_cells(f"A{DT}:B{DT}")
celda(ws, f"A{DT}", "Demanda total", F_NEGRITA, SUAVE, IZQ)
ws[f"B{DT}"].border = BORDE
celda(ws, f"C{DT}", f"=SUM(C{D0 + 1}:C{FM - 1})", F_NEGRITA, SUAVE, CENTRO, "#,##0")
celda(ws, f"D{DT}", f"=SUM(D{D0 + 1}:D{FM})", F_NEGRITA, SUAVE, CENTRO, "#,##0")
ws.merge_cells(f"E{DT}:F{DT}")
celda(ws, f"E{DT}", f'=IF(C{DT}>0,D{DT}/(C{DT}/{FP}),"")', F_NEGRITA, SUAVE, CENTRO, "0%")
ws[f"F{DT}"].border = BORDE
ws.merge_cells(f"G{DT}:{cT}{DT}")
celda(ws, f"G{DT}",
      f'=IF(ABS({cPt}{RT}-C{DT})>0.5,"Atención: hay "&ROUND({cPt}{RT}-C{DT},0)&" W en circuitos sin un tipo de carga válido; no entran en la demanda.","")',
      Font(name=FUENTE, size=9, bold=True, color="C00000"), alin=IZQ, borde=False)
nota(ws, DT + 2,
     "Método de reparto de fases: los circuitos se ordenan de mayor a menor carga y cada uno se conecta a la fase "
     "(1 polo) o al par de fases (2 polos) con menos carga acumulada; los de 3 polos se reparten en R, S y T. "
     "Los seis circuitos de 1 polo más pequeños se reparten al final probando todas sus combinaciones (hoja Auxiliar) "
     "y se elige la de menor diferencia entre fases. La carga de un circuito de 2 o 3 polos se divide por igual entre "
     "sus fases: es una aproximación de diseño, porque la corriente real por fase depende del ángulo de cada carga.",
     13, alto=56)
nota(ws, DT + 3,
     "Breaker: primer valor comercial ≥ corriente de diseño (NTC 2050, 210.20 y 240.6). Calibre: primer conductor de cobre cuya "
     "ampacidad (Tabla 310.16, columna elegida en Datos, con el tope de 240.4(D)) es ≥ el breaker. No incluye caída de tensión, "
     "factores de corrección por temperatura o agrupamiento, ni conductor de puesta a tierra.",
     13, alto=44)
# ---- Validaciones ----
dv_tipo = DataValidation(type="list", formula1=f"={TIPOS}", allow_blank=True, showErrorMessage=True,
                         errorTitle="Tipo no válido", error="Elija un tipo de carga de la lista (hoja Datos).")
dv_pol = DataValidation(type="list", formula1='"1,2,3"', allow_blank=True, showErrorMessage=True,
                        errorTitle="Polos", error="Escriba 1, 2 o 3.")
dv_fase = DataValidation(type="list", formula1='"R,S,T,RS,ST,TR,RST"', allow_blank=True, showErrorMessage=True,
                         errorTitle="Fase fija", error="Use R, S, T, RS, ST, TR o RST (tantas letras como polos).")
dv_num = DataValidation(type="decimal", operator="greaterThanOrEqual", formula1="0", allow_blank=True,
                        showErrorMessage=True, errorTitle="Número", error="Escriba un número mayor o igual a 0.")
for dv in (dv_tipo, dv_pol, dv_fase, dv_num):
    ws.add_data_validation(dv)
dv_tipo.add(f"{cTipo}{R0}:{cTipo}{R1}")
dv_pol.add(f"{cPol}{R0}:{cPol}{R1}")
dv_fase.add(f"{cFija}{R0}:{cFija}{R1}")
dv_num.add(f"{cCant}{R0}:{cPu}{R1}")
dv_num.add(f"{cBmin}{R0}:{cBmin}{R1}")

anchos = [5, 36, 27, 10, 12, 12, 9, 10, 12, 11, 11, 11, 11, 11, 11, 11, 13, 10, 42, 3]
for i, a in enumerate(anchos):
    ws.column_dimensions[L(i + 1)].width = a
for i in range(21, 39):
    ws.column_dimensions[L(i)].width = 12
ws.freeze_panes = f"C{R0}"
ws.page_setup.orientation = "landscape"
ws.page_setup.fitToWidth = 1
ws.page_setup.fitToHeight = 0
ws.sheet_properties.pageSetUpPr.fitToPage = True
ws.print_area = f"A1:{cObs}{DT + 3}"

# =====================================================================
# Hoja "Acometida"
# =====================================================================
ws = ws_a
titulo(ws, "Acometida y breaker principal", 4)
celda(ws, "A2", "Se calcula con la demanda total del cuadro de cargas. Celdas amarillas = datos de entrada.", F_NOTA, borde=False)

FASES_TOT = f"{CC}${cR}${RT}:${cT}${RT}"
filas_a = [
    ("s", "1. Demanda y corriente de diseño"),
    ("Carga instalada", f"={CC}{cPt}{RT}", "W", "#,##0", False, "Total de la hoja «Cuadro de cargas»."),
    ("Demanda total con factores", f"={CC}D{DT}", "VA", "#,##0", False,
     "Demanda por tipo de carga con los factores de la hoja Datos (NTC 2050, sección 220)."),
    ("Tensión fase-fase", f"={V_LL}", "V", "0", False, "Hoja Datos."),
    ("Corriente de demanda con carga equilibrada", "=B5/(SQRT(3)*B6)", "A", "0.0", False,
     "I = S ÷ (√3 × tensión fase-fase)."),
    ("Factor por desbalance", f"=IF(SUM({FASES_TOT})=0,1,MAX({FASES_TOT})/AVERAGE({FASES_TOT}))", "", "0.000", False,
     "Fase más cargada ÷ promedio de las tres fases. Lleva la corriente a la fase más cargada."),
    ("Reserva para ampliaciones", 0, "%", "0%", True,
     "Criterio de diseño, no normativo. Escriba, por ejemplo, 20 % si quiere dejar capacidad para cargas futuras."),
    ("Corriente de diseño de la acometida", "=B7*B8*(1+B9)", "A", "0.0", False,
     "Corriente de demanda × factor por desbalance × (1 + reserva)."),
    ("s", "2. Breaker principal y conductores"),
    ("Capacidad mínima del breaker principal (opcional)", None, "A", "0", True,
     "La NTC 2050, 230.79 fija capacidades mínimas del medio de desconexión (por ejemplo, 100 A para vivienda "
     "unifamiliar). Confirme el valor en la versión vigente y en las normas del operador de red, y escríbalo aquí."),
    ("Breaker principal sugerido (3 polos)",
     f'=IF(B10>0,IFERROR(INDEX({BRK},SUMPRODUCT(--({BRK}<MAX(B10,B12)))+1),"Fuera de tabla"),"")', "A", "0", False,
     "Primer valor comercial ≥ máx(corriente de diseño; capacidad mínima). NTC 2050, 230.90 y 240.6(A)."),
    ("Calibre mínimo de la acometida", "8 AWG", "", None, True,
     "NTC 2050, 230.23(B) y 230.31(B): mínimo 8 AWG en cobre. Verifique también el mínimo que exige el operador de red."),
    ("Calibre sugerido por fase (cobre)",
     f'=IF(ISNUMBER(B13),IFERROR(INDEX({CAL},MAX(SUMPRODUCT(--({AMP_A}<B13))+1,IFERROR(MATCH(B14&"",{CAL},0),1))),"Fuera de tabla"),"")',
     "", None, False,
     "Primer conductor con ampacidad ≥ breaker principal (Tabla 310.16, columna de temperatura de la hoja Datos), sin bajar del calibre mínimo."),
    ("Sección del conductor", f'=IFERROR(INDEX({MM2},MATCH(B15,{CAL},0)),"")', "mm²", "0.0#", False, "Equivalencia en SI del calibre sugerido."),
    ("Ampacidad del conductor", f'=IFERROR(INDEX({AMP_A},MATCH(B15,{CAL},0)),"")', "A", "0", False,
     "Tabla 310.16: máximo tres conductores portadores, 30 °C ambiente, sin factores de corrección."),
    ("Neutro", '=IF(B15="","",B15)', "", None, False,
     "Se sugiere el mismo calibre de las fases. La NTC 2050, 220.61 permite reducirlo en algunos casos: evalúelo aparte."),
    ("Verificación", '=IF(ISNUMBER(B17),IF(AND(B17>=B13,B17>=B10),"Cumple: ampacidad ≥ breaker ≥ corriente de diseño","Revisar"),"")',
     "", None, False, ""),
]
fila = 3
for item in filas_a:
    if item[0] == "s":
        seccion(ws, fila, item[1], 4)
        fila += 1
        continue
    nombre, valor, unidad, fmt, entrada, texto = item
    celda(ws, f"A{fila}", nombre, F_NORMAL, alin=IZQ)
    celda(ws, f"B{fila}", valor, F_NEGRITA, AMARILLO if entrada else None, CENTRO, fmt)
    celda(ws, f"C{fila}", unidad, F_NORMAL, alin=CENTRO)
    celda(ws, f"D{fila}", texto, F_NOTA, alin=IZQ)
    ws.row_dimensions[fila].height = 42 if len(texto) > 150 else (30 if len(texto) > 75 else 22)
    fila += 1
assert fila == 20, fila
ws.merge_cells("B19:D19")
ws["B19"].alignment = IZQ
ws.conditional_formatting.add("B19", FormulaRule(formula=['$B$19="Revisar"'], fill=ROJO,
                                                 font=Font(name=FUENTE, bold=True, color="FFFFFF")))
dv_cal = DataValidation(type="list", formula1=f"={CAL}", allow_blank=False, showErrorMessage=True,
                        errorTitle="Calibre", error="Elija un calibre de la lista (hoja Datos).")
ws.add_data_validation(dv_cal)
dv_cal.add("B14")
dv_pos = DataValidation(type="decimal", operator="greaterThanOrEqual", formula1="0", allow_blank=True,
                        showErrorMessage=True, errorTitle="Número", error="Escriba un número mayor o igual a 0.")
ws.add_data_validation(dv_pos)
dv_pos.add("B9")
dv_pos.add("B12")
nota(ws, 21,
     "Alcance: selección por ampacidad. No incluye caída de tensión, factores de corrección por temperatura o agrupamiento, "
     "corriente de cortocircuito, conductor de puesta a tierra ni los requisitos propios del operador de red (tipo de medida, "
     "acometida aérea o subterránea, calibres normalizados). La demanda de una vivienda se trata como carga no continua.",
     4, alto=54)
nota(ws, 22,
     "Verifique siempre la versión vigente del RETIE y de la NTC 2050. Herramienta educativa: no reemplaza el criterio de un "
     "profesional con matrícula vigente.", 4, alto=30)
for col, ancho in zip("ABCD", (46, 34, 8, 92)):
    ws.column_dimensions[col].width = ancho
ws.page_setup.orientation = "landscape"
ws.page_setup.fitToWidth = 1
ws.page_setup.fitToHeight = 0
ws.sheet_properties.pageSetUpPr.fitToPage = True

# =====================================================================
# Hoja "Instrucciones"
# =====================================================================
ws = ws_i
titulo(ws, "Cuadro de cargas para instalaciones eléctricas en Colombia", 2)
celda(ws, "A2", "Wiki Eléctrica CO · Basado en la NTC 2050 (Código Eléctrico Colombiano) y el RETIE · Herramienta educativa",
      F_NOTA, borde=False)
ws.merge_cells("A2:B2")
bloques = [
    ("s", "Qué hace este libro"),
    ("", "Arma el cuadro de cargas de un tablero trifásico (120/208 V por defecto): reparte los circuitos entre las fases R, S y T, "
         "calcula la corriente, sugiere breaker y calibre de cada circuito, aplica factores de demanda y dimensiona la acometida. "
         "Todo se calcula con fórmulas: al cambiar un dato, el resto se actualiza."),
    ("s", "Cómo usarlo"),
    ("1", "Escriba solo en las celdas amarillas. Las demás tienen fórmulas."),
    ("2", "Hoja «Datos»: revise la tensión fase-neutro (120 V da 120/208 V; 127 V da 127/220 V), el factor de potencia, "
          "el límite de desbalance y la columna de temperatura (60 o 75 °C) de los conductores. "
          "Ajuste los factores de demanda si su proyecto lo requiere."),
    ("3", "Hoja «Cuadro de cargas»: llene una fila por circuito con la descripción, el tipo de carga (lista desplegable), "
          "la cantidad, la potencia unitaria en W y el número de polos (1, 2 o 3). Hay espacio para 30 circuitos. "
          "El libro trae como ejemplo una vivienda de 12 circuitos: borre o reemplace esos datos."),
    ("4", "Las fases se asignan solas buscando el mejor balance. Si un circuito debe ir en una fase determinada, "
          "escríbala en «Fase fija» (R, S, T, RS, ST, TR o RST, con tantas letras como polos); el resto se reacomoda."),
    ("5", "Si un circuito necesita un breaker mayor al calculado, escríbalo en «Breaker mínimo». Por ejemplo, los circuitos de "
          "pequeños artefactos de cocina y de lavandería deben ser de 20 A (NTC 2050, 210.11(C))."),
    ("6", "Revise la columna «Observación» y el desbalance entre fases: se pone en rojo si supera el límite (5 % por defecto)."),
    ("7", "Hoja «Acometida»: lea el breaker principal y el calibre sugeridos. Si quiere, agregue una reserva para ampliaciones "
          "o una capacidad mínima del breaker principal."),
    ("s", "Cómo se calcula"),
    ("", "Potencia total = cantidad × potencia unitaria."),
    ("", "Corriente del circuito: 1 polo, I = P ÷ (Vfn × FP); 2 polos, I = P ÷ (Vff × FP); 3 polos, I = P ÷ (√3 × Vff × FP)."),
    ("", "Reparto de fases: los circuitos se ordenan de mayor a menor carga y cada uno se conecta a la fase (o al par de fases) "
         "con menos carga acumulada. Los seis circuitos de 1 polo más pequeños se reparten al final probando sus 729 combinaciones "
         "(hoja «Auxiliar», que no se edita) y se elige la más balanceada. La carga de un circuito de 2 o 3 polos se divide "
         "por igual entre sus fases. Es un método aproximado: no garantiza el balance óptimo."),
    ("", "Desbalance = (fase mayor − fase menor) ÷ fase mayor."),
    ("", "Breaker sugerido: primer valor comercial mayor o igual a la corriente de diseño (corriente × 1,25 en cargas continuas "
         "y motores). Valores de la NTC 2050, 240.6(A)."),
    ("", "Calibre sugerido: primer conductor de cobre con ampacidad mayor o igual al breaker, según la NTC 2050, Tabla 310.16, "
         "con el tope de 15, 20 y 30 A para 14, 12 y 10 AWG de 240.4(D)."),
    ("", "Demanda: a la carga de cada tipo (en VA) se le aplica su factor de la hoja Datos. Alumbrado y tomas generales de vivienda: "
         "primeros 3 000 VA al 100 % y el resto al 35 % (NTC 2050, Tabla 220.42). Se suma el 25 % del motor mayor (430.24)."),
    ("", "Acometida: corriente = demanda ÷ (√3 × Vff), llevada a la fase más cargada y con la reserva que se indique."),
    ("s", "Límites y advertencias"),
    ("", "Solo sistemas trifásicos de cuatro hilos (estrella con neutro). No sirve tal cual para acometidas monofásicas "
         "o bifásicas de tres hilos."),
    ("", "Selección por ampacidad solamente: no calcula caída de tensión, no aplica factores de corrección por temperatura "
         "(más de 30 °C) ni por agrupamiento (más de tres conductores portadores en un ducto), y no dimensiona el conductor "
         "de puesta a tierra."),
    ("", "Un solo factor de potencia para todas las cargas. Las potencias del ejemplo son ilustrativas."),
    ("", "La numeración de artículos corresponde a la NTC 2050 segunda actualización; en la primera actualización (1998) "
         "los mismos temas usan guion (por ejemplo, Tabla 220-11 y Tabla 310-16)."),
    ("", "Verifique siempre la versión vigente del RETIE y de la NTC 2050, y las normas del operador de red. "
         "Esta herramienta es educativa y no reemplaza el criterio de un profesional con matrícula vigente."),
]
fila = 4
for marca, texto in bloques:
    if marca == "s":
        seccion(ws, fila, texto, 2)
    else:
        celda(ws, f"A{fila}", marca if marca else "•", F_NEGRITA, alin=Alignment(horizontal="center", vertical="top"), borde=False)
        celda(ws, f"B{fila}", texto, F_NORMAL, alin=ARRIBA, borde=False)
        ws.row_dimensions[fila].height = 15 * (1 + len(texto) // 118) + 4
    fila += 1
celda(ws, f"B{fila + 1}", "Ejemplo de celda de entrada", F_NEGRITA, AMARILLO, CENTRO)
ws.column_dimensions["A"].width = 5
ws.column_dimensions["B"].width = 125
ws.sheet_view.showGridLines = False

# =====================================================================
# Hoja "Auxiliar": combinaciones de los M circuitos de 1 polo más pequeños
# =====================================================================
ws = ws_x
titulo(ws, "Cálculo auxiliar del reparto de fases (no editar)", 7)
nota(ws, 2, "Prueba las 729 formas de repartir entre R, S y T los seis circuitos de 1 polo más pequeños (sin fase fija) "
            "y elige la que deja la menor diferencia entre la fase más cargada y la menos cargada.", 7, alto=30)
encabezados(ws, 3, ["", "Fase R", "Fase S", "Fase T"], alto=20)
celda(ws, "A4", "Carga acumulada tras repartir los demás circuitos (W)", F_AUX, GRIS, IZQ)
for col, x in (("B", xR), ("C", xS), ("D", xT)):
    celda(ws, f"{col}4", f"=SUM({CC}{RNG(x)})", F_AUX, GRIS, CENTRO, "#,##0")
encabezados(ws, 6, ["Circuito pequeño n.º"] + list(range(1, M + 1)), alto=20)
celda(ws, "A7", "Carga (W)", F_AUX, GRIS, IZQ)
celda(ws, "A8", "Peso de la combinación (3^(n−1))", F_AUX, GRIS, IZQ)
celda(ws, "A9", "Fase elegida", F_AUX, GRIS, IZQ)
celda(ws, "A11", "Mejor combinación", F_AUX, GRIS, IZQ)
DIF = f"$E${AX0}:$E${AX1}"
celda(ws, "B11", f"=MATCH(MIN({DIF}),{DIF},0)-1", F_AUX, GRIS, CENTRO, "0")
for j in range(1, M + 1):
    col = L(1 + j)
    celda(ws, f"{col}7", f"=SUMPRODUCT(({CC}{RNG(xCola)}={j})*{CC}{RNG(xCand)})", F_AUX, GRIS, CENTRO, "#,##0")
    celda(ws, f"{col}8", 3 ** (j - 1), F_AUX, GRIS, CENTRO, "0")
    # El dígito n de la combinación (en base 3) indica la fase: 0 = R, 1 = S, 2 = T
    celda(ws, f"{col}9", f'=MID("RST",MOD(INT($B$11/{col}8),3)+1,1)', F_AUX, GRIS, CENTRO)
encabezados(ws, AX0 - 1, ["Combinación", "Fase R (W)", "Fase S (W)", "Fase T (W)", "Mayor − menor (W)"], alto=20)
PJ, PW = f"$B$7:${L(1 + M)}$7", f"$B$8:${L(1 + M)}$8"
for c in range(3 ** M):
    r = AX0 + c
    ws.cell(r, 1, c).font = F_AUX
    for k, base in enumerate(("$B$4", "$C$4", "$D$4")):
        cel = ws.cell(r, 2 + k, f"={base}+SUMPRODUCT({PJ}*(MOD(INT($A{r}/{PW}),3)={k}))")
        cel.font = F_AUX
        cel.number_format = "#,##0"
    cel = ws.cell(r, 5, f"=MAX(B{r}:D{r})-MIN(B{r}:D{r})")
    cel.font = F_AUX
    cel.number_format = "#,##0"
ws.column_dimensions["A"].width = 48
for col in "BCDEFG":
    ws.column_dimensions[col].width = 14
ws.freeze_panes = f"A{AX0}"

# Impresión: cada hoja ajustada al ancho de la página
for hoja, orient in ((ws_i, "portrait"), (ws_d, "landscape"), (ws_x, "portrait")):
    hoja.page_setup.orientation = orient
    hoja.page_setup.fitToWidth = 1
    hoja.page_setup.fitToHeight = 0
    hoja.sheet_properties.pageSetUpPr.fitToPage = True

wb.calculation.fullCalcOnLoad = True
SALIDA.parent.mkdir(parents=True, exist_ok=True)
wb.save(SALIDA)
print("Guardado:", SALIDA)
