import youtube_dl
import discord
import spotify_api
import asyncio
import json
from yt_dlp import YoutubeDL
from yt_dlp import utils
import requests
from bs4 import BeautifulSoup
import re

YTDL_OPTIONS = {
    'format': 'bestaudio',
    # 'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': False,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0', # bind to ipv4 since ipv6 addresses cause issues sometimes
    #'match_filter': utils.match_filter_func('duration < 100')
    'skip_download': True,
}
ytdl = YoutubeDL(YTDL_OPTIONS)


FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, title, url, duration, volume=0.5):
        super().__init__(source, volume)


        self.title = title
         # a specific URL needed for discord to play the music
        self.url = url
        self.duration = self.time_converter(duration)

    def time_converter(self, seconds):
        if ':' in seconds:
            return seconds
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
    async def load_youtube_playlist(cls, url):
        players = []
        response = requests.get(url)

        html_text = response.text
        soup = BeautifulSoup(html_text, 'lxml')

        pattern = re.compile(r"( )*var ytInitialData", re.MULTILINE | re.DOTALL)
        result = soup.find("script", text=pattern).text
        split_index = result.find('=')
        result = result[split_index + 1:-1]
        result_data = json.loads(result)

        play_list = result_data['contents']['twoColumnWatchNextResults']['playlist']['playlist']

        title = play_list['title']
        print(title)
        content = play_list['contents']
        for key in content:
            try:
                song = key['playlistPanelVideoRenderer']
                song_title = song['title']['simpleText']
                song_duration = song['lengthText']['simpleText']
                song_url = "https://www.youtube.com" + song['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url']
                print(song_url)
                players.append(cls(discord.FFmpegPCMAudio(song_url, **FFMPEG_OPTIONS), title=song_title, url=song_url, duration=song_duration))

            except KeyError as e:
                print("Does not contain a song")
        return players


    @classmethod
    async def from_url(cls, url, *, loop: asyncio.BaseEventLoop = None):
        players = []
        loop = loop or asyncio.get_event_loop()

        if '&list=' in url:
            response = requests.get(url)

            html_text = response.text
            soup = BeautifulSoup(html_text, 'lxml')

            pattern = re.compile(r"( )*var ytInitialData", re.MULTILINE | re.DOTALL)
            result = soup.find("script", text=pattern).text
            split_index = result.find('=')
            result = result[split_index + 1:-1]
            result_data = json.loads(result)

            play_list = result_data['contents']['twoColumnWatchNextResults']['playlist']['playlist']

            title = play_list['title']
            content = play_list['contents']
            for key in content:
                try:
                    song = key['playlistPanelVideoRenderer']
                    song_title = song['title']['simpleText']
                    song_duration = song['lengthText']['simpleText']
                    song_url = "https://www.youtube.com" + song['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url']
                    players.append(cls(discord.FFmpegPCMAudio(song_url, **FFMPEG_OPTIONS), title=song_title, url=song_url, duration=song_duration))

                except KeyError as e:
                    print(e)
                    print("Does not contain a song")
        else:
            try:
                # if it is a youtube playlist
                # await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False)) # use the default exectutor (exectute calls asynchronously)
                meta_data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

            except:
                search_term = url

                if "spotify" in url:
                    spotify = spotify_api.SpotifyApi()
                    name, artists, duration = spotify.extract_meta_data(url)
                    artist_name_list = [artist["name"] for artist in artists]
                    search_term = name + ' ' + ' '.join(artist_name_list)

                meta_data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"{search_term}", download=False))

            # with open("output.json", 'w') as f:
            #         f.write(json.dumps(meta_data))

            # TODO handle if it is a playlist, currently just takes the first song
            if 'entries' in meta_data:
                for entry in meta_data['entries']:
                    players.append(cls(discord.FFmpegPCMAudio(entry.get('url'), **FFMPEG_OPTIONS), title=entry.get('title'), url=entry.get('url'), duration=entry.get('duration')))
            else:
                entry = meta_data
                players.append(cls(discord.FFmpegPCMAudio(entry.get('url'), **FFMPEG_OPTIONS), title=entry.get('title'), url=entry.get('url'), duration=entry.get('duration')))

        return players

if __name__ == '__main__':
    songlist = asyncio.run(YTDLSource.from_url('https://www.youtube.com/watch?v=hT_nvWreIhg&list=PLbZIPy20-1pN7mqjckepWF78ndb6ci_qi'))

    # songlist = asyncio.run(YTDLSource.from_url('https://www.youtube.com/watch?v=EgFceI6yYAU'))
    print("Size "  + str(len(songlist)))