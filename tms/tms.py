""" Made to scarp update from TMS official website
"""
import os
import asyncio
import datetime
import logging

from bs4 import BeautifulSoup
from selenium import webdriver
from chromedriver_py import binary_path

import discord
from redbot.core import commands, checks, Config

log=logging.getLogger("red.eunsahcogs.tms")

class Tms(commands.Cog):
    """ Made to scarp update from TMS official website
    """
    default_config = {
        "gochannel":0,
        "announcements":[],
        }

    def __init__(self,bot):
        super().__init__()
        self.bot = bot
        self.config = Config.get_conf(self, identifier=164900704526401545)
        self.config.register_global(**self.default_config)
        self.bg_loop_task = None
        self.LOOP_INTERVAL = 30

        self.url = "https://tw.beanfun.com/MapleStory/"
        self.mainpage = "main?section=mBulletin"

        options = webdriver.chrome.options.Options()
        options.headless = True

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1200")
        self.driver = webdriver.Chrome(options=options, executable_path=binary_path)

    async def check_update(self):
        # load saved
        # print ("Preparing to load announcements")
        past_announcements = await self.config.announcements()
        new_announcements = list()

        # Driver read and setup
        self.driver.get(self.url+self.mainpage)
        soup = BeautifulSoup(self.driver.page_source, "lxml")
        mBulletin = soup.find_all("a", class_="mBulletin-items-link")

        # Iterate uBulletin
        for item in mBulletin:
            href = item['href']
            date = item.find(class_="mBulletin-items-date").text
            cate = item.find(class_="mBulletin-items-cate").text
            title = item.find(class_="mBulletin-items-title").text
            n = list([cate, title, date, self.url+href])
            # print (f"Found {n}")
            if n not in past_announcements:
                print ("red.eunsahcogs.tms: Found new announcement!")
                new_announcements.append(n)
                # print ("line 67", n)
            else:
                # print ("Announcement found in past, breaking...")
                break

        if len(new_announcements)>0:
            for a in new_announcements[::-1]:
                # print ("line 73", a)
                await self.tms_out(a)
                past_announcements.insert(0, a)

        await self.config.announcements.set(past_announcements)

    async def initialize(self):
        self._enable_bg_loop()

    def _enable_bg_loop(self):
        self.bg_loop_task = self.bot.loop.create_task(self.bg_loop())
        def error_handler(fut: asyncio.Future):
            try:
                fut.result()
            except asyncio.CancelledError:
                pass
            except Exception as exc:
                log.exception(
                    "Unexpected exception occurred in background loop of TMS: ",
                    exc_info=exc,
                )
                asyncio.create_task(
                    self.bot.send_to_owners(
                        "An unexpected exception occurred in the background loop of TMS.\n"
                        "Check your console or logs for details, and consider opening a bug report for this."
                    )
                )

        self.bg_loop_task.add_done_callback(error_handler)

    def cog_unload(self):
        if self.bg_loop_task:
            self.bg_loop_task.cancel()
        self.driver.quit()

    async def tms_out(self, item):
        data = await self.config.all()
        channel = data["gochannel"]
        channel = self.bot.get_channel(channel)

        if channel == 0:
            print ("channel unset, set a channel using [p]setchannel")
        else:
            e = discord.Embed(
                title = item[1],
                description=item[0]+ "消息 - " + item[2] ,
                url = item[3],
                timestamp = datetime.datetime.utcnow(),
                color=0x69D4C2,
            )
            # e.set_thumbnail(url="https://imgur.com/zCBuRCE.jpg")
            await channel.send(embed=e)

    async def bg_loop(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(self.LOOP_INTERVAL*2)
        while True:
            await self.check_update()
            await asyncio.sleep(self.LOOP_INTERVAL)

    @checks.is_owner()
    @commands.group()
    async def tms(self, ctx):
        pass

    @tms.command()
    async def setchannel(self, ctx, channel: discord.TextChannel = None):
        """ [p]setchannel [channel_name] to set channel, blank to unset
        """
        if channel:
            await self.config.gochannel.set(channel.id)
            await ctx.send(f"channel set to {channel.mention}")
        else:
            await self.config.gochannel.set(0)
            await ctx.send(f"channel unset, [p]unload tms")

    @checks.is_owner()
    @tms.command()
    async def updatenow(self, ctx):
        """Manually checks official websites announcements"""
        await self.check_update()
        await ctx.send("Up to date!")

    @checks.is_owner()
    @tms.command()
    async def clearcache(self, ctx):
        """Clears all cached announcements"""
        await self.config.announcements.set(list())
        await ctx.send("cleared past announcements.")
