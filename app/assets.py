"""Compile static assets."""
from config import Config
from flask_assets import Bundle
from webassets.exceptions import BuildError


def compile_static_assets(assets, flask_app):
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
        try:
            default_style_bundle.build()
            default_js_bundle.build()
        except BuildError as e:
            raise BuildError(
                "Nothing to build - tried looking for files to build in paths"
                f" relative to the STATIC_FOLDER ({flask_app.static_folder})."
                " Please check the static folder exists and expected static"
                " files exist at the relative paths, defined here in the"
                f" contents of the bundle object -> {e}."
            )
