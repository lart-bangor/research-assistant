"""Utility functions for the LART Research Client app."""

import logging
from pathlib import Path
from tkinter import Tk, Label, filedialog
from .config import config

logger = logging.getLogger(__name__)


def export_backup(filename: Path | str | None = None) -> bool:
    """Export app data as a ZIP archive. Prompt for filename if needed."""
    logger.debug("Exporting data backup...")
    import os
    import shutil
    if filename is None:
        tkroot = Tk()
        tkroot.title("LART Research Client data backup")
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
