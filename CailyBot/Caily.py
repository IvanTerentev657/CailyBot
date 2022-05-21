import asyncio, asyncpraw, os
from asyncio import sleep

import pymorphy2
import requests

from config import CLIENT_ID, SECRET, TOKEN
from random import choice
import discord
from discord.ext import commands


def main():
    intents = discord.Intents.default()
    intents.members = True

    bot = commands.Bot(command_prefix='$', intents=intents)
    bot.add_cog(Post(bot))
    bot.add_cog(Calculator(bot))
    bot.add_cog(Timer(bot))
    bot.add_cog(Morphy(bot))
    bot.add_cog(Translate(bot))
    bot.run(TOKEN)


class Post(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reddit = asyncpraw.Reddit(client_id=CLIENT_ID, client_secret=SECRET, user_agent='meme_reddit_bot/0.0.1')
        self.checked = []

    @commands.command(name='new_post')
    async def new_post(self, ctx, subreddit=''):
        try:
            if subreddit == '':
                raise ValueError
            result = await self.reddit.subreddit(subreddit)
            result = result.new(limit=1)

            post = await result.__anext__()
        except ValueError:
            await ctx.send(f'Тебе вместе с командой также следует ввести имя суббредита')
            return
        except Exception:
            await ctx.send(f'Прочти, но субреддита с именем {subreddit} не существует')
            return

        if post not in self.checked:
            self.checked.append(post)
            await ctx.send(post.url)
        else:
            await ctx.send('Подожди, пока что нет новых постов')

class Calculator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='calculate')
    async def calculate(self, ctx, *example):
        example = ''.join(list(example))
        if example == '':
            await ctx.send('Тебе стоит ввести пример после этой команды')
            return
        await ctx.send(eval(example.replace('^', '**').replace(':', '/')))

class Timer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='set_timer')
    async def timer(self, ctx, *context):
        try:
            context = list(filter(lambda x: x.isdigit(), list(context)))
            if len(context) != 2:
                raise Exception
            await sleep(60 * (int(context[0]) * 60 + int(context[1])))
            await ctx.send('Time X come!')
        except Exception:
            return

class Morphy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='numerals')
    async def numerals(self, ctx, w, n):
        await ctx.send(f'{int(n)} {pymorphy2.MorphAnalyzer().parse(w)[0].make_agree_with_number(int(n)).word}')

    @commands.command(name='alive')
    async def alive(self, ctx, w):
        w = pymorphy2.MorphAnalyzer().parse(w)[0]
        tag = str(w.tag).split(',')
        if tag[1] == 'anim':
            b = pymorphy2.MorphAnalyzer().parse('живой')[0].inflect({*tag[2].split(), tag[3]})
            await ctx.send(f'{w.word} {b.word}')
        else:
            b = pymorphy2.MorphAnalyzer().parse('живой')[0].inflect({*tag[2].split(), tag[3]})
            await ctx.send(f'{w.word} не {b.word}')

    @commands.command(name='noun')
    async def noun(self, ctx, w, pad, num):
        await ctx.send(f'{pymorphy2.MorphAnalyzer().parse(w)[0].inflect({pad, num}).word}')

    @commands.command(name='inf')
    async def inf(self, ctx, w):
        await ctx.send(f'{pymorphy2.MorphAnalyzer().parse(w)[0].normal_form}')

    @commands.command(name='morph')
    async def morph(self, ctx, w):
        w = pymorphy2.MorphAnalyzer().parse(w)[0]
        await ctx.send(f'{w.tag}\n{w.normal_form}')

class Translate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lang = "en|ru"
        self.headers = {
            "X-RapidAPI-Host": "translated-mymemory---translation-memory.p.rapidapi.com",
            "X-RapidAPI-Key": "71ca48a578mshc4181efc62ee37ap1493bejsn7bb28c430226"
        }

    @commands.command(name='text')
    async def text(self, ctx, *w):
        w = ' '.join(list(w))
        response = requests.request("GET", 'https://translated-mymemory---translation-memory.p.rapidapi.com/api/get',
                                    headers=self.headers, params={"langpair": self.lang, "q": w})
        await ctx.send(response.json()['responseData']['translatedText'])

    @commands.command(name='set_lang')
    async def set_lang(self, ctx, l):
        self.lang = l


if __name__ == '__main__':
    main()