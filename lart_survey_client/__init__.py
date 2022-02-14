"""LART Survey Client App

An app to collect survey-type data for research on regional and minority languages, developed by the Language Attitudes Research Team at Bangor University.
"""
import eel
import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent

@eel.expose
def lsbq_rml_get_versions():
    return {
        'CymEng_Eng_GB': 'Welsh – English (United Kingdom)',
        'CymEng_Cym_GB': 'Cymraeg – Saesneg (Deyrnas Unedig)',
        'LmoIta_Ita_IT': 'Lombard – Italiano (Italia)',
        'LtzGer_Ger_BE': 'Moselfränkisch – Deutsch (Belgien)',
    }

@eel.expose
def lsbq_rml_init(data):
    for (key, value) in data.items():
        print(f"{key}: {value}")
    print("That's it...")
    return True

@eel.expose
def navigate_to(target):
    print(f"Navigating to {target}")
    eel.show(str(ROOT_DIR / target))

def main():
    eel.init(ROOT_DIR / 'web')
    eel.start('templates/main-entry.html', size=(800, 600), jinja_templates='templates')

if __name__ == '__main__':
    main()