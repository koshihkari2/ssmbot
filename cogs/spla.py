import discord
from discord.ext import commands
import aiohttp

import datetime
import random
import numpy as np

class Spla(commands.Cog,name="スプラトゥーン"):
    def __init__(self,bot):
        self.bot = bot
        
    @commands.command()
    async def stage(self,ctx,hour=None):
        """
        スプラトゥーン2の現在のステージ情報を取得します。
        hour引数には取得したい時刻を入れます（省略可能）
        
        現在のステージ情報を取得
        `_stage`
        
        8時のステージ情報を取得
        `_stage 8`
        """
    
        target = datetime.datetime.now().replace(minute=0,second=0,microsecond=0)
        
        if hour is not None:
            hour = int(hour)
            print(hour)
            if hour < target.hour:
                # もし、指定したい時刻が現在時刻より前だったら、一日足す
                target = target.replace(day=target.day+1)
            target = target.replace(hour=hour - (not hour%2))
        else:
            # もし、引数なしで呼び出されたら現在のステージ情報を取得
            rules = ["regular","gachi","league"]
            now_rules = []
            
            url = "https://spla2.yuu26.com/"
            stages = []
            session = aiohttp.ClientSession() #セッションを使いまわす
            
            for rule in rules:
                async with session.get(f"{url}{rule}/now") as r:
                    if r.status != 200:
                        await ctx.send("情報の取得に失敗しました。")
                        return
                    data = await r.json()
                stages.append(data["result"][0]["maps"])
                
                if rule == "gachi" or rule == "league":
                    now_rules.append(data["result"][0]["rule"])
                    
            await session.close()

            content = "__★ナワバリバトルのステージ情報★__\n"
            content += "・**" + "**\n・**".join(stages[0]) + "**\n\n"
            content += f"__★ガチマッチのステージ情報（{now_rules[0]}）★__\n"
            content += "・**" + "**\n・**".join(stages[1]) + "**\n\n"
            content += f"__★リーグマッチのステージ情報（{now_rules[1]}）★__\n"
            content += "・**" + "**\n・**".join(stages[2]) + "**\n\n"
            
            await ctx.send(content)
            return
            
        target_str = target.strftime("%Y-%m-%dT%H:%M:%S")
        url = "https://spla2.yuu26.com/schedule"
        
        headers = {"User-Agent":"個人用bot [tw:@shidoro_onn]"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url,headers=headers) as r:
                if r.status != 200:
                    await ctx.send("情報の取得に失敗しました。")
                    return
                data = await r.json()
                
        print(target_str)
                
        regular_data = data["result"]["regular"]
        regular_stages = [datum["maps"] for datum in regular_data if datum["start"] == target_str][0]
        
        gachi_data = data["result"]["gachi"]
        gachi_stages = [datum["maps"] for datum in gachi_data if datum["start"] == target_str][0]
        gachi_rule = [datum["rule"] for datum in gachi_data if datum["start"] == target_str][0]
        
        league_data = data["result"]["league"]
        league_stages = [datum["maps"] for datum in league_data if datum["start"] == target_str][0]
        league_rule = [datum["rule"] for datum in league_data if datum["start"] == target_str][0]
        
        content = "__★ナワバリバトルのステージ情報★__\n"
        content += f"・**{regular_stages[0]}**\n"
        content += f"・**{regular_stages[1]}**\n\n"
        
        content += f"__★ガチマッチのステージ情報（{gachi_rule}）★__\n"
        content += f"・**{gachi_stages[0]}**\n"
        content += f"・**{gachi_stages[1]}**\n\n"
        
        content += f"__★リーグマッチのステージ情報（{league_rule}）★__\n"
        content += f"・**{league_stages[0]}**\n"
        content += f"・**{league_stages[1]}**\n\n"
        
        await ctx.send(content)
        
    @commands.command()
    async def bukiru(self,ctx,mode=""):
        """
        武器ルーレットを行います。
        """
        bukis = []
        with open("src/bukis.txt") as f:
            bukis = f.readlines()
        members = [ctx.author]
        if mode == "ch" and ctx.author.voice is not None:
            members = ctx.author.voice.channel.members
        content = "**ルーレットの結果**\n"
        for member in members:
            content += f"{member}：{random.choice(bukis)}"
        
        await ctx.send(content)
        
    @commands.command()
    async def team(self,ctx,channel_name):
        """
        ランダムでチーム分けを行い、コマンド実行者のボイスチャンネルと、指定された名前のボイスチャンネルとにメンバーを振り分けます。
        引数には割り当て先のボイスチャンネル名を入力します。
        """
        if ctx.author.voice is None or ctx.author.voice.channel is None:
            await ctx.send("あなたが参加しているボイスチャンネルを取得できませんでした。")
            
        channel = discord.utils.get(ctx.guild.voice_channels,name=channel_name)
        if channel is None:
            await ctx.send("指定されたボイスチャンネルが見つかりませんでした。")
            return
        
        members = [member for member in ctx.author.voice.channel.members + channel.members if not member.bot]
        channels = [ctx.author.voice.channel,channel]
        random.shuffle(members)
        tmp = np.array_split(members,2)
        reply = "**チーム分けの結果：**"
        nl = "\n"
        
        for i,array in enumerate(tmp):
            members_name = [member.name for member in list(array)]
            reply += f"チーム{i+1} ： ```{nl.join(members_name)}```{nl}"
            
            for member in list(array):
                await member.move_to(channels[i])
        
        await ctx.send(reply)
        
def setup(bot):
    bot.add_cog(Spla(bot))
