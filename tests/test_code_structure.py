def test_1_fit_life_exists(file_path):
    assert file_path.exists(), (
        "Не найден файл `fit_life.py`.\n"
        "Проверьте, что основной файл проекта называется `fit_life.py` "
        "и находится в корне проекта."
    )


def test_2_syntax_errors(source_code):
    try:
        compile(source_code, "fit_life.py", "exec")
    except SyntaxError as error:
        raise AssertionError(
            "В коде обнаружена синтаксическая ошибка.\n"
            f"{error.__class__.__name__}: {error}"
        )