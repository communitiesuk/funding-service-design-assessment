import re


def remove_currency_symbols(currency_str):

    return re.sub("[,$£]", "", currency_str)


def question_to_table_view(
    question_data: dict,
    numeric_answers=False,
    with_total=False,
    total_prefix="£",
) -> dict:

    return_dict = {"rows": []}

    if numeric_answers:

        return_dict["rows"] = [
            [
                {"text": field["title"]},
                {"text": field["answer"], "format": "numeric"},
            ]
            for field in question_data["fields"]
        ]

    else:

        return_dict["rows"] = [
            [{"text": field["title"]}, {"text": field["answer"]}]
            for field in question_data["fields"]
        ]

    if with_total and numeric_answers:
        try:
            total = sum(
                [
                    int(remove_currency_symbols(field["answer"]))
                    for field in question_data["fields"]
                ]
            )
            total_str = f"{total_prefix}{total}"
        except TypeError:
            total_str = "N/A"

        return_dict["rows"].append(
            [{"text": "Total"}, {"text": total_str, "format": "numeric"}]
        )

    return return_dict
