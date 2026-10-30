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
