Feature: Сравнение производительности алгоритмов

  As a system architect
  I want to compare Set and BitSet implementations
  So that I can choose the optimal structure for large datasets

  Background:
    Given the FCA module is available

  Scenario Outline: Сравнение на контекстах разного размера
    Given a <type> context with <size> objects and <size> attributes
    When the context is loaded
    And both implementations are run and compared
    Then the BitSet implementation should be faster than Set

    Examples:
      | type   | size |
      | sparse | 10   |
      | sparse | 20   |
      | dense  | 10   |
      | dense  | 20   |
      | sparse | 30   |
      | dense  | 30   |

  @slow
  Scenario: Максимальный нагрузочный тест
    Given a dense context with 25 objects and 25 attributes
    When the context is loaded
    And both implementations are run and compared
    Then the BitSet implementation should be faster than Set
    And the number of concepts should be greater than 0