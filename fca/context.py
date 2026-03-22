"""
Модуль для работы с формальным контекстом (G, M, I).
"""
from dataclasses import dataclass, field
import json
import os
from typing import List, Set, Tuple, Optional, Dict, Any


@dataclass
class FormalContext:
    """
    Формальный контекст (G, M, I).
    
    Атрибуты:
        objects: список объектов G
        attributes: список признаков M
        matrix: матрица инцидентности I
    """
    objects: List[str]
    attributes: List[str]
    matrix: List[List[int]]
    
    # Поля, которые будут вычислены после инициализации
    _obj_to_idx: Dict[str, int] = field(init=False, repr=False, default_factory=dict)
    _attr_to_idx: Dict[str, int] = field(init=False, repr=False, default_factory=dict)
    
    def __init__(self, objects: List[str], attributes: List[str], matrix: List[List[int]]):
        """Инициализация с вызовом валидации."""
        self.objects = objects
        self.attributes = attributes
        self.matrix = matrix
        
        # Вызываем валидацию
        self._validate()
        
        # Создаем отображения для быстрого доступа
        self._obj_to_idx = {obj: i for i, obj in enumerate(self.objects)}
        self._attr_to_idx = {attr: j for j, attr in enumerate(self.attributes)}
    
    def _validate(self):
        """Валидация контекста."""
        # Проверка, что объекты и атрибуты не пусты
        if not self.objects:
            raise ValueError("Список объектов не может быть пустым")
        if not self.attributes:
            raise ValueError("Список признаков не может быть пустым")
        
        # Проверка, что матрица не пуста
        if not self.matrix:
            raise ValueError("Матрица не может быть пустой")
        
        # Проверка соответствия количества объектов и строк матрицы
        if len(self.objects) != len(self.matrix):
            raise ValueError(
                f"Количество объектов ({len(self.objects)}) не совпадает "
                f"с количеством строк матрицы ({len(self.matrix)})"
            )
        
        # Проверка соответствия количества атрибутов и столбцов матрицы
        if len(self.attributes) != len(self.matrix[0]):
            raise ValueError(
                f"Количество атрибутов ({len(self.attributes)}) не совпадает "
                f"с количеством столбцов матрицы ({len(self.matrix[0])})"
            )
        
        # Проверка каждой строки
        for i, row in enumerate(self.matrix):
            if len(row) != len(self.attributes):
                raise ValueError(
                    f"Длина строки {i} ({len(row)}) "
                    f"не совпадает с количеством признаков ({len(self.attributes)})"
                )
            for val in row:
                if val not in (0, 1):
                    raise ValueError(f"Значение {val} в матрице должно быть 0 или 1")
    
    def __post_init__(self):
        """Для совместимости с dataclass."""
        self._validate()
    
    @property
    def object_count(self) -> int:
        """Количество объектов в контексте."""
        return len(self.objects)
    
    @property
    def attribute_count(self) -> int:
        """Количество признаков в контексте."""
        return len(self.attributes)
    
    def object_attributes(self, obj: str) -> Set[str]:
        """
        Возвращает множество признаков, присущих объекту.
        
        Args:
            obj: объект из контекста
            
        Returns:
            множество признаков, которыми обладает объект
            
        Raises:
            ValueError: если объект не найден в контексте
        """
        if obj not in self._obj_to_idx:
            raise ValueError(f"Объект '{obj}' не найден в контексте")
        
        idx = self._obj_to_idx[obj]
        result = set()
        for j, attr in enumerate(self.attributes):
            if self.matrix[idx][j] == 1:
                result.add(attr)
        return result
    
    def objects_with_attribute(self, attr: str) -> Set[str]:
        """
        Возвращает множество объектов, обладающих признаком.
        
        Args:
            attr: признак из контекста
            
        Returns:
            множество объектов, обладающих признаком
            
        Raises:
            ValueError: если признак не найден в контексте
        """
        if attr not in self._attr_to_idx:
            raise ValueError(f"Признак '{attr}' не найден в контексте")
        
        j = self._attr_to_idx[attr]
        result = set()
        for i, obj in enumerate(self.objects):
            if self.matrix[i][j] == 1:
                result.add(obj)
        return result
    
    def closure(self, objects: Set[str]) -> Set[str]:
        """
        Оператор замыкания: возвращает множество признаков,
        общих для всех объектов из objects.
        
        Args:
            objects: множество объектов
            
        Returns:
            множество признаков, общих для всех объектов
        """
        if not objects:
            return set(self.attributes)
        
        # Берем признаки первого объекта
        first = next(iter(objects))
        result = self.object_attributes(first)
        
        # Пересекаем с признаками остальных объектов
        for obj in objects:
            result &= self.object_attributes(obj)
            if not result:  # Раннее прерывание, если пересечение пусто
                break
        
        return result
    
    def closure_dual(self, attributes: Set[str]) -> Set[str]:
        """
        Двойственный оператор замыкания: возвращает множество объектов,
        обладающих всеми признаками из attributes.
        
        Args:
            attributes: множество признаков
            
        Returns:
            множество объектов, обладающих всеми признаками
        """
        if not attributes:
            return set(self.objects)
        
        # Берем объекты с первым признаком
        first = next(iter(attributes))
        result = self.objects_with_attribute(first)
        
        # Пересекаем с объектами, обладающими остальными признаками
        for attr in attributes:
            result &= self.objects_with_attribute(attr)
            if not result:  # Раннее прерывание, если пересечение пусто
                break
        
        return result


def load_context_from_json(filepath: str) -> FormalContext:
    """Загружает контекст из JSON-файла."""
    import json
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return FormalContext(
        objects=data['objects'],
        attributes=data['attributes'],
        matrix=data['matrix']
    )


def save_context_to_json(context: FormalContext, filepath: str) -> None:
    """Сохраняет контекст в JSON-файл."""
    import json
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({
            'objects': context.objects,
            'attributes': context.attributes,
            'matrix': context.matrix
        }, f, ensure_ascii=False, indent=2)