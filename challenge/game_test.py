
from game import Game
from channel import Channel

import unittest

class TestGame(unittest.TestCase):
    def setUp(self):
        # load game.json file (example/puzzle/*.json must exist!)
        self.game = Game('example/game.json')

    def test_game(self):
        self.assertEqual(self.game.name, 'Test Game Name')
        self.assertEqual(self.game.begin.isoformat('T'), '2014-04-10T06:00:00+02:00')
        self.assertEqual(self.game.end.isoformat('T'), '2014-04-20T12:00:00+02:00')

    def test_game_lobby(self):
        self.assertEqual(self.game.lobby.name, '####_TEST_LOBBY')
        self.assertEqual(self.game.lobby.topic, 'Welcome to Test Game Name! | Choose your path: join ####_TEST_first_path (First Track) or ####_TEST_first_path (First Track) to start!')

    def test_track_access(self):
        self.assertEqual(len(self.game.tracks), 2)
        first_track = self.game.tracks[0]
        self.assertEqual(first_track.get_start().name, '####_TEST_first_path')
        self.assertEqual(first_track.get_start().topic, 'First | Clue: ebgfbyhgvba | Hint: -')
        self.assertEqual(first_track.get_finish().name, '####_TEST_BAR')
        self.assertEqual(first_track.get_finish().topic, 'This is the end, well done!')

    def test_track_channel(self):
        first_track = self.game.tracks[0]
        first_channel = first_track.get_start()

        # channel instances include name and topic
        self.assertIs(type(first_channel), Channel)
        self.assertEqual(first_channel.name, '####_TEST_first_path')
        self.assertEqual(first_channel.topic, 'First | Clue: ebgfbyhgvba | Hint: -')

        # with references to the puzzle:
        # .. that is giving this channel its name:
        self.assertEqual(first_channel.puzzle.name, 'Rot13 Easy')
        # .. and the one that is setting the topic (with the clue to the next channel)
        self.assertEqual(first_channel.get_topic_puzzle().name, 'Base64 Encoded')
        # with references to the next channel:
        self.assertIs(type(first_channel.next), Channel)
        self.assertEqual(first_channel.next.name, '####_TEST_rotsolution')
        # and previous (the first channel has no previous ones):
        self.assertIsNone(first_channel.prev)
        self.assertEqual(first_channel, first_channel.next.prev)

if __name__ == '__main__':
    unittest.main()

