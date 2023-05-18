#!/usr/bin/env python3
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


# Utilitie required from startup
def safe_str(string: str) -> str:
    """Removes characters from strings that would be unsuitable as paths, handles, etc."""
    allowed = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-'
    return ''.join(c for c in string.replace(' ', '_') if c in allowed)


# Define constant values for project
WORKSPACE_PATH: Final[Path] = Path(__file__).parent
config = ConfigParser()
config.read(WORKSPACE_PATH / "setup.cfg")
PYPI_PKG_NAME: Final[str] = config.get("metadata", "name")
QUALIFIED_PKG_NAME: Final[str] = config.get("app.options", "qualified_pkg_name")
APP_VERSION: Final[str] = config.get("metadata", "version")
APP_URL: Final[str] = config.get("metadata", "url")
APP_NAME: Final[str] = config.get("app.options", "name")
APP_AUTHOR: Final[str] = config.get("app.options", "author")
APP_LONG_AUTHOR: Final[str] = config.get("app.options", "long_author")
SPLASH_IMAGE: Final[str] = str(WORKSPACE_PATH / QUALIFIED_PKG_NAME / "web" / "img" / "appicon.png")
INDENT: Final[str] = "    "

# System-dependent parameters
M_SUPPORTED_SYSTEMS: Final[tuple[str, ...]] = ("Windows", "Linux")
M_SUPPORTED_MACHINES: Final[tuple[str, ...]] = ("AMD64", "x86_64")
M_PLATFORM_SYSTEM: Final[str] = platform.system()
if M_PLATFORM_SYSTEM not in M_SUPPORTED_SYSTEMS:
    print(
        f"WARNING: Running on unknown system type {M_PLATFORM_SYSTEM!r}. "
        f"Supported system types are {M_SUPPORTED_SYSTEMS}. \n"
        "You can still use manage.py, but you may run into unexpected errors.\n"
    )
if M_PLATFORM_SYSTEM == "Windows":
    short_system = "win"
elif M_PLATFORM_SYSTEM == "Linux":
    short_system = "linux"
else:
    short_system = M_PLATFORM_SYSTEM.lower()
M_PLATFORM_SHORT_SYSTEM: Final[str] = short_system
del short_system
M_PLATFORM_MACHINE: Final[str] = platform.machine()
if M_PLATFORM_MACHINE not in M_SUPPORTED_MACHINES:
    print(
        f"WARNING: Running on unknown machine type {M_PLATFORM_MACHINE!r}. "
        f"Supported system types are {M_SUPPORTED_MACHINES}. \n"
        "You can still use manage.py, but you may run into unexpected errors.\n"
    )
if M_PLATFORM_MACHINE in ("AMD64", "x86_64"):
    short_machine = "64"
else:
    short_machine = M_PLATFORM_MACHINE.lower()
