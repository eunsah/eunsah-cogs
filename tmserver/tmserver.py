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
        updatecheck = updatecheck[server]['update']
        if (time() - updatecheck) > 30:
            plswait = await ctx.send('重新刷新伺服器資料...')
            await self.server_refresh(server)
            await plswait.delete()

        pu = dict()
        async with self.config.TMServer() as tms:
            pu = tms[server]
        pu.pop('update')

        return pu

    def make_embed(self, title: str, content: dict):

        info = {
            'Aria':     ['艾麗亞'   ,'0x5151A2', 'https://i.imgur.com/4Zpashj.png'],
            'Freud':    ['普力特'   ,'0xFF8000', 'https://i.imgur.com/aoiB4fo.png'],
            'Ryude':    ['琉德'     ,'0x004B97', 'https://i.imgur.com/xabVrds.png'],
            'Rhinne':   ['優伊娜'   ,'0x844200', 'https://i.imgur.com/4jNiuGA.png'],
            'Alicia':   ['愛麗西亞' ,'0x00DB00', 'https://i.imgur.com/rdzMel4.png'],
            'Orca':     ['殺人鯨'   ,'0x00FFFF', 'https://i.imgur.com/TMqMsaN.png'],
            'Reboot':   ['Reboot'   ,'0x336666', 'https://i.imgur.com/bQra31g.png']
        }
        try:
            # exception for reboot
            market = content['拍賣']
        except KeyError:
            market = '沒有拍賣'

        int_val = int(info[title][1], 16)
        e = discord.Embed(
            title = info[title][0],
            description = f'''**副本**：{content['副本']}        **商城**：{content['商城']}        **拍賣**：{market}''',
            color = int_val
            )
        e.set_thumbnail(url=info[title][2])

        e.add_field(name='頻道列表', value=f'''**CH.01**：{content['CH.01']}\n**CH.02**：{content['CH.02']}\n**CH.03**：{content['CH.03']}\n**CH.04**：{content['CH.04']}\n**CH.05**：{content['CH.05']}\n**CH.06**：{content['CH.06']}\n**CH.07**：{content['CH.07']}\n**CH.08**：{content['CH.08']}\n**CH.09**：{content['CH.09']}\n**CH.10**：{content['CH.10']}\n''', inline=True)
        e.add_field(name='\a',      value=f'''**CH.11**：{content['CH.11']}\n**CH.12**：{content['CH.12']}\n**CH.13**：{content['CH.13']}\n**CH.14**：{content['CH.14']}\n**CH.15**：{content['CH.15']}\n**CH.16**：{content['CH.16']}\n**CH.17**：{content['CH.17']}\n**CH.18**：{content['CH.18']}\n**CH.19**：{content['CH.19']}\n**CH.20**：{content['CH.20']}\n''', inline=True)
        e.add_field(name='\a',      value=f'''**CH.21**：{content['CH.21']}\n**CH.22**：{content['CH.22']}\n**CH.23**：{content['CH.23']}\n**CH.24**：{content['CH.24']}\n**CH.25**：{content['CH.25']}\n**CH.26**：{content['CH.26']}\n**CH.27**：{content['CH.27']}\n**CH.28**：{content['CH.28']}\n**CH.29**：{content['CH.29']}\n**CH.30**：{content['CH.30']}\n''', inline=True)
        return e

    @commands.group(name='tmserver', aliases=['tms'])
    async def commands_tmserver(self, ctx):
        '''
            各伺服器列表
            可以使用 [p]tmserver <伺服器> 或是 [p]tms <伺服器>
        '''
        pass

    @commands_tmserver.command(name='Public', aliases=['pu'])
    async def tms_public(self, ctx):
        '''
        '''
        pu = await self.latency_dict(ctx, 'Public')

        e = discord.Embed(title = '公用')

        e.add_field(name='登入伺服器', value=f'''**登入1**：{pu['登入1']:>8s}\n**登入2**：{pu['登入2']:>8s}''', inline=True)
        # e.add_field(name='登入伺服器', value=f'''**登入1**：{pu['登入1']:>8s}\n**登入4**：{pu['登入4']:>8s}\n**測試**：{pu['登入測試']:>8s}''', inline=True)
        e.add_field(name='\a',       value=f'''**登入3**：{pu['登入3']:>8s}\n**登入4**：{pu['登入4']:>8s}''', inline=True)
        e.add_field(name='\a',       value=f'''**登入5**：{pu['登入5']:>8s}\n**登入6**：{pu['登入6']:>8s}''', inline=True)

        e.add_field(name='跨服伺服器', value=f'''**跨服1**：{pu['跨服1']:>8s}\n**跨服4**：{pu['跨服4']:>8s}''', inline=True)
        e.add_field(name='\a', value=f'''**跨服2**：{pu['跨服2']:>8s}\n**跨服5**：{pu['跨服5']:>8s}''', inline=True)
        e.add_field(name='\a', value=f'''**跨服3**：{pu['跨服3']:>8s}''', inline=True)

        await ctx.send(embed = e)

    @commands_tmserver.command(name='Aria', aliases=['ar', 'w0'])
    async def tms_aria(self, ctx):
        '''
            艾麗亞 伺服器
        '''
        await ctx.send(embed = self.make_embed('Aria', await self.latency_dict(ctx, 'Aria')))

    @commands_tmserver.command(name='Freud', aliases=['fr', 'w1'])
    async def tms_freud(self, ctx):
        '''
            普力特 伺服器
        '''
        await ctx.send(embed = self.make_embed('Freud', await self.latency_dict(ctx, 'Freud')))

    @commands_tmserver.command(name='Ryude', aliases=['ry', 'w2'])
    async def tms_ryude(self, ctx):
        '''
            琉德 伺服器
        '''
        await ctx.send(embed = self.make_embed('Ryude', await self.latency_dict(ctx, 'Ryude')))

    @commands_tmserver.command(name='Rhinne', aliases=['rh', 'w3'])
    async def tms_rhinne(self, ctx):
        '''
            優伊娜 伺服器
        '''
        await ctx.send(embed = self.make_embed('Rhinne', await self.latency_dict(ctx, 'Rhinne')))

    @commands_tmserver.command(name='Alicia', aliases=['al', 'ii', 'w4'])
    async def tms_alicia(self, ctx):
        '''
            愛麗西亞 伺服器
        '''
        await ctx.send(embed = self.make_embed('Alicia', await self.latency_dict(ctx, 'Alicia')))

    @commands_tmserver.command(name='Orca', aliases=['or', 'w6'])
    async def tms_orca(self, ctx):
        '''
            殺人鯨 伺服器
        '''
        await ctx.send(embed = self.make_embed('Orca ', await self.latency_dict(ctx, 'Orca')))

    @commands_tmserver.command(name='Reboot', aliases=['rb', 'w45'])
    async def tms_reboot(self, ctx):
        '''
            Reboot 伺服器
        '''
        await ctx.send(embed = self.make_embed('Reboot', await self.latency_dict(ctx, 'Reboot')))

    @commands_tmserver.command(name='check', aliases=['c'])
    async def tms_check(self, ctx, server: str, channel: int):
        '''
            確認伺服器單一頻道，準確度較高
            使用方式：[p]tms check <伺服器> <頻道>
        '''
        if server not in ['Aria', 'Freud', 'Ryude', 'Rhinne', 'Alicia', 'Orca', 'Reboot']:
            await ctx.help()
            return
        if channel not in range(31):
            await ctx.help()
            return

        port = self.server_ip[server][f'CH.{str(channel).zfill(2)}'].split(':')
        host = '.'.join([ip_head, port[0]])
        port = port[1]

        latency = []
        for i in range(10):
            await asyncio.sleep(1)
            latency.append(self.latency_point(host=host, port=port))

        try:
            latency = sum(latency)/10
            await ctx.send(f'{ctx.author.mention}該頻道的延遲為：{round(latency, 2)}ms')
            return
        except TypeError:
            await ctx.send(f'{ctx.author.mention}該頻道的延遲炸了：{latency}')


