Feature: Загрузка формального контекста

  As a analyst
  I want to load formal contexts from JSON files
  So that I can perform Formal Concept Analysis on different datasets

  Background:
    Given the FCA module is available

  Rule: Контекст должен быть валидным

    Scenario: Загрузка контекста из JSON-словаря
      Given a JSON mapping with context
        | objects       | attributes    | matrix                                 |
        | ["o1","o2"]   | ["a1","a2"]   | [[true,false],[false,true]]            |
      When the context is loaded from the JSON mapping
      Then 2 objects should be loaded
      And 2 attributes should be loaded
      And the context matrix should have 2 rows

    Scenario: Загрузка контекста из JSON-файла с полной структурой
      Given a JSON file containing formal context
        | objects | attributes | matrix              |
        | ["o1"]  | ["a1"]     | [[true]]            |
      When the context is loaded from the JSON file
      Then 1 object should be loaded
      And 1 attribute should be loaded
      And the object "o1" should have attribute "a1"

  Rule: Некорректные данные должны вызывать ошибку

    Scenario: Загрузка контекста с несоответствием размеров
      Given a JSON mapping with invalid context
        | objects       | attributes    | matrix                    |
        | ["o1","o2"]   | ["a1"]        | [[true],[false]]          |
      When the context is loaded from the invalid JSON
      Then a ValueError should be raised

    Scenario Outline: Загрузка контекстов разных размеров
      Given a generated context with <size> objects and <attr_count> attributes
      When the context is loaded
      Then the context should be valid

      Examples:
        | size | attr_count |
        | 1    | 1          |
        | 5    | 3          |
        | 10   | 10         |