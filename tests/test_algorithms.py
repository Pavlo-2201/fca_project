"""
Тесты для алгоритмов построения решетки понятий.
"""

import pytest
from fca.context import FormalContext
from fca.algorithms import (
    build_concepts_set,
    build_concepts_bitset,
    compare_implementations
)
from fca.structures import BitsetContext

def test_build_concepts_simple():
    """
    Тест на простом контексте 2x2 с диагональной матрицей.
    
    Контекст:
        obj1: attr1
        obj2: attr2
    
    Ожидаемые понятия:
        1. ({}, {attr1, attr2})                 - верхнее (все признаки)
        2. ({obj1}, {attr1})                     - понятие obj1
        3. ({obj2}, {attr2})                     - понятие obj2
        4. ({obj1, obj2}, {})                    - нижнее (все объекты)
    """
    context = FormalContext(
        objects=["obj1", "obj2"],
        attributes=["attr1", "attr2"],
        matrix=[
            [1, 0],
            [0, 1]
        ]
    )
    
    concepts = build_concepts_set(context)
    
    # Должно быть 4 понятия
    assert len(concepts) == 4
    
    # Преобразуем в множество для удобства сравнения
    concepts_set = {(frozenset(e), frozenset(i)) for e, i in concepts}
    
    # Проверяем наличие всех ожидаемых понятий
    expected = {
        (frozenset(), frozenset({"attr1", "attr2"})),
        (frozenset({"obj1"}), frozenset({"attr1"})),
        (frozenset({"obj2"}), frozenset({"attr2"})),
        (frozenset({"obj1", "obj2"}), frozenset())
    }
    
    assert concepts_set == expected


def test_build_concepts_all_ones():
    """
    Контекст, где все объекты обладают всеми признаками.
    
    Матрица 2x2 со всеми единицами.
    
    Ожидаемые понятия:
        1. ({}, {attr1, attr2})  - верхнее
        2. ({obj1, obj2}, {attr1, attr2}) - все объекты и все признаки
    """
    context = FormalContext(
        objects=["obj1", "obj2"],
        attributes=["attr1", "attr2"],
        matrix=[
            [1, 1],
            [1, 1]
        ]
    )
    
    concepts = build_concepts_set(context)
    
    assert len(concepts) == 2
    
    concepts_set = {(frozenset(e), frozenset(i)) for e, i in concepts}
    
    expected = {
        (frozenset(), frozenset({"attr1", "attr2"})),
        (frozenset({"obj1", "obj2"}), frozenset({"attr1", "attr2"}))
    }
    
    assert concepts_set == expected


def test_build_concepts_with_common_attributes():
    """
    Контекст с общими признаками.
    
    Ожидается 8 понятий.
    """
    context = FormalContext(
        objects=["obj1", "obj2", "obj3"],
        attributes=["attr1", "attr2", "attr3"],
        matrix=[
            [1, 1, 0],
            [1, 0, 1],
            [0, 1, 1]
        ]
    )
    
    concepts = build_concepts_set(context)
    
    # Для этого контекста должно быть 8 понятий
    assert len(concepts) == 8
    
    # Проверяем наличие всех понятий
    concepts_set = {(frozenset(e), frozenset(i)) for e, i in concepts}
    
    expected = {
        # Верхнее
        (frozenset(), frozenset({"attr1", "attr2", "attr3"})),
        # Нижнее
        (frozenset({"obj1", "obj2", "obj3"}), frozenset()),
        # По два объекта
        (frozenset({"obj1", "obj2"}), frozenset({"attr1"})),
        (frozenset({"obj1", "obj3"}), frozenset({"attr2"})),
        (frozenset({"obj2", "obj3"}), frozenset({"attr3"})),
        # По одному объекту
        (frozenset({"obj1"}), frozenset({"attr1", "attr2"})),
        (frozenset({"obj2"}), frozenset({"attr1", "attr3"})),
        (frozenset({"obj3"}), frozenset({"attr2", "attr3"})),
    }
    
    assert concepts_set == expected


