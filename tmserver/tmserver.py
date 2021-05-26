import os
import asyncio
# import logging
import discord
import json
from datetime import datetime
from typing import Optional
from redbot.core import commands, checks, Config
from time import time
from statistics import mean
import socket

# log = logging.getLogger('red.eunsahcogs.mapletcp')
ip_head = '202.80.104'
folder = 'TMS'
server_json = 'server_list.json'
dir_path = os.path.dirname(os.path.realpath(__file__))
AUTH_UID = 164900704526401545

class Tmserver(commands.Cog):
    '''
        Tmserver 楓之谷伺服器狀態列
    '''
    def __init__(self, bot):
        self.bot = bot
        with open(os.path.join(dir_path, folder, server_json)) as j:
            self.server_ip = json.load(j)
        self.config = Config.get_conf(self, identifier=int(str(AUTH_UID)+'002'),  force_registration=True)
        default_global = {
            'TMServer':{
                'Public':{
                    'update': 0,
                    '登入1': 0,
                    '登入2': 0,
                    '登入3': 0,
                    '登入4': 0,
                    '登入5': 0,
                    '登入6': 0,
                    '登入測試': 0,
                    '跨服1': 0,
                    '跨服2': 0,
                    '跨服3': 0,
                    '跨服4': 0,
                    '跨服5': 0},
                "Aria": {
                    "update": 0,
                    "副本": 0,
                    "商城": 0,
                    "拍賣": 0,
                    "CH.01": 0,
                    "CH.02": 0,
                    "CH.03": 0,
                    "CH.04": 0,
                    "CH.05": 0,
                    "CH.06": 0,
                    "CH.07": 0,
                    "CH.08": 0,
                    "CH.09": 0,
                    "CH.10": 0,
                    "CH.11": 0,
                    "CH.12": 0,
                    "CH.13": 0,
                    "CH.14": 0,
                    "CH.15": 0,
                    "CH.16": 0,
                    "CH.17": 0,
                    "CH.18": 0,
                    "CH.19": 0,
                    "CH.20": 0,
                    "CH.21": 0,
                    "CH.22": 0,
                    "CH.23": 0,
                    "CH.24": 0,
                    "CH.25": 0,
                    "CH.26": 0,
                    "CH.27": 0,
                    "CH.28": 0,
                    "CH.29": 0,
                    "CH.30": 0},
                "Freud": {
                    "update": 0,
                    "副本": 0,
                    "商城": 0,
                    "拍賣": 0,
                    "CH.01": 0,
                    "CH.02": 0,
                    "CH.03": 0,
                    "CH.04": 0,
                    "CH.05": 0,
                    "CH.06": 0,
                    "CH.07": 0,
                    "CH.08": 0,
                    "CH.09": 0,
                    "CH.10": 0,
                    "CH.11": 0,
                    "CH.12": 0,
                    "CH.13": 0,
                    "CH.14": 0,
                    "CH.15": 0,
                    "CH.16": 0,
                    "CH.17": 0,
                    "CH.18": 0,
                    "CH.19": 0,
                    "CH.20": 0,
                    "CH.21": 0,
                    "CH.22": 0,
                    "CH.23": 0,
                    "CH.24": 0,
                    "CH.25": 0,
                    "CH.26": 0,
                    "CH.27": 0,
                    "CH.28": 0,
                    "CH.29": 0,
                    "CH.30": 0},
                "Ryude": {
                    "update": 0,
                    "副本": 0,
                    "商城": 0,
                    "拍賣": 0,
                    "CH.01": 0,
                    "CH.02": 0,
                    "CH.03": 0,
                    "CH.04": 0,
                    "CH.05": 0,
                    "CH.06": 0,
                    "CH.07": 0,
                    "CH.08": 0,
                    "CH.09": 0,
                    "CH.10": 0,
                    "CH.11": 0,
                    "CH.12": 0,
                    "CH.13": 0,
                    "CH.14": 0,
                    "CH.15": 0,
                    "CH.16": 0,
                    "CH.17": 0,
                    "CH.18": 0,
                    "CH.19": 0,
                    "CH.20": 0,
                    "CH.21": 0,
                    "CH.22": 0,
                    "CH.23": 0,
                    "CH.24": 0,
                    "CH.25": 0,
                    "CH.26": 0,
                    "CH.27": 0,
                    "CH.28": 0,
                    "CH.29": 0,
                    "CH.30": 0},
                "Rhinne": {
                    "update": 0,
                    "副本": 0,
                    "商城": 0,
                    "拍賣": 0,
                    "CH.01": 0,
                    "CH.02": 0,
                    "CH.03": 0,
                    "CH.04": 0,
                    "CH.05": 0,
                    "CH.06": 0,
                    "CH.07": 0,
                    "CH.08": 0,
                    "CH.09": 0,
                    "CH.10": 0,
                    "CH.11": 0,
                    "CH.12": 0,
                    "CH.13": 0,
                    "CH.14": 0,
                    "CH.15": 0,
                    "CH.16": 0,
                    "CH.17": 0,
                    "CH.18": 0,
                    "CH.19": 0,
                    "CH.20": 0,
                    "CH.21": 0,
                    "CH.22": 0,
                    "CH.23": 0,
                    "CH.24": 0,
                    "CH.25": 0,
                    "CH.26": 0,
                    "CH.27": 0,
                    "CH.28": 0,
                    "CH.29": 0,
                    "CH.30": 0},
                "Alicia": {
                    "update": 0,
                    "副本": 0,
                    "商城": 0,
                    "拍賣": 0,
                    "CH.01": 0,
                    "CH.02": 0,
                    "CH.03": 0,
                    "CH.04": 0,
                    "CH.05": 0,
                    "CH.06": 0,
                    "CH.07": 0,
                    "CH.08": 0,
                    "CH.09": 0,
                    "CH.10": 0,
                    "CH.11": 0,
                    "CH.12": 0,
                    "CH.13": 0,
                    "CH.14": 0,
                    "CH.15": 0,
                    "CH.16": 0,
                    "CH.17": 0,
                    "CH.18": 0,
                    "CH.19": 0,
                    "CH.20": 0,
                    "CH.21": 0,
                    "CH.22": 0,
                    "CH.23": 0,
                    "CH.24": 0,
                    "CH.25": 0,
                    "CH.26": 0,
                    "CH.27": 0,
                    "CH.28": 0,
                    "CH.29": 0,
                    "CH.30": 0},
                "Orca": {
                    "update": 0,
                    "副本": 0,
                    "商城": 0,
                    "拍賣": 0,
                    "CH.01": 0,
                    "CH.02": 0,
                    "CH.03": 0,
                    "CH.04": 0,
                    "CH.05": 0,
                    "CH.06": 0,
                    "CH.07": 0,
                    "CH.08": 0,
                    "CH.09": 0,
                    "CH.10": 0,
                    "CH.11": 0,
                    "CH.12": 0,
                    "CH.13": 0,
                    "CH.14": 0,
                    "CH.15": 0,
                    "CH.16": 0,
                    "CH.17": 0,
                    "CH.18": 0,
                    "CH.19": 0,
                    "CH.20": 0,
                    "CH.21": 0,
                    "CH.22": 0,
                    "CH.23": 0,
                    "CH.24": 0,
                    "CH.25": 0,
                    "CH.26": 0,
                    "CH.27": 0,
                    "CH.28": 0,
                    "CH.29": 0,
                    "CH.30": 0},
                "Reboot": {
                    "update": 0,
                    "副本": 0,
                    "商城": 0,
                    "CH.01": 0,
                    "CH.02": 0,
                    "CH.03": 0,
                    "CH.04": 0,
                    "CH.05": 0,
                    "CH.06": 0,
                    "CH.07": 0,
                    "CH.08": 0,
                    "CH.09": 0,
                    "CH.10": 0,
                    "CH.11": 0,
                    "CH.12": 0,
                    "CH.13": 0,
                    "CH.14": 0,
                    "CH.15": 0,
                    "CH.16": 0,
                    "CH.17": 0,
                    "CH.18": 0,
                    "CH.19": 0,
                    "CH.20": 0,
                    "CH.21": 0,
                    "CH.22": 0,
                    "CH.23": 0,
                    "CH.24": 0,
                    "CH.25": 0,
                    "CH.26": 0,
                    "CH.27": 0,
                    "CH.28": 0,
                    "CH.29": 0,
                    "CH.30": 0
                }}}
        self.config.register_global(**default_global)

    def latency_point(self, host: str, port: str, timeout: float = 5) -> Optional[float]:
        '''
            credit to : https://github.com/dgzlopes/tcp-latency
        '''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s_start = time()

        try:
            s.connect((host, int(port)))
            s.shutdown(socket.SHUT_RD)

        except socket.timeout:
            return None
        except OSError:
            return None

        s_runtime = (time() - s_start) * 1000

        return round(float(s_runtime)-140, 2)

    async def server_refresh(self, server: str) -> None:
        async with self.config.TMServer() as tms:
            for key in tms[server]:
                if key != 'update':
                    port = self.server_ip[server][key].split(':')
                    host = '.'.join([ip_head, port[0]])
                    latency = self.latency_point(host=host, port=port[1])
                    tms[server][key] = f'{latency:.2f}ms' if latency != None else 'Timeout!'
            tms[server]['update'] = time()

    async def latency_dict(self, ctx: commands.Context, server: str) -> dict:
        updatecheck = await self.config.TMServer()
        updatecheck = updatecheck['Public']['update']
        if (time() - updatecheck) > 60:
            plswait = await ctx.send('Updating Serverinfo...')
            await self.server_refresh('Public')
            await plswait.delete()

        pu = dict()
        async with self.config.TMServer() as tms:
            pu = tms['Public']
        pu.pop('update')

        return pu

    def make_embed(self, title: str, content: dict):
        e = discord.Embed(
            title = title
        )


    @commands.group(name='tmserver', aliases=['tms'])
    async def commands_tmserver(self, ctx):
        '''
        '''
        pass

    @commands_tmserver.command(name='Public', aliases=['pu'])
    async def tms_public(self, ctx):
        '''
        '''
        pu = await self.latency_dict(ctx, 'Public')

        e = discord.Embed(
            title = '公用伺服器'
        )
        e.add_field(name='登入', value=rf'''**登入1** ({pu['登入1']}) \ \ \t **登入2** ({pu['登入2']}) \ \ \t **登入3** ({pu['登入3']}) \ \ \t\n **登入4** ({pu['登入4']}) \ \ \t **登入5** ({pu['登入5']}) \ \ \t **登入6** ({pu['登入6']}) \ \ \t\n **登入測試**( {pu['登入測試']}) \ \ \t ''', inline=False)
        e.add_field(name='跨服', value=rf'''**跨服1** ({pu['跨服1']}) \ \ \t **跨服2** ({pu['跨服2']}) \ \ \t **跨服3** ({pu['跨服3']}) \ \ \t\n **跨服4** ({pu['跨服4']}) \ \ \t **跨服5** ({pu['跨服5']}) \ \ \t ''', inline=False)

        await ctx.send(embed = e)



    # @commands_tmserver.command(name='Aria', aliases=['ar'])
    # async def tms_aria(self, ctx):


    # @commands_tmserver.command(name='Freud', aliases=['fr'])
    # async def tms_freud(self, ctx):


    # @commands_tmserver.command(name='Ryude', aliases=['ry'])
    # async def tms_ryude(self, ctx):


    # @commands_tmserver.command(name='Rhinne', aliases=['rh'])
    # async def tms_rhinne(self, ctx):


    # @commands_tmserver.command(name='Alicia', aliases=['al'])
    # async def tms_alicia(self, ctx):


    # @commands_tmserver.command(name='Orca', aliases=['or'])
    # async def tms_orca(self, ctx):


    # @commands_tmserver.command(name='Reboot', aliases=['rb'])
    # async def tms_reboot(self, ctx):


