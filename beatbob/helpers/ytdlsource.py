import youtube_dl
import discord
import json
from discord.ext.commands.errors import CommandInvokeError

ydl_opts = {
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
ytdl = youtube_dl.YoutubeDL(ydl_opts)


ffmpeg_options = {
    'options': '-vn'
}

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, meta_data, volume=0.5):
        super().__init__(source, volume)

        self.meta_data = meta_data

        self.title = meta_data.get('title')
         # a specific URL needed for discord to play the music
        self.url = meta_data.get('url')
        self.duration = meta_data.get('duration')

    @classmethod
    async def from_url(cls, url, *, loop=None):

        try:
            # await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False)) # use the default exectutor (exectute calls asynchronously)
            meta_data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch:{url}", download=False))
        except CommandInvokeError:
            print("The youtube search is not valid")
        # # TODO This is redundant asnd for debug purposes only!
        with open('output.json', 'w') as f:
            f.write(json.dumps(meta_data))

        # TODO handle if it is a playlist, currently just takes the first song
        if 'entries' in meta_data:
            # take first item from a playlist
            meta_data = meta_data['entries'][0]

        print(meta_data)

        return cls(discord.FFmpegPCMAudio(meta_data['url'], **ffmpeg_options), meta_data=meta_data)

