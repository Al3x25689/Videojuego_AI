# Procedencia de los recursos gráficos

Fecha de creación: 30 de octubre de 2026.

No se descargaron sprites de videojuegos ni imágenes de sitios de terceros.

- `sprites_original.png`: ilustración generada mediante la herramienta integrada imagegen de OpenAI a petición del usuario. Contiene interpretaciones de Gardevoir, Gengar, Pikachu y Lucario; no son sprites oficiales extraídos de juegos.
- `gardevoir_sprite.png`, `gengar_sprite.png`, `pikachu_sprite.png`, `lucario_sprite.png`: recortes de esa ilustración con transparencia y tamaño proporcional. Reducción con vecino más cercano y ampliación entera de 2x para evitar suavizado y deformación.
- `gardevoir.png`, `gengar.png`, `pikachu.png`, `lucario.png`: cartas de 148 × 172 píxeles con los sprites anteriores y un marco geométrico creado para este proyecto.
- `fondo_original.png`: paisaje generado mediante imagegen, inspirado en escenarios de RPG clásicos, sin copiar un mapa concreto.
- `fondo.png`: recorte proporcional y ajuste con vecino más cercano a 920 × 740 píxeles.
- `reverso.png`: diseño geométrico original creado para este proyecto, con un motivo de Poké Ball, sin reproducir el reverso oficial del juego de cartas.

## Derechos y límites

El usuario puede utilizar los resultados generados conforme a los términos de OpenAI aplicables a su cuenta. Esto no concede una licencia sobre personajes, nombres, marcas o diseños Pokémon. Sus derechos pertenecen a sus respectivos titulares. Este proyecto no es oficial ni está afiliado a ellos. No se ha verificado autorización para distribuir o explotar comercialmente estas ilustraciones derivadas; para ese uso se necesitan los permisos correspondientes. No se presenta ningún recurso como CC0, de dominio público o con licencia oficial Pokémon.

Referencias de consulta: https://openai.com/policies/terms-of-use/ y https://www.pokemon.com/us/legal/

## Instrucciones de generación utilizadas

Sprites (herramienta integrada, sin API externa en el juego):
“Game asset sprite sheet, four separate equally sized cells in one horizontal row, left to right GARDEVOIR, GENGAR, PIKACHU, LUCARIO. Each exact recognizable Pokemon fully visible standing, classic handheld RPG pixel art, hard pixel edges, limited palette, no antialiasing. Transparent background, no text, no lettering, no shadows outside sprites. Each sprite centered in its own quarter with generous clear gutters so the sheet can be cut into four equal quarters. Front three-quarter view, consistent scale, charming polished sprites.”

Fondo:
“Pixel art background for a classic Pokemon-inspired handheld RPG memory game. Landscape 3:2. Peaceful grassy clearing with tan path, tiny wildflowers, rounded green trees framing sides, blue pond bottom right, distant hills and soft blue sky. Top-down classic tile map aesthetic, crisp chunky pixels, limited cheerful palette. Center broad quiet grass area for UI overlay, no characters, no text, no logos, no interface.”


## Versión 3.0 · sprites de HeartGold & SoulSilver (30 de octubre de 2026)

Los apartados anteriores describen los recursos históricos de la versión 2.0. La versión 3.0 reemplaza TODOS los personajes activos por los sprites frontales normales de una sola colección de PokéAPI: `sprites/pokemon/versions/generation-iv/heartgold-soulsilver/`. No se utilizaron nuevas imágenes generadas mediante IA en esta versión. El fondo y el reverso de la versión 2.0 permanecen intactos.

Repositorio: https://github.com/PokeAPI/sprites

Revisión fijada: `1dd55c0436d2a5b6e324c0b780e1b1b416fbfb64`.

Los dieciséis PNG descargados fueron comprobados: formato PNG, 80 × 80 píxeles, transparencia y contenido no vacío. Los archivos originales se guardan sin modificar en `assets/hgss/<número>.png`. `assets/hgss/manifest.json` contiene URL por archivo, identificador nacional y hash SHA-256. `assets/hgss/LICENCE_PokeAPI.txt` conserva la licencia original.

### Personajes y distribución

| Pokémon | Número nacional | Niveles |
|---|---:|---|
| Gardevoir | 282 | Fácil, Medio, Difícil |
| Gengar | 94 | Fácil, Medio, Difícil |
| Pikachu | 25 | Fácil, Medio, Difícil |
| Lucario | 448 | Fácil, Medio, Difícil |
| Charizard | 6 | Medio, Difícil |
| Dragonite | 149 | Medio, Difícil |
| Eevee | 133 | Medio, Difícil |
| Umbreon | 197 | Medio, Difícil |
| Absol | 359 | Difícil |
| Riolu | 447 | Difícil |
| Bulbasaur | 1 | Difícil |
| Squirtle | 7 | Difícil |
| Mew | 151 | Difícil |
| Espeon | 196 | Difícil |
| Tyranitar | 248 | Difícil |
| Metagross | 376 | Difícil |

### Preparación y copias de seguridad

`assets/<nombre>_sprite.png` contiene el sprite transparente centrable: se recorta únicamente el margen vacío y se aplica el mismo aumento de 1.5× a todos los personajes con vecino más cercano, conservando sus proporciones relativas. `assets/<nombre>.png` compone la carta de 148 × 172 sobre crema uniforme `#f5edce`, con los bordes dorados anteriores. Tkinter escala las cartas con muestreo de píxeles, sin filtros de suavizado. Las cartas visibles conservan el estado visual normal y la lógica de turnos bloquea selecciones repetidas; así se evita el punteado automático de los botones deshabilitados de Tkinter.

`assets/v2_originales/` conserva copias byte a byte de todos los PNG anteriores y del PROCEDENCIA.md histórico, incluyendo los cuatro sprites y cartas reemplazados. El README y las capturas históricas no se modificaron. El juego no carga personajes desde esa copia.

### Derechos y limitaciones

El archivo LICENCE.txt del repositorio declara que el contenido de las imágenes está protegido por copyright de The Pokémon Company, aunque el repositorio se distribuya bajo CC0 1.0. No debe interpretarse CC0 como una licencia sobre los personajes, marcas o derechos de terceros. No se ha obtenido autorización oficial para su explotación comercial. El proyecto no está afiliado ni avalado por los titulares.

Fuente de la licencia: https://github.com/PokeAPI/sprites/blob/1dd55c0436d2a5b6e324c0b780e1b1b416fbfb64/LICENCE.txt

Todos los recursos de ejecución se cargan desde archivos locales. No se realizan peticiones de red ni se requieren Pillow o herramientas de generación al jugar.