def test_build_concepts_empty_context():
    """
    Пустой контекст (без объектов) должен обрабатываться корректно.
    """
    with pytest.raises(ValueError, match="Список объектов не может быть пустым"):
        FormalContext(
            objects=[],
            attributes=["attr1"],
            matrix=[]
        )


def test_build_concepts_one_object():
    """
    Контекст с одним объектом.
    
    obj1: attr1, attr2
    
    Ожидаемые понятия:
        1. ({}, {attr1, attr2})
        2. ({obj1}, {attr1, attr2})
    """
    context = FormalContext(
        objects=["obj1"],
        attributes=["attr1", "attr2"],
        matrix=[[1, 1]]
    )
    
    concepts = build_concepts_set(context)
    
    assert len(concepts) == 2
    
    concepts_set = {(frozenset(e), frozenset(i)) for e, i in concepts}
    
    expected = {
        (frozenset(), frozenset({"attr1", "attr2"})),
        (frozenset({"obj1"}), frozenset({"attr1", "attr2"}))
    }
    
    assert concepts_set == expected
    
    
def test_build_concepts_bitset_simple():
    """Тест bitset-реализации на простом контексте."""
    context = FormalContext(
        objects=["obj1", "obj2"],
        attributes=["attr1", "attr2"],
        matrix=[
            [1, 0],
            [0, 1]
        ]
    )
    
    concepts = build_concepts_bitset(context)
    
    # Должно быть 4 понятия
    assert len(concepts) == 4
    
    # Проверяем с помощью structures
    from fca.structures import BitsetContext
    bitset_ctx = BitsetContext(context)
    
    readable = [bitset_ctx.concept_to_readable(e, i) for e, i in concepts]
    readable_set = {(frozenset(e), frozenset(i)) for e, i in readable}
    
    expected = {
        (frozenset(), frozenset({"attr1", "attr2"})),
        (frozenset({"obj1"}), frozenset({"attr1"})),
        (frozenset({"obj2"}), frozenset({"attr2"})),
        (frozenset({"obj1", "obj2"}), frozenset())
    }
    
    assert readable_set == expected


def test_build_concepts_bitset_all_ones():
    """Тест bitset-реализации на контексте со всеми единицами."""
    context = FormalContext(
        objects=["obj1", "obj2"],
        attributes=["attr1", "attr2"],
        matrix=[
            [1, 1],
            [1, 1]
        ]
    )
    
    concepts = build_concepts_bitset(context)
    assert len(concepts) == 2


def test_build_concepts_bitset_one_object():
    """Тест bitset-реализации на контексте с одним объектом."""
    context = FormalContext(
        objects=["obj1"],
        attributes=["attr1", "attr2"],
        matrix=[[1, 1]]
    )
    
    concepts = build_concepts_bitset(context)
    assert len(concepts) == 2


def test_compare_implementations():
    """Тест сравнения двух реализаций."""
    context = FormalContext(
        objects=["obj1", "obj2", "obj3"],
        attributes=["attr1", "attr2", "attr3"],
        matrix=[
            [1, 1, 0],
            [1, 0, 1],
            [0, 1, 1]
        ]
    )
    
    result = compare_implementations(context)
    
    # Количество понятий должно совпадать
    assert result["set_count"] == result["bitset_count"]
    assert result["set_count"] == 8
    
    # Результаты должны совпадать
    assert result["results_match"] is True
    
    # Bitset должен быть быстрее (или хотя бы не намного медленнее)
    assert result["speedup"] >= 0.5  # не более чем в 2 раза медленнее
    
    print(f"\nСравнение производительности:")
    print(f"  Set-реализация:    {result['set_time_ms']:.3f} мс")
    print(f"  Bitset-реализация: {result['bitset_time_ms']:.3f} мс")
    print(f"  Ускорение:          {result['speedup']:.2f}x")