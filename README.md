# newsletter-publicar

Publica la web de [`belmontealvaro/newsletter`](https://github.com/belmontealvaro/newsletter) en Cloudflare. Es el
único sitio que tiene la llave para publicar, y vive aparte a propósito.

**No conectes este repositorio a ninguna tarea programada ni a una conversación de Claude que lea páginas de
internet.** Toda su utilidad está en que las tareas automáticas no pueden tocarlo.

## Por qué existe

Las tareas diarias de la newsletter leen páginas de internet y suben artículos a `main` sin que nadie los revise.
Si una página consiguiera engañar a la IA, podría intentar cambiar el código de la web o los prompts. Las tareas
solo pueden tocar los repositorios que tienen conectados, así que el portero y los secretos están aquí, fuera de
su alcance.

## Cómo funciona

Cada 10 minutos por la mañana, y cada hora el resto del día, el flujo `Publicar la web`:

1. Descarga `main` de `newsletter` (solo lectura) y lee en `ultimo-publicado` cuál fue el último commit publicado.
2. Si no hay nada nuevo, termina.
3. Pasa el portero (`guardia.py`): compara ese commit con el nuevo y mira archivo por archivo.
   - **Solo contenido** (carpetas de artículos, `Redes/`, resúmenes, informes; archivos normales, sin borrados):
     pasa las pruebas y los validadores, construye la web, la publica y apunta el commit en `ultimo-publicado`.
   - **Cualquier otra cosa** (código, prompts, configuración): no publica y abre aquí una incidencia
     «Publicación retenida» con la lista de archivos.

## Aprobar un cambio de código

Cuando hayas revisado lo retenido: **Actions > Publicar la web > Run workflow**, marca la casilla «He revisado los
cambios…» y pulsa el botón. Si no reconoces el cambio, no lo apruebes: revierte el commit en `newsletter`.

«Run workflow» sin marcar la casilla sirve para publicar ya, sin esperar al siguiente turno, pasando el portero.

## Puesta en marcha (una vez)

En **Settings > Secrets and variables > Actions > New repository secret** de este repositorio:

| Secreto | De dónde sale |
| --- | --- |
| `NEWSLETTER_TOKEN` | GitHub > Settings > Developer settings > Fine-grained tokens > Generate new token. Repository access: solo `newsletter`. Permissions: Contents, Read-only. Caducidad: la más larga que deje (apúntate renovarlo) |
| `CLOUDFLARE_API_TOKEN` | Cloudflare > My Profile > API Tokens > Create Token > plantilla «Edit Cloudflare Workers» |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare > Workers & Pages, columna derecha |

Después:

1. En Cloudflare > Worker «newsletter» > Settings > Build, desconecta el repositorio. Hasta entonces Cloudflare
   publica cada push por su cuenta y el portero no protege nada.
2. Pulsa «Run workflow» con la casilla marcada: es la primera publicación aprobada.

## Qué considera contenido

La lista está en `guardia.py` (`PERMITIDO`). Si una tarea nueva escribe en otra carpeta, añádela ahí. Pruebas:
`python3 -m unittest discover -s tests`.
