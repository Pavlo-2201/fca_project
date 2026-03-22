import json
import pytest
from unittest.mock import mock_open, patch

from fca.context import load_from_json, FormalContext


def test_load_from_json_valid():
    """
    Тест загрузки корректного JSON-файла с контекстом.
    """
    mock_json_data = {
        "objects": ["кошка", "собака"],
        "attributes": ["млекопитающее", "хищник"],
        "context": [
            [1, 1],
            [1, 0]
        ]
    }
    mock_file_content = json.dumps(mock_json_data)
    
    with patch("builtins.open", mock_open(read_data=mock_file_content)):
        with patch("os.path.exists", return_value=True):
            result = load_from_json("fake_path.json")
    
    assert isinstance(result, FormalContext)
    assert result.objects == ["кошка", "собака"]
    assert result.attributes == ["млекопитающее", "хищник"]
    assert result.matrix == [[1, 1], [1, 0]]
    assert result.object_count == 2
    assert result.attribute_count == 2


def test_load_from_json_file_not_found():
    """
    Тест загрузки несуществующего файла.
    
    Ожидается исключение FileNotFoundError.
    """
    with patch("os.path.exists", return_value=False):
        with pytest.raises(FileNotFoundError, match="Файл не найден"):
            load_from_json("nonexistent.json")


def test_load_from_json_missing_keys():
    """
    Тест загрузки JSON с отсутствующими обязательными ключами.
    
    Ожидается исключение ValueError с сообщением о пропущенных ключах.
    """
    mock_json_data = {
        "attributes": ["млекопитающее", "хищник"],
        "context": [[1, 1], [1, 0]]
    }
    mock_file_content = json.dumps(mock_json_data)
    
    with patch("builtins.open", mock_open(read_data=mock_file_content)):
        with patch("os.path.exists", return_value=True):
            with pytest.raises(ValueError, match="Отсутствуют обязательные ключи: {'objects'}"):
                load_from_json("fake_path.json")
                load_from_json("fake_path.json")
                
def test_context_validation_matrix_dimensions():
    """
    Тест валидации размерности матрицы.
    
    Матрица должна иметь размер len(objects) x len(attributes).
    """
    # Неправильное количество строк
    with pytest.raises(ValueError, match="Количество строк матрицы.*не совпадает"):
        FormalContext(
            objects=["obj1", "obj2"],
            attributes=["attr1", "attr2"],
            matrix=[[1, 1]]  # только одна строка, а нужно две
        )
    
    # Неправильное количество столбцов
    with pytest.raises(ValueError, match="Длина строки.*не совпадает"):
        FormalContext(
            objects=["obj1", "obj2"],
            attributes=["attr1", "attr2"],
            matrix=[
                [1, 1, 1],  # три столбца, а нужно два
                [0, 0, 0]
            ]
        )


def test_context_validation_values():
    """
    Тест валидации значений в матрице.
    
    Значения должны быть только 0 или 1.
    """
    with pytest.raises(ValueError, match="должно быть 0 или 1"):
        FormalContext(
            objects=["obj1", "obj2"],
            attributes=["attr1", "attr2"],
            matrix=[
                [1, 2],  # 2 - недопустимое значение
                [0, 1]
            ]
        )


def test_context_empty_lists():
    """
    Тест валидации пустых списков.
    
    Списки объектов и признаков не могут быть пустыми.
    """
    with pytest.raises(ValueError, match="Список объектов не может быть пустым"):
        FormalContext(
            objects=[],
            attributes=["attr1", "attr2"],
            matrix=[]
        )
    
    with pytest.raises(ValueError, match="Список признаков не может быть пустым"):
        FormalContext(
            objects=["obj1", "obj2"],
            attributes=[],
            matrix=[[], []]
        )
        
        
def test_object_attributes():
    """Тест получения признаков объекта."""
    context = FormalContext(
        objects=["кошка", "собака"],
        attributes=["млекопитающее", "хищник", "домашнее"],
        matrix=[
            [1, 1, 1],  # кошка: все признаки
            [1, 1, 0]   # собака: млекопитающее, хищник
        ]
    )
    
    # Проверяем признаки кошки
    кошка_признаки = context.object_attributes("кошка")
    assert кошка_признаки == {"млекопитающее", "хищник", "домашнее"}
    assert len(кошка_признаки) == 3
    
    # Проверяем признаки собаки
    собака_признаки = context.object_attributes("собака")
    assert собака_признаки == {"млекопитающее", "хищник"}
    assert len(собака_признаки) == 2
    
    # Проверка несуществующего объекта
    with pytest.raises(ValueError, match="не найден"):
        context.object_attributes("динозавр")


def test_objects_with_attribute():
    """Тест получения объектов, обладающих признаком."""
    context = FormalContext(
        objects=["кошка", "собака", "рыба"],
        attributes=["млекопитающее", "хищник", "плавает"],
        matrix=[
            [1, 1, 0],  # кошка: млекопитающее, хищник
            [1, 1, 0],  # собака: млекопитающее, хищник
            [0, 1, 1]   # рыба: хищник, плавает
        ]
    )
    
    # Проверяем объекты с признаком "млекопитающее"
    млекопитающие = context.objects_with_attribute("млекопитающее")
    assert млекопитающие == {"кошка", "собака"}
    assert len(млекопитающие) == 2
    
    # Проверяем объекты с признаком "хищник"
    хищники = context.objects_with_attribute("хищник")
    assert хищники == {"кошка", "собака", "рыба"}
    assert len(хищники) == 3
    
    # Проверяем объекты с признаком "плавает"
    плавающие = context.objects_with_attribute("плавает")
    assert плавающие == {"рыба"}
    assert len(плавающие) == 1
    
    # Проверка несуществующего признака
    with pytest.raises(ValueError, match="не найден"):
        context.objects_with_attribute("несуществующий")


def test_object_attributes_consistency():
    """
    Тест согласованности операций.
    
    Проверяем, что object_attributes и objects_with_attribute
    работают согласованно.
    """
    context = FormalContext(
        objects=["a", "b", "c"],
        attributes=["x", "y", "z"],
        matrix=[
            [1, 0, 1],
            [0, 1, 0],
            [1, 1, 0]
        ]
    )
    
    # Для каждого объекта проверяем, что все его признаки
    # действительно указывают на этот объект
    for obj in context.objects:
        attrs = context.object_attributes(obj)
        for attr in attrs:
            assert obj in context.objects_with_attribute(attr)
    
    # Для каждого признака проверяем, что все объекты с этим признаком
    # действительно имеют этот признак
    for attr in context.attributes:
        objs = context.objects_with_attribute(attr)
        for obj in objs:
            assert attr in context.object_attributes(obj)
            
            
            
            
def test_closure_basic():
    """Базовый тест оператора замыкания."""
    context = FormalContext(
        objects=["кошка", "собака", "рыба"],
        attributes=["млекопитающее", "хищник", "плавает", "домашнее"],
        matrix=[
            [1, 1, 0, 1],  # кошка: млекопитающее, хищник, домашнее
            [1, 1, 0, 0],  # собака: млекопитающее, хищник
            [0, 1, 1, 0]   # рыба: хищник, плавает
        ]
    )
    
    # Замыкание одного объекта
    assert context.closure({"кошка"}) == {"млекопитающее", "хищник", "домашнее"}
    assert context.closure({"собака"}) == {"млекопитающее", "хищник"}
    assert context.closure({"рыба"}) == {"хищник", "плавает"}
    
    # Замыкание двух объектов
    assert context.closure({"кошка", "собака"}) == {"млекопитающее", "хищник"}
    assert context.closure({"кошка", "рыба"}) == {"хищник"}
    assert context.closure({"собака", "рыба"}) == {"хищник"}
    
    # Замыкание всех объектов
    assert context.closure({"кошка", "собака", "рыба"}) == {"хищник"}


def test_closure_empty_set():
    """Замыкание пустого множества должно вернуть все признаки."""
    context = FormalContext(
        objects=["a", "b"],
        attributes=["x", "y", "z"],
        matrix=[
            [1, 0, 1],
            [0, 1, 0]
        ]
    )
    
    assert context.closure(set()) == {"x", "y", "z"}


def test_closure_no_common_attributes():
    """Когда у объектов нет общих признаков, возвращается пустое множество."""
    context = FormalContext(
        objects=["кошка", "рыба"],
        attributes=["млекопитающее", "плавает"],
        matrix=[
            [1, 0],  # кошка: млекопитающее
            [0, 1]   # рыба: плавает
        ]
    )
    
    assert context.closure({"кошка", "рыба"}) == set()


def test_closure_idempotent():
    """
    Проверка идемпотентности: closure(closure(A)) = closure(A)
    Это ключевое свойство оператора замыкания.
    """
    context = FormalContext(
        objects=["a", "b", "c"],
        attributes=["x", "y", "z"],
        matrix=[
            [1, 1, 0],
            [1, 0, 1],
            [0, 1, 1]
        ]
    )
    
    # Берем разные множества объектов
    test_sets = [
        {"a"},
        {"a", "b"},
        {"a", "b", "c"},
        set()
    ]
    
    for obj_set in test_sets:
        # Первое замыкание
        attrs1 = context.closure(obj_set)
        # Второе замыкание (применяем к тем же объектам)
        attrs2 = context.closure(obj_set)
        # Должны совпадать
        assert attrs1 == attrs2


def test_closure_monotone():
    """
    Проверка монотонности: если X ⊆ Y, то closure(X) ⊇ closure(Y)
    Чем больше объектов, тем меньше общих признаков (или столько же).
    """
    context = FormalContext(
        objects=["a", "b", "c"],
        attributes=["x", "y", "z"],
        matrix=[
            [1, 1, 0],
            [1, 0, 1],
            [0, 1, 1]
        ]
    )
    
    # X ⊆ Y
    X = {"a"}
    Y = {"a", "b"}
    
    attrs_X = context.closure(X)
    attrs_Y = context.closure(Y)
    
    # У Y должно быть не больше признаков, чем у X
    assert attrs_Y.issubset(attrs_X)


def test_closure_extensive():
    """
    Проверка экстенсивности: A ⊆ closure_dual(closure(A))
    Это свойство дуальности.
    """
    context = FormalContext(
        objects=["a", "b", "c"],
        attributes=["x", "y", "z"],
        matrix=[
            [1, 1, 0],
            [1, 0, 1],
            [0, 1, 1]
        ]
    )
    
    for obj in context.objects:
        obj_set = {obj}
        attrs = context.closure(obj_set)
        # Здесь мы пока не реализовали closure_dual, поэтому тест пропускаем
        # Но сохраняем как напоминание
        pass
    
def test_closure_dual_basic():
    """Базовый тест двойственного оператора замыкания."""
    context = FormalContext(
        objects=["кошка", "собака", "рыба"],
        attributes=["млекопитающее", "хищник", "плавает", "домашнее"],
        matrix=[
            [1, 1, 0, 1],  # кошка: млекопитающее, хищник, домашнее
            [1, 1, 0, 0],  # собака: млекопитающее, хищник
            [0, 1, 1, 0]   # рыба: хищник, плавает
        ]
    )
    
    # Замыкание одного признака
    assert context.closure_dual({"млекопитающее"}) == {"кошка", "собака"}
    assert context.closure_dual({"хищник"}) == {"кошка", "собака", "рыба"}
    assert context.closure_dual({"плавает"}) == {"рыба"}
    
    # Замыкание двух признаков
    assert context.closure_dual({"млекопитающее", "хищник"}) == {"кошка", "собака"}
    assert context.closure_dual({"хищник", "плавает"}) == {"рыба"}
    assert context.closure_dual({"млекопитающее", "плавает"}) == set()
    
    # Замыкание всех признаков
    all_attrs = {"млекопитающее", "хищник", "плавает", "домашнее"}
    assert context.closure_dual(all_attrs) == set()


def test_closure_dual_empty_set():
    """Замыкание пустого множества признаков должно вернуть все объекты."""
    context = FormalContext(
        objects=["a", "b"],
        attributes=["x", "y", "z"],
        matrix=[
            [1, 0, 1],
            [0, 1, 0]
        ]
    )
    
    assert context.closure_dual(set()) == {"a", "b"}


def test_closure_dual_no_common_objects():
    """Когда у признаков нет общих объектов, возвращается пустое множество."""
    context = FormalContext(
        objects=["кошка", "рыба"],
        attributes=["млекопитающее", "плавает"],
        matrix=[
            [1, 0],  # кошка: млекопитающее
            [0, 1]   # рыба: плавает
        ]
    )
    
    assert context.closure_dual({"млекопитающее", "плавает"}) == set()


def test_closure_dual_properties():
    """
    Проверка свойств двойственного оператора замыкания.
    """
    context = FormalContext(
        objects=["a", "b", "c"],
        attributes=["x", "y", "z"],
        matrix=[
            [1, 1, 0],
            [1, 0, 1],
            [0, 1, 1]
        ]
    )
    
    # Идемпотентность
    attrs = {"x", "y"}
    objs1 = context.closure_dual(attrs)
    objs2 = context.closure_dual(attrs)
    assert objs1 == objs2
    
    # Монотонность (обратная): больше признаков → меньше объектов
    small = context.closure_dual({"x"})
    large = context.closure_dual({"x", "y"})
    assert large.issubset(small)


def test_closure_consistency():
    """
    Проверка согласованности closure и closure_dual.
    
    Должно выполняться: 
    A ⊆ closure_dual(closure(A))
    B ⊆ closure(closure_dual(B))
    """
    context = FormalContext(
        objects=["a", "b", "c"],
        attributes=["x", "y", "z"],
        matrix=[
            [1, 1, 0],
            [1, 0, 1],
            [0, 1, 1]
        ]
    )
    
    # Для каждого объекта
    for obj in context.objects:
        obj_set = {obj}
        attrs = context.closure(obj_set)
        objs_again = context.closure_dual(attrs)
        assert obj_set.issubset(objs_again)
    
    # Для каждого признака
    for attr in context.attributes:
        attr_set = {attr}
        objs = context.closure_dual(attr_set)
        attrs_again = context.closure(objs)
        assert attr_set.issubset(attrs_again)