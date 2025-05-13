from champion import Champion
from db_func import db_manager
from item import Item
from spell import Spell
from rune import Rune


class BuildRecommender:
    def __init__(self, champion: Champion):
        """
        Recommends builds (items, spells, and runes) for a given champion based on data fetched from the database and API

        :param champion: champion for which the build is being recommended
        """
        self.champion = champion
        self.items = Item.fetch_items(champion.version)
        self.runes = Rune.fetch_runes(champion.version)
        self.spells = Spell.fetch_spells(champion.version)
        self.build = db_manager.read_build(champion.name)
        self.skill_priority = self.build.get('skill_priority', [])
        self.runes_primary_tree = {}
        self.runes_primary_runes = []
        self.runes_secondary_tree = {}
        self.runes_secondary_runes = []
        self.stat_shards = self.build.get('stat_shards', [])
        self.spell_1 = []
        self.spell_2 = []
        self.starting_items = []
        self.core_items = []
        self.situational_items = []


    @staticmethod
    def add_to_build(elem: Item or Spell or Rune, build_place: list) -> None:
        """
        Adds an element (item, spell, or rune) to a given build list if it doesn't already exist in that list

        :param elem: element to be added to the build
        :param build_place: list to which the element will be added
        """
        if elem.name not in [i.name for i in build_place]:
            build_place.append(elem)


    def recommend_items(self) -> tuple:
        """
        Recommends items (starting, core, and situational) for the champion based on the champion's build from the database

        :return: tuple containing lists of starting items, core items and situational items for the champion
        """
        for item in self.items:
            for k, v in self.build.items():
                if item.name in v:
                    self.add_to_build(item, getattr(self, k))

        return self.starting_items, self.core_items, self.situational_items


    def recommend_spells(self) -> tuple:
        """
        Recommends spells for the champion based on the champion's build from the database

        :return: tuple containing lists of the first and second spells for the champion
        """
        for spell in self.spells:
            for key in ['spell_1', 'spell_2']:
                if key in self.build:
                    if spell.name in self.build[key]:
                        self.add_to_build(spell, getattr(self, key))

        return self.spell_1, self.spell_2


    def recommend_runes(self) -> tuple:
        """
        Recommends runes (primary and secondary trees and runes) for the champion based on the champion's build from the database

        :return: tuple containing dictionaries of the primary and secondary rune trees
                lists of primary and secondary runes for the champion
        """
        primary_tree_names = self.build.get('runes_primary_tree', [])
        primary_rune_names = self.build.get('runes_primary_runes', [])
        secondary_tree_names = self.build.get('runes_secondary_tree', [])
        secondary_rune_names = self.build.get('runes_secondary_runes', [])

        for rune in self.runes:
            if rune.tree_name in primary_tree_names and rune.name in primary_rune_names:
                self.add_to_build(rune, self.runes_primary_runes)
                if rune.tree_name not in self.runes_primary_tree:
                    self.runes_primary_tree[rune.tree_name] = rune.tree_icon

            elif rune.tree_name in secondary_tree_names and rune.name in secondary_rune_names:
                self.add_to_build(rune, self.runes_secondary_runes)
                if rune.tree_name not in self.runes_secondary_tree:
                    self.runes_secondary_tree[rune.tree_name] = rune.tree_icon

        return (
            self.runes_primary_tree,
            self.runes_primary_runes,
            self.runes_secondary_tree,
            self.runes_secondary_runes
        )