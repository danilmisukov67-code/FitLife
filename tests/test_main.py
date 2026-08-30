import ast
import re
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
                timeout=5,  # Увеличил таймаут для надёжности
                cwd=str(file_path.parent),  # Установка рабочей директории
            )
        except subprocess.TimeoutExpired:
            pytest.fail("Программа превысила лимит времени выполнения (5 секунд)")
        except FileNotFoundError:
            pytest.fail(f"Не удалось запустить {file_path}. Проверьте права доступа.")
        
        assert result.returncode == 0, (
            "Программа завершилась с ошибкой.\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )
        return result.stdout
    
    return _run


def is_call_to(node: ast.AST, func_name: str) -> bool:
    """Проверяет, является ли узел вызовом указанной функции."""
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == func_name
    )


def extract_numbers(text: str) -> list[str]:
    """Извлекает все числа из текста."""
    return re.findall(r"\d+(?:\.\d+)?", text)


def test_1_has_input(ast_tree):
    """Проверяет наличие минимум 4 вызовов input()."""
    input_calls = [node for node in ast.walk(ast_tree) if is_call_to(node, "input")]
    assert len(input_calls) >= 4, (
        "Ожидается минимум 4 вызова `input()` для имени, возраста, веса и роста."
    )


def test_2_has_int(ast_tree):
    """Проверяет использование int() для преобразования."""
    int_calls = sum(1 for node in ast.walk(ast_tree) if is_call_to(node, "int"))
    assert int_calls >= 1, (
        "Проверьте, что для возраста используется преобразование типа `int()`. "
        "Не найдено использование функции `int()`."
    )


def test_3_has_float(ast_tree):
    """Проверяет использование float() для преобразования."""
    float_calls = sum(1 for node in ast.walk(ast_tree) if is_call_to(node, "float"))
    assert float_calls >= 1, (
        "Проверьте, что для веса и роста используется преобразование типа `float()`. "
        "Не найдено использование функции `float()`."
    )


def test_4_has_round_or_float_formatting(ast_tree):
    """Проверяет округление результата."""
    has_round = False
    has_float_format = False
    
    for node in ast.walk(ast_tree):
        if is_call_to(node, "round"):
            has_round = True
        if isinstance(node, ast.FormattedValue) and node.format_spec:
            format_spec = ast.unparse(node.format_spec)
            if ".1f" in format_spec or ".2f" in format_spec:
                has_float_format = True
    
    assert has_round or has_float_format, (
        "Проверьте, что результат округляется до одного знака после запятой: "
        "например, с помощью `round()` или форматирования вида `:.1f`."
    )


def test_5_has_f_string_in_print(ast_tree):
    """Проверяет использование f-строк в print()."""
    f_string_prints = 0
    for node in ast.walk(ast_tree):
        if is_call_to(node, "print"):
            if any(isinstance(arg, ast.JoinedStr) for arg in node.args):
                f_string_prints += 1
    
    assert f_string_prints >= 1, (
        "Проверьте, что для вывода результата используется f-строка."
    )


def test_6_result(run_program):
    """Проверяет корректность вычислений."""
    try:
        output = run_program("Анна\n25\n75.5\n1.8\n")
    except AssertionError:
        raise AssertionError(
            "Проверьте порядок ввода данных.\n"
            "Программа должна запрашивать данные в таком порядке: "
            "имя, возраст, вес, рост."
        )
    
    assert output.strip(), (
        "Программа ничего не вывела.\n"
        "Проверьте порядок ввода данных: "
        "имя, возраст, вес, рост."
    )

    numbers = extract_numbers(output)
    age, weight, height = 25, 75.5, 1.8
    expected_bmi = str(round(weight / height ** 2, 1))

    # Проверка на неправильные комбинации
    wrong_bmi_values = {
        str(round(height / weight ** 2, 1)),
        str(round(age / height ** 2, 1)),
        str(round(weight / age ** 2, 1)),
        str(round(height / age ** 2, 1)),
        str(round(age / weight ** 2, 1)),
    }
    
    if any(num in wrong_bmi_values for num in numbers):
        raise AssertionError(
            "Проверьте порядок ввода данных. "
            "Программа должна запрашивать данные в таком порядке: "
            "имя, возраст, вес, рост."
        )
    
    assert expected_bmi in numbers, (
        "Неверно рассчитан ИМТ. "
        "Для веса 75.5 кг и роста 1.8 м должно получиться около 23.3."
    )

    # Допустимые значения для нормы воды
    allowed_water_values = {"2.3", "2.26", "2.27", "2.265"}
    assert any(num in allowed_water_values for num in numbers), (
        "Неверно рассчитана норма воды. "
        "Для веса 75.5 кг должно получиться около 2.265 л."
    )