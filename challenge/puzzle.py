import os
from os.path import basename, splitext
import json
import logging
logger = logging.getLogger('ircpuzzles')

from channel import Channel

class Puzzle(object):
    def __init__(self, id):
        """Initialize puzzle definition."""
        self.id = id
        self.name = None
        self.creator = None
        self.clue = None
        self.hints = None
        self.incorrect_topic = None
        self.solution = None

    def get_correct(self):
        return self.solution.get('correct')

    def get_incorrect(self):
        return self.solution.get('incorrect', [])

    @staticmethod
    def parse(path):
        """Load specified puzzle json definition.

        Args:
            path (str): path to puzzle json file.
        Return:
            Puzzle instance
        """
        id, ext = splitext(basename(path))

        logger.info('reading puzzle definition file: %s', path)
        with open(path) as f:
            content = json.load(f)
            puzzle = Puzzle(id)
            puzzle.name = content.get('name')
            puzzle.creator = content.get('creator')
            puzzle.clue = content.get('clue')
            puzzle.hints = content.get('hints', [])
            puzzle.incorrect_topic = content.get('incorrect_topic', '')
            puzzle.solution = content.get('solution')
            return puzzle

