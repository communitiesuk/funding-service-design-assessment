"""
Utility functions for running tests and generating reports
"""

import os

from flask import url_for

from config import Config


def get_service_html_filepath(root_dir: str, service_dict: dict, route_rel: str):
    service = get_service(service_dict)
    path = [root_dir]

    route_list = route_rel.split("/")
    filename = route_list.pop(len(route_list) - 1)
    if not filename:
        filename = "index"
    filename = filename + ".html"

    if service["name"] and service["name"] != Config.LOCAL_SERVICE_NAME:
        path.append(service["name"])

    if len(route_list) > 0:
        cleaned_route_list = list(filter(lambda a: a != "", route_list))
        path.extend(cleaned_route_list)

    basename = os.path.join(*path) + os.path.sep

    return basename, filename


def print_html_page(html: str, service_dict: dict, route_rel: str):
    """
    Prints an html page to local dir
    """
    html_basename, filename = get_service_html_filepath("html", service_dict, route_rel)

    os.makedirs(html_basename, exist_ok=True)
    f = open(html_basename + filename, "w")
    f.write(html)
    f.close()


def get_service(service: dict):
    if not service:
        service = {
            "name": Config.LOCAL_SERVICE_NAME,
            "host": url_for("default_bp.index", _external=True),
        }
    else:
        if "name" not in service:
            raise Exception("Service, if set, must be a dict with a 'name' attribute")
        elif "host" not in service:
            raise Exception("Service, if set, must be a dict with a 'host' attribute")
    return service
