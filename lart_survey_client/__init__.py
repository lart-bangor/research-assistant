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
from lsbqrml import LsbqRml


# Set up logger for main runtime
logger = logging.getLogger(__name__)
logging.getLogger("geventwebsocket.handler").setLevel(logging.WARNING)
# Set global root dir for resource reference
ROOT_DIR = Path(__file__).parent
logger.debug(f"ROOT_DIR set to `{ROOT_DIR}`")


@eel.expose  # type: ignore
def lsbq_rml_get_versions():
    """Get versions for LsbqRml."""
    return {
        "CymEng_Eng_GB": "Welsh – English (United Kingdom)",
        "CymEng_Cym_GB": "Cymraeg – Saesneg (Deyrnas Unedig)",
        "LmoIta_Ita_IT": "Lombard – Italiano (Italia)",
        "LtzGer_Ger_BE": "Moselfränkisch – Deutsch (Belgien)",
    }


@eel.expose  # type: ignore
def lsbq_rml_init(data: dict[Any, Any]):
    """Initialise new LsbqRml."""
    instance = LsbqRml(
        data["selectSurveyVersion"],
        data["researcherId"],
        data["researchLocation"],
        data["participantId"],
        data["confirmConsent"]
    )
    print("That's it: ", instance)
    print("Data: ", instance.data)
    return True


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

    # Run app using eel
    eel.init(ROOT_DIR / "web")  # type: ignore
    eel.start(  # type: ignore
        "templates/main-entry.html",
        size=(800, 600),
        jinja_templates="templates",
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
