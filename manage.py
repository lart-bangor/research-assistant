"""Script to automate common project management tasks.

The goal is to eventually implement the following functionality:
    build:  build the app.
    check:  check the app development enviroment.
    clean:  remove artifacts from the development environment.
    debug:  run the app from the development environment with --debug debug.
    doc:    build the documentation.
    help:   show a help message.
    run:    run the app from the development environment.
    test:   run the tests.
"""
import os
import subprocess
from argparse import ArgumentParser
from pathlib import Path
from typing import Final, Iterable

WORKSPACE_PATH: Final[Path] = Path(__file__).parent
QUALIFIED_PKG_NAME: Final[str] = "lart_research_client"
INDENT: Final[str] = "    "


def main():
    """Script main function, parses arguments and runs commands."""
    parser = ArgumentParser(description="Manage the app's development environment.")
    subparsers = parser.add_subparsers(
        title="sub-commands",
        metavar="COMMAND",
        description="available sub-commands",
        help="additional help",
        required=True
    )
    parser_clean = subparsers.add_parser(
        "clean",
        help="clean the workspace"
    )
    parser_clean.set_defaults(command="clean")
    parser_clean.add_argument(
        "clean_env",
        metavar="ENV",
        nargs="?",
        default="all",
        choices=("src", "build", "all"),
        help=(
            "The part of the development environment to be cleaned.\n"
            "One of {all,build,src}, default=all."
        )
    )
    parser_debug = subparsers.add_parser(
        "debug",
        help=(
            "debug the app from the development environment and continue the"
            "session in the Python interpreter after the app exits"
        )
    )
    parser_debug.set_defaults(command="debug")
    parser_run = subparsers.add_parser(
        "run",
        help="run the app from the development environment"
    )
    parser_run.set_defaults(command="run")
    args = parser.parse_args()
    print(f"Workspace path: {WORKSPACE_PATH}.")
    if args.command == "clean":
        clean(args.clean_env)
    elif args.command == "run":
        run()
    elif args.command == "debug":
        debug()


def clean(env: str):
    """Clean the development environment."""
    errors: bool = False
    if env == "build" or env == "all":
        if not _clean_build():
            errors = True
    if env == "src" or env == "all":
        if not _clean_src():
            errors = True
    return not errors


def debug():
    """Debug the app from the development environment and continue in Python interpreter."""
    oldwd: Path = Path.cwd()
    os.chdir(WORKSPACE_PATH)
    print("Running app...")
    print(f"{INDENT}Working directory is now '{Path.cwd()!s}'.")
    print(f"{INDENT}Running command: py -im {QUALIFIED_PKG_NAME} --debug debug")
    child = subprocess.run(["py", "-im", QUALIFIED_PKG_NAME, "--debug", "debug"])
    print(f"{INDENT}Process returned with code '{child.returncode}'.")
    os.chdir(oldwd)
    print("Done.")


def run():
    """Run the app from the development environment."""
    oldwd: Path = Path.cwd()
    os.chdir(WORKSPACE_PATH)
    print("Running app...")
    print(f"{INDENT}Working directory is now '{Path.cwd()!s}'.")
    print(f"{INDENT}Running command: py -m {QUALIFIED_PKG_NAME}")
    child = subprocess.run(["py", "-m", QUALIFIED_PKG_NAME])
    print(f"{INDENT}Process returned with code '{child.returncode}'.")
    os.chdir(oldwd)
    print("Done.")


def _clean_build() -> bool:
    errors: bool = False
    build_dir: Path = WORKSPACE_PATH / "build"
    print(f"Cleaning build directory at '{build_dir!s}'...")
    if _create_dir_if_not_exists(build_dir):
        if not _recursively_delete_dir(build_dir):
            print(f"{INDENT}ERROR: Could not delete build directory.")
            errors = True
        if not _create_dir_if_not_exists(build_dir):
            print(f"{INDENT}ERROR: Could not reinstate build directory.")
            errors = True
        print("Done.")
    else:
        print(f"{INDENT}ERROR: '{build_dir}' is not a valid directory path.")
        print("Failed.")
        errors = True
    return not errors


def _clean_src() -> bool:
    errors: bool = False
    src_dir: Path = WORKSPACE_PATH / QUALIFIED_PKG_NAME
    print(f"Cleaning source directory at '{src_dir}'...")
    if src_dir.exists():
        for file in _multi_rglob(src_dir, ["*.pyc", "*.pyo", "*.pyd", "*$py.class"]):
            file.unlink()
            if file.exists():
                print(f"{INDENT}ERROR: Could not remove file: '{file!s}'")
                errors = True
        for dir in _multi_rglob(src_dir, ["__pycache__"]):
            dir.rmdir()
            if dir.exists():
                print(f"{INDENT}ERROR: Could not remove directory: '{dir!s}'")
                errors = True
        print("Done.")
    else:
        print(f"{INDENT}ERROR: '{src_dir}' is not a valid directory path.")
        print("Failed.")
        errors = True
    return not errors


def _create_dir_if_not_exists(path: Path) -> bool:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        return path.exists()
    return path.is_dir()


def _recursively_delete_dir(path: Path) -> bool:
    if path.exists():
        if path.is_dir():
            for subpath in path.iterdir():
                if not _recursively_delete_dir(subpath):
                    return False
            path.rmdir()
        else:
            path.unlink()
        if path.exists():
            print(f"{INDENT}ERROR: Could not remove file or directory: '{path!s}'.")
            return False
        return True
    return False


def _multi_rglob(path: Path, globs: Iterable[str]) -> set[Path]:
    paths: set[Path] = set()
    for glob in globs:
        paths.update({_ for _ in path.rglob(glob)})
    return paths


if __name__ == "__main__":
    main()
