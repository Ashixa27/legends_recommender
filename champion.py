import requests
from init_config import config


class Champion:
    def __init__(self, name):
        self.name = name
        self.version = requests.get(config['versions_url']).json()[0]
        self.data = self.get_champion_data()
        self.tags = self.data.get('tags', [])
        self.title = self.data.get('title', '')


    def get_champion_data(self):
        data = requests.get(config['champion_url'].format(version=self.version, name=self.name)).json()
        return data['data'][self.name]


