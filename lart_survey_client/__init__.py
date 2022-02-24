"""LART Survey Client App.

An app to collect survey-type data for research on regional and minority languages,
developed by the Language Attitudes Research Team at Bangor University.
"""
import eel
import gevent
import sys
import logging
import argparse
import booteel
from pathlib import Path
from typing import Any
from datavalidator import DataValidationError
import lsbqrml


# Set up logger for main runtime
logger = logging.getLogger(__name__)
logging.getLogger("geventwebsocket.handler").setLevel(logging.WARNING)


@eel.expose  # type: ignore
def lsbq_rml_get_versions():
    """Get versions for LsbqRml."""
    try:
        return {
            "CymEng_Eng_GB": "Welsh – English (United Kingdom)",
            "CymEng_Cym_GB": "Cymraeg – Saesneg (Deyrnas Unedig)",
            "LmoIta_Ita_IT": "Lombard – Italiano (Italia)",
            "LtzGer_Ger_BE": "Moselfränkisch – Deutsch (Belgien)",
        }
    except Exception as exc:
        booteel.displayexception(exc)


@eel.expose
def atol_c_items():
    """get label pairs for each AToL item"""
    return {
         "logic":    ("logical", "illogical"),
         "elegance": ("inelegant", "elegant"),
     }


@eel.expose  # type: ignore
def lsbq_rml_init(data: dict[Any, Any]):
    """Initialise new LsbqRml."""
    try:
        instance = lsbqrml.Response()
        instance.setmeta(
            data["selectSurveyVersion"],
            data["researcherId"],
            data["researchLocation"],
            data["participantId"],
            data["confirmConsent"]
        )
        print("That's it: ", instance)
        booteel.setlocation(f"part1.html?instance={instance.getid()}")
        return True
    except DataValidationError as exc:
        booteel.modal(
            "Data Validation Error",
            exc.validator.tohtml(errorsonly=True)
        )
    except Exception as exc:
        booteel.displayexception(exc)
    return False


def main():
    """App main function called on app launch."""
    global logger, ROOT_DIR

    # Parse command line arguments
    argparser = argparse.ArgumentParser(description="Launch the LART Survey Client App.")
    argparser.add_argument(
        "--debug",
        dest="level",
        metavar="LEVEL",
        default="warning",
        choices=("debug", "info", "warning", "error", "critical"),
        help=(
            "set the debug level,\n"
            "choices = {debug, info, warning, error, critical},\n"
            "default = warning"
        )
    )
    args = argparser.parse_args()
    logger.debug("Starting with the following command line arguments:", args)
    try:
        loglevel = getattr(logging, args.level.upper())
    except AttributeError:
        loglevel = logging.WARNING
    logging.basicConfig(level=loglevel)
    booteel.setloglevel(loglevel)

    # Run app using eel
    eel.init(  # type: ignore
        Path(__file__).parent / "web",
        allowed_extensions=[".html", ".js", ".css", ".woff", ".svg", ".svgz", ".png"]
    )
    eel.start(  # type: ignore
        "app/index.html",
        jinja_templates="app",
        close_callback=close,
        block=False
    )  # type: ignore
    logger.info(
        f"Now running on "
        f"http://{eel._start_args['host']}:{eel._start_args['port']}"  # type: ignore
    )
    gevent.get_hub().join()  # type: ignore

    # Gracefully exit program execution
    logger.info("Exiting app...")
    sys.exit(0)


def close(page: str, opensockets: list[Any]):
    """Callback when an app socket is closed."""
    logger.info("Socket closed: %s", page)
    logger.debug("Remaining sockets: %s", len(opensockets))

    # Exit gevent event loop if no further sockets open after 1s delay
    if len(opensockets) == 0:

        def conditional_shutdown():
            if len(eel._websockets) == 0:  # type: ignore
                logger.debug("Still no websockets found.")
                logger.debug("Destroying gevent event loop...")
                ghub = gevent.get_hub()  # type: ignore
                ghub.loop.destroy()  # type: ignore
            else:
                logger.debug("New websockets found, cancelling shutdown...")
                gevent.getcurrent().kill()  # type: ignore

        logger.debug("No websockets left, registering shutodwn after 1.0s.")
        gevent.spawn_later(1.0, conditional_shutdown)  # type: ignore


if __name__ == "__main__":
    main()
