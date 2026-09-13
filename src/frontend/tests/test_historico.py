"""Testes da leitura da base consolidada do histórico."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.historico import carregar_historico


class HistoricoServiceTest(unittest.TestCase):
    def test_carrega_resultados_e_cobertura_de_subsidios(self):
        dados, erros = carregar_historico()

        self.assertEqual(erros, [])
        self.assertEqual(len(dados), 60000)
        self.assertTrue(
            {
                "processo",
                "resultado_macro",
                "valor_causa",
                "valor_condenacao",
                "subsidios_disponiveis",
            }.issubset(dados.columns)
        )
        self.assertTrue(dados["subsidios_disponiveis"].between(0, 6).all())


if __name__ == "__main__":
    unittest.main()
