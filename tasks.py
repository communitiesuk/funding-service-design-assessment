import shutil

from invoke import task


@task
def copy_styles(c):

    source_path = "./app/static/src/styles/"
    dist_path = "./app/static/dist/styles/"

    shutil.copytree(source_path, dist_path, dirs_exist_ok=True)
