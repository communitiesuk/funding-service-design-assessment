class AssessorField(object):

    def __init__(
        self,
        name: str = "assessment",
        field_type: str = "MultilineTextField",
        label: str = "Please give reasons for your assessment",
        placeholder_text: str = "",
        help_text: str = "",
        hint: str = "",
        required: str = None,
        classes: str = "",
        choices: [] = None,
        choices_type: str = "string",
    ):
        self.name = name
        self.field_type = field_type
        self.label = label
        self.placeholder_text = placeholder_text
        self.help_text = help_text
        self.hint = hint
        self.required = required
        self.classes = classes
        self.choices = choices
        self.choices_type = choices_type

    @staticmethod
    def from_json(data: dict):
        return AssessorField(
                name=data.get("name"),
                field_type=data.get("field_type"),
                label=data.get("label"),
                placeholder_text=data.get("placeholder_text"),
                help_text=data.get("help_text"),
                hint=data.get("hint"),
                required=data.get("required"),
                classes=data.get("classes"),
                choices=data.get("choices"),
                choices_type=data.get("choices_type"),
            )
