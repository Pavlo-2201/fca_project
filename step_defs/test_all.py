"""Импорт всех BDD-сценариев."""

from pytest_bdd import scenarios

# Импортируем все feature-файлы
scenarios('../features/context_loading.feature')
scenarios('../features/concept_building.feature')
scenarios('../features/performance.feature')