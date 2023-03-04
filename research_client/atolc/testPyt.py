

def atol_test():
    """Get label pairs for each AToL item depending on language selection."""
    EngVrs = {
        "version_code": "CymEng_Eng_GB",
        "version_name": "Welsh-English (United Kingdom)",
        "language_Maj": "English",
            "atol_items": {
                "logical": ["logical", "illogical"],
                "beauty": ["beautiful", "ugly"]
            }
              

    }
    print(EngVrs)
        


EngVersion = {
    "ENG": {"logic": ("logical", "illogical"),
            "elegance": ("inelegant", "elegant"),
            "fluency": ("choppy", "fluent"),
            "ambiguity": ("unambiguous", "ambiguous"),
            "appeal": ("appealing", "abhorrent"),
            "structure": ("unstructured", "structured"),
            "precision": ("precise", "vague"),
            "harshness": ("harsh", "soft"),
            "flow": ("flowing", "abrupt"),
            "beauty": ("beautiful", "ugly"),
            "sistem": ("systematic", "unsystematic"),
            "pleasure": ("pleasant", "unpleasant"),
            "smoothness": ("smooth", "raspy"),
            "grace": ("clumsy", "graceful"),
            "angularity": ("angular", "round")
            },
    "CYM": { "logic": ("logisch", "unlogisch"),
            "elegance": ("stillos", "stilvoll"),
            "fluency": ("stockend", "fließend")
            }
    }
    
people = {1: {'name': 'John', 'age': '27', 'sex': 'Male'},
          2: {'name': 'Marie', 'age': '22', 'sex': 'Female'}}