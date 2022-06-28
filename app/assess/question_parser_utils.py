import ast


def standardise_question_data(question) -> dict:

    """
    Standardise the question data to provide a standardised input for templates

    ast.literal_eval: Safely evaluate an expression node or a string
    containing a Python literal or container display. The string or
    node provided may only consist of the following Python literal
    structures: strings, bytes, numbers, tuples, lists, dicts, sets,
     booleans, None, bytes and sets.
    """
    return_dict = {}
    title = question.title
    for question_field in question.fields:
        answer = question_field.answer
        try:
            if type(ast.literal_eval(answer)) == list:
                return_dict[
                    title + ": " + question_field.title
                ] = ast.literal_eval(answer)
                continue
        except (ValueError, SyntaxError):
            # literal_eval cannot parse string values
            pass
        return_dict[title + ": " + question_field.title] = [answer]

    return return_dict
