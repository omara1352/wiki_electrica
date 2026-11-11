# CLAUDE.md — Wiki Eléctrica CO

Reglas para trabajar en este repositorio. Responde y escribe todo el contenido en **español**.

## Propósito

Wiki de ingeniería eléctrica para Colombia, en español, publicada en **GitHub Pages** desde la rama `main` (carpeta raíz). Es contenido educativo: explicaciones cortas, procesos paso a paso, fórmulas, normativa colombiana y calculadoras.

## Tecnología

- **HTML, CSS y JavaScript puros.** Sin compilación, sin frameworks, sin `npm`, sin empaquetadores. El sitio debe funcionar abriendo `index.html` o con `python3 -m http.server 8000`.
- Única dependencia externa: **KaTeX 0.16.9** desde jsDelivr (CSS, `katex.min.js` y `contrib/auto-render.min.js`, con `defer`), más las fuentes Inter y JetBrains Mono de Google Fonts. No agregues otras librerías.
- JavaScript en estilo ES5 dentro de una IIFE con `"use strict"` (como los archivos existentes).
- Mantén el archivo `.nojekyll` en la raíz.
- Usa rutas relativas (`../css/styles.css`, `../js/main.js`, `../index.html`) para que funcione en `https://<usuario>.github.io/wiki_electrica/`.

## Estructura

```
index.html             Página principal: tarjetas de temas y marco normativo
temas/<tema>.html      Una página por tema
js/<tema>.js           Calculadora de cada tema
js/main.js             Comportamiento compartido y utilidades window.Wiki
css/styles.css         Estilos compartidos (colores en variables de :root)
assets/favicon.svg     Ícono
herramientas/          Archivos descargables (por ejemplo, cuadro_de_cargas.xlsx) y el script que los genera
```

Nombres de archivo en minúsculas, sin tildes, con guiones (`seleccion-conductores`).

## Diseño

- **Tema oscuro con acentos amarillo eléctrico** (`--accent: #ffd60a`, `--accent-2: #ffb703`; fondo `--bg: #0a0d14`). Colores de apoyo: `--cyan`, `--green`, `--red`.
- **Adaptable a celular**: revisa que todo se vea bien en pantallas angostas (menú `☰`, tablas dentro de `.table-wrap`, SVG con `viewBox`).
- **Reutiliza `css/styles.css` y `js/main.js`.** No crees hojas de estilo ni scripts compartidos nuevos; si hace falta un estilo nuevo, agrégalo a `styles.css` usando las variables de `:root`. Evita estilos en línea salvo ajustes puntuales (como `--d`, `--len` o `margin-top`).
- Clases existentes a reutilizar: `topbar`, `page-hero`, `breadcrumb`, `section-title`, `panel`, `concept`, `keypoints`, `stepper`, `formula`, `norms`/`norm`, `notice`, `calc`, `field`, `row-2`, `results`/`result`, `status`, `calc-note`, `table-wrap`, `pager`, `reveal` (con `data-delay`).
- Animaciones SVG disponibles en `styles.css`: `draw` (usa `--len`), `pop`, `fade`, `rise`, `grow`, `flow`, `pulse`, `blink`, `spin`. El retraso se da con `style="--d:0.5s"`.

## Estructura de cada tema

Copia el formato de `temas/puesta-a-tierra.html` (o de otro tema existente). Cada página tiene, en este orden, secciones numeradas con `section-title`:

1. **¿Qué es?** (`#concepto`): explicación corta en un `panel concept` con una lista `keypoints`.
2. **Proceso paso a paso** (`#proceso`): un `stepper` con `step-list` y un `step-panel` por paso. Cada paso lleva un **diagrama SVG animado** (`svg.diagram` con `role="img"` y `aria-label`), un título y un párrafo. Mantén los controles Anterior / Reproducir / Siguiente.
3. **Fórmulas clave** (`#formulas`): tarjetas `formula` con la ecuación en **KaTeX** (`$$...$$` dentro de `.eq`) y un párrafo `.where` que define cada variable con su unidad entre corchetes y la fuente (norma, guía o autor).
4. **Normativa colombiana aplicable** (`#normativa`): tarjetas `norm` con la norma y el artículo o sección que aplica (RETIE, NTC 2050, NTC 4552, Ley 1715 de 2014, CREG 174 de 2021, RETILAP u otras; referencias internacionales como IEEE o IEC marcadas como "Ref. internacional"). Siempre cierra con un bloque `notice` que pida **verificar la versión vigente** de las normas citadas.
5. **Calculadora** (`#calculadora`): formularios `calc` con campos, resultados y una `calc-note` que explique la fórmula usada y sus límites.

Al final: `pager` con enlaces al tema anterior y siguiente, y el `footer` con el aviso educativo. Scripts al final del `body`: `../js/main.js` y luego `../js/<tema>.js`.

### Calculadoras

- Usa las utilidades de `window.Wiki` definidas en `main.js`: `num` (acepta coma decimal), `fmt` (formato `es-CO`), `out`, `status` (`ok` | `bad` | `info`) y `bind` (recalcula al cambiar un campo).
- Valida entradas y muestra un mensaje con `status("...", "bad", ...)` si son inválidas; muestra `—` en los resultados.
- Comenta en el código la fórmula que implementa y su fuente.
- Indica la unidad en cada etiqueta y en cada resultado.

## Agregar un tema nuevo

1. Crea `temas/<tema>.html` y `js/<tema>.js` con el mismo formato de los temas existentes.
2. En `index.html`, cambia la tarjeta "próximamente" del tema por una tarjeta activa: `<div class="card soon ..." aria-disabled="true">` pasa a `<a class="card live ..." href="temas/<tema>.html">`, quita el badge "Próximamente" (o usa `<span class="badge new">Nuevo</span>`) y agrega `<span class="go">Ver tema <span>→</span></span>`.
3. Agrega el enlace al menú `nav` de `index.html` y de todas las páginas de `temas/`, y actualiza los `pager` de los temas vecinos.
4. Actualiza la tabla de contenido del `README.md`.

## Valores técnicos

- Usa **unidades del SI** (con su símbolo: Ω, Ω·m, mm², kA, s, °C, W/m²). Si una norma usa unidades del sistema inglés o calibres AWG/kcmil (por ejemplo, NTC 2050), muestra también la equivalencia en SI.
- Formato colombiano en el texto: coma decimal (`2,4 m`), espacio o punto como separador de miles.
- **Cita la norma o la fuente de cada tabla, valor y fórmula** (norma, versión, artículo/sección/tabla, o autor de la fórmula).
- **Si algún dato es dudoso, avísame** en tu respuesta y no lo publiques como seguro: dilo explícitamente (por ejemplo, numeración que cambió entre versiones del RETIE, o valores que no pudiste confirmar en una fuente oficial).
- No inventes artículos, tablas ni valores normativos.

## Flujo de trabajo

- Al terminar cada cambio: haz commit, sube la rama y **crea el pull request con un resumen en español** (qué se agregó o cambió, normas y fuentes usadas, y datos dudosos pendientes de verificar).
- Antes de crear el PR, revisa que las páginas abran sin errores en la consola y que se vean bien en celular.
