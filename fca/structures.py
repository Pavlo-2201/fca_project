"""
Модуль для работы с битовыми векторами.
Содержит обертку BitsetContext для эффективных операций над множествами.
"""

from typing import Set, List, Tuple, Optional
from .context import FormalContext


class BitsetContext:
    """
    Обертка над FormalContext, использующая битовые маски
    для эффективного хранения множеств.
    
    Каждому объекту и признаку назначается битовая позиция.
    Множество объектов/признаков представляется целым числом,
    где i-й бит означает наличие i-го элемента.
    
    Пример:
        Для 3 объектов: маска 0b101 означает {объект0, объект2}
    """
    
    def __init__(self, context: FormalContext):
        """
        Инициализация BitsetContext на основе обычного контекста.
        
        Args:
            context: исходный формальный контекст
        """
        self.context = context
        self.n_objects = len(context.objects)
        self.n_attributes = len(context.attributes)
        
        # Маппинги для быстрого доступа
        self.obj_to_idx = context._obj_to_idx
        self.attr_to_idx = context._attr_to_idx
        
        # Для каждого объекта - битовая маска признаков
        self.object_masks: List[int] = self._build_object_masks()
        
        # Для каждого признака - битовая маска объектов
        self.attribute_masks: List[int] = self._build_attribute_masks()
    
    def _build_object_masks(self) -> List[int]:
        """Строит битовые маски для всех объектов."""
        masks = []
        for obj in self.context.objects:
            mask = 0
            attrs = self.context.object_attributes(obj)
            for attr in attrs:
                j = self.attr_to_idx[attr]
                mask |= (1 << j)
            masks.append(mask)
        return masks
    
    def _build_attribute_masks(self) -> List[int]:
        """Строит битовые маски для всех признаков."""
        masks = []
        for attr in self.context.attributes:
            mask = 0
            objs = self.context.objects_with_attribute(attr)
            for obj in objs:
                i = self.obj_to_idx[obj]
                mask |= (1 << i)
            masks.append(mask)
        return masks
    
    def objects_to_bitset(self, objects: Set[str]) -> int:
        """
        Преобразует множество объектов в битовую маску.
        
        Args:
            objects: множество объектов
            
        Returns:
            битовая маска, где i-й бит = 1, если объект присутствует
        """
        mask = 0
        for obj in objects:
            idx = self.obj_to_idx[obj]
            mask |= (1 << idx)
        return mask
    
    def attributes_to_bitset(self, attributes: Set[str]) -> int:
        """
        Преобразует множество признаков в битовую маску.
        
        Args:
            attributes: множество признаков
            
        Returns:
            битовая маска, где j-й бит = 1, если признак присутствует
        """
        mask = 0
        for attr in attributes:
            idx = self.attr_to_idx[attr]
            mask |= (1 << idx)
        return mask
    
    def bitset_to_objects(self, mask: int) -> Set[str]:
        """
        Преобразует битовую маску в множество объектов.
        
        Args:
            mask: битовая маска
            
        Returns:
            множество объектов, соответствующих маске
        """
        objects = set()
        for i, obj in enumerate(self.context.objects):
            if mask & (1 << i):
                objects.add(obj)
        return objects
    
    def bitset_to_attributes(self, mask: int) -> Set[str]:
        """
        Преобразует битовую маску в множество признаков.
        
        Args:
            mask: битовая маска
            
        Returns:
            множество признаков, соответствующих маске
        """
        attributes = set()
        for j, attr in enumerate(self.context.attributes):
            if mask & (1 << j):
                attributes.add(attr)
        return attributes
    
    def closure_bitset(self, object_mask: int) -> int:
        """
        Оператор замыкания для битовых масок.
        Возвращает маску признаков, общих для всех объектов.
        
        Args:
            object_mask: битовая маска объектов
            
        Returns:
            битовая маска признаков, общих для всех объектов
            
        Пример:
            >>> bitset_ctx.closure_bitset(0b011)  # объекты 0 и 1
            0b001  # только признак 0 общий
        """
        if object_mask == 0:
            # Пустое множество объектов -> все признаки
            return (1 << self.n_attributes) - 1
        
        # Находим первый объект и инициализируем результат его маской
        result_mask = (1 << self.n_attributes) - 1  # все признаки
        first_found = False
        
        for i in range(self.n_objects):
            if object_mask & (1 << i):
                if not first_found:
                    result_mask = self.object_masks[i]
                    first_found = True
                else:
                    result_mask &= self.object_masks[i]
                
                if result_mask == 0:
                    break
        
        return result_mask
    
    def closure_dual_bitset(self, attribute_mask: int) -> int:
        """
        Двойственный оператор замыкания для битовых масок.
        Возвращает маску объектов, обладающих всеми признаками.
        
        Args:
            attribute_mask: битовая маска признаков
            
        Returns:
            битовая маска объектов, обладающих всеми признаками
        """
        if attribute_mask == 0:
            # Пустое множество признаков -> все объекты
            return (1 << self.n_objects) - 1
        
        result_mask = (1 << self.n_objects) - 1
        first_found = False
        
        for j in range(self.n_attributes):
            if attribute_mask & (1 << j):
                if not first_found:
                    result_mask = self.attribute_masks[j]
                    first_found = True
                else:
                    result_mask &= self.attribute_masks[j]
                
                if result_mask == 0:
                    break
        
        return result_mask
    
    def concept_to_readable(self, extent_mask: int, intent_mask: int) -> Tuple[Set[str], Set[str]]:
        """
        Преобразует понятие из битовых масок в читаемый вид.
        
        Args:
            extent_mask: битовая маска объема
            intent_mask: битовая маска содержания
            
        Returns:
            кортеж (множество_объектов, множество_признаков)
        """
        return (
            self.bitset_to_objects(extent_mask),
            self.bitset_to_attributes(intent_mask)
        )