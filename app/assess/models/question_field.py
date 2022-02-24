class QuestionField(object):

    def __init__(
            self,
            key: str,
            title: str,
            field_type: str,
            answer: str,
    ):
        self.key = key
        self.title = title
        self.field_type = field_type
        self.answer = answer

    @staticmethod
    def from_json(data: dict):
        return QuestionField(
            key=data.get("key"),
            title=data.get("title"),
            field_type=data.get("field_type"),
            answer=data.get("answer")
        )
