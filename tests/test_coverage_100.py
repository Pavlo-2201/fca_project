"""
Тесты для достижения 100% покрытия.
Добиваем редкие ветки и исключения.
"""

import pytest
import json
import os
from unittest.mock import patch, mock_open
from fca.context import FormalContext, load_from_json
from fca.algorithms import build_concepts_set, build_concepts_bitset, compare_implementations
from fca.structures import BitsetContext


def test_context_object_not_found():
    """Тест обращения к несуществующему объекту."""
    context = FormalContext(
        objects=["obj1"],
        attributes=["attr1"],
        matrix=[[1]]
    )
    
    with pytest.raises(ValueError, match="не найден"):
        context.object_attributes("non_existent")


def test_context_attribute_not_found():
    """Тест обращения к несуществующему признаку."""
    context = FormalContext(
        objects=["obj1"],
        attributes=["attr1"],
        matrix=[[1]]
    )
    
    with pytest.raises(ValueError, match="не найден"):
        context.objects_with_attribute("non_existent")


def test_load_from_json_invalid_json():
    """Тест загрузки невалидного JSON."""
    with patch("builtins.open", mock_open(read_data="invalid json")):
        with patch("os.path.exists", return_value=True):
            with pytest.raises(json.JSONDecodeError):
                load_from_json("test.json")


def test_closure_early_break():
    """Тест раннего прерывания в closure (когда пересечение становится пустым)."""
    context = FormalContext(
        objects=["obj1", "obj2"],
        attributes=["a", "b"],
        matrix=[
            [1, 0],
            [0, 1]
        ]
    )
    
    # Эти объекты не имеют общих признаков
    result = context.closure({"obj1", "obj2"})
    assert result == set()


def test_closure_dual_early_break():
    """Тест раннего прерывания в closure_dual."""
    context = FormalContext(
        objects=["obj1", "obj2"],
        attributes=["a", "b"],
        matrix=[
            [1, 0],
            [0, 1]
        ]
    )
    
    # Эти признаки не имеют общих объектов
    result = context.closure_dual({"a", "b"})
    assert result == set()


def test_bitset_closure_early_break():
    """Тест раннего прерывания в bitset closure."""
    context = FormalContext(
        objects=["obj1", "obj2"],
        attributes=["a", "b"],
        matrix=[
            [1, 0],
            [0, 1]
        ]
    )
    
    bitset_ctx = BitsetContext(context)
    
    # Объекты 0 и 1 (маска 0b11) не имеют общих признаков
    result = bitset_ctx.closure_bitset(0b11)
    assert result == 0


def test_bitset_closure_dual_early_break():
    """Тест раннего прерывания в bitset closure_dual."""
    context = FormalContext(
        objects=["obj1", "obj2"],
        attributes=["a", "b"],
        matrix=[
            [1, 0],
            [0, 1]
        ]
    )
    
    bitset_ctx = BitsetContext(context)
    
    # Признаки 0 и 1 (маска 0b11) не имеют общих объектов
    result = bitset_ctx.closure_dual_bitset(0b11)
    assert result == 0


def test_bitset_closure_single_object():
    """Тест bitset closure с одним объектом."""
    context = FormalContext(
        objects=["obj1", "obj2", "obj3"],
        attributes=["a", "b", "c"],
        matrix=[
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ]
    )
    
    bitset_ctx = BitsetContext(context)
    
    # Только объект 0
    result = bitset_ctx.closure_bitset(0b001)
    assert result == 0b001  # признак a


def test_compare_implementations_empty_context():
    """Тест сравнения на контексте, который вызовет все ветки."""
    with pytest.raises(ValueError):
        FormalContext(
            objects=[],
            attributes=[],
            matrix=[]
        )


def test_export_without_context():
    """Тест экспорта без контекста."""
    from fca.cli import export_command
    with patch('fca.cli.last_concepts', [(set(), set())]):
        with patch('fca.cli.current_context', None):
            # Должно напечатать ошибку, но не упасть
            export_command("test.json")