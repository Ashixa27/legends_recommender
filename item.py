import requests
from init_config import config


class Item:
    def __init__(self, item_id, data):
        self.id = item_id
        self.name = data.get('name')
        self.description = data.get('description', '')
        self.stats = data.get('stats', {})
        self.gold = data.get('gold', {}).get('total', 0)
        self.tags = data.get('tags', [])


    @staticmethod
    def fetch_items(version):
        data = requests.get(config["items_url"].format(version=version)).json()['data']
        return [Item(item_id, item_data) for item_id, item_data in data.items()]