M_PLATFORM_SHORT_MACHINE: Final[str] = short_machine
del short_machine
M_PLATFORM_RELEASE: Final[str] = platform.release()
M_PLATFORM_STRING: Final[str] = f"{M_PLATFORM_SHORT_SYSTEM}{M_PLATFORM_SHORT_MACHINE}"
M_COMMAND_PYTHON: Final[str] = "py" if M_PLATFORM_SYSTEM == "Windows" else "python3"


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
        choices=("all", "build", "dist", "docs", "src"),
        help=(
            "The part of the development environment to be cleaned.\n"
            "One of {all,build,dist,src}, default=all."
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
    parser_debug.add_argument(
        "--disable-gpu",
        dest="disable_gpu",
        action="store_true",
        help=(
            "Pass the --disable-gpu flag to created chrome "
            "instances.\nCan be useful when running in a VM."
        )
    )
    parser_docs = subparsers.add_parser(
        "docs",
        help=(
            "build/update the app documentation"
        )
    )
    parser_docs.set_defaults(command="docs")
    parser_run = subparsers.add_parser(
        "run",
        help="run the app from the development environment"
    )
    parser_run.set_defaults(command="run")
    parser_run.add_argument(
        "--disable-gpu",
        dest="disable_gpu",
        action="store_true",
        help=(
            "Pass the --disable-gpu flag to created chrome "
            "instances.\nCan be useful when running in a VM."
        )
    )
    args = parser.parse_args()
    print(f"Workspace path: {WORKSPACE_PATH}.")
    if args.command == "build":
        build()
    elif args.command == "clean":
        clean(args.clean_env)
    elif args.command == "run":
        run(disable_gpu=args.disable_gpu)
    elif args.command == "debug":
        debug(disable_gpu=args.disable_gpu)
    elif args.command == "docs":
        docs()


def docs() -> bool:                                                             # noqa: C901
    """Build/update the app documentation from source."""
    # Set up paths
    oldwd: Path = Path.cwd()
    docs_dir: Path = WORKSPACE_PATH / "docs"

    # Make sure dist dir exists..
    dist_dir: Path = WORKSPACE_PATH / "dist" / "docs"
    if not dist_dir.is_dir():
        dist_dir.mkdir(parents=True)

    # Run the sphinx make procedure
    os.chdir(docs_dir)
    print(f"Changed current working directory to '{Path.cwd()}'.")
    if platform.system() == "Windows":
        try:
            subprocess.run(["make.bat", "clean"])
            subprocess.run(["make.bat", "html"])
        except FileNotFoundError:
            print(
                f"{INDENT}ERROR: './docs/make.bat' was not found. Is Sphinx set up correctly?"
            )
            os.chdir(oldwd)
            return False
    else:
        try:
            subprocess.run(["make", "clean"])
            subprocess.run(["make", "html"])
        except FileNotFoundError:
            print(
                f"{INDENT}ERROR: could not run 'make ./docs/Makefile'. Is Sphinx set up correctly?"
            )
            os.chdir(oldwd)
            return False
    os.chdir(oldwd)

    # Move documentation to dist dir
    html_docs_dir: Path = docs_dir / "build" / "html"
    if html_docs_dir.exists():
        print(f"Moving HTML documentation to '{dist_dir}'..")
        if not _copy_dir_clean(html_docs_dir, dist_dir / "html"):
            print(
                f"{INDENT}ERROR: Could not copy directory "
                f"'{html_docs_dir}' to '{dist_dir}/html'."
            )
            print("Failed.")
            return False
        print("Success.")

    return True


def build() -> bool:                                                            # noqa: C901
    """Build app from source."""
    # Set up paths
    oldwd: Path = Path.cwd()
    src_dir: Path = WORKSPACE_PATH / QUALIFIED_PKG_NAME
    build_dir: Path = WORKSPACE_PATH / "build" / M_PLATFORM_STRING
    dist_dir: Path = WORKSPACE_PATH / "dist" / M_PLATFORM_STRING
    pyi_pkg_dir: Path = build_dir / QUALIFIED_PKG_NAME

    # Make sure dist dir exists..
    if not dist_dir.is_dir():
        dist_dir.mkdir(parents=True)

    # Installer name
    pkg_name: str = safe_str(f"{APP_AUTHOR} {APP_NAME} v{APP_VERSION}-{M_PLATFORM_STRING}")

    # Clean the source directory
    if not clean("src"):
        return False

    # Build with PyInstaller
    result = _build_pyinstaller(src_dir, build_dir / "pyinstaller", dist_dir, pkg_name)
    os.chdir(oldwd)
    if not result:
        return False

    # Make Inno Setup installer if on Windows
    if M_PLATFORM_SYSTEM == "Windows":
        result = _build_inno_installer(build_dir / "pyinstaller", dist_dir, pkg_name)
        os.chdir(oldwd)
        if not result:
            return False

    # Build Wheel with Setuptools...
    result = _build_setuptools_package(src_dir, build_dir / "setuptools", dist_dir)
    os.chdir(oldwd)
    if not result:
        return False

    return True


def _build_setuptools_package(src_dir, build_dir: str, dist_dir: str) -> bool:
    # Make wheel with setuptools
    print("Running setuptools to build Python wheel...")

    # Make clean copy of package...
    print(f"{INDENT}Setting up clean copy of source...")
    if not _copy_dir_clean(src_dir, build_dir / QUALIFIED_PKG_NAME):
        print(f"{INDENT*2}ERROR: Could not copy directory '{src_dir}' to '{build_dir}'.")
        print(f"{INDENT*2}!! Failed !!")
        return False
    files_to_copy: tuple[str, ...] = (
        'setup.cfg',
        'pyproject.toml',
        'LICENSE',
        'LICENSE.AGPL-3.0',
        'LICENSE.EUPL-1.2',
        'README.rst'
    )
    for file in files_to_copy:
        print(f"{INDENT*2}Copying file {file}.")
        shutil.copy(src_dir.parent / file, build_dir / file)

    # Set working directory for setuptools
    os.chdir(build_dir)
    print(f"{INDENT}Changed current working directory to '{Path.cwd()}'.")

    # Run build
    print(f"{INDENT}Running 'python -m build'...")
    try:
        child = subprocess.run([M_COMMAND_PYTHON, "-m", "build"])
    except FileNotFoundError:
        print(
            f"{INDENT*2}ERROR: Command '{M_COMMAND_PYTHON}' not found. Is the pipenv virtualenv set up correctly?"
        )
        print(f"{INDENT*2}!! Failed !!")
        return False
    if child.returncode > 0:
        print(
            f"{INDENT*2}ERROR: Python returned an error (code: {child.returncode}). "
            "Are the setuptools and build packages installed?"
        )
        print(f"{INDENT*2}!! Failed !!")
        return False

    # Check that build produced a dist dir
    if not Path("dist").is_dir():
        print(f"{INDENT*2}ERROR: Setuptools dist dir at '{build_dir}/dist' not found.")
        print(f"{INDENT*2} !! Failed !!")
        return False

    # Move wheel and sdist archive to dist_dir
    for file in Path("dist").iterdir():
        print(f"{INDENT*2}Moving file {file}.")
        file = file.replace(dist_dir / file.name)
    print(f"{INDENT}Distributables moved to {dist_dir}.")

    return True


def _build_inno_installer(pyinstaller_dir: str, dist_dir: str, pkg_name: str) -> bool:
    # Make Inno Setup installer
    print("Running Windows installer build with Inno Setup...")

    # Make installer script...
    print(f"{INDENT}Making installer script...")
    with open(WORKSPACE_PATH / "windows.iss", "r") as fp:
        inno_tpl: str = fp.read()
    inno_tpl = _str_replace_all(
        inno_tpl,
        {
            "APP_NAME": APP_NAME,
            "APP_VERSION": APP_VERSION,
            "APP_AUTHOR": APP_AUTHOR,
            "APP_LONG_AUTHOR": APP_LONG_AUTHOR,
            "SAFE_APP_NAME": safe_str(APP_NAME),
            "SAFE_APP_VERSION": safe_str(APP_VERSION),
            "SAFE_APP_AUTHOR": safe_str(APP_AUTHOR),
            "SAFE_APP_LONG_AUTHOR": safe_str(APP_LONG_AUTHOR),
            "APP_URL": APP_URL,
            "PLATFORM_STRING": M_PLATFORM_STRING,
            "WORKSPACE_PATH": str(WORKSPACE_PATH),
        }
    )
    inno_script: Path = pyinstaller_dir / "artifacts" / M_PLATFORM_STRING / "windows.iss"
    with inno_script.open("w+") as fp:
        fp.write(inno_tpl)
    try:
        child = subprocess.run(["iscc", inno_script])
    except FileNotFoundError:
        print(
            f"{INDENT*2}ERROR: Command 'iscc' not found. Is Inno Setup installed an on the path?"
        )
        print(f"{INDENT*2}!! Failed !!")
        return False
    installer_file = pyinstaller_dir / "dist" / f"{pkg_name}.exe"
    if not installer_file.exists():
        print(
            f"{INDENT}ERROR: Expected installer file '{installer_file}' not found."
        )
        return False
    installer_file = installer_file.replace(dist_dir / installer_file.name)
    print(f"{INDENT}EXE installer distributable moved to '{installer_file}'.")
    print(child)
    print("Done.")
    return True


def _build_pyinstaller(src_dir: Path, build_dir: Path, dist_dir: Path, pkg_name: str) -> bool:  # noqa: C901
    # Make clean copy of source for pyinstaller
    print("Running PyInstaller build...")
    print(f"{INDENT}Setting up files for pyinstaller build...")
    print(f"{INDENT*2}Creating package directory for pyinstaller...")
    if not _copy_dir_clean(src_dir, build_dir / QUALIFIED_PKG_NAME):
        print(f"{INDENT*2}ERROR: Could not copy directory '{src_dir}' to '{build_dir}'.")
        print(f"{INDENT*2}!! Failed !!")
        return False

    # Create PyInstaller runner file..
    print(f"{INDENT}Creating runner file...")
    runner_path: Path = build_dir / f"{safe_str(APP_NAME)}.py"
    with runner_path.open("w") as fp:
        fp.writelines(
            [
                f"'''Runner for {safe_str(APP_AUTHOR)}_{safe_str(APP_NAME)}.\n\n",
                f"This is a wrapper/runner for `{QUALIFIED_PKG_NAME}` to run with PyInstaller.\n",
                "It has been automatically generated and changes will not persist across\n",
                "fresh builds.\n",
                "'''\n\n",
                f"import {QUALIFIED_PKG_NAME}.app as app\n\n",
                "app.main()\n\n"
                "# EOF\n"
            ]
        )
    if not runner_path.is_file():
        print(f"{INDENT*2}!! Failed !!")
        return False

    # Set working directory for PyInstaller...
    os.chdir(build_dir)
    print(f"{INDENT}Changed current working directory to '{Path.cwd()}'.")

    # Run PyInstaller...
    import PyInstaller.__main__ as pyi                                          # type: ignore
    pyi_args: list[str] = [
        "--noconfirm", "--log-level=WARN",
        f"--workpath=artifacts/{M_PLATFORM_STRING}", f"--distpath=dist/{pkg_name}",
        "--clean", f"{safe_str(APP_NAME)}.py",
        "--hidden-import", "bottle_websocket",
        "--add-data", f"{str(resources.path('eel', 'eel.js'))}{os.pathsep}eel",
        "--collect-data", QUALIFIED_PKG_NAME,
    ]
    # if SPLASH_IMAGE:
    #     # CURRENTLY BROKEN IN PyInstaller (tcl/tk lib dependency with vcruntime)
    #     pyi_args.append("--splash")
    #     pyi_args.append(SPLASH_IMAGE)
    if platform.system() == "Windows" or platform.system() == "Darwin":
        if SPLASH_IMAGE:
            pyi_args.append("-i")
            pyi_args.append(SPLASH_IMAGE)
        # pyi_args.append("--windowed")
    print(f"{INDENT}Running PyInstaller...")
    print(f"{INDENT*2}Arguments:")
    for i in range(0, len(pyi_args), 2):
        print(f"{INDENT*3}{pyi_args[i]}", end="")
        if i+1 < len(pyi_args):
            print(f" {pyi_args[i+1]}", end="")
        print("")
    pyi.run(pyi_args)                                                           # type: ignore
    if not Path(f"dist/{pkg_name}").is_dir():
        print(f"{INDENT*2}ERROR: PyInstaller dist dir at 'dist/{pkg_name}' not found.")
        print(f"{INDENT*2} !! Failed !!")
        return False
    print(f"{INDENT*2}Success: PyInstaller distribution at 'dist/{pkg_name}'.")

    # Make distributable archive
    print(f"{INDENT}Making archive from PyInstaller build...")

    # Set working directory for archiving...
    os.chdir(f"dist")
    print(f"{INDENT*2}Changed current working directory to '{Path.cwd()}'.")

    # Make the archive
    archive_format: str = "zip"
    if platform.system() == "Linux":
        archive_format = "gztar"
    print(f"{INDENT*2}Packaging distributable {archive_format.upper()} from PyInstaller distribution...")
    archive_file = Path(shutil.make_archive(
        base_name=pkg_name,
        format=archive_format,
        root_dir=pkg_name,
        base_dir=safe_str(APP_NAME)
    ))
    archive_file = archive_file.replace(dist_dir / archive_file.name)
    print(f"{INDENT}Archive with distributable moved to '{archive_file}'.")

    return True


def _str_replace_all(
    x: str,
    mapping: dict[str, str],
    open_delim: str = "[[",
    close_delim: str = "]]"
) -> str:
    for key, value in mapping.items():
        x = x.replace(f"{open_delim}{key}{close_delim}", value)
    return x


def _copy_dir_clean(source: Path, dest: Path):
    print(f"{INDENT*2}Copying contents of source directory...")
    print(f"{INDENT*3}Source: '{source}'.")
    print(f"{INDENT*3}Destination: '{dest}'.")
    _recursively_delete_dir(dest)
    try:
        shutil.copytree(source, dest)
    except OSError as exc:
        print(f"{INDENT*3}ERROR: {exc}.")
        print(f"{INDENT*3}!! Failed !!")
        return False
    return True


def clean(env: str) -> bool:                                                    # noqa: C901
    """Clean the development environment."""
    errors: bool = False
    if env == "build" or env == "all":
        if not _clean_build():
            errors = True
    if env == "dist" or env == "all":
        if not _clean_dist():
            errors = True
    if env == "src" or env == "all":
        if not _clean_src():
            errors = True
    if env == "docs" or env == "all":
        if not _clean_docs():
            errors = True
    return not errors


def debug(disable_gpu: bool = False) -> bool:
    """Debug the app from the development environment and continue in Python interpreter."""
    oldwd: Path = Path.cwd()
    os.chdir(WORKSPACE_PATH)
    command: list[str] = [
        M_COMMAND_PYTHON,
        "-m",
        QUALIFIED_PKG_NAME,
        "--debug",
        "debug"
    ]
    if disable_gpu:
        command.append("--disable-gpu")
    print("Running app...")
    print(f"{INDENT}Working directory is now '{Path.cwd()!s}'.")
    print(f"{INDENT}Running command: {' '.join(command)}")
    child = subprocess.run(command)
    print(f"{INDENT}Process returned with code '{child.returncode}'.")
    os.chdir(oldwd)
    print("Done.")
    return child.returncode == 0


def run(disable_gpu: bool = False) -> bool:
    """Run the app from the development environment."""
    oldwd: Path = Path.cwd()
    os.chdir(WORKSPACE_PATH)
    command: list[str] = [
        M_COMMAND_PYTHON,
        "-m",
        QUALIFIED_PKG_NAME
    ]
    if disable_gpu:
        command.append("--disable-gpu")
    print("Running app...")
    print(f"{INDENT}Working directory is now '{Path.cwd()!s}'.")
    print(f"{INDENT}Running command: {' '.join(command)}")
    child = subprocess.run(command)
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


def _clean_dist() -> bool:
    errors: bool = False
    dist_dir: Path = WORKSPACE_PATH / "dist"
    print(f"Cleaning distribution directory at '{dist_dir!s}'...")
    if _create_dir_if_not_exists(dist_dir):
        if not _recursively_delete_dir(dist_dir):
            print(f"{INDENT}ERROR: Could not delete dist directory.")
            errors = True
        if not _create_dir_if_not_exists(dist_dir):
            print(f"{INDENT}ERROR: Could not reinstate dist directory.")
            errors = True
        print("Done.")
    else:
        print(f"{INDENT}ERROR: '{dist_dir}' is not a valid directory path.")
        print("Failed.")
        errors = True
    return not errors


def _clean_docs() -> bool:
    errors: bool = False
    docs_dir: Path = WORKSPACE_PATH / "docs" / "build"
    print(f"Cleaning documentation directory at '{docs_dir!s}'...")
    if _create_dir_if_not_exists(docs_dir):
        if not _recursively_delete_dir(docs_dir):
            print(f"{INDENT}ERROR: Could not delete docs/build directory.")
            errors = True
        if not _create_dir_if_not_exists(docs_dir):
            print(f"{INDENT}ERROR: Could not reinstate docs/build directory.")
            errors = True
        print("Done.")
    else:
        print(f"{INDENT}ERROR: '{docs_dir!s}' is not a valid directory path.")
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
