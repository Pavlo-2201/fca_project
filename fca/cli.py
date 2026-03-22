"""
Модуль с консольным интерфейсом пользователя (CLI).
"""

import os
import json
import time
from typing import Optional, List, Tuple, Any, Dict

from .context import FormalContext, load_from_json
from .algorithms import build_concepts_set, build_concepts_bitset, compare_implementations
from .structures import BitsetContext

# Глобальное состояние
current_context: Optional[FormalContext] = None
last_concepts: Optional[List] = None
last_method: Optional[str] = None
last_time: Optional[float] = None

EXIT_COMMANDS = {"выход", "quit", "exit", "q"}
UI_WIDTH = 72


def print_divider(char: str = "-"):
    """Печатает разделитель."""
    print(char * UI_WIDTH)


def print_section(title: str):
    """Вывод секции с рамкой."""
    print()
    print_divider("=")
    print(f"{title:^{UI_WIDTH}}")
    print_divider("=")


def print_help():
    """Вывод справки по командам."""
    print_section("СПРАВКА ПО КОМАНДАМ")
    print("load_context <путь>   - загрузить контекст из JSON-файла")
    print("build_set             - построить понятия (set-реализация)")
    print("build_bitset          - построить понятия (bitset-реализация)")
    print("compare               - сравнить производительность двух реализаций")
    print("export [путь]         - экспортировать результаты в JSON")
    print("list [страница]       - показать список понятий (по 10 на странице)")
    print("show <номер>          - показать детали понятия по номеру")
    print("info                  - информация о текущем контексте")
    print("help                  - показать эту справку")
    print("exit, quit, q, выход  - завершить программу")


def print_context_info():
    """Вывод информации о текущем контексте."""
    global current_context
    
    if current_context is None:
        print("Контекст не загружен")
        return
    
    print_section("ИНФОРМАЦИЯ О КОНТЕКСТЕ")
    print(f"Объектов: {current_context.object_count}")
    print(f"Признаков: {current_context.attribute_count}")
    print(f"Плотность матрицы: {_calculate_density():.2%}")


def _calculate_density() -> float:
    """Вычисляет плотность матрицы контекста."""
    global current_context
    
    if current_context is None:
        return 0.0
    
    total = current_context.object_count * current_context.attribute_count
    if total == 0:
        return 0.0
    
    ones = sum(sum(row) for row in current_context.matrix)
    return ones / total


def load_context_command(path: str):
    """Обработка команды load_context."""
    global current_context
    
    try:
        if not os.path.exists(path):
            print(f"Ошибка: файл {path} не найден")
            return
        
        current_context = load_from_json(path)
        print(f"✓ Контекст загружен: {current_context.object_count} объектов, "
              f"{current_context.attribute_count} признаков")
        print(f"  Плотность: {_calculate_density():.2%}")
    except Exception as e:
        print(f"✗ Ошибка загрузки контекста: {e}")


def build_set_command():
    """Построение понятий set-реализацией."""
    global current_context, last_concepts, last_method, last_time
    
    if current_context is None:
        print("✗ Сначала загрузите контекст командой load_context")
        return
    
    print("Построение понятий (set-реализация)...")
    start = time.time()
    concepts = build_concepts_set(current_context)
    elapsed = (time.time() - start) * 1000  # в миллисекундах
    
    last_concepts = concepts
    last_method = "set"
    last_time = elapsed
    
    print(f"✓ Найдено понятий: {len(concepts)}")
    print(f"✓ Время выполнения: {elapsed:.3f} мс")


def build_bitset_command():
    """Построение понятий bitset-реализацией."""
    global current_context, last_concepts, last_method, last_time
    
    if current_context is None:
        print("✗ Сначала загрузите контекст командой load_context")
        return
    
    print("Построение понятий (bitset-реализация)...")
    start = time.time()
    concepts = build_concepts_bitset(current_context)
    elapsed = (time.time() - start) * 1000
    
    last_concepts = concepts
    last_method = "bitset"
    last_time = elapsed
    
    print(f"✓ Найдено понятий: {len(concepts)}")
    print(f"✓ Время выполнения: {elapsed:.3f} мс")


def compare_command():
    """Сравнение производительности двух реализаций."""
    global current_context
    
    if current_context is None:
        print("✗ Сначала загрузите контекст командой load_context")
        return
    
    print_section("СРАВНЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ")
    
    result = compare_implementations(current_context)
    
    print(f"Set-реализация:    {result['set_count']} понятий, {result['set_time_ms']:.3f} мс")
    print(f"Bitset-реализация: {result['bitset_count']} понятий, {result['bitset_time_ms']:.3f} мс")
    print(f"Ускорение: {result['speedup']:.2f}x")
    
    if result['results_match']:
        print("✓ Результаты совпадают")
    else:
        print("✗ Результаты НЕ совпадают!")


def export_command(path: str = "concepts.json"):
    """Экспорт результатов в JSON."""
    global last_concepts, last_method, last_time, current_context
    
    if last_concepts is None:
        print("✗ Нет результатов для экспорта. Сначала выполните build_set или build_bitset")
        return
    
    if current_context is None:
        print("✗ Контекст не загружен")
        return
    
    # Подготовка данных для экспорта
    concepts_json = []
    
    if last_method == "set":
        for extent, intent in last_concepts:
            concepts_json.append({
                "extent": sorted(list(extent)),
                "intent": sorted(list(intent))
            })
    else:  # bitset
        bitset_ctx = BitsetContext(current_context)
        for extent_mask, intent_mask in last_concepts:
            concepts_json.append({
                "extent": sorted(list(bitset_ctx.bitset_to_objects(extent_mask))),
                "intent": sorted(list(bitset_ctx.bitset_to_attributes(intent_mask)))
            })
    
    output = {
        "algorithm": "VanDerMerweKourie2002",
        "data_structure": last_method,
        "concepts_count": len(last_concepts),
        "execution_time_ms": last_time,
        "context_info": {
            "object_count": current_context.object_count,
            "attribute_count": current_context.attribute_count,
            "density": _calculate_density()
        },
        "concepts": concepts_json,
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0.0"
        }
    }
    
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"✓ Результаты сохранены в {path}")
    except Exception as e:
        print(f"✗ Ошибка сохранения: {e}")


def list_command(page: int = 1, page_size: int = 10):
    """Постраничный просмотр списка понятий."""
    global last_concepts, current_context, last_method
    
    if last_concepts is None:
        print("✗ Сначала выполните построение понятий")
        return
    
    total = len(last_concepts)
    pages = (total + page_size - 1) // page_size
    
    if page < 1 or page > pages:
        print(f"✗ Страница {page} вне диапазона (1-{pages})")
        return
    
    start = (page - 1) * page_size
    end = min(start + page_size, total)
    
    print_section(f"СПИСОК ПОНЯТИЙ (страница {page}/{pages})")
    print(f"{'№':>4} | {'Объем (объекты)':30} | {'Содержание (признаки)':30}")
    print_divider("-")
    
    for i in range(start, end):
        extent, intent = last_concepts[i]
        
        if last_method == "bitset" and current_context:
            bitset_ctx = BitsetContext(current_context)
            extent = bitset_ctx.bitset_to_objects(extent)
            intent = bitset_ctx.bitset_to_attributes(intent)
        
        extent_str = ", ".join(sorted(list(extent))[:3])
        if len(extent) > 3:
            extent_str += f" ... и еще {len(extent)-3}"
        elif not extent:
            extent_str = "∅"
        
        intent_str = ", ".join(sorted(list(intent))[:3])
        if len(intent) > 3:
            intent_str += f" ... и еще {len(intent)-3}"
        elif not intent:
            intent_str = "∅"
        
        print(f"{i+1:4} | {extent_str:30} | {intent_str:30}")
    
    print_divider("-")
    print(f"Всего понятий: {total}")


def show_command(index: int):
    """Показать детали конкретного понятия."""
    global last_concepts, current_context, last_method
    
    if last_concepts is None:
        print("✗ Сначала выполните построение понятий")
        return
    
    if index < 1 or index > len(last_concepts):
        print(f"✗ Индекс {index} вне диапазона (1-{len(last_concepts)})")
        return
    
    extent, intent = last_concepts[index - 1]
    
    if last_method == "bitset" and current_context:
        bitset_ctx = BitsetContext(current_context)
        extent = bitset_ctx.bitset_to_objects(extent)
        intent = bitset_ctx.bitset_to_attributes(intent)
    
    print_section(f"ПОНЯТИЕ #{index}")
    print(f"Размер объема: {len(extent)} объектов")
    print(f"Размер содержания: {len(intent)} признаков")
    
    print("\n📦 Объем (объекты):")
    if extent:
        for obj in sorted(list(extent)):
            print(f"  • {obj}")
    else:
        print("  ∅ (пустое множество)")
    
    print("\n🏷️ Содержание (признаки):")
    if intent:
        for attr in sorted(list(intent)):
            print(f"  • {attr}")
    else:
        print("  ∅ (пустое множество)")


def run_cli():
    """Главный цикл CLI."""
    print_section("ПОСТРОИТЕЛЬ РЕШЕТКИ ФОРМАЛЬНЫХ ПОНЯТИЙ")
    print("Версия 1.0.0 | Алгоритм Van Der Merwe, Kourie, 2002")
    print("Введите 'help' для списка команд, 'exit' для выхода\n")
    
    while True:
        try:
            cmd = input("fca> ").strip()
            
            if not cmd:
                continue
            
            if cmd.lower() in EXIT_COMMANDS:
                print("До свидания!")
                break
            
            parts = cmd.split()
            command = parts[0].lower()
            
            if command == "help":
                print_help()
            
            elif command == "info":
                print_context_info()
            
            elif command == "load_context":
                if len(parts) < 2:
                    print("Использование: load_context <путь>")
                else:
                    load_context_command(parts[1])
            
            elif command == "build_set":
                build_set_command()
            
            elif command == "build_bitset":
                build_bitset_command()
            
            elif command == "compare":
                compare_command()
            
            elif command == "export":
                if len(parts) >= 2:
                    export_command(parts[1])
                else:
                    export_command()
            
            elif command == "list":
                if len(parts) >= 2:
                    try:
                        page = int(parts[1])
                        list_command(page)
                    except ValueError:
                        print("Номер страницы должен быть числом")
                else:
                    list_command()
            
            elif command == "show":
                if len(parts) < 2:
                    print("Использование: show <номер>")
                else:
                    try:
                        index = int(parts[1])
                        show_command(index)
                    except ValueError:
                        print("Номер должен быть числом")
            
            else:
                print(f"Неизвестная команда: {command}")
        
        except KeyboardInterrupt:
            print("\nДо свидания!")
            break
        except Exception as e:
            print(f"Ошибка: {e}")


def main():
    """Точка входа."""
    run_cli()


if __name__ == "__main__":
    main()