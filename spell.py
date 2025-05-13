import requests
from champion import Champion
from init_config import config


class Spell:
    def __init__(self, spell_id, data):
        self.id = spell_id
        self.name = data.get('name')
        self.description = data.get('description', '')


    @staticmethod
    def fetch_spells(version):
        data = requests.get(config["spells_url"].format(version=version)).json()['data']
        return [Spell(spell_id, spell_data) for spell_id, spell_data in data.items()]


if __name__ == '__main__':
    champ = Champion("Ahri")
    version = champ.version
    print(Spell.fetch_spells(version))
