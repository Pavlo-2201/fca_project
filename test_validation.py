from fca.context import FormalContext

try:
    context = FormalContext(
        objects=["o1", "o2"],
        attributes=["a1"],
        matrix=[[1]]
    )
    print("Ошибка: контекст должен был вызвать исключение!")
except ValueError as e:
    print(f"✅ Исключение поймано: {e}")