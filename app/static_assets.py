from os import path

from flask import Flask
from flask_assets import Bundle
from flask_assets import Environment


def init(app=None, auto_build=False):
    app = app or Flask(__name__)
    with app.app_context():
        env = Environment(app)
        env.load_path = [path.join(path.dirname(__file__), "static/src")]
        # env.append_path('assets')
        # env.set_directory(env_directory)
        # App Engine doesn't support automatic rebuilding.
        env.auto_build = auto_build
        # This file needs to be shipped with your code.
        env.manifest = "file"

        js = Bundle(
            "./js/namespaces.js",
            "./js/helpers.js",
            "./js/all.js",
            "./js/components/*/*.js",
            filters="jsmin",
            output="js/main.min.js",
        )
        css = Bundle(
            "./scss/*.scss",
            filters="pyscss,cssmin",
            output="css/main.min.css",
            extra={"rel": "stylesheet/css"},
        )

        env.register("default_styles", css)
        env.register("main_js", js)

        bundles = [css, js]
        return bundles


if __name__ == "__main__":
    bundles = init()
    for bundle in bundles:
        bundle.build()
