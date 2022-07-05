"""Compile static assets."""
from config import Config
from flask_assets import Bundle


def compile_static_assets(assets):
    """Configure and build asset bundles."""

    # Main asset bundles
    # Paths are relative to Flask static_folder
    default_style_bundle = Bundle(
        "../src/scss/*.scss",
        filters="pyscss,cssmin",
        output="css/main.min.css",
        extra={"rel": "stylesheet/css"},
    )

    default_js_bundle = Bundle(
        "../src/js/namespaces.js",
        "../src/js/helpers.js",
        "../src/js/all.js",
        "../src/js/components/*/*.js",
        filters="jsmin",
        output="js/main.min.js",
    )

    assets.register("default_styles", default_style_bundle)
    assets.register("main_js", default_js_bundle)
    if Config.FLASK_ENV == "development":
        default_style_bundle.build()
        default_js_bundle.build()
