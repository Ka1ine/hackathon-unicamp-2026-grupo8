"""Execute: python -m unittest discover -s login/tests (na raiz)."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from streamlit.testing.v1 import AppTest


class ProcessosFlowTest(unittest.TestCase):
    def test_login_search_and_filters(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"))
        app.run(timeout=20)
        self.assertFalse(app.exception)
        app.text_input[0].set_value("demo@enter.com")
        app.text_input[1].set_value("123456")
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.title[0].value, "Processos")
        cards = lambda: [m.value for m in app.markdown if 'class="linha process-card-row"' in m.value]
        self.assertEqual(len(cards()), 2)
        app.text_input(key="busca_processos").set_value("jose").run()
        self.assertEqual(len(cards()), 1)
        self.assertIn("25.000,00", cards()[0])
        app.text_input(key="busca_processos").set_value("08012345620248100001").run()
        self.assertEqual(len(cards()), 1)
        self.assertIn("MARIA DAS GRAÇAS SILVA PEREIRA", cards()[0])
        app.selectbox(key="filtro_risco").select("Alto").run()
        self.assertEqual(len(cards()), 0)
        self.assertTrue(app.info)
        app.text_input(key="busca_processos").set_value("")
        app.selectbox(key="filtro_risco").select("A avaliar")
        app.selectbox(key="filtro_recomendacao").select("A avaliar").run()
        self.assertEqual(len(cards()), 2)
        app.selectbox(key="filtro_recomendacao").select("Manter defesa").run()
        self.assertEqual(len(cards()), 0)
        self.assertFalse(app.exception)
        app.button[0].click().run()
        self.assertFalse(app.session_state.get("authenticated", False) if hasattr(app.session_state, "get") else "authenticated" in app.session_state)

    def test_pdf_values_and_missing_folder(self):
        from services.processos import carregar_processos
        from tempfile import TemporaryDirectory
        processos, erros = carregar_processos()
        self.assertEqual(erros, [])
        self.assertEqual([p["valor"] for p in processos], [20000, 25000])
        self.assertEqual(processos[1]["id"], "0654321-09.2024.8.04.0001")
        self.assertEqual(processos[1]["nome"], "JOSÉ RAIMUNDO OLIVEIRA COSTA")
        with TemporaryDirectory() as directory:
            processos, erros = carregar_processos(directory)
            self.assertEqual(processos, [])
            self.assertEqual(len(erros), 2)


if __name__ == "__main__":
    unittest.main()
