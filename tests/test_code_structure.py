def test_1_fit_life_exists(file_path):
    """Проверяет наличие файла fit_life.py."""
    assert file_path.exists(), (
        "Не найден файл `fit_life.py`.\n"
        "Проверьте, что основной файл проекта называется `fit_life.py` "
        "и находится в корне проекта."
    )
    assert file_path.is_file(), (
        "`fit_life.py` существует, но не является файлом.\n"
        "Проверьте, что это обычный файл, а не директория."
    )


def test_2_syntax_errors(source_code):
    """Проверяет отсутствие синтаксических ошибок в коде."""
    # Проверка на пустой файл
    assert source_code.strip(), (
        "Файл `fit_life.py` пустой.\n"
        "Добавьте код программы в файл."
    )
    
    try:
        compile(source_code, "fit_life.py", "exec")
    except SyntaxError as error:
        # Формируем понятное сообщение об ошибке
        error_message = (
            "В коде обнаружена синтаксическая ошибка.\n"
            f"Тип ошибки: {error.__class__.__name__}\n"
            f"Сообщение: {error.msg}\n"
        )
        
        # Добавляем информацию о местоположении ошибки, если она есть
        if error.lineno is not None:
            error_message += f"Строка: {error.lineno}"
            if error.offset is not None:
                error_message += f", позиция: {error.offset}"
            error_message += "\n"
            
            # Показываем строку с ошибкой
            lines = source_code.splitlines()
            if error.lineno <= len(lines):
                error_line = lines[error.lineno - 1]
                error_message += f"Строка с ошибкой: {error_line}\n"
                
                # Добавляем указатель на место ошибки
                if error.offset is not None:
                    pointer = " " * (error.offset - 1) + "^"
                    error_message += f"{" " * 14}{pointer}\n"
        
        # Добавляем текст ошибки, если он есть
        if error.text:
            error_message += f"Текст ошибки: {error.text}"
        
        raise AssertionError(error_message)
    except Exception as error:
        # Обработка других возможных ошибок компиляции
        raise AssertionError(
            "Ошибка при проверке синтаксиса кода.\n"
            f"{error.__class__.__name__}: {error}"
        )