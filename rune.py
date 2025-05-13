import requests
from init_config import config

class Rune:
    def __init__(self, tree_id, tree_name, tree_icon, data):
        self.tree_id = tree_id
        self.tree_name = tree_name
        self.tree_icon = tree_icon
        self.id = data.get('key')
        self.name = data.get('name')
        self.description = data.get('longDesc', '')
        self.icon = data.get('icon')

    @staticmethod
    def fetch_runes(version):
        data = requests.get(config["runes_url"].format(version=version)).json()
        runes_data = []

        # Loop through all trees and slots to collect rune objects
        for tree in data:
            tree_id = tree['key']
            tree_name = tree['name']
            tree_icon = tree['icon']

            for slot in tree['slots']:
                for rune in slot['runes']:
                    rune_obj = Rune(tree_id, tree_name, tree_icon, rune)
                    runes_data.append(rune_obj)

        return runes_data