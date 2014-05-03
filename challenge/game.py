
import os
from os.path import join, isfile
import json
import logging
logger = logging.getLogger('ircpuzzles')

import dateutil.parser # pip install dateutil

from puzzle import Puzzle
from channel import Channel

class Game(object):
    def __init__(self, filename):
        """Initialize game, parse definition files into internal structures.

        Args:
           filename (str): Path to the game.json file.
        """
        self.filename = filename
        self.path = os.path.dirname(filename)
        self.puzzles = {}
        self.tracks = []

        self.name = None

        self.begin= None
        self.end = None

        self.channel_prefix = None
        self.tracks = []
        self.lobby = None

        self.parse_puzzles()
        self.parse_game()

    def parse_puzzles(self):
        """Discover and parse puzzle for this game."""
        puzzle_path = join(self.path, 'puzzle')
        for filename in os.listdir(puzzle_path):
            path = join(puzzle_path, filename)
            if isfile(path) and filename.endswith('.json'):
                puzzle = Puzzle.parse(path)
                self.puzzles[puzzle.id] = puzzle

    def parse_game(self):
        """Read game file."""
        logger.info('reading game definition file: %s', self.filename)
        with open(self.filename) as f:
            content = json.load(f)

        self.name = content['name']

        # NOTE: make sure timezone information is maintained,
        self.begin = dateutil.parser.parse(content['begin'])
        self.end = dateutil.parser.parse(content['end'])

        self.channel_prefix = content['channel_prefix']
        for i,track in enumerate(content['tracks']):
            self.tracks.append(Track.parse(self, track, i))
        self.lobby = Channel(
            self.format_channel(content['lobby']['channel']),
            self.format_lobby_topic(content['lobby']['topic']))

    def format_channel(self, channel):
        return self.channel_prefix + channel

    def format_lobby_topic(self, topic_format):
        keys = { 'name': self.name }
        for i,track in enumerate(self.tracks):
            keys.update({
                ('track%d_name' % (i+1)): track.name,
                ('track%d_start' % (i+1)): track.get_start().name
            })

        return topic_format % keys

    def get_channel(self, channel_name):
        if self.lobby.name == channel_name:
            return self.lobby
        for track in self.tracks:
            for channel in track.channels:
                if channel.name == channel_name:
                    return channel

class Track(object):
    def __init__(self):
        self.index = 0
        self.name = None
        # the topic format is applied to all channel topics, except the finish channel
        self.topic_format = None
        # Channel for this track, in order
        self.channels = []
        self.channels_incorrect = []

    @staticmethod
    def parse(game, content, index):
        track = Track()

        track.index = index
        track.name = content.get('name')
        track.topic_format = content.get('topic_format')

        puzzles = [game.puzzles[x] for x in content.get('puzzles', [])]
        for i in xrange(0, len(puzzles)+1):
            puzzle = puzzles[i] if i<len(puzzles) else None

            # channel name: correct solution of the previous level:
            if i == 0: # start channel (without a previous puzzle)
                name = game.format_channel(content['start']['channel'])
            else:
                name = game.format_channel(puzzles[i-1].get_correct())

            # channel topic: current puzzle clue
            if not puzzle: # finish channel (without current puzzle)
                topic = track.format_finish_topic(content['finish']['topic'], game, i+1, len(puzzles))
            else:
                topic = track.format_puzzle_topic(puzzles[i], game, i+1, len(puzzles))

            channel = Channel(name, topic)

            # set cross reference to puzzle:
            channel.puzzle = puzzle

            # set incorrect channel list:
            if puzzle:
                for incorrect in puzzle.get_incorrect():
                    incorrect_channel = Channel(
                        incorrect,
                        puzzle.incorrect_topic
                    )
                    channel.next_incorrect.append(incorrect_channel)
                    # also generate a per-track list of incorrect channel:
                    track.channels_incorrect.append(incorrect_channel)

            track.channels.append(channel)

        # build internal links between channel:
        for i in xrange(0, len(track.channels)):
            track.channels[i].prev = track.channels[i-1] if i > 0 else None
            track.channels[i].next = track.channels[i+1] if i < len(track.channels)-1 else None

        return track

    def get_start(self):
        return self.channels[0]

    def get_finish(self):
        return self.channels[-1]

    def format_puzzle_topic(self, puzzle, game, puzzle_num, puzzle_max):
        """Format the topic, the following format keys are placed:

            %(clue)s - the clue of the puzzle
            %(hint)s - the first hint of the puzzle
            %(track_name)s - name of the track
            %(track_num)s - number of the track (starting with 1)
            %(puzzle_num)s - number of the puzzle in current track
            %(puzzle_prev)s - number of the previous puzzle in current track
            %(puzzle_max)s - puzzle count in this track
            %(game_name)s - puzzle count in this track
        """
        return self.topic_format % {
            'clue': puzzle.clue,
            'hint': puzzle.hints[0] if len(puzzle.hints) else '-',
            'track_name': self.name,
            'track_num': self.index+1,
            'puzzle_num': puzzle_num,
            'puzzle_prev': puzzle_num - 1,
            'puzzle_max': puzzle_max,
            'game_name': game.name
        }

    def format_finish_topic(self, topic, game, puzzle_num, puzzle_max):
        """Format the topic, the following format keys are placed:

            %(track_name)s - name of the track
            %(track_num)s - number of the track (starting with 1)
            %(puzzle_num)s - number of the puzzle in current track
            %(puzzle_prev)s - number of the previous puzzle in current track
            %(puzzle_max)s - puzzle count in this track
            %(game_name)s - puzzle count in this track
        """
        return topic % {
            'track_name': self.name,
            'track_num': self.index+1,
            'puzzle_num': puzzle_num,
            'puzzle_prev': puzzle_num - 1,
            'puzzle_max': puzzle_max,
            'game_name': game.name
        }

if __name__ == '__main__':
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)

    # usage example:
    ########################################

    # from local.challenge import Game

    game = Game('example/game.json')

    print 'Game Name: ' + game.name
    print 'Lobby Channel: ' + game.lobby.name
    print 'Lobby Topic: ' + game.lobby.topic
    print
    first_track = game.tracks[0]
    print 'Track 1: ' + first_track.name
    print 'Track Channel:            Puzzle:                Topic:'
    print '---------------------------------------------------------------------------------'
    for channel in first_track.channels:
        print '%-25s %-22s %s' % (channel.name, channel.puzzle.name if channel.puzzle else 'no-puzzle', channel.topic)

    print
    second_track = game.tracks[1]
    print 'Track 2: ' + second_track.name
    print 'Track Channel:            Puzzle:                Topic:'
    print '---------------------------------------------------------------------------------'
    for channel in second_track.channels:
        print '%-25s %-22s %s' % (channel.name, channel.puzzle.name if channel.puzzle else 'no-puzzle', channel.topic)


