Feature: Построение решетки формальных понятий

  As a researcher
  I want to build concept lattices from formal contexts
  So that I can analyze relationships between objects and attributes

  Background:
    Given the FCA module is available

  Rule: Решетка должна содержать корректные понятия

    Scenario: Построение решетки для контекста 2x2
      Given a JSON mapping with context
        | objects       | attributes    | matrix                                 |
        | ["o1","o2"]   | ["a1","a2"]   | [[true,false],[false,true]]            |
      When the context is loaded from the JSON mapping
      And the lattice is built using Set implementation
      Then the number of concepts should be 4

    Scenario: Построение решетки для контекста с одинаковыми атрибутами
      Given a JSON mapping with context
        | objects       | attributes    | matrix                                 |
        | ["o1","o2"]   | ["a1"]        | [[true],[true]]                        |
      When the context is loaded from the JSON mapping
      And the lattice is built using Set implementation
      Then the number of concepts should be 2

  Rule: Разные реализации должны давать одинаковые результаты

    Scenario: Сравнение Set и BitSet реализаций
      Given a JSON mapping with context
        | objects       | attributes    | matrix                                 |
        | ["o1","o2"]   | ["a1","a2"]   | [[true,false],[false,true]]            |
      When the context is loaded from the JSON mapping
      And both implementations are run and compared
      Then both implementations should return the same number of concepts
      And both implementations should return the same concepts

    Scenario Outline: Проверка на разных размерах
      Given a <type> context with <size> objects and <attr_count> attributes
      When the context is loaded
      And both implementations are run and compared
      Then both implementations should return the same number of concepts

      Examples:
        | type   | size | attr_count |
        | sparse | 5    | 5          |
        | sparse | 10   | 10         |
        | dense  | 5    | 5          |
        | dense  | 10   | 10         |