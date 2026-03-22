"""
Тесты для CLI интерфейса.
"""

import pytest
from unittest.mock import patch, MagicMock
from fca.cli import main, run_cli


def test_cli_help_command(capsys):
    """Тест команды help."""
    with patch('builtins.input', side_effect=['help', 'exit']):
        run_cli()
    
    captured = capsys.readouterr()
    assert "СПРАВКА ПО КОМАНДАМ" in captured.out
    assert "load_context" in captured.out
    assert "build_set" in captured.out
    assert "build_bitset" in captured.out
    assert "compare" in captured.out
    assert "export" in captured.out
    assert "list" in captured.out
    assert "show" in captured.out
    assert "info" in captured.out
    assert "exit" in captured.out


def test_cli_exit_command(capsys):
    """Тест выхода из программы."""
    with patch('builtins.input', side_effect=['exit']):
        run_cli()
    
    captured = capsys.readouterr()
    assert "До свидания" in captured.out


def test_cli_unknown_command(capsys):
    """Тест неизвестной команды."""
    with patch('builtins.input', side_effect=['unknown123', 'exit']):
        run_cli()
    
    captured = capsys.readouterr()
    assert "Неизвестная команда: unknown123" in captured.out


@patch('fca.cli.load_from_json')
@patch('os.path.exists', return_value=True)
def test_cli_load_context(mock_exists, mock_load, capsys):
    """Тест загрузки контекста."""
    from fca.context import FormalContext
    
    # Создаем мок-контекст
    mock_context = MagicMock(spec=FormalContext)
    mock_context.object_count = 3
    mock_context.attribute_count = 4
    mock_load.return_value = mock_context
    
    with patch('builtins.input', side_effect=['load_context test.json', 'exit']):
        run_cli()
    
    mock_load.assert_called_once_with('test.json')
    captured = capsys.readouterr()
    assert "Контекст загружен: 3 объектов, 4 признаков" in captured.out


@patch('fca.cli.build_concepts_set')
def test_cli_build_set(mock_build, capsys):
    """Тест построения понятий set-реализацией."""
    # Мокаем возвращаемое значение
    mock_build.return_value = [
        ({"obj1"}, {"attr1"}),
        ({"obj2"}, {"attr2"})
    ]
    
    # Сначала загружаем контекст, потом строим понятия
    with patch('fca.cli.current_context', MagicMock()):
        with patch('builtins.input', side_effect=['build_set', 'exit']):
            run_cli()
    
    captured = capsys.readouterr()
    assert "Построение понятий (set-реализация)" in captured.out


def test_cli_build_without_context(capsys):
    """Тест построения понятий без загруженного контекста."""
    with patch('fca.cli.current_context', None):
        with patch('builtins.input', side_effect=['build_set', 'exit']):
            run_cli()
    
    captured = capsys.readouterr()
    assert "Сначала загрузите контекст" in captured.out


def test_cli_list_without_concepts(capsys):
    """Тест list без построенных понятий."""
    with patch('fca.cli.last_concepts', None):
        with patch('builtins.input', side_effect=['list', 'exit']):
            run_cli()
    
    captured = capsys.readouterr()
    assert "Сначала выполните построение понятий" in captured.out


def test_cli_export_without_results(capsys):
    """Тест export без результатов."""
    with patch('fca.cli.last_concepts', None):
        with patch('builtins.input', side_effect=['export', 'exit']):
            run_cli()
    
    captured = capsys.readouterr()
    assert "Нет результатов для экспорта" in captured.out