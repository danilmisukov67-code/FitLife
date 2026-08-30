import subprocess
import sys
from pathlib import Path

import pytest


BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPT_PATH = BASE_DIR / "fit_life.py"


@pytest.fixture(scope="session")
def file_path():
    return SCRIPT_PATH


@pytest.fixture(scope="session")
def source_code(file_path):
    assert file_path.exists(), (
        "Не найден файл `fit_life.py`.\n"
        "Проверьте, что основной файл проекта называется `fit_life.py` "
        "и находится в корне проекта."
    )
    code = file_path.read_text(encoding="utf-8")
    assert code.strip(), "Файл `fit_life.py` пустой"
    return code


@pytest.fixture(scope="session")
def ast_tree(source_code):
    import ast
    try:
        return ast.parse(source_code)
    except SyntaxError as e:
        pytest.fail(f"Ошибка синтаксиса в fit_life.py: {e}")


@pytest.fixture
def run_program(file_path):
    def _run(user_input=""):
        if user_input is None:
            user_input = ""
        
        try:
            result = subprocess.run(
                [sys.executable, str(file_path)],
                input=user_input,
                text=True,
                capture_output=True,
                encoding="utf-8",
                timeout=5,  # Увеличен таймаут для надёжности
                cwd=str(file_path.parent),  # Установка рабочей директории
                check=False,  # Не вызывать исключение при ненулевом коде возврата
            )
        except subprocess.TimeoutExpired:
            pytest.fail("Программа превысила лимит времени выполнения (5 секунд)")
        except FileNotFoundError:
            pytest.fail(f"Не удалось запустить {file_path}. Проверьте права доступа.")
        except Exception as e:
            pytest.fail(f"Ошибка при запуске программы: {e}")
        
        assert result.returncode == 0, (
            "Программа завершилась с ошибкой.\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )
        return result.stdout

    return _run