import discord
from discord.ext import commands
import yt_dlp
import asyncio

global is_playing
global song_name
global n
global did_skipped
global number_of_skips
global duration
global repeat_song
global inactivity_count
is_playing = False
song_name = "No song"
n = 0
did_skipped = False
number_of_skips = 0
duration = 0
repeat_song = False
inactivity_count = 0


def set_default():
    global is_playing
    global song_name
    global n
    global did_skipped
    global number_of_skips
    global duration
    global repeat_song
    global inactivity_count
    is_playing = False
    song_name = "No song"
    n = 0
    did_skipped = False
    number_of_skips = 0
    duration = 0
    repeat_song = False
    inactivity_count = 0


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *, name):
        global n
        global duration
        global song_name
        check_once = False
        global is_playing
        global did_skipped
        global repeat_song
        global inactivity_count
        #if bot isnt playing songs at the moment
        if is_playing == False:
            join_msg = await ctx.send("Give songs some time to load please.")
            n = 0
            voice_channel = ctx.author.voice.channel
            if ctx.author.voice is None:
                await ctx.send('NO.')
            if ctx.voice_client is None:
                await voice_channel.connect()
                vc = ctx.voice_client
            else:
                await ctx.voice_client.move_to(voice_channel)

            YDL_OPTIONS = {
                'format': "bestaudio",
            }
            vc = ctx.voice_client

            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                if "youtube.com" in name:
                    url = ydl.extract_info(name, download=False)
                else:
                    url = ydl.extract_info("ytsearch:%s" % name,
                                           download=False)['entries'][0]

                duration = url.get('duration')
                song_name = url.get('title')
                url2 = url['url']

                FFMPEG_OPTIONS = {
                    'before_options':
                    '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                    'options': '-vn'
                }
                source = await discord.FFmpegOpusAudio.from_probe(
                    url2,
                    **FFMPEG_OPTIONS,
                )
                vc.play(source)
                minutes = int(duration / 60)
                seconds = int(duration % 60)
                await join_msg.delete()
                if seconds < 10:
                    msg = await ctx.send('Now playing: ' + str(song_name) +
                                         '  duration: ' + str(minutes) + ':0' +
                                         str(seconds) + ' requested by: ' +
                                         str(ctx.message.author))
                else:
                    msg = await ctx.send('Now playing: ' + str(song_name) +
                                         '  duration: ' + str(minutes) + ':' +
                                         str(seconds) + ' requested by: ' +
                                         str(ctx.message.author))
            await ctx.message.delete()
            is_playing = True
            #timer for the song. if song was skipped, break out of timer
            for i in range(duration):
                if did_skipped == True:
                    did_skipped = False
                    break
                else:
                    await asyncio.sleep(1)
            await msg.delete()
            #check if loop is on. if on, repeat same song
            while repeat_song == True:
                FFMPEG_OPTIONS = {
                    'before_options':
                    '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                    'options': '-vn'
                }
                YDL_OPTIONS = {
                    'format': "bestaudio",
                }
                vc = ctx.voice_client

                with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                    if "youtube.com/watch" in name:
                        url = ydl.extract_info(name, download=False)
                    else:
                        url = ydl.extract_info("ytsearch:%s" % name,
                                               download=False)['entries'][0]
                    duration = url.get('duration')
                    url2 = url['url']
                    url3 = url.get('id')
                    print(url3)
                    song_name = url.get('title')
                    source = await discord.FFmpegOpusAudio.from_probe(
                        url2, **FFMPEG_OPTIONS)
                    vc.play(source)
                    minutes = int(duration / 60)
                    seconds = int(duration % 60)
                    if seconds < 10:
                        msg = await ctx.send('Now playing: ' + str(song_name) +
                                             '  duration: ' + str(minutes) +
                                             ':0' + str(seconds) +
                                             ' requested by: ' +
                                             str(ctx.message.author) +
                                             ' Loop was ON')
                    else:
                        msg = await ctx.send('Now playing: ' + str(song_name) +
                                             '  duration: ' + str(minutes) +
                                             ':' + str(seconds) +
                                             ' requested by: ' +
                                             str(ctx.message.author) +
                                             ' Loop was ON')
                for i in range(duration):
                    if did_skipped == True:
                        did_skipped = False
                        break
                    else:
                        await asyncio.sleep(1)
                await msg.delete()
            #timer for inactivity once song stops playing. once inactive for 5 minutes will disconnect
            is_playing = False
            song_name = "No Song"
            for i in range(300):
                if is_playing == False and n == 0:
                    await asyncio.sleep(1)
                    inactivity_count = inactivity_count + 1
                    if is_playing == False and n == 0 and inactivity_count == 300:
                        set_default()
                        disc_msg = await ctx.send(
                            "Disconnected due to inactivity")
                        await ctx.voice_client.disconnect()
                        await asyncio.sleep(10)
                        await disc_msg.delete()
                else:
                    inactivity_count = 0
                    break
        #queue function so you can queue 5 songs for the bot to play automatically once the song ends. im too stupid to shorten the code i know theres a way but this works so i just stuck with it
        elif is_playing == True and n < 100:
            n = n + 1
            for i in range(n):
                await asyncio.sleep(2)
                print(str(name), "queue", str(n))
                while is_playing == True:
                    while check_once == False:
                        qmsg = await ctx.send('Song queued: ' + str(name))
                        await ctx.message.delete()
                        check_once = True
                    await asyncio.sleep(2)
            is_playing = True
            n = n - 1
            await qmsg.delete()
            if ctx.author.voice is None:
                await ctx.send('NO.')
            voice_channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                await voice_channel.connect()
            else:
                await ctx.voice_client.move_to(voice_channel)

            #everything here is the same as on top just that i never arrange properly

            FFMPEG_OPTIONS = {
                'before_options':
                '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn'
            }
            YDL_OPTIONS = {
                'format': "bestaudio",
            }
            vc = ctx.voice_client

            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                if "youtube.com/watch" in name:
                    url = ydl.extract_info(name, download=False)
                else:
                    url = ydl.extract_info("ytsearch:%s" % name,
                                           download=False)['entries'][0]
                duration = url.get('duration')
                url2 = url['url']
                song_name = url.get('title')
                source = await discord.FFmpegOpusAudio.from_probe(
                    url2, **FFMPEG_OPTIONS)
                vc.play(source)
                minutes = int(duration / 60)
                seconds = int(duration % 60)
                if seconds < 10:
                    msg = await ctx.send('Now playing: ' + str(song_name) +
                                         '  duration: ' + str(minutes) + ':0' +
                                         str(seconds) + ' requested by: ' +
                                         str(ctx.message.author))
                else:
                    msg = await ctx.send('Now playing: ' + str(song_name) +
                                         '  duration: ' + str(minutes) + ':' +
                                         str(seconds) + ' requested by: ' +
                                         str(ctx.message.author))

            print(ctx.message.author)
            for i in range(duration):
                if did_skipped == True:
                    did_skipped = False
                    break
                else:
                    await asyncio.sleep(1)
            await msg.delete()

            while repeat_song == True:
                FFMPEG_OPTIONS = {
                    'before_options':
                    '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                    'options': '-vn'
                }
                YDL_OPTIONS = {
                    'format': "bestaudio",
                }
                vc = ctx.voice_client

                with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                    if "youtube.com/watch" in name:
                        url = ydl.extract_info(name, download=False)
                    else:
                        url = ydl.extract_info("ytsearch:%s" % name,
                                               download=False)['entries'][0]
                    duration = url.get('duration')
                    url2 = url['url']
                    song_name = url.get('title')
                    source = await discord.FFmpegOpusAudio.from_probe(
                        url2, **FFMPEG_OPTIONS)
                    vc.play(source)
                    minutes = int(duration / 60)
                    seconds = int(duration % 60)
                    if seconds < 10:
                        msg = await ctx.send('Now playing: ' + str(song_name) +
                                             '  duration: ' + str(minutes) +
                                             ':0' + str(seconds) +
                                             ' requested by: ' +
                                             str(ctx.message.author) +
                                             ' Loop was ON')
                    else:
                        msg = await ctx.send('Now playing: ' + str(song_name) +
                                             '  duration: ' + str(minutes) +
                                             ':' + str(seconds) +
                                             ' requested by: ' +
                                             str(ctx.message.author) +
                                             ' Loop was ON')
                for i in range(duration):
                    if did_skipped == True:
                        did_skipped = False
                        break
                    else:
                        await asyncio.sleep(1)
                await msg.delete()

            is_playing = False
            song_name = "No Song"
            for i in range(300):
                if is_playing == False and n == 0:
                    await asyncio.sleep(1)
                    inactivity_count = inactivity_count + 1
                    if is_playing == False and n == 0 and inactivity_count == 300:
                        set_default()
                        disc_msg = await ctx.send(
                            "Disconnected due to inactivity")
                        await ctx.voice_client.disconnect()
                        await asyncio.sleep(10)
                        await disc_msg.delete()
                else:
                    inactivity_count = 0
                    break
        else:
            print("more than 100 in queue")
            qmsg = await ctx.send(
                "Already 100 songs in queue. Song not queued please calm down")
            await ctx.message.delete()
            await asyncio.sleep(6)
            await qmsg.delete()

    @commands.command(pass_context=True)
    async def status(self, ctx):
        await ctx.send('online')

    @commands.command(name="skip", aliases=["fs"])
    async def skip(self, ctx):
        global is_playing
        global did_skipped
        did_skipped = True
        print(ctx.message.author)
        print("skip")
        ctx.voice_client.stop()
        msg = await ctx.send("Skipped")
        await ctx.message.delete()
        await asyncio.sleep(4)
        await msg.delete()

    @commands.command(name="np", aliases=["nowplaying", "song"])
    async def np(self, ctx):
        global song_name
        msg = await ctx.send(song_name)
        await asyncio.sleep(10)
        await msg.delete()
        await ctx.message.delete()

    @commands.command()
    async def clear(self, ctx):
        global is_playing
        global n
        x = 12
        if is_playing == False:
            await ctx.message.delete()
            msg = await ctx.send("No song in queue though")
            await asyncio.sleep(5)
            await msg.delete()
        else:
            is_playing = False
            await ctx.message.delete()
            msg = await ctx.send("Clearing queue please wait...")
            for i in range(x):
                is_playing = False
                await asyncio.sleep(1)
            n = 0
            is_playing = True
            await msg.delete()
            msg = await ctx.send("Queue Cleared!")
            await asyncio.sleep(7)
            await msg.delete()

    @commands.command(name="disconnect", aliases=["reset"])
    async def disconnect(self, ctx):
        await ctx.message.delete()
        ctx.voice_client.stop()
        set_default()
        await ctx.voice_client.disconnect()

    @commands.command(name="queue", aliases=["q"])
    async def queue(self, ctx):
        msg = await ctx.send("THERES NO QUEUE FUNCTION")
        await asyncio.sleep(20)
        await msg.delete()

    @commands.command(name="loop", aliases=["repeat"])
    async def loop(self, ctx):
        global repeat_song
        await ctx.message.delete()
        if repeat_song == False:
            msg = await ctx.send("Loop ON")
            print("LOOP ON")
            repeat_song = True
        else:
            msg = await ctx.send("Loop OFF")
            print("LOOP OFF")
            repeat_song = False
        await asyncio.sleep(10)
        await msg.delete()

    @commands.command(pass_context=True)
    async def ping(self, ctx, user: discord.User):
        for i in range(5):
            await asyncio.sleep(1)
            await user.send(str(ctx.author) + " is calling for you")

    @commands.command(pass_context=True)
    async def spamping(self, ctx, user: discord.User):
        for i in range(30):
            await asyncio.sleep(0.5)
            await user.send(str(ctx.author) + " is calling for you")

    @commands.command()
    async def leaveserver(self, ctx):
        if ctx.message.author.id != 208909582930673665:
            await ctx.send("developer only command")
            return
        else:
            id = ctx.author.guild
            print(id)
            await id.leave()

    @commands.command()
    async def stop(self, ctx):
        if ctx.message.author.id == 340304524411404288:
            await ctx.send(
                "stop it la dilong tell u how many times dont have !stop command already"
            )
            return
        else:
            await ctx.send("use !skip or !clear instead")

    @commands.command(name="list_commands")
    async def list_commands(self, ctx):
        await ctx.message.delete()
        await ctx.send(
            "**!play/!p** - Play song with URL or title \n**!status** - Check if bot is online \n**!skip/!fs** - Skip currently playing song \n**!np/!nowplaying/!song** - Show current playing song \n**!clear** - Clear queued songs \n**!disconnect/!reset** - Use this if bot isn't working as intended \n**!loop/!repeat** - Toggle loop on/off \n**!ping** - Bot pings someone in DMs (!ping @user) \n**!spamping** - Bot spam pings someone in DMs (!spamping @user) \n**!leaveserver** - Kicks bot from server "
        )
      
    def setup(client):
        client.add_cog(Music(client))
