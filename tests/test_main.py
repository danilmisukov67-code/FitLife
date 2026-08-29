import ast
import re


def is_call_to(node: ast.AST, func_name: str) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == func_name
    )


def extract_numbers(text: str) -> list[str]:
    return re.findall(r"\d+(?:\.\d+)?", text)


def test_1_has_input(ast_tree):
    input_calls = [node for node in ast.walk(ast_tree) if is_call_to(node, "input")]
    assert len(input_calls) >= 4, (
        "Ожидается минимум 4 вызова `input()` для имени, возраста, веса и роста."
    )


def test_2_has_int(ast_tree):
    int_calls = sum(1 for node in ast.walk(ast_tree) if is_call_to(node, "int"))
    assert int_calls >= 1, (
        "Проверьте, что для возраста используется преобразование типа `int()`. "
        "Не найдено использование функции `int()`."
    )


def test_3_has_float(ast_tree):
    float_calls = sum(1 for node in ast.walk(ast_tree) if is_call_to(node, "float"))
    assert float_calls >= 1, (
        "Проверьте, что для веса и роста используется преобразование типа `float()`. "
        "Не найдено использование функции `float()`."
    )


def test_4_has_round_or_float_formatting(ast_tree):
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
    f_string_prints = 0
    for node in ast.walk(ast_tree):
        if is_call_to(node, "print"):
            if any(isinstance(arg, ast.JoinedStr) for arg in node.args):
                f_string_prints += 1
    assert f_string_prints >= 1, (
        "Проверьте, что для вывода результата используется f-строка."
    )


def test_6_result(run_program):
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

    allowed_water_values = {"2.3", "2.26", "2.27", "2.265"}
    assert any(num in allowed_water_values for num in numbers), (
        "Неверно рассчитана норма воды. "
        "Для веса 75.5 кг должно получиться около 2.265 л."
    )