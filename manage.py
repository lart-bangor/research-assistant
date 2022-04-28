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
import platform
import shutil
import subprocess
from argparse import ArgumentParser
from configparser import ConfigParser
from importlib import resources
from pathlib import Path
from typing import Final, Iterable


# Define constant values for project
WORKSPACE_PATH: Final[Path] = Path(__file__).parent
config = ConfigParser()
config.read(WORKSPACE_PATH / "setup.cfg")
QUALIFIED_PKG_NAME: Final[str] = config.get("metadata", "name")
APP_VERSION: Final[str] = config.get("metadata", "version")
APP_URL: Final[str] = config.get("metadata", "url")
APP_NAME: Final[str] = config.get("app.options", "name")
APP_AUTHOR: Final[str] = config.get("app.options", "author")
APP_LONG_AUTHOR: Final[str] = config.get("app.options", "long_author")
SPLASH_IMAGE: Final[str] = str(WORKSPACE_PATH / QUALIFIED_PKG_NAME / "web" / "img" / "appicon.png")
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
    parser_build = subparsers.add_parser(
        "build",
        help=(
            "build the app from source"
        )
    )
    parser_build.set_defaults(command="build")
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
    if args.command == "build":
        build()
    elif args.command == "clean":
        clean(args.clean_env)
    elif args.command == "run":
        run()
    elif args.command == "debug":
        debug()


