import re
import ast


def remove_currency_symbols(currency_str):

    return re.sub("[,$£]", "", currency_str)

def question_to_table_view(question_data : dict, numeric_answers = False, with_total = False, total_prefix="£") -> dict:

    return_dict = {"rows" : []}

    if numeric_answers:

        return_dict["rows"] = [ [{"text" : field["title"]}, {"text" : field["answer"], 'format': 'numeric'}] for field in question_data["fields"] ]

    else:

        return_dict["rows"] = [ [{"text" : field["title"]}, {"text" : field["answer"]}] for field in question_data["fields"] ]

    if with_total and numeric_answers:
        try:
            total = sum([int(remove_currency_symbols(field["answer"])) for field in question_data["fields"]])
            total_str = f"{total_prefix}{total}"
        except TypeError:
            total_str = "N/A"

        return_dict["rows"].append([{"text" : "Total"}, {"text" : total_str,  'format': 'numeric'}])

    return return_dict


def format_selection_fragment_dict(question_data : dict) -> dict:

    """
    Standardise the template input formt to a list

    ast.literal_eval: Safely evaluate an expression node or a string
    containing a Python literal or container display. The string or
    node provided may only consist of the following Python literal
    structures: strings, bytes, numbers, tuples, lists, dicts, sets,
     booleans, None, bytes and sets.
    """
    return_dict = {}

    for field in question_data["fields"]:
        answer = field["answer"]
        try:
            if type(ast.literal_eval(answer)) == list:
                return_dict[field["title"]] = ast.literal_eval(answer)
                continue
        except (ValueError, SyntaxError) as e:
            # literal_eval cannot parse string values
            pass
        return_dict[field["title"]] = [answer]

    return return_dict