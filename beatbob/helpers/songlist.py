import collections
import random
import asyncio

class SongList:
    """Class that contains the song queue and different ways of manipulating it
    """
    def __init__(self) -> None:
        self.current = None
        self.songs = {} # all the songs that are added (until cleared)
        self.queue = asyncio.Queue() # all the songs that are currently in the player queue

    def get_previous(self):
        return self.current

    def get_current(self):
        return self.current

    def add_song(self, song):
        self.songs.append(song)
        self.song_queue.append(song)
        print("Current queue: ")

    def clear(self):
        self.songs.clear()
        self.song_queue.clear()

    async def get_next(self):
        self.current = await self.queue.get()
        return self.current