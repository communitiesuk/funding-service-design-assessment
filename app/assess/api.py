from urllib.parse import urlencode

from app.assess.data import get_local_data
from flask import Blueprint
from flask import jsonify
from flask import make_response
from flask import request

api_bp = Blueprint(
    "api_bp",
    __name__,
    url_prefix="/api",
)


@api_bp.route("/", defaults={"path": ""})
@api_bp.route("/<path:path>", methods=["GET"])
def api(path):

    endpoint = str(path) + "?" + urlencode(request.args.to_dict())
    result = get_local_data(endpoint)
    if not result:
        return make_response(jsonify({"message": "Not found"}), 404)

    return jsonify(result)