def build() -> bool:                                                            # noqa: C901
    """Build app from source."""
    # Set up paths
    oldwd: Path = Path.cwd()
    src_dir: Path = WORKSPACE_PATH / QUALIFIED_PKG_NAME
    pyi_dir: Path = WORKSPACE_PATH / "build" / "pyinstaller"
    pyi_pkg_dir: Path = pyi_dir / QUALIFIED_PKG_NAME

    # Platform string
    platform_str: str = platform.system()
    if platform.machine():
        platform_str += f"_{platform.machine()}"
    platform_str = platform_str.lower()

    # Clean the source directory
    if not clean("src"):
        return False

    # Make clean copy of source for pyinstaller
    print("Setting up files for building...")
    print(f"{INDENT}Creating package directory for pyinstaller...")
    if not _copy_dir_clean(src_dir, pyi_pkg_dir):
        print(f"{INDENT}ERROR: Could not copy directory '{src_dir}' to '{pyi_pkg_dir}'.")
        print("Failed.")
        return False
    print("Done.")

    # Create PyInstaller runner file..
    print("Creating runner file for PyInstaller...")
    runner_path: Path = pyi_dir / f"{APP_NAME}.py"
    with runner_path.open("w") as fp:
        fp.writelines(
            [
                f"'''Runner for {APP_NAME}.\n\n",
                f"This is a wrapper/runner for {APP_NAME} to run with PyInstaller builds.\n",
                "It has been automatically generated and changes will not persist across\n",
                "fresh builds.\n",
                "'''\n\n",
                f"import {QUALIFIED_PKG_NAME}.app as app\n\n",
                "app.main()\n\n"
                "# EOF\n"
            ]
        )
    if not runner_path.is_file():
        print("Failed.")
        return False
    print("Done.")

    # Set working directory for PyInstaller...
    os.chdir(pyi_dir)
    print(f"Changed current working directory to '{Path.cwd()}'.")

    # Run PyInstaller...
    import PyInstaller.__main__ as pyi                                          # type: ignore
    pyi_args: list[str] = [
        "--noconfirm", "--log-level=WARN",
        f"--workpath=artifacts/{platform_str}", f"--distpath=dist/{APP_NAME}.{platform_str}",
        "--clean", f"{APP_NAME}.py",
        "--hidden-import", "bottle_websocket",
        "--add-data", f"{str(resources.path('eel', 'eel.js'))}{os.pathsep}eel",
        "--collect-data", QUALIFIED_PKG_NAME,
    ]
    # if SPLASH_IMAGE:
    #     CURRENTLY BROKEN IN PyInstaller (tcl/tk lib dependency with vcruntime)
    #     pyi_args.append("--splash")
    #     pyi_args.append(SPLASH_IMAGE)
    if platform.system() == "Windows" or platform.system() == "Darwin":
        if SPLASH_IMAGE:
            pyi_args.append("-i")
            pyi_args.append(SPLASH_IMAGE)
        # pyi_args.append("--windowed")
    print("Running PyInstaller...")
    print(f"{INDENT}Arguments:")
    for i in range(0, len(pyi_args), 2):
        print(f"{INDENT}{INDENT}{pyi_args[i]}", end="")
        if i+1 < len(pyi_args):
            print(f" {pyi_args[i+1]}", end="")
        print("")
    pyi.run(pyi_args)                                                           # type: ignore
    pyi_dist_dir: Path = pyi_dir / "dist" / f"{APP_NAME}.{platform_str}"
    if not pyi_dist_dir.is_dir():
        print(f"{INDENT}ERROR: PyInstaller dist dir at '{pyi_dist_dir}' not found.")
        print("Failed.")
        return False
    print(f"{INDENT}Success: PyInstaller distribution at '{pyi_dist_dir}'.")
    print("Done.")

    # Set working directory for archiving...
    os.chdir(pyi_dist_dir)
    print(f"Changed current working directory to '{Path.cwd()}'.")

    # Make distributable archive
    archive_format: str = "zip"
    if platform.system() == "Linux":
        archive_format = "gztar"
    print(f"Packaging distributable {archive_format.upper()} from PyInstaller distribution...")
    shutil.make_archive(str(pyi_dist_dir), archive_format)
    print("Done.")

    # Make Inno Setup installer
    if platform.system() == "Windows":
        print("Building Windows installer with Inno Setup...")
        with open(WORKSPACE_PATH / "windows.iss", "r") as fp:
            inno_tpl: str = fp.read()
        inno_tpl = _str_replace_all(
            inno_tpl,
            {
                "APP_NAME": APP_NAME,
                "APP_VERSION": APP_VERSION,
                "APP_AUTHOR": APP_AUTHOR,
                "APP_LONG_AUTHOR": APP_LONG_AUTHOR,
                "APP_URL": APP_URL,
                "PLATFORM_STRING": platform_str,
                "WORKSPACE_PATH": str(WORKSPACE_PATH),
            }
        )
        inno_script: Path = pyi_dir / "artifacts" / platform_str / "windows.iss"
        with inno_script.open("w+") as fp:
            fp.write(inno_tpl)
        try:
            child = subprocess.run(["iscc", inno_script])
        except FileNotFoundError:
            print(
                f"{INDENT}ERROR: Command 'iscc' not found. Is Inno Setup installed an on the path?"
            )
            return False
        print(child)
        print("Done.")

    os.chdir(oldwd)
    return True


def _str_replace_all(
    x: str,
    mapping: dict[str, str],
    open_delim: str ="[[",
    close_delim: str = "]]"
) -> str:
    for key, value in mapping.items():
        x = x.replace(f"{open_delim}{key}{close_delim}", value)
    return x

def _copy_dir_clean(source: Path, dest: Path):
    print(f"{INDENT}Copying contents of source directory...")
    print(f"{INDENT}{INDENT}Source: '{source}'.")
    print(f"{INDENT}{INDENT}Destination: '{dest}'.")
    _recursively_delete_dir(dest)
    try:
        shutil.copytree(source, dest)
    except OSError as exc:
        print(f"{INDENT}ERROR: {exc}.")
        return False
    print(f"{INDENT}Done.")
    return True


def clean(env: str) -> bool:
    """Clean the development environment."""
    errors: bool = False
    if env == "build" or env == "all":
        if not _clean_build():
            errors = True
    if env == "src" or env == "all":
        if not _clean_src():
            errors = True
    return not errors


def debug() -> bool:
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
    return child.returncode == 0


def run() -> bool:
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
    return child.returncode == 0


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
