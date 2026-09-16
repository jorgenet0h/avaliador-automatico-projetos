# CLAUDE.md

Contexto para quem (humano ou IA) for mexer neste repositório depois de mim.

## O que este projeto é

Um avaliador que confere se um projeto está pronto para ser entregue, usando
regras objetivas (existe README? existe teste? existe commit?) e, opcionalmente,
um parecer qualitativo de um modelo Claude por cima disso. As regras estão em
`src/evaluator/checklist.py`; o parecer opcional está em `src/evaluator/ai_review.py`.

## Como eu quero que isso evolua

- **Regra nova = teste novo.** Toda checagem em `checklist.py` precisa de um
  teste em `tests/test_checklist.py` cobrindo o caso que passa e o caso que
  falha. Uma checagem sem teste do caso negativo é decoração, não regra.
- **Sem dependência para o caminho principal.** O checklist objetivo
  (`evaluate_project`) não pode depender de rede nem de chave de API. Só o
  parecer de IA (`--ai`) pode chamar serviço externo, e precisa continuar
  funcionando (com aviso, não erro) se a chave não estiver configurada.
- **Heurística explícita, não configuração escondida.** Prefira listas e
  limiares visíveis no código (como `JARGON_WORDS` e `REAL_ARTIFACT_MIN_LINES`)
  a arquivos de configuração externos. É mais fácil de revisar em um PR.
- **Não adicionar checagem que eu não consiga explicar em uma frase simples.**
  Se uma regra nova precisar de parágrafo de justificativa, ela provavelmente
  está tentando resolver um problema específico demais para ser genérica.

## O que não fazer

- Não trocar o checklist objetivo por "deixa a IA decidir" — o valor deste
  projeto é justamente ter regras verificáveis por trás do parecer qualitativo.
- Não prometer 100% de acerto nos testes como critério de qualidade. O
  objetivo do comando de teste é rodar e mostrar onde as regras erram, não
  chegar a verde absoluto a qualquer custo.
- Não gerar este arquivo de novo do zero sem ler o que já está aqui.
