"""Utilities to work with Python Eel and Bootstrap."""
import eel
import logging
import traceback
import html
from typing import Any, Callable, Optional

# Set up module loggers
pylogger = logging.getLogger(__name__ + ".py")
jslogger = logging.getLogger(__name__ + ".js")


def setloglevel(level: int):
    """Set the log level for the booteel module in both Python and JavaScript."""
    global pylogger, jslogger
    pylogger.setLevel(level)
    jslogger.setLevel(level)


@eel.expose  # type: ignore
def _booteel_logger_getlevel():
    """Grant access to the module's loglevel to booteel.js."""
    return jslogger.level


@eel.expose  # type: ignore
def _booteel_log(level: int, message: str, args: list[Any]):
    """Expose logging interface to booteel.js."""
    global jslogger
    if args:
        message += " " + ", ".join([repr(_) for _ in args])
    jslogger.log(level, message)


_modal_callbacks: dict[str, Callable[[str, str], bool]] = {}


def modal(
    title: str,
    body: str,
    options: Optional[dict[str, str]] = None,
    primary: str = "ok",
    dismissable: bool = True,
    callback: Optional[Callable[[str, str], bool]] = None,
    icon: Optional[str] = None
) -> str:
    """Display a client-side modal via bootstrap."""
    if options is None:
        options = {"ok": "OK"}
    modal_id = eel._booteel_modal(  # type: ignore
        title,
        body,
        options,
        primary,
        dismissable,
        None,
        icon
    )()
    if callback is not None:
        _modal_callbacks[modal_id] = callback  # type: ignore
    return modal_id  # type: ignore


def displayexception(exc: Exception):
    """Display an exception as a dismissable client-side bootstrap modal."""
    exc_type = type(exc).__name__
    exc_text = html.escape(traceback.format_exc(), True)
    exc_text = exc_text.replace("\n", "<br />\n")
    modal(
        f"Error: {exc_type}",
        f'<code class="text-danger">{exc_text}</code>',
        icon="bug-fill text-danger"
    )

def setlocation(location: str):
    eel._booteel_setlocation(location)()  # type: ignore


@eel.expose  # type: ignore
def _booteel_handlemodal(modal_id: str, choice: str):
    if modal_id in _modal_callbacks:
        return _modal_callbacks[modal_id](modal_id, choice)
    else:
        return True
