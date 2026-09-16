"""Parecer qualitativo opcional, gerado por um modelo de linguagem.

O checklist em checklist.py cobre as regras objetivas ("existe README?",
"existe commit?"). Esta parte cobre o que regra nenhuma capta bem: se o
README realmente explica o problema para um humano, ou se o CLAUDE.md diz
algo útil. Sem chave de API configurada, o avaliador continua funcionando
normalmente — só pula esta parte.
"""

from __future__ import annotations

import os
from pathlib import Path

from .checklist import Report

PROMPT_TEMPLATE = """Você está avaliando se um projeto de software está pronto para ser entregue.
Leia o relatório de checagens automáticas abaixo e o conteúdo do README.
Em até 3 frases, em português simples, diga o que mais precisa de atenção
antes da entrega. Não repita o que já está no relatório, dê um julgamento.

Relatório automático:
{report}

Conteúdo do README:
{readme}
"""


def is_available() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def review(report: Report) -> str:
    """Pede um parecer curto a um modelo Claude. Levanta RuntimeError se
    a chave de API não estiver configurada ou a chamada falhar."""
    if not is_available():
        raise RuntimeError("ANTHROPIC_API_KEY não configurada; parecer de IA indisponível")

    try:
        import anthropic
    except ImportError as exc:
        raise RuntimeError("pacote 'anthropic' não instalado (veja requirements.txt)") from exc

    readme_path = Path(report.project_path) / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8", errors="ignore") if readme_path.is_file() else "(sem README)"

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": PROMPT_TEMPLATE.format(report=report.as_text(), readme=readme_text),
        }],
    )
    return message.content[0].text.strip()
