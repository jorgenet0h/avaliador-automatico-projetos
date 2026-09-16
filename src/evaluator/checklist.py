"""Regras de verificação usadas para decidir se um projeto está pronto para ser entregue.

Cada checagem é uma função pura que recebe o caminho do projeto e devolve um
CheckResult. Isso mantém as regras fáceis de testar isoladamente e fáceis de
adicionar/remover sem mexer no restante do avaliador.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

JARGON_WORDS = {
    "framework", "middleware", "endpoint", "arquitetura", "runtime",
    "orquestração", "microsserviço", "microservico", "abstração", "abstracao",
    "singleton", "polimorfismo", "instanciar", "refatorar", "refatoração",
}

SOURCE_DIR_NAMES = {"src", "lib", "app"}
TEST_DIR_NAMES = {"tests", "test"}
TEST_CONFIG_FILES = {"pytest.ini", "setup.cfg", "pyproject.toml", "tox.ini"}
CLAUDE_MD_MIN_CHARS = 150
REAL_ARTIFACT_MIN_LINES = 15


@dataclass
class CheckResult:
    id: str
    label: str
    passed: bool
    detail: str


@dataclass
class Report:
    project_path: Path
    results: list[CheckResult]

    @property
    def score(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def total(self) -> int:
        return len(self.results)

    def as_text(self) -> str:
        lines = [f"Avaliação de {self.project_path}", ""]
        for r in self.results:
            mark = "[x]" if r.passed else "[ ]"
            lines.append(f"{mark} {r.label} — {r.detail}")
        lines.append("")
        lines.append(f"Pontuação: {self.score}/{self.total}")
        return "\n".join(lines)


def _run_git(path: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(path), *args],
        capture_output=True,
        text=True,
    )


def check_git_initialized(path: Path) -> CheckResult:
    exists = (path / ".git").is_dir()
    detail = "repositório git encontrado" if exists else "nenhum repositório git em .git/"
    return CheckResult("git_initialized", "Repositório git inicializado", exists, detail)


def check_first_commit(path: Path) -> CheckResult:
    if not (path / ".git").is_dir():
        return CheckResult("first_commit", "Existe pelo menos um commit", False, "sem repositório git para checar")
    result = _run_git(path, "log", "-1", "--oneline")
    passed = result.returncode == 0 and bool(result.stdout.strip())
    detail = "commit encontrado" if passed else "nenhum commit encontrado"
    return CheckResult("first_commit", "Existe pelo menos um commit", passed, detail)


def check_readme_plain_language(path: Path) -> CheckResult:
    readme = path / "README.md"
    if not readme.is_file():
        return CheckResult("readme", "README explica o problema em linguagem simples", False, "README.md não encontrado")

    text = readme.read_text(encoding="utf-8", errors="ignore").strip()
    if not text:
        return CheckResult("readme", "README explica o problema em linguagem simples", False, "README.md está vazio")

    first_paragraph = text.split("\n\n", 1)[0]
    words = [w.strip(".,!?():`").lower() for w in first_paragraph.split()]
    jargon_hits = [w for w in words if w in JARGON_WORDS]

    if len(words) < 4:
        return CheckResult("readme", "README explica o problema em linguagem simples", False, "primeira frase é curta demais para explicar o problema")
    if jargon_hits:
        return CheckResult(
            "readme", "README explica o problema em linguagem simples", False,
            f"jargão técnico encontrado logo no início: {', '.join(sorted(set(jargon_hits)))}",
        )
    return CheckResult("readme", "README explica o problema em linguagem simples", True, "primeira frase é direta e sem jargão")


def check_code_test_separation(path: Path) -> CheckResult:
    has_source_dir = any((path / name).is_dir() for name in SOURCE_DIR_NAMES)
    has_test_dir = any((path / name).is_dir() for name in TEST_DIR_NAMES)
    passed = has_source_dir and has_test_dir
    if passed:
        detail = "código e testes ficam em pastas separadas"
    elif has_test_dir:
        detail = "há pasta de testes, mas o código não está isolado em src/lib/app"
    else:
        detail = "não há separação clara entre pasta de código e pasta de testes"
    return CheckResult("code_test_separation", "Separação clara entre código e teste", passed, detail)


def check_runnable_test_command(path: Path) -> CheckResult:
    has_config = any((path / name).is_file() for name in TEST_CONFIG_FILES)
    test_files: list[Path] = []
    for name in TEST_DIR_NAMES:
        test_dir = path / name
        if test_dir.is_dir():
            test_files.extend(test_dir.glob("test_*.py"))
            test_files.extend(test_dir.glob("*_test.py"))
    passed = has_config and bool(test_files)
    if passed:
        detail = f"{len(test_files)} arquivo(s) de teste com configuração de pytest disponível"
    elif test_files:
        detail = "há arquivos de teste, mas falta configuração de pytest (pyproject.toml/pytest.ini)"
    else:
        detail = "nenhum arquivo de teste encontrado"
    return CheckResult("runnable_tests", "Um comando de teste roda de fato", passed, detail)


def check_claude_md(path: Path) -> CheckResult:
    claude_md = path / "CLAUDE.md"
    if not claude_md.is_file():
        return CheckResult("claude_md", "CLAUDE.md escrito com intenção", False, "CLAUDE.md não encontrado")
    text = claude_md.read_text(encoding="utf-8", errors="ignore").strip()
    passed = len(text) >= CLAUDE_MD_MIN_CHARS
    detail = (
        f"{len(text)} caracteres de conteúdo" if passed
        else f"CLAUDE.md tem só {len(text)} caracteres, parece placeholder"
    )
    return CheckResult("claude_md", "CLAUDE.md escrito com intenção", passed, detail)


def check_real_artifact(path: Path) -> CheckResult:
    source_files: list[Path] = []
    for name in SOURCE_DIR_NAMES:
        source_dir = path / name
        if source_dir.is_dir():
            source_files.extend(source_dir.rglob("*.py"))

    total_lines = 0
    for file in source_files:
        for line in file.read_text(encoding="utf-8", errors="ignore").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                total_lines += 1

    passed = total_lines >= REAL_ARTIFACT_MIN_LINES
    detail = f"{total_lines} linhas de código real encontradas"
    return CheckResult("real_artifact", "Existe um artefato real, não só estrutura vazia", passed, detail)


CHECKS = (
    check_git_initialized,
    check_first_commit,
    check_readme_plain_language,
    check_code_test_separation,
    check_runnable_test_command,
    check_claude_md,
    check_real_artifact,
)


def evaluate_project(project_path: str | Path) -> Report:
    path = Path(project_path).resolve()
    results = [check(path) for check in CHECKS]
    return Report(project_path=path, results=results)
