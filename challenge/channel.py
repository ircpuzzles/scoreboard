
class Channel(object):
    def __init__(self, name, topic):
        self.name = name
        self.topic = topic
        # the puzzle that is giving this channel its name, either
        # via a correct or incorrect solution
        self.puzzle = None

        # previous channel (if there is one)
        self.prev = None
        # next channel (the one you'll get to if you solve the clue
        #    in this channels topic)
        self.next = None
        # other channel with incorrect solutions
        self.next_incorrect = []
        self.puzzle = None

    def __str__(self):
        name_puzzle = self.puzzle.name if self.puzzle else '-'
        topic_puzzle = self.get_topic_puzzle().name if self.get_topic_puzzle() else '-'
        return '<Channel %s [topic:%s] [name_puzzle:%s topic_puzzle:%s]>' % (self.name, self.topic, name_puzzle, topic_puzzle)

    def get_topic_puzzle(self):
        """The puzzle that is giving this channel its topic."""
        return self.next.puzzle if self.next else None

