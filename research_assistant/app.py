"""LART Research Assistant app.

An app to collect survey-type data for research on regional and minority languages,
developed by the Language Attitudes Research Team at Bangor University.
"""
import argparse
import eel
import gevent                                                           # type: ignore
import logging
import multiprocessing
import sys
from gevent import signal
from pathlib import Path
from typing import Any, Sequence
from . import atolc                                                     # type: ignore  # noqa: F401
from . import consent                                                   # type: ignore  # noqa: F401
from .config import config
from . import booteel
from .lsbq import expose_to_eel as expose_lsbq
from .memorytask.eel import eel_api as MemoryTaskAPI
from .agt import expose_to_eel as expose_agt
from .settings import expose_to_eel as expose_settings
from .conclusion import expose_to_eel as expose_conclusion
from .utils import export_backup, manage_settings, show_error_dialog

# Enable multiprocessing in frozen apps (e.g. pyinstaller)
multiprocessing.freeze_support()

# Set up logger for main runtime
logging.getLogger("geventwebsocket.handler").setLevel(logging.WARNING)
root_logger_name = __name__.split(".", maxsplit=2)[0]
root_logger = logging.getLogger(root_logger_name)
root_logger.setLevel(config.logging.default_level)
root_logger.addHandler(config.logging.get_stream_handler())                 # > sys.stderr
root_logger.addHandler(config.logging.get_file_handler(root_logger_name))   # > app log dir
logger = logging.getLogger(__name__)

# Expose Eel APIs for subpackages
expose_lsbq()
expose_agt()
expose_settings()
expose_conclusion()

memory_task_api = MemoryTaskAPI()
memory_task_api.expose()

# from pprint import pprint
# pprint(config.sequences)
# pprint(dir(config.sequences))
# pprint(hasattr(config.sequences, "memorytask"))
# pprint(getattr(config.sequences, "memorytask"))
# exit()


@eel.expose
def atol_rating(data: dict[Any, Any]):
    """Retrieve atol rating and print to screen."""
    print("ATOL DATA FROM INDEX.HTML:")
    print(data)


def main():                                                                     # noqa: C901
    """App main function called on app launch."""
    # Parse command line arguments
    argparser = argparse.ArgumentParser(
        description="Launch the LART Research Assistant App."
    )

    class StoreOptionalAction(argparse.Action):
        def __call__(
            self,
            parser: argparse.ArgumentParser,
            namespace: argparse.Namespace,
            values: str | Sequence[Any] | None,
            option_string: str | None = ...
        ) -> None:
            setattr(namespace, self.dest, values)

    argparser.add_argument(
        "-b, --backup",
        action=StoreOptionalAction,
        nargs="?",
        dest="backup",
        metavar="FILE",
        help=(
            "backup data as ZIP archive to FILE if given,\n"
            "otherwise display a save as ... dialog."
        ),
        default=False
    )

    argparser.add_argument(
        "-c, --config",
        action=StoreOptionalAction,
        nargs="?",
        dest="config",
        metavar="CMD",
        help=(
            "Modify the app's settings file according to CMD.\n"
            "CMD may be one of the literals 'clear' (delete the "
            "current settings file), 'update' (ensure the settings "
            "file is updated to include all current app settings, "
            "preserving compatible already-saved settings), or "
            "'reset' (overwrite the current settings file with the "
            "app defaults.\n"
            "Alternatively, CMD may be a JSON string of key-value "
            "pairs enclosed by curly braces ('{...}'), where each key "
            "represents a configuration attribute and the value the new "
            "value it should be set to. For example '{\"sequences.consent\":"
            "\"memorytask\"'} will set the follow-on sequence for the consent "
            "task to the memorytask."
        ),
        default=False
    )

    argparser.add_argument(
        "--debug",
        dest="level",
        metavar="LEVEL",
        choices=("debug", "info", "warning", "error", "critical"),
        help=(
            "set the debug level,\n"
            "choices = {debug, info, warning, error, critical},\n"
            "default = warning"
        )
    )

    argparser.add_argument(
        "--disable-gpu",
        dest="disable_gpu",
        action="store_true",
        help=(
            "Pass the --disable-gpu flag to created chrome "
            "instances.\nCan be useful when running in a VM."
        )
    )

    args = argparser.parse_args()
    logger.debug("Starting with command line arguments: %s", args)
    try:
        loglevel = getattr(logging, args.level.upper())
    except AttributeError:
        loglevel = config.logging.default_level
    root_logger.setLevel(loglevel)
    booteel.setloglevel(loglevel)

    # Run backup exporter and exit if --backup supplied
    if args.backup is not False:
        if export_backup(args.backup):
            sys.exit(0)
        else:
            sys.exit(1)

    # Run settings manager and exit if --config supplied
    if args.config is not False:
        if manage_settings(args.config):
            sys.exit(0)
        else:
            sys.exit(1)

    # Check args.disable_gpu
    if args.disable_gpu:
        logger.info("Running with --disable-gpu flag.")

    # Run app using eel
    eel.init(
        str(Path(__file__).parent / "web"),
        allowed_extensions=[".html", ".js", ".css", ".woff", ".svg", ".svgz", ".png", ".mp3"]
    )
    # Further arguments for the eel/chrome launch
    cmdline_args: list[str] = []
    if args.disable_gpu:
        cmdline_args.append("--disable-gpu")
    try:
        eel.start(
            "app/index.html",
            mode="chrome",
            jinja_templates="app",
            close_callback=close,
            block=False,
            cmdline_args=cmdline_args
        )
    except OSError:
        logger.warning("Chrome not found... attempting fallback to Edge.")
        try:
            eel.start(
                "app/index.html",
                mode="edge",
                jinja_templates="app",
                close_callback=close,
                block=False,
                cmdline_args=cmdline_args
            )
        except OSError as exc2:
            logger.critical(str(exc2))
            show_error_dialog(
                "Missing Chrome or Edge installation",
                (
                    "Can't find Google Chrome/Chromium or Microsoft Edge installation.\n\n"
                    "Please install either Google Chrome/Chromium or Microsoft Edge before "
                    "running the Research Assistant."
                )
            )
            raise
    logger.info(
        f"Now running on "
        f"http://{eel._start_args['host']}:{eel._start_args['port']}"           # type: ignore
    )
    if sys.platform not in ("win32", "win64"):
        gevent.signal.signal(signal.SIGTERM, shutdown)
        gevent.signal.signal(signal.SIGQUIT, shutdown)
        gevent.signal.signal(signal.SIGINT,  shutdown)
    gevent.get_hub().join()                                                     # type: ignore


# Timer for close() function internal callbacks, do not modify outside close() method.
_close_countdown_timer: float = config.shutdown_delay


def close(page: str, opensockets: list[Any]):
    """Callback when an app socket is closed."""
    logger.info("Socket closed: %s", page)
    logger.debug("Remaining sockets: %s", len(opensockets))

    # Exit gevent event loop if no further sockets open after config.shutdown_delay seconds delay
    if len(opensockets) == 0:

        def conditional_shutdown():
            global _close_countdown_timer
            if len(eel._websockets) == 0 and _close_countdown_timer < 1.0:      # type: ignore
                logger.debug("Still no websockets found.")
                logger.debug(f"Shutdown delay timeout remaining is {_close_countdown_timer}.")
                shutdown()
            elif len(eel._websockets) > 0:                                      # type: ignore
                _close_countdown_timer = config.shutdown_delay
                logger.debug("New websockets found, cancelling shutdown...")
                gevent.getcurrent().kill()                                      # type: ignore
            else:
                _close_countdown_timer -= 1.0
                logger.debug("Still no websockets found.")
                logger.debug(f"Shutdown delay timeout remaining is {_close_countdown_timer}.")
                gevent.spawn_later(1.0, conditional_shutdown)  # type: ignore

        logger.debug(f"No websockets left, registering shutodwn after {config.shutdown_delay}s.")
        gevent.spawn_later(1.0, conditional_shutdown)         # type: ignore


def shutdown(sig=None, frame=None):
    """Shut down the app."""
    if sig is not None:
        signames = {
            int(signal.SIGTERM): "SIGTERM",
            int(signal.SIGQUIT): "SIGQUIT",
            int(signal.SIGINT): "SIGINT"
        }
        signame = signames.get(sig, str(sig))
        logger.critical(f"Signal '{signame}' received. Shutdown initiated.")
    logger.info("App shutdown triggered...")
    logger.debug("Destroying gevent event loop...")
    ghub = gevent.get_hub()                                         # type: ignore
    if sys.platform in ("win32", "win64"):
        gevent.kill(ghub)  # Worth trying to see whether this works on Linux/Mac!?
        sys.exit(0)
    else:
        ghub.destroy()                                   # type: ignore
        # This should not have survived and already returned 0...
        logger.debug("Execution survived event loop destruction, hard exiting...")
        sys.exit(1)


# Expose export_backup to spawn self --backup
@eel.expose
def export_data_backup():
    """Non-blocking eel wrapper for the app's `export_backup()` function."""
    p = multiprocessing.Process(target=export_backup)
    p.start()


if __name__ == "__main__":
    main()
