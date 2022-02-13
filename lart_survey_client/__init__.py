"""LART Survey Client App

An app to collect survey-type data for research on regional and minority languages, developed by the Language Attitudes Research Team at Bangor University.
"""
import eel
import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent

def main():
    eel.init(ROOT_DIR / 'web')
    eel.start('main.html')

if __name__ == '__main__':
    main()