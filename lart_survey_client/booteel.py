"""Utilities to work with Python Eel and Bootstrap."""
import eel
import logging
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
    callback: Optional[Callable[[str, str], bool]] = None
) -> str:
    """Foo."""
    # booteel.modal = async function (title, body, options = {ok: 'OK'}, primary = 'ok', dismissable = true, callback = null)
    if options is None:
        options = {"ok": "OK"}
    modal_id = eel._booteel_modal(  # type: ignore
        title,
        body,
        options,
        primary,
        dismissable
    )()
    if callback is not None:
        _modal_callbacks[modal_id] = callback
    return modal_id  # type: ignore

@eel.expose  # type: ignore
def _booteel_handlemodal(modal_id: str, choice: str):
    if modal_id in _modal_callbacks:
        return _modal_callbacks[modal_id](modal_id, choice)
    else:
        return True
