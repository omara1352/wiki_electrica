# Wiki Eléctrica CO ⚡

Wiki web de ingeniería eléctrica para Colombia, en español. Sitio estático (HTML, CSS y JavaScript sin dependencias de compilación) listo para publicar en **GitHub Pages**.

## Contenido

| Tema | Calculadora |
|------|-------------|
| [Puesta a tierra](temas/puesta-a-tierra.html) | Resistividad (Wenner) y resistencia de una varilla |
| [Energía solar fotovoltaica](temas/energia-solar.html) | Número de paneles y módulos en serie por string |
| [Selección de conductores](temas/seleccion-conductores.html) | Calibre por ampacidad y caída de tensión |

Próximamente: cortocircuito y coordinación de protecciones, transitorios y coordinación de aislamiento, subestaciones, iluminación y calidad de energía.

Cada tema incluye: explicación corta, proceso paso a paso con diagramas SVG animados, fórmulas clave, normativa colombiana (RETIE, NTC 2050, NTC 4552, Ley 1715, CREG 174 de 2021) y una calculadora.

## Estructura

```
index.html                  Página principal (tarjetas de temas)
temas/                      Una página por tema
css/styles.css              Estilos (colores en las variables de :root)
js/main.js                  Menú, animaciones de scroll, paso a paso, fórmulas
js/<tema>.js                Calculadora de cada tema
assets/favicon.svg          Ícono
.nojekyll                   Indica a GitHub Pages que sirva los archivos tal cual
```

Las fórmulas se muestran con [KaTeX](https://katex.org) cargado desde CDN.

## Ver en local

Abra `index.html` en el navegador, o sirva la carpeta:

```bash
python3 -m http.server 8000
```

y visite <http://localhost:8000>.

## Publicar en GitHub Pages

1. Lleve los cambios a la rama `main` (por ejemplo, fusionando el pull request).
2. En GitHub, vaya a **Settings → Pages**.
3. En **Build and deployment → Source**, elija **Deploy from a branch**.
4. En **Branch**, seleccione `main` y la carpeta `/ (root)`. Pulse **Save**.
5. Espere uno o dos minutos. El sitio quedará en `https://<usuario>.github.io/wiki_electrica/`.

## Cómo agregar un tema nuevo

1. Copie una página de `temas/` (por ejemplo `puesta-a-tierra.html`) con el nuevo nombre.
2. Cambie textos, diagramas SVG, fórmulas y normativa. Las animaciones usan clases listas en `css/styles.css`: `draw`, `pop`, `fade`, `rise`, `grow`, `flow`, `pulse`, `blink`, `spin` (retraso con `style="--d:0.5s"`).
3. Cree `js/<nuevo-tema>.js` para la calculadora usando las utilidades de `window.Wiki` (`num`, `fmt`, `out`, `status`, `bind`).
4. En `index.html`, convierta la tarjeta “Próximamente” en un enlace: cambie `<div class="card soon">` por `<a class="card live" href="temas/nuevo-tema.html">` y quite el distintivo.
5. Agregue el enlace al menú de navegación de cada página si lo desea.

## Aviso

Contenido con fines educativos. No reemplaza el criterio de un profesional con matrícula vigente ni el texto oficial de las normas. **Verifique siempre la versión vigente** del RETIE, la NTC 2050 y la regulación de la CREG.
