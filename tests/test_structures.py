"""
Тесты для модуля structures.py (битовые вектора).
"""

import pytest
from fca.context import FormalContext
from fca.structures import BitsetContext


def test_bitset_initialization():
    """Тест инициализации BitsetContext."""
    context = FormalContext(
        objects=["obj1", "obj2"],
        attributes=["attr1", "attr2", "attr3"],
        matrix=[
            [1, 0, 1],
            [0, 1, 0]
        ]
    )
    
    bitset_ctx = BitsetContext(context)
    
    assert bitset_ctx.n_objects == 2
    assert bitset_ctx.n_attributes == 3
    assert len(bitset_ctx.object_masks) == 2
    assert len(bitset_ctx.attribute_masks) == 3


def test_objects_to_bitset():
    """Тест преобразования множества объектов в битовую маску."""
    context = FormalContext(
        objects=["obj1", "obj2", "obj3"],
        attributes=["attr1"],
        matrix=[[1], [1], [0]]
    )
    
    bitset_ctx = BitsetContext(context)
    
    # Пустое множество
    assert bitset_ctx.objects_to_bitset(set()) == 0
    
    # Один объект
    assert bitset_ctx.objects_to_bitset({"obj1"}) == 0b001  # бит 0
    assert bitset_ctx.objects_to_bitset({"obj2"}) == 0b010  # бит 1
    assert bitset_ctx.objects_to_bitset({"obj3"}) == 0b100  # бит 2
    
    # Несколько объектов
    assert bitset_ctx.objects_to_bitset({"obj1", "obj3"}) == 0b101
    assert bitset_ctx.objects_to_bitset({"obj1", "obj2", "obj3"}) == 0b111


def test_attributes_to_bitset():
    """Тест преобразования множества признаков в битовую маску."""
    context = FormalContext(
        objects=["obj1"],
        attributes=["attr1", "attr2", "attr3", "attr4"],
        matrix=[[1, 1, 0, 1]]
    )
    
    bitset_ctx = BitsetContext(context)
    
    # Пустое множество
    assert bitset_ctx.attributes_to_bitset(set()) == 0
    
    # Один признак
    assert bitset_ctx.attributes_to_bitset({"attr1"}) == 0b0001  # бит 0
    assert bitset_ctx.attributes_to_bitset({"attr2"}) == 0b0010  # бит 1
    assert bitset_ctx.attributes_to_bitset({"attr3"}) == 0b0100  # бит 2
    assert bitset_ctx.attributes_to_bitset({"attr4"}) == 0b1000  # бит 3
    
    # Несколько признаков
    assert bitset_ctx.attributes_to_bitset({"attr1", "attr3"}) == 0b0101
    assert bitset_ctx.attributes_to_bitset({"attr1", "attr2", "attr4"}) == 0b1011


def test_bitset_to_objects():
    """Тест преобразования битовой маски в множество объектов."""
    context = FormalContext(
        objects=["A", "B", "C", "D"],
        attributes=["x"],
        matrix=[[1], [1], [0], [1]]
    )
    
    bitset_ctx = BitsetContext(context)
    
    # Пустая маска
    assert bitset_ctx.bitset_to_objects(0) == set()
    
    # Отдельные биты
    assert bitset_ctx.bitset_to_objects(0b0001) == {"A"}
    assert bitset_ctx.bitset_to_objects(0b0010) == {"B"}
    assert bitset_ctx.bitset_to_objects(0b0100) == {"C"}
    assert bitset_ctx.bitset_to_objects(0b1000) == {"D"}
    
    # Комбинации
    assert bitset_ctx.bitset_to_objects(0b0101) == {"A", "C"}
    assert bitset_ctx.bitset_to_objects(0b1111) == {"A", "B", "C", "D"}


def test_bitset_to_attributes():
    """Тест преобразования битовой маски в множество признаков."""
    context = FormalContext(
        objects=["obj"],
        attributes=["p1", "p2", "p3"],
        matrix=[[1, 1, 0]]
    )
    
    bitset_ctx = BitsetContext(context)
    
    # Пустая маска
    assert bitset_ctx.bitset_to_attributes(0) == set()
    
    # Отдельные биты
    assert bitset_ctx.bitset_to_attributes(0b001) == {"p1"}
    assert bitset_ctx.bitset_to_attributes(0b010) == {"p2"}
    assert bitset_ctx.bitset_to_attributes(0b100) == {"p3"}
    
    # Комбинации
    assert bitset_ctx.bitset_to_attributes(0b011) == {"p1", "p2"}
    assert bitset_ctx.bitset_to_attributes(0b111) == {"p1", "p2", "p3"}


