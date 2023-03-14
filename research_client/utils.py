"""Utility functions for the LART Research Client app."""
import os
import shutil
import logging
import json
from pathlib import Path
from tkinter import Tk, Label, Button, filedialog, messagebox
from typing import Any, Literal
from .config import config, Config, _default_dirs                               # type: ignore

logger = logging.getLogger(__name__)


def manage_settings(command: Literal["update", "reset", "clear"] | str) -> bool:  # noqa: C901
    """Manage app settings file.

    Args:
        command: One of the operations to be carried out on the settings file,
            or a JSON string with key-value pairs to be merged into the current
            settings for the app.

            The following commands are available by keyword:
                - `update`: Load app settings from current file and save them
                    again. This is useful if a settings file may not include
                    all the key-value pairs that a user may want to control, for
                    instance after an app update.
                - `reset`: Reset the settings file to the hard-coded app
                    defaults. This is useful in cases where a settings file may
                    have become corrupted and where the user wants to start
                    afresh with manually edit the local settings. Effectively,
                    this is the same as using `clear` followed by `update`.
                - `clear`: Remove the settings file. On the next start-up, the
                    app will then use the hard-coded app defaults. This is
                    useful in cases where the user wants to revert to the apps
                    default settings, without the intent to make manual changes.
    """
    config_file = Path(_default_dirs.user_config_dir) / "settings.json"
    if command == "clear":
        logger.debug("Clearing the settings file...")
        if config_file.is_file():
            config_file.unlink()
            if not config_file.is_file():
                logger.info(f"Successfully deleted settings file '{config_file!s}'")
                return True
            else:
                logger.error(f"Failed to delete settings file at '{config_file!s}'")
                return False
        logger.info(f"No settings file found at '{config_file!s}'")
        return True
    if command == "update":
        logger.debug("Updating the settings file...")
        if config_file.exists():
            loaded = Config.load("settings.json")
            logger.debug(f"Loaded settings from file '{config_file!s}'.")
            if not manage_settings("clear"):
                return False
        else:
            loaded = Config()
            logger.debug(f"No settings file found at {config_file!s}, using app defaults")
        loaded.save("settings.json")
        if config_file.exists():
            logger.info(f"Successfully updated config file at '{config_file!s}'")
            return True
        logger.error(f"Failed to save settings file to '{config_file!s}'")
        return False
    if command == "reset":
        logger.debug("Resetting the settings file...")
        if not manage_settings("clear"):
            return False
        if not manage_settings("update"):
            return False
        logger.info(f"Successfully restored defaults to settings file at {config_file!s}")
        return True
    if command.startswith("{") and command.endswith("}"):
        logger.debug(f"Updating settings with supplied JSON string: {command}")
        data: Any = json.loads(command)
        loaded = Config.load("settings.json")
        stored_attrs: list[str] = []
        unknown_attrs: list[Any] = []
        if isinstance(data, dict):
            for key, value in data.items():                                     # type: ignore
                if isinstance(key, str) and _recursively_overwrite_attr(loaded, key, value):
                    stored_attrs.append(key)
                else:
                    unknown_attrs.append(key)
        else:
            logger.error("Supplied JSON string is not a valid dict of key-value pairs.")
            return False
        logger.info(f"Successfully modified settings: {stored_attrs!r}")
        if unknown_attrs:
            logger.error(f"Failed to modify unknown settings: {unknown_attrs!r}")
        loaded.save("settings.json")
        logger.info(f"Successfully stored modified settings file at {config_file!s}")
        return True
    logger.error(f"Unrecognised settings management command: '{command}'")
    return False


def _recursively_overwrite_attr(obj: object, attr: str, value: Any) -> bool:
    subattr: str | None = None
    if "." in attr:
        tmp = attr.split(".", 1)
        attr = tmp[0]
        subattr = tmp[1]
    if hasattr(obj, attr):
        if subattr and isinstance(getattr(obj, attr), object):
            if _recursively_overwrite_attr(getattr(obj, attr), subattr, value):
                return True
        if not subattr:
            setattr(obj, attr, value)
            return True
    return False


def export_backup(filename: Path | str | None = None) -> bool:
    """Export app data as a ZIP archive. Prompt for filename if needed."""
    logger.debug("Exporting data backup...")
    if filename is None:
        tkroot = Tk()
        tkroot.title("LART Research Client data backup")
        if os.name == "nt":
            tkroot.iconbitmap(  # type: ignore
                str(Path(__file__).parent / "web" / "img" / "appicon.ico")
            )
        label = Label(
            master=tkroot,
            text="Please select the path to save the data backup to...",
            font=("Helvetica 13")
        )
        label.pack()
        tkroot.geometry("500x50")
        tkroot.lift()
        tkroot.withdraw()
        from datetime import datetime
        dialog = filedialog.SaveAs(
            master=tkroot,
            title="Save Data Backup as...",
            initialfile=datetime.now().strftime("lartrc_backup_%Y-%m-%dT%H%M%S.zip"),
            filetypes=[("ZIP Archives", "*.zip")],
            # takefocus="initialfile",
        )
        filename = str(dialog.show())  # type: ignore
    if not filename:
        logger.error("No filename provided.")
        return False
    filename = Path(filename)
    logger.debug(f"Backup filename: '{filename}'")
    if str(filename).endswith(".zip"):
        filename = filename.with_suffix("")
    old_wd = Path.cwd()
    os.chdir(config.paths.data)
    result = shutil.make_archive(str(filename), "zip", logger=logger)
    os.chdir(old_wd)
    if Path(result).exists():
        logger.info(f"Backup saved to file '{result}'.")
        return True
    logger.info("Failed to create backup.")
    return False


def show_error_dialog(title: str | None = None, message: str | None = None):
    """Display a graphical error message box even if eel is not active."""
    tkroot = Tk()
    tkroot.withdraw()
    messagebox.showerror(
        title if title else "Error",
        message if message else "An unknown error occured."
    )
