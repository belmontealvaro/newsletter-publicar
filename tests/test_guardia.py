"""Pruebas del portero. Uso: python3 -m unittest discover -s tests -v"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import guardia  # noqa: E402


class Portero(unittest.TestCase):
    def ok(self, ruta, modo="100644", estado="A", peso=1000):
        return guardia.revisar([(modo, estado, ruta, peso)]) == []

    def test_contenido_de_las_tareas(self):
        for ruta in ("Web/noticias/2026/11/android-sms-muerte-bloqueo-movil/articulo.json",
                     "Web/noticias/2026/11/android-sms-muerte-bloqueo-movil/es.webp",
                     "Web/noticias/2026/11/android-sms-muerte-bloqueo-movil/fondo.jpg",
                     "Redes/textos/2026/11/2026-11-09.md", "Redes/candidatas/2026/11/2026-11-06.md",
                     "Resumenes/resumen-diario/datos/2026/2026-11-09.json", "Resumenes/resumen-diario/README.md",
                     "Resumenes/newsletter-semanal/datos/2026-11-09.json",
                     "Resumenes/newsletter-semanal/email/2026-11-09-en.html",
                     "Resumenes/newsletter-semanal/2026-11-09.md", "Resumenes/config/recomendaciones.md",
                     "Info/informes/2026-11-09.md"):
            self.assertTrue(self.ok(ruta), ruta)

    def test_codigo_prompts_y_configuracion_se_retienen(self):
        for ruta in ("Web/scripts/construir.py", "Web/js/app.js", "Web/js/marca.js", "Web/index.html",
                     "Web/PROMPT_NOTICIAS.md", "Resumenes/resumen-diario/PROMPT_RUTINA.md",
                     "Resumenes/config/secciones.md", "Resumenes/scripts/validar.py",
                     ".github/workflows/comprobar.yml", ".claude/skills/corregir/SKILL.md", "wrangler.jsonc",
                     "README.md", "tests/test_scripts.py", "Info/Plan/plan-maestro.md",
                     "Web/noticias/2026/11/un-articulo-cualquiera/index.html",
                     "Web/noticias/2026/11/un-articulo-cualquiera/articulo.json.py",
                     "Web/noticias/2026/11/../../scripts/construir.py",
                     "Web/noticias/2026/11/Un-Articulo/articulo.json",
                     "Redes/textos/2026/11/2026-11-09.md\nwrangler.jsonc"):
            self.assertFalse(self.ok(ruta), ruta)

    def test_enlaces_borrados_y_archivos_enormes_se_retienen(self):
        ruta = "Web/noticias/2026/11/android-sms-muerte-bloqueo-movil/es.webp"
        self.assertFalse(self.ok(ruta, modo="120000"))   # enlace simbólico
        self.assertFalse(self.ok(ruta, modo="100755"))
        self.assertFalse(self.ok(ruta, estado="D"))
        self.assertFalse(self.ok(ruta, peso=guardia.MAX_BYTES + 1))
        self.assertTrue(self.ok(ruta, estado="M"))


if __name__ == "__main__":
    unittest.main()
