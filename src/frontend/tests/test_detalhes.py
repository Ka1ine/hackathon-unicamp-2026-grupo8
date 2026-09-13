"""Regressão da navegação e integridade do download, sem serviços externos."""
import base64
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from streamlit.testing.v1 import AppTest
from services.detalhes import carregar_detalhes, ler_documento
from services.processos import carregar_processos


class DetalhesTest(unittest.TestCase):
    def test_documentos_correspondem_ao_processo_e_download_original(self):
        processos, _ = carregar_processos()
        for processo, count in zip(processos, (7, 4)):
            detalhes, erros = carregar_detalhes(processo['id'])
            self.assertEqual(erros, [])
            self.assertEqual(len(detalhes['documents']), count)
            for doc in detalhes['documents']:
                original = Path(processo['fonte']).parent / doc['filename']
                self.assertEqual(base64.b64decode(doc['base64']), original.read_bytes())
                self.assertEqual(len(doc['previews']), doc['pages'])
                self.assertTrue(all(p['image'] or p['text'] for p in doc['previews']))

    def test_linha_do_tempo_usa_apenas_eventos_extraidos_dos_autos(self):
        processos, _ = carregar_processos()
        detalhes, erros = carregar_detalhes(processos[0]['id'])
        self.assertEqual(erros, [])
        eventos = detalhes['timeline']['events']
        self.assertTrue(eventos)
        self.assertTrue(all(evento['source'] == 'file' for evento in eventos))
        self.assertEqual(detalhes['start_date'], '2024-02-05')
        self.assertEqual(detalhes['pending_action'], 'Protocolar Petição/Manifestação')
        self.assertEqual(detalhes['policy']['next_recommended_action'], 'Defesa')
        perfil = {item['label']: item['value'] for item in detalhes['author_profile']}
        self.assertEqual(perfil['Nome'], 'MARIA DAS GRAÇAS SILVA PEREIRA')
        self.assertEqual(perfil['Gênero'], 'Feminino')
        self.assertEqual(perfil['Idade'], 'Pessoa idosa')
        self.assertEqual(perfil['Localização'], 'São Luís/MA')
        self.assertEqual(perfil['Renda'], 'Exclusivamente do benefício previdenciário')
        self.assertEqual(perfil['Tipo de benefício'], 'Aposentadoria pelo RGPS (INSS)')
        self.assertEqual(perfil['Instrução'], 'Baixa escolaridade')

    def test_status_reflete_a_recomendacao_individual_do_processo(self):
        detalhes_defesa, _ = carregar_detalhes('0801234-56.2024.8.10.0001')
        detalhes_acordo, _ = carregar_detalhes('0654321-09.2024.8.04.0001')
        self.assertEqual(detalhes_defesa['status'], 'Recomendação: Defesa')
        self.assertEqual(detalhes_acordo['status'], 'Recomendação: Acordo Mandatório')

    def test_sem_previa_usa_texto_e_numero_desconhecido_nao_abre_outro_caso(self):
        processos, _ = carregar_processos()
        with tempfile.TemporaryDirectory() as directory:
            arquivo = Path(directory) / 'autos.pdf'
            arquivo.write_bytes(Path(processos[0]['fonte']).read_bytes())
            doc = ler_documento(arquivo)
            self.assertIsNone(doc['previews'][0]['image'])
            self.assertTrue(doc['previews'][0]['text'])
        detalhes, erros = carregar_detalhes('inexistente')
        self.assertIsNone(detalhes)
        self.assertTrue(erros)

    def test_cartoes_abrem_detalhes_preservando_sessao(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run(timeout=20)
        app.text_input[0].set_value('demo@enter.com')
        app.text_input[1].set_value('123456')
        app.button[0].click().run()
        self.assertFalse(app.exception)
        botoes = [b for b in app.button if b.label.startswith('Abrir detalhes do processo')]
        self.assertEqual(len(botoes), 2)
        self.assertNotIn('Abrir detalhes de um processo', [s.label for s in app.selectbox])
        botoes[1].click().run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['processo_detalhe_id'], '0654321-09.2024.8.04.0001')
        self.assertTrue(app.session_state['authenticated'])
        self.assertEqual(app.button[0].label, '← Voltar aos processos')


if __name__ == '__main__':
    unittest.main()