def test_object_masks_correct():
    """Проверка, что маски объектов построены правильно."""
    context = FormalContext(
        objects=["obj1", "obj2"],
        attributes=["a", "b", "c"],
        matrix=[
            [1, 0, 1],  # obj1: a, c
            [0, 1, 0]   # obj2: b
        ]
    )
    
    bitset_ctx = BitsetContext(context)
    
    # obj1 должен иметь биты 0 (a) и 2 (c)
    assert bitset_ctx.object_masks[0] == 0b101
    
    # obj2 должен иметь бит 1 (b)
    assert bitset_ctx.object_masks[1] == 0b010


def test_attribute_masks_correct():
    """Проверка, что маски признаков построены правильно."""
    context = FormalContext(
        objects=["obj1", "obj2", "obj3"],
        attributes=["a", "b"],
        matrix=[
            [1, 0],
            [1, 1],
            [0, 1]
        ]
    )
    
    bitset_ctx = BitsetContext(context)
    
    # Признак a должны иметь obj1 (бит 0) и obj2 (бит 1)
    assert bitset_ctx.attribute_masks[0] == 0b011
    
    # Признак b должны иметь obj2 (бит 1) и obj3 (бит 2)
    assert bitset_ctx.attribute_masks[1] == 0b110


def test_closure_bitset():
    """Тест оператора замыкания на битовых масках."""
    context = FormalContext(
        objects=["obj1", "obj2", "obj3"],
        attributes=["a", "b", "c"],
        matrix=[
            [1, 1, 0],
            [1, 0, 1],
            [0, 1, 1]
        ]
    )
    
    bitset_ctx = BitsetContext(context)
    
    # Пустое множество объектов -> все признаки
    assert bitset_ctx.closure_bitset(0) == 0b111
    
    # Один объект
    # obj1 (бит 0) имеет признаки a (0) и b (1) -> маска 0b011
    assert bitset_ctx.closure_bitset(0b001) == 0b011
    
    # obj2 (бит 1) имеет признаки a (0) и c (2) -> маска 0b101
    assert bitset_ctx.closure_bitset(0b010) == 0b101
    
    # obj3 (бит 2) имеет признаки b (1) и c (2) -> маска 0b110
    assert bitset_ctx.closure_bitset(0b100) == 0b110
    
    # Два объекта
    # obj1 и obj2: общие признаки a -> маска 0b001
    assert bitset_ctx.closure_bitset(0b011) == 0b001
    
    # obj1 и obj3: общие признаки b -> маска 0b010
    assert bitset_ctx.closure_bitset(0b101) == 0b010
    
    # obj2 и obj3: общие признаки c -> маска 0b100
    assert bitset_ctx.closure_bitset(0b110) == 0b100
    
    # Все объекты: нет общих признаков -> пустая маска
    assert bitset_ctx.closure_bitset(0b111) == 0


def test_closure_dual_bitset():
    """Тест двойственного оператора замыкания на битовых масках."""
    context = FormalContext(
        objects=["obj1", "obj2", "obj3"],
        attributes=["a", "b", "c"],
        matrix=[
            [1, 1, 0],
            [1, 0, 1],
            [0, 1, 1]
        ]
    )
    
    bitset_ctx = BitsetContext(context)
    
    # Пустое множество признаков -> все объекты
    assert bitset_ctx.closure_dual_bitset(0) == 0b111
    
    # Один признак
    # a (бит 0) имеют obj1 (0) и obj2 (1) -> маска 0b011
    assert bitset_ctx.closure_dual_bitset(0b001) == 0b011
    
    # b (бит 1) имеют obj1 (0) и obj3 (2) -> маска 0b101
    assert bitset_ctx.closure_dual_bitset(0b010) == 0b101
    
    # c (бит 2) имеют obj2 (1) и obj3 (2) -> маска 0b110
    assert bitset_ctx.closure_dual_bitset(0b100) == 0b110
    
    # Два признака
    # a и b: общие объекты obj1 -> маска 0b001
    assert bitset_ctx.closure_dual_bitset(0b011) == 0b001
    
    # a и c: общие объекты obj2 -> маска 0b010
    assert bitset_ctx.closure_dual_bitset(0b101) == 0b010
    
    # b и c: общие объекты obj3 -> маска 0b100
    assert bitset_ctx.closure_dual_bitset(0b110) == 0b100
    
    # Все признаки: нет общих объектов -> пустая маска
    assert bitset_ctx.closure_dual_bitset(0b111) == 0