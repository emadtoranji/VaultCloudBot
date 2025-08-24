import json
import os


class Language:
    def __init__(self, lang='FA'):
        self.lang = lang
        self.data = {}
        self.__export_language()

    def __export_language(self):
        path = os.path.join("src", "languages", f"{self.lang.lower()}.json")
        with open(path, mode='r', encoding="utf-8") as file:
            self.data = json.load(file)
