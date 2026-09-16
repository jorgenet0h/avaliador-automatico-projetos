# Avaliador automático de projetos

Antes de entregar um projeto, alguém precisa conferir se o básico está ali — e esse alguém geralmente é um humano cansado, olhando isso pela terceira vez no dia. Este projeto faz essa primeira conferência sozinho, apontando o que falta antes que uma pessoa precise olhar.

## O que ele checa

Dado o caminho de um projeto, o avaliador confirma, item por item:

- se existe um repositório git inicializado e com pelo menos um commit;
- se o `README.md` explica o problema numa frase simples, sem jargão técnico logo de cara;
- se código e testes estão em pastas separadas;
- se existe um comando de teste que realmente roda;
- se existe um `CLAUDE.md` com conteúdo de verdade, não um placeholder;
- se existe um artefato real do projeto, e não só pastas vazias.

Essas são as mesmas exigências que este próprio repositório teve que cumprir — por isso ele consegue se avaliar.

## Como usar

```bash
pip install -r requirements.txt

# Linux/macOS
export PYTHONPATH=src

# Windows (PowerShell)
$env:PYTHONPATH = "src"

# avalia este próprio projeto
python -m evaluator .

# avalia outro projeto
python -m evaluator /caminho/para/outro/projeto

# opcional: pede também um parecer curto de um modelo Claude
# (requer a variável de ambiente ANTHROPIC_API_KEY)
python -m evaluator . --ai
```

O comando precisa rodar a partir da raiz do repositório, com `src/` no `PYTHONPATH`.

## Como rodar os testes

```bash
pytest
```

Os testes cobrem casos que passam e casos que devem falhar de propósito (README com jargão, pasta de testes ausente etc.) — o objetivo é confiar nas regras, não só ver tudo verde.

## Estrutura

```
src/evaluator/   código do avaliador
tests/           testes das regras de checagem
```
