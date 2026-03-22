"""Вспомогательные функции для BDD-тестов."""

import random
import sys
import os

# Добавляем корень проекта
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


def generate_random_context(n_objects, n_attributes, density=0.5, seed=42):
    """
    Генерирует случайный формальный контекст.
    
    Args:
        n_objects: количество объектов
        n_attributes: количество атрибутов
        density: плотность связей (0-1)
        seed: seed для воспроизводимости
    
    Returns:
        FormalContext
    """
    from fca.context import FormalContext
    
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


def generate_sparse_context(n_objects, n_attributes, seed=42):
    """Генерирует разреженный контекст (density ~0.1)."""
    return generate_random_context(n_objects, n_attributes, density=0.1, seed=seed)


def generate_dense_context(n_objects, n_attributes, seed=42):
    """Генерирует плотный контекст (density ~0.9)."""
    return generate_random_context(n_objects, n_attributes, density=0.9, seed=seed)