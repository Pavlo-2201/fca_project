#!/usr/bin/env python3
"""
Нагрузочное тестирование алгоритмов построения решетки формальных понятий.
Сравнение Set и BitSet реализаций.
"""

import sys
import os
import time
import json
import random
from datetime import datetime

# Добавляем корень проекта в путь
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from fca.context import FormalContext
from fca.algorithms import build_concepts_set, build_concepts_bitset, compare_implementations


def generate_context(n_objects, n_attributes, density=0.5, seed=42):
    """
    Генерирует случайный формальный контекст.
    
    Args:
        n_objects: количество объектов
        n_attributes: количество атрибутов
        density: плотность связей (0-1)
        seed: seed для воспроизводимости
    """
    rng = random.Random(seed)
    
    objects = [f"o{i}" for i in range(n_objects)]
    attributes = [f"a{i}" for i in range(n_attributes)]
    
    matrix = [
        [1 if rng.random() < density else 0 for _ in range(n_attributes)]
        for _ in range(n_objects)
    ]
    
    return FormalContext(objects, attributes, matrix)


def run_performance_test(context, name):
    """
    Запускает тест производительности для одного контекста.
    
    Returns:
        dict с результатами
    """
    result = {
        "name": name,
        "objects": len(context.objects),
        "attributes": len(context.attributes),
        "density": None,  # будет вычислено
    }
    
    # Вычисляем плотность
    total_cells = len(context.objects) * len(context.attributes)
    ones = sum(sum(row) for row in context.matrix)
    result["density"] = ones / total_cells if total_cells > 0 else 0
    
    print(f"\n📊 Тестирование: {name}")
    print(f"   Объекты: {result['objects']}, Атрибуты: {result['attributes']}, Плотность: {result['density']:.2%}")
    
    # Set реализация
    print("   ⏱️  Set реализация...", end="", flush=True)
    start = time.time()
    set_concepts = build_concepts_set(context)
    set_time = time.time() - start
    print(f" {set_time:.4f} сек")
    
    # BitSet реализация
    print("   ⏱️  BitSet реализация...", end="", flush=True)
    start = time.time()
    bitset_concepts = build_concepts_bitset(context)
    bitset_time = time.time() - start
    print(f" {bitset_time:.4f} сек")
    
    # Сравнение
    speedup = set_time / bitset_time if bitset_time > 0 else 0
    
    result["set_time"] = set_time
    result["bitset_time"] = bitset_time
    result["set_count"] = len(set_concepts)
    result["bitset_count"] = len(bitset_concepts)
    result["speedup"] = speedup
    
    print(f"   📈 Ускорение BitSet: {speedup:.2f}x")
    
    return result


def run_test_suite(test_configs, output_file=None):
    """
    Запускает набор тестов.
    
    Args:
        test_configs: список словарей с параметрами (name, objects, attributes, density)
        output_file: путь для сохранения результатов (JSON)
    """
    results = []
    
    print("=" * 60)
    print("🚀 НАГРУЗОЧНОЕ ТЕСТИРОВАНИЕ")
    print("=" * 60)
    print(f"Дата и время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    for config in test_configs:
        context = generate_context(
            n_objects=config["objects"],
            n_attributes=config["attributes"],
            density=config.get("density", 0.5),
            seed=config.get("seed", 42)
        )
        
        result = run_performance_test(context, config["name"])
        results.append(result)
    
    # Сохраняем результаты
    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Результаты сохранены в: {output_file}")
    
    # Вывод сводки
    print("\n" + "=" * 60)
    print("📊 СВОДНАЯ ТАБЛИЦА")
    print("=" * 60)
    print(f"{'Название':<20} {'Объекты':<8} {'Атрибуты':<8} {'Set (с)':<10} {'BitSet (с)':<12} {'Ускорение':<10}")
    print("-" * 70)
    for r in results:
        print(f"{r['name']:<20} {r['objects']:<8} {r['attributes']:<8} {r['set_time']:<10.4f} {r['bitset_time']:<12.4f} {r['speedup']:<10.2f}")
    
    return results


def main():
    """Основная функция."""
    
    # Конфигурации тестов
    test_configs = [
        # Малые контексты
        {"name": "tiny_sparse", "objects": 5, "attributes": 5, "density": 0.1},
        {"name": "tiny_dense", "objects": 5, "attributes": 5, "density": 0.9},
        
        # Малые
        {"name": "small_sparse", "objects": 10, "attributes": 10, "density": 0.1},
        {"name": "small_dense", "objects": 10, "attributes": 10, "density": 0.9},
        
        # Средние
        {"name": "medium_sparse", "objects": 20, "attributes": 20, "density": 0.1},
        {"name": "medium_dense", "objects": 20, "attributes": 20, "density": 0.9},
        
        # Большие
        {"name": "large_sparse", "objects": 25, "attributes": 25, "density": 0.1},
        {"name": "large_dense", "objects": 25, "attributes": 25, "density": 0.9},
        
        
        # Максимальные (только если нужно)
        # {"name": "maximal_sparse", "objects": 100, "attributes": 100, "density": 0.1},
        # {"name": "maximal_dense", "objects": 100, "attributes": 100, "density": 0.9},
    ]
    
    # Запускаем тесты
    results = run_test_suite(
        test_configs,
        output_file="benchmark/results.json"
    )
    
    # Вычисляем среднее ускорение
    avg_speedup = sum(r["speedup"] for r in results) / len(results)
    print(f"\n📈 Среднее ускорение BitSet: {avg_speedup:.2f}x")


if __name__ == "__main__":
    main()