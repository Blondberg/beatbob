import collections
import random
import asyncio
import logging

class SongList:
    """Class that contains the song queue and different ways of manipulating it
    """
    def __init__(self) -> None:
        self.current = None
        self.songs = [] # all the songs that are added (until cleared)
        self.queue = asyncio.Queue() # all the songs that are currently in the player queue

        # flags
        self.loop = False
        self.shuffle = False

        self.songnumber = -1

        self.logger = logging.getLogger('musicplayer')


    def get_song_size(self):
        return len(self.songs)

    def get_queue_size(self):
        return self.queue.qsize()

    def get_songs(self):
        return self.songs

    def get_queue(self):
        return self.queue

    def get_previous(self):
        return self.current

    def get_current(self):
        return self.current

    def set_shuffle(self, shuffle):
        self.shuffle = shuffle

    def set_loop(self, loop):
        self.loop = loop

    async def add_song(self, player):
        self.songs.append(player)
        await self.queue.put(player)

        self.logger.debug("Added song {} to queue".format(player.title))

    def clear(self):
        self.songs.clear()

    async def get_next(self):
        self.current = await self.queue.get()
        return self.current

    def get_queue_embed(self):
        pass
