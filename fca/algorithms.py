"""
Модуль с реализациями алгоритма Van Der Merwe, Kourie, 2002
для построения решетки формальных понятий.
"""

from typing import List, Set, Tuple
from .context import FormalContext


def build_concepts_set(context: FormalContext) -> List[Tuple[Set[str], Set[str]]]:
    """
    Построение всех формальных понятий с явной проверкой верхнего понятия.
    """
    # Нижнее понятие (все объекты)
    all_objects = set(context.objects)
    bottom_intent = context.closure(all_objects)
    bottom_concept = (all_objects, bottom_intent)
    
    # Верхнее понятие (пустой объем)
    top_concept = (set(), set(context.attributes))
    
    # Стек для обработки
    stack = [bottom_concept]
    
    # Множество для хранения уникальных понятий
    seen = {
        (frozenset(bottom_concept[0]), frozenset(bottom_concept[1])),
        (frozenset(top_concept[0]), frozenset(top_concept[1]))
    }
    
    concepts = [bottom_concept, top_concept]
    
    while stack:
        current_extent, current_intent = stack.pop()
        
        for attr in context.attributes:
            if attr in current_intent:
                continue
            
            objects_with_attr = context.objects_with_attribute(attr)
            new_extent = current_extent & objects_with_attr
            
            if not new_extent or new_extent == current_extent:
                continue
            
            new_intent = context.closure(new_extent)
            new_concept = (new_extent, new_intent)
            
            key = (frozenset(new_extent), frozenset(new_intent))
            if key not in seen:
                concepts.append(new_concept)
                stack.append(new_concept)
                seen.add(key)
    
    return concepts

def build_concepts_bitset(context: FormalContext) -> List[Tuple[int, int]]:
    """
    Построение всех формальных понятий с использованием битовых векторов.
    Реализация алгоритма Van Der Merwe, Kourie, 2002.
    
    Args:
        context: формальный контекст
        
    Returns:
        список понятий в виде кортежей (маска_объектов, маска_признаков)
    """
    from .structures import BitsetContext
    
    bitset_ctx = BitsetContext(context)
    
    # Множество для хранения уникальных понятий
    concepts_set = set()
    
    def process(extent_mask: int, intent_mask: int):
        """Рекурсивная обработка понятия."""
        key = (extent_mask, intent_mask)
        if key in concepts_set:
            return
        
        concepts_set.add(key)
        
        # Для каждого признака, не входящего в содержание
        for j in range(bitset_ctx.n_attributes):
            if intent_mask & (1 << j):
                continue
            
            # Новый объем: текущий объем ∩ объекты с этим признаком
            new_extent = extent_mask & bitset_ctx.attribute_masks[j]
            
            if new_extent == 0:
                continue
            
            # Новое содержание: замыкание нового объема
            new_intent = bitset_ctx.closure_bitset(new_extent)
            
            # Рекурсивно обрабатываем
            process(new_extent, new_intent)
    
    # Начинаем с нижнего понятия (все объекты)
    all_objects_mask = (1 << bitset_ctx.n_objects) - 1
    bottom_intent = bitset_ctx.closure_bitset(all_objects_mask)
    process(all_objects_mask, bottom_intent)
    
    # Добавляем верхнее понятие (пустой объем)
    top_intent = (1 << bitset_ctx.n_attributes) - 1
    concepts_set.add((0, top_intent))
    
    # Преобразуем в список и сортируем
    concepts = list(concepts_set)
    def concept_sort_key(x):
        return (bin(x[0]).count('1'), x[0])

    concepts.sort(key=concept_sort_key)
    
    return concepts


def compare_implementations(context: FormalContext) -> dict:
    """
    Сравнивает две реализации алгоритма.
    
    Args:
        context: формальный контекст
        
    Returns:
        словарь с результатами сравнения
    """
    import time
    
    # Set-реализация
    start = time.time()
    set_concepts = build_concepts_set(context)
    set_time = (time.time() - start) * 1000
    
    # Bitset-реализация
    start = time.time()
    bitset_concepts = build_concepts_bitset(context)
    bitset_time = (time.time() - start) * 1000
    
    # Конвертируем bitset-понятия для сравнения
    from .structures import BitsetContext
    bitset_ctx = BitsetContext(context)
    
    bitset_concepts_readable = [
        bitset_ctx.concept_to_readable(e_mask, i_mask)
        for e_mask, i_mask in bitset_concepts
    ]
    
    # Проверка совпадения результатов
    set_set = {(frozenset(e), frozenset(i)) for e, i in set_concepts}
    bitset_set = {(frozenset(e), frozenset(i)) for e, i in bitset_concepts_readable}
    
    return {
        "set_count": len(set_concepts),
        "bitset_count": len(bitset_concepts),
        "set_time_ms": set_time,
        "bitset_time_ms": bitset_time,
        "speedup": set_time / bitset_time if bitset_time > 0 else float('inf'),
        "results_match": set_set == bitset_set
    }