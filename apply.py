import fnmatch

from manager import Manager
from utils import auth_error_handler
from dotemulsion import DotEmulsionInterpreter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sources import Source
from sources import source_map

manager = Manager.get()


def apply_deps(dep):
    s_type, project = dep.split("|")
    project, *directive = project.split(":")
    source = source_map[s_type](manager, project)
    apply_fn(source, directive=directive[0] if directive else "main")


def download_folder(source, path, exclude=None, include=None, recursive=None):
    files, folders = source.ls(path)
    if exclude:
        files = filter(
            lambda f: not any([fnmatch.fnmatch(f["path"], e) for e in exclude]),
            files
        )
        folders = filter(
            lambda f: not any([fnmatch.fnmatch(f["path"], e) for e in exclude]),
            folders
        )
    if include:
        files = filter(
            lambda f: any([fnmatch.fnmatch(f["path"], e) for e in include]),
            files
        )
        folders = filter(
            lambda f: any([fnmatch.fnmatch(f["path"], e) for e in include]),
            folders
        )
    for file in files:
        if path == "" and file["path"] == "init.emulsion":
            continue
        source.download(file["path"], file["path"], verbose=True)
    if recursive:
        for folder in folders:
            download_folder(source, folder["path"], exclude=exclude, include=include, recursive=recursive)


def apply_directive(source, directives, directive):
    directive_data = directives.get(directive, None)
    if not directive_data:
        raise Exception(f"Error: directive '{directive}' can not be found!")
    # Apply run directives
    for run in directive_data["runs"]:
        print(f"Running Directive: {run}")
        apply_directive(source, directives, run)

    # Apply deps
    for dep in directive_data["pre_deps"]:
        print(f"Applying pre-dep: {dep}")
        apply_deps(dep)

    # Apply project
    print(f"Applying Project")
    download_folder(source, "", exclude=directive_data["exclude"], include=directive_data["include"])

    # Apply post deps
    for dep in directive_data["post_deps"]:
        print(f"Applying post-dep: {dep}")
        apply_deps(dep)


@auth_error_handler
def apply_fn(source: "Source", directive="main"):
    if source.has_emulsion:
        interpreter = DotEmulsionInterpreter(source.get_content_stream("init.emulsion", chunk_size=1))
        directives = interpreter.evaluate()
        print("DotEmulsion loaded for this project!")
        if directives.get(directive, None):
            apply_directive(source, directives, directive)
        else:
            d_list = "-\t" + "\n-\t".join(list(directives.keys()))
            print(f"Can't find the 'main' directive please specify a directive from the following: \n{d_list}")
    else:
        print("Project does not support dotEmulsion")
    print(f"Applied {source.resource_name()}")
