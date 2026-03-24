"""
Фаззинг-тестирование модулей FCA с помощью Hypothesis.

Hypothesis — фреймворк для property-based (фаззинг) тестирования на Python.
Автоматически генерирует входные данные и ищет нарушения инвариантов.
"""

import sys
import os
import time
import random

# Добавляем корневую папку проекта в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from fca.context import FormalContext
from fca.algorithms import build_concepts_set, build_concepts_bitset


# ============================================================
# Стратегии для генерации случайных контекстов
# ============================================================

def generate_random_context(n_objects, n_attributes, density=0.5, seed=42):
    """Генерирует случайный формальный контекст."""
    rng = random.Random(seed)
    
    objects = [f"o{i}" for i in range(n_objects)]
    attributes = [f"a{i}" for i in range(n_attributes)]
    
    if n_objects == 0 or n_attributes == 0:
        matrix = []
    else:
        matrix = [
            [1 if rng.random() < density else 0 for _ in range(n_attributes)]
            for _ in range(n_objects)
        ]
    
    return FormalContext(objects, attributes, matrix)


# Стратегия для Hypothesis
@st.composite
def context_strategy(draw):
    """Стратегия генерации случайных контекстов."""
    n_objects = draw(st.integers(min_value=1, max_value=8))
    n_attributes = draw(st.integers(min_value=1, max_value=8))
    density = draw(st.floats(min_value=0.0, max_value=1.0))
    
    rng = random.Random(42)
    objects = [f"o{i}" for i in range(n_objects)]
    attributes = [f"a{i}" for i in range(n_attributes)]
    
    matrix = [
        [1 if rng.random() < density else 0 for _ in range(n_attributes)]
        for _ in range(n_objects)
    ]
    
    return FormalContext(objects, attributes, matrix)


# ============================================================
# Фаззинг-тесты для build_concepts_set
# ============================================================

@given(context=context_strategy())
@settings(max_examples=1000, suppress_health_check=[HealthCheck.too_slow])
def test_fuzz_build_concepts_set_no_crash(context):
    """
    Фаззинг build_concepts_set: функция не должна падать на случайных контекстах.
    """
    try:
        concepts = build_concepts_set(context)
        assert isinstance(concepts, list)
        for extent, intent in concepts:
            assert isinstance(extent, set)
            assert isinstance(intent, set)
    except Exception as e:
        # Если ошибка произошла, выводим контекст для воспроизведения
        print(f"\nОшибка при контексте: {context.objects}x{context.attributes}")
        print(f"Матрица: {context.matrix}")
        raise e


@given(context=context_strategy())
@settings(max_examples=1000, suppress_health_check=[HealthCheck.too_slow])
def test_fuzz_build_concepts_set_closure_property(context):
    """
    Фаззинг: проверка свойства замыкания для всех понятий.
    Для каждого понятия (A, B): closure(A) == B.
    """
    concepts = build_concepts_set(context)
    
    for extent, intent in concepts:
        # Вычисляем замыкание объема
        computed_intent = context.closure(extent)
        # Должно совпадать с содержанием
        assert computed_intent == intent, \
            f"closure({extent}) = {computed_intent}, ожидалось {intent}"


# ============================================================
# Фаззинг-тесты для build_concepts_bitset
# ============================================================

@given(context=context_strategy())
@settings(max_examples=1000, suppress_health_check=[HealthCheck.too_slow])
def test_fuzz_build_concepts_bitset_no_crash(context):
    """
    Фаззинг build_concepts_bitset: функция не должна падать на случайных контекстах.
    """
    try:
        concepts = build_concepts_bitset(context)
        assert isinstance(concepts, list)
        for extent_mask, intent_mask in concepts:
            assert isinstance(extent_mask, int)
            assert isinstance(intent_mask, int)
    except Exception as e:
        print(f"\nОшибка при контексте: {context.objects}x{context.attributes}")
        print(f"Матрица: {context.matrix}")
        raise e


# ============================================================
# Фаззинг-тесты для сравнения реализаций
# ============================================================

@given(context=context_strategy())
@settings(max_examples=500, suppress_health_check=[HealthCheck.too_slow])
def test_fuzz_set_and_bitset_agree(context):
    """
    Фаззинг: Set и BitSet реализации должны давать одинаковые результаты.
    """
    set_concepts = build_concepts_set(context)
    bitset_concepts = build_concepts_bitset(context)
    
    # Преобразуем bitset-понятия в читаемый формат
    from fca.structures import BitsetContext
    bitset_ctx = BitsetContext(context)
    bitset_readable = [
        bitset_ctx.concept_to_readable(e_mask, i_mask)
        for e_mask, i_mask in bitset_concepts
    ]
    
    set_set = {(frozenset(e), frozenset(i)) for e, i in set_concepts}
    bitset_set = {(frozenset(e), frozenset(i)) for e, i in bitset_readable}
    
    assert set_set == bitset_set, "Результаты Set и BitSet различаются"


# ============================================================
# Фаззинг-тесты для closure (с ошибкой)
# ============================================================

@given(
    obj_indices=st.sets(st.integers(min_value=0, max_value=7), min_size=0, max_size=5),
    context=context_strategy()
)
@settings(max_examples=500, suppress_health_check=[HealthCheck.too_slow])
def test_fuzz_closure_empty_set(obj_indices, context):
    """
    Фаззинг closure: проверка обработки пустого множества.
    При пустом множестве должно возвращаться множество всех атрибутов.
    """
    # Преобразуем индексы в имена объектов, существующие в контексте
    objects = set()
    for idx in obj_indices:
        if idx < len(context.objects):
            objects.add(context.objects[idx])
    
    if not objects:
        # Пустое множество: должно вернуть все атрибуты
        result = context.closure(set())
        assert result == set(context.attributes), \
            f"При пустом множестве ожидалось {set(context.attributes)}, получено {result}"
    else:
        # Непустое множество: проверяем, что замыкание работает
        result = context.closure(objects)
        assert isinstance(result, set)


# ============================================================
# Основной запуск
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ФАЗЗИНГ-ТЕСТИРОВАНИЕ FCA")
    print("=" * 60)
    
    tests = [
        ("build_concepts_set: устойчивость", test_fuzz_build_concepts_set_no_crash),
        ("build_concepts_set: свойство замыкания", test_fuzz_build_concepts_set_closure_property),
        ("build_concepts_bitset: устойчивость", test_fuzz_build_concepts_bitset_no_crash),
        ("Set и BitSet: согласованность", test_fuzz_set_and_bitset_agree),
        ("closure: пустое множество", test_fuzz_closure_empty_set),
    ]
    
    results = []
    
    for name, test_fn in tests:
        print(f"\n--- {name} ---")
        start = time.time()
        try:
            test_fn()
            elapsed = time.time() - start
            print(f"✅ ПРОЙДЕН ({elapsed:.2f} с)")
            results.append((name, "ПРОЙДЕН", elapsed, None))
        except AssertionError as e:
            elapsed = time.time() - start
            msg = str(e)[:200]
            print(f"❌ ОШИБКА ({elapsed:.2f} с): {msg}")
            results.append((name, "ОШИБКА", elapsed, msg))
        except Exception as e:
            elapsed = time.time() - start
            msg = str(e)[:200]
            print(f"💥 ИСКЛЮЧЕНИЕ ({elapsed:.2f} с): {msg}")
            results.append((name, "ИСКЛЮЧЕНИЕ", elapsed, msg))
    
    print("\n" + "=" * 60)
    print("ИТОГИ ФАЗЗИНГА")
    print("=" * 60)
    for name, status, elapsed, msg in results:
        line = f" [{status}] {name} --- {elapsed:.2f} с"
        if msg:
            line += f"\n   {msg}"
        print(line)