import collections
import random

class SongList:
    """Class that contains the song queue and different ways of manipulating it
    """
    def __init__(self) -> None:
        self.current = None
        self.songs = []
        self.song_queue = collections.deque()

    def add(self, song):
        self.songs.append(song)
        self.song_queue.append(song)
        print("Current queue: ")


    def clear(self):
        self.songs.clear()
        self.song_queue.clear()


    def next(self):
        self.current = self.song_queue.pop()
        return self.current