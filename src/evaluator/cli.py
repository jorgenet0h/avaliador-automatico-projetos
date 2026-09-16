"""Ponto de entrada de linha de comando: `python -m evaluator <caminho> [--ai]`."""

from __future__ import annotations

import argparse
import sys

from .checklist import evaluate_project
from . import ai_review


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verifica se um projeto está pronto para ser entregue."
    )
    parser.add_argument("path", help="Caminho do projeto a avaliar")
    parser.add_argument(
        "--ai", action="store_true",
        help="Também pede um parecer curto a um modelo Claude (requer ANTHROPIC_API_KEY)",
    )
    args = parser.parse_args(argv)

    report = evaluate_project(args.path)
    print(report.as_text())

    if args.ai:
        print()
        if ai_review.is_available():
            print("Parecer da IA:")
            print(ai_review.review(report))
        else:
            print("(--ai pedido, mas ANTHROPIC_API_KEY não está configurada; pulando)")

    return 0 if report.score == report.total else 1


if __name__ == "__main__":
    sys.exit(main())
