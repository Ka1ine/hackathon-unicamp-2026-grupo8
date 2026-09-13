# Detalhes de processo

Na tela Processos, clique diretamente no cartão do caso que deseja abrir.
O cartão inteiro é interativo e também pode ser acessado pelo teclado. O login demonstrativo permanece
`demo@enter.com` / `123456`. **Voltar aos processos** retorna à listagem.

A tela tem cabeçalho extraído dos autos locais, abas Análise/Documentos/Acordo,
seleção de PDFs, prévia paginada e download dos bytes originais. Campos que
não foram encontrados aparecem como Não informado. A avaliar é o status da
análise interna, não um andamento judicial consultado. Análise e Acordo são
áreas preparadas, sem lógica jurídica ou negociação.

O chat ocupa 50% da área de trabalho no desktop e é empilhado abaixo em telas
até 720px. A conversa permanece ao mudar abas, documentos e abrir/fechar o
painel. Ao sair da página, ela é descartada. Respostas estão identificadas como
simuladas. Não há chamadas de LLM, autenticação nova ou persistência.

## Prévias locais

Os PDFs originais estão em `data/0801234-56-2024-8-10-0001` e `data/0654321-09-2024-8-04-0001`.
As imagens pré-renderizadas ficam em `.previews/<hash-do-pdf>/page-N.png`
nessas mesmas pastas (já ignoradas pelo Git). Não se altera o PDF original.
O hash impede uma imagem antiga de ser associada a um documento alterado.

Para gerar/atualizar imagens, execute na raiz:

```sh
python src/frontend/services/gerar_previas.py
```

Somente esse comando de preparação requer o executável `pdftoppm` do Poppler
no PATH. Nenhuma dependência Python foi acrescentada. Sem imagens, a tela
mostra a transcrição local da página e mantém o download original funcionando.
PDFs sem camada textual também podem ser visualizados quando renderizados;
o projeto não executa OCR nem análise jurídica desses documentos.

## Isolamento e futura integração

HTML, CSS e JavaScript estão em `assets/process-details.*`, dentro do iframe
de `st.iframe`. As abas e o chat mudam no cliente, sem
recarregar a página nem executar novamente o Streamlit. Os arquivos de estilos
existentes não foram alterados. A listagem transforma cada cartão em um link
para os detalhes; o login só ganhou o registro da página autenticada.

O adaptador `requestAssistant({message, context, messages})` em
`process-details.js` é o ponto de integração futura. O contexto carrega o ID
do processo, catálogo de TODOS os documentos e documento selecionado; a API
futura deve buscar conteúdo e evidências por esses IDs no servidor. Não coloque
chaves de LLM no navegador. Nesta etapa os PDFs não são enviados a serviços.

## Verificação

```sh
python -m unittest discover -s src/frontend/tests
```

Os testes originais cobrem login, busca com/sem acento, número sem pontuação,
filtros e saída. Os novos verificam navegação e retorno, separação entre casos,
igualdade do download com o PDF original e fallback quando não há imagem.
Validação visual adicional: seleção/paginação, download, três abas com chat
aberto, envio simulado, fechamento/reabertura e layout desktop/celular.
