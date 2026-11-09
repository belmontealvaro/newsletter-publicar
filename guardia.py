#!/usr/bin/env python3
"""El portero de la publicación: decide si lo que ha entrado en main de «newsletter» se puede publicar solo.

Uso (lo llama .github/workflows/publicar.yml desde la copia descargada de «newsletter»):
    python3 guardia.py BASE HEAD

BASE es el último commit que se publicó y HEAD el que se quiere publicar. Sale con 0 si entre los dos
solo hay CONTENIDO de las tareas automáticas (artículos, textos de redes, resúmenes, informes) y con 1
si hay cualquier otra cosa: código, prompts, configuración, la plantilla…

Por qué existe: las tareas diarias leen páginas de internet y suben su trabajo a main sin que nadie lo
revise. Si una de esas páginas consiguiera engañar a la IA (una «inyección de instrucciones»), lo peor
que puede pasar con este portero es que se publique un artículo malo, nunca que cambie el código que
construye la web, los prompts de las tareas o lo que se ejecuta con las claves de Cloudflare. Todo lo que
no es contenido se queda sin publicar hasta que una persona lo aprueba con «Run workflow».

Este archivo y el flujo viven en un repositorio aparte a propósito: las tareas solo pueden tocar los
repositorios que tienen conectados, y este no lo está. Solo biblioteca estándar.
"""
import re
import subprocess
import sys

FECHA = r"\d{4}-\d{2}-\d{2}"
# Lo único que las tareas automáticas pueden añadir o cambiar. Si una tarea nueva escribe en otro sitio,
# añade aquí su ruta.
PERMITIDO = [re.compile(p) for p in (
    # Noticias del día: una carpeta por artículo, con estos archivos y ninguno más
    r"Web/noticias/\d{4}/\d{2}/[a-z0-9]+(?:-[a-z0-9]+)*/(?:articulo\.json|imagen\.json|fondo\.jpg|(?:es|en)(?:-m)?\.webp)",
    rf"Redes/(?:textos|candidatas)/\d{{4}}/\d{{2}}/{FECHA}\.md",
    # Amanecer (resumen diario)
    rf"Resumenes/resumen-diario/datos/\d{{4}}/{FECHA}\.json",
    r"Resumenes/resumen-diario/README\.md",
    # Resumen semanal
    rf"Resumenes/newsletter-semanal/datos/{FECHA}\.json",
    rf"Resumenes/newsletter-semanal/email/{FECHA}-(?:es|en)\.html",
    rf"Resumenes/newsletter-semanal/(?:{FECHA}|README)\.md",
    r"Resumenes/config/recomendaciones\.md",
    rf"Info/informes/{FECHA}\.md",
)]
ARCHIVO_NORMAL = "100644"       # ni enlaces simbólicos (120000), ni submódulos (160000), ni ejecutables (100755)
MAX_BYTES = 3 * 1024 * 1024     # ningún archivo de contenido pesa más (las fotos rondan los 300 kB)


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True).stdout


def permitido(ruta):
    return any(p.fullmatch(ruta) for p in PERMITIDO)


def revisar(cambios):
    """cambios: [(modo_nuevo, estado, ruta, bytes)]. Devuelve la lista de motivos para no publicar solo."""
    motivos = []
    for modo, estado, ruta, peso in cambios:
        if not permitido(ruta):
            motivos.append(f"{ruta}: no es contenido de las tareas automáticas")
        elif estado == "D":
            motivos.append(f"{ruta}: se borra (lo publicado no se borra solo)")
        elif estado not in ("A", "M"):
            motivos.append(f"{ruta}: cambio de tipo «{estado}»")
        elif modo != ARCHIVO_NORMAL:
            motivos.append(f"{ruta}: no es un archivo normal (modo {modo})")
        elif peso > MAX_BYTES:
            motivos.append(f"{ruta}: pesa {peso // 1024} kB (máximo {MAX_BYTES // 1024} kB)")
    return motivos


def cambios_entre(base, head):
    # -z: rutas tal cual, separadas por NUL; --no-renames: un cambio de nombre es un borrado y un alta
    campos = git("diff", "--raw", "-z", "--no-renames", "--no-abbrev", base, head).decode("utf-8", "replace").split("\0")
    cambios = []
    for meta, ruta in zip(campos[0::2], campos[1::2]):
        _, modo, _, sha, estado = meta.lstrip(":").split(" ")
        peso = int(git("cat-file", "-s", sha)) if estado != "D" and modo != "160000" else 0
        cambios.append((modo, estado[0], ruta, peso))
    return cambios


def main(args):
    if len(args) != 2:
        sys.exit("Uso: python3 guardia.py BASE HEAD")
    base, head = args
    if subprocess.run(["git", "merge-base", "--is-ancestor", base, head]).returncode != 0:
        print(f"RETENIDO: {base[:7]} (lo último publicado) no es un antepasado de {head[:7]}: la historia de main se ha reescrito.")
        return 1
    cambios = cambios_entre(base, head)
    motivos = revisar(cambios)
    if motivos:
        print(f"RETENIDO: entre {base[:7]} y {head[:7]} hay cambios que no son contenido de las tareas:")
        for m in motivos:
            print(f"- {m}")
        return 1
    print(f"OK: {len(cambios)} archivos de contenido entre {base[:7]} y {head[:7]}; se puede publicar.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
