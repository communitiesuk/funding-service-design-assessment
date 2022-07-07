"""Compile static assets."""
from flask_assets import Bundle
from webassets.exceptions import BuildError


def compile_static_assets(assets, flask_app):
    """
    Configure and build asset bundles.

    Paths in each Bundle() instance below
    are relative to Flask static_folder.
    This is set in the config/envs/default.py
    eg.
    STATIC_FOLDER = "static/dist"
    STATIC_URL_PATH = "/assets"

    Bundle(contents,{filters,output,extra,...})

    Note: filters (compilers must be installed in the environment)

    example:
    default_style_bundle = Bundle(
        "../src/scss/*.scss", <------- These are the file types to match
        filters="pyscss,cssmin", <---- These are how to process them
        output="css/main.min.css", <--- This is the single file that is output
        extra={"rel": "stylesheet/css"}, <--- Extra template tag attributes
    )
    """

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
    try:
        default_style_bundle.build()
        default_js_bundle.build()
    except BuildError as e:
        raise BuildError(
            "Static Files Build Error - tried looking for static files to"
            " build in paths relative to the STATIC_FOLDER"
            f" ({flask_app.static_folder}). Please check the static folder"
            " exists and expected static files exist at the relative paths,"
            f" defined here in the contents of the bundle object -> {e}."
        )
