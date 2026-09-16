"""Testes das regras de checagem. Não é preciso 100% de sucesso para o
comando de teste ser considerado válido — o que importa é que ele roda e
mostra onde o avaliador acerta e onde ele erra."""

import subprocess
from pathlib import Path

import pytest

from evaluator.checklist import evaluate_project


def make_git_repo(path: Path) -> None:
    subprocess.run(["git", "init", "-b", "main", str(path)], capture_output=True, check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.name", "Test"], check=True)


def commit_all(path: Path) -> None:
    subprocess.run(["git", "-C", str(path), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(path), "commit", "-m", "initial"], capture_output=True, check=True)


def test_empty_directory_fails_every_check(tmp_path: Path):
    report = evaluate_project(tmp_path)
    assert report.score == 0
    assert report.total == len(report.results)


def test_well_formed_project_passes_every_check(tmp_path: Path):
    make_git_repo(tmp_path)

    (tmp_path / "README.md").write_text(
        "Este projeto ajuda times a saber se um trabalho está pronto para ser entregue.\n"
    )

    (tmp_path / "CLAUDE.md").write_text(
        "Este projeto avalia se outro projeto está pronto para entrega.\n"
        "Mantenha as regras simples e testáveis. Não adicione dependências\n"
        "sem necessidade. Prefira heurísticas explícitas a lógica escondida.\n"
        "Qualquer checagem nova precisa de um teste cobrindo o caso positivo\n"
        "e o caso negativo antes de ser considerada pronta.\n"
    )

    src_dir = tmp_path / "src" / "evaluator"
    src_dir.mkdir(parents=True)
    (src_dir / "__init__.py").write_text("")
    (src_dir / "core.py").write_text(
        "\n".join(f"value_{i} = {i}" for i in range(20)) + "\n"
    )

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_core.py").write_text("def test_placeholder():\n    assert True\n")

    (tmp_path / "pyproject.toml").write_text("[tool.pytest.ini_options]\n")

    commit_all(tmp_path)

    report = evaluate_project(tmp_path)
    failed = [r.label for r in report.results if not r.passed]
    assert failed == [], f"checagens que não passaram: {failed}"
    assert report.score == report.total


def test_readme_with_jargon_fails_its_check(tmp_path: Path):
    make_git_repo(tmp_path)
    (tmp_path / "README.md").write_text(
        "Este framework implementa uma arquitetura de middleware para orquestração.\n"
    )
    commit_all(tmp_path)

    report = evaluate_project(tmp_path)
    readme_result = next(r for r in report.results if r.id == "readme")
    assert readme_result.passed is False


def test_missing_test_directory_fails_separation_check(tmp_path: Path):
    make_git_repo(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "core.py").write_text("value = 1\n")
    commit_all(tmp_path)

    report = evaluate_project(tmp_path)
    separation_result = next(r for r in report.results if r.id == "code_test_separation")
    assert separation_result.passed is False
