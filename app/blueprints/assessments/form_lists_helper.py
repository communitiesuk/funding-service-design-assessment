from app.blueprints.shared.filters import (
    remove_dashes_underscores_capitalize_keep_uppercase,
)
from app.blueprints.assessments.form_lists_generated_translations import (
    _LIST_TRANSLATIONS_GENERATED,
)


_LIST_TRANSLATIONS = {
    **_LIST_TRANSLATIONS_GENERATED,
    "none": "None of these",  # See PR 338 on GitHub.
}


def map_form_json_list_value(value: str):
    if mapping := _LIST_TRANSLATIONS.get(value.strip()):
        return remove_dashes_underscores_capitalize_keep_uppercase(mapping)
    return value