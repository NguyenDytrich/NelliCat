import os
import json
import re
import requests

from discord import Embed

class MwDefinition:

    base_url = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/"

    def __init__(self, word):
        self.word = word
        self.definitions = self._retrieve(word)

    def _retrieve(self, word):
        response = requests.get(f"{self.base_url}/{word}?key={os.getenv('MW_API_KEY')}")
        data = response.json()

        defs = []

        for entry in data:
            # Check if the meta.id of the word is of direct relevance
            entry_id = re.search(f"{word}:?\d", entry["meta"]["id"])
            if entry_id:
                defs.append({"defs": entry["shortdef"], "func": entry["fl"]})
        return defs

    def get_embed(self):
        embed = Embed()

        embed.title = self.word

        for definition in self.definitions:
            embed.add_field(name=definition["func"], value='\n'.join(definition["defs"]))

        return embed
