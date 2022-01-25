import youtube_dl
import discord
from apis import spotify_api
import asyncio

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}
ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, meta_data, volume=0.5):
        super().__init__(source, volume)

        self.meta_data = meta_data

        self.title = meta_data.get('title')
         # a specific URL needed for discord to play the music
        self.url = meta_data.get('url')
        self.duration = self.time_converter(meta_data.get('duration'))

    def time_converter(self, seconds):
        """Covert time in seconds to d, h, m, so

        Args:
            seconds (int): seconds
        """
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)

        if(d > 0):
            return("Duration: {}d {}h {}m {}s".format(d, h, m, s))

        if(h > 0):
            return("Duration: {}h {}m {}s".format(h, m, s))

        if(m > 0):
            return("Duration: {}m {}s".format(m, s))

        return("Duration: {}s".format(s))


    @classmethod
    async def from_url(cls, url, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()
        try:
            # await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False)) # use the default exectutor (exectute calls asynchronously)
            meta_data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        except:
            print("Youtube url invalid. Doing youtube search instead")

            search_term = url

            if "spotify" in url:
                spotify = spotify_api.SpotifyApi()
                name, artists = spotify.extract_meta_data(url)
                artist_name_list = [artist["name"] for artist in artists]
                search_term = name + ' ' + ' '.join(artist_name_list)

            meta_data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch:{search_term}", download=False))

        # # TODO This is redundant asnd for debug purposes only!
        # with open('output.json', 'w') as f:
        #     f.write(json.dumps(meta_data))

        # TODO handle if it is a playlist, currently just takes the first song
        if 'entries' in meta_data:
            # take first item from a playlist
            meta_data = meta_data['entries'][0]

        return cls(discord.FFmpegPCMAudio(meta_data['url'], **FFMPEG_OPTIONS), meta_data=meta_data)
