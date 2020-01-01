import discord
from discord.ext import commands
import aiohttp

class Spla(commands.Cog,name="Splatoon"):
    def __init__(self,bot):
        self.bot = bot
        
    @commands.command()
    async def stage(self,ctx,hour=None):
    
        target = datetime.datetime.now().replace(minute=0,second=0,microsecond=0)
        
        if hour is not None:
            target.replace(hour=hour - hour%2)
        else:
            target.replace(hour=target.hour - target.hour%2)
            
        target_str = target.strftime("%Y-%m-%dT%H:%M%S")
        url = ""
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status != 200:
                    await ctx.send("情報の取得に失敗しました。")
                    return
                data = await r.json()
                
        regular_data = data["result"]["regular"]
        regular_stages = [datum["maps"] for datum in regular_data if datum["start"] == target_str][0]
        
        gachi_data = data["result"]["gachi"]
        gachi_stages = [datum["maps"] for datum in gachi_data if datum["start"] == target_str][0]
        gachi_rule = [datum["rule"] for datum in gachi_data if datum["start"] == target_str][0]
        
        league_data = data["result"]["league"]
        gachi_stages = [datum["maps"] for datum in league_data if datum["start"] == target_str][0]
        gachi_rule = [datum["rule"] for datum in league_data if datum["start"] == target_str][0]
        
        content = "__★ナワバリバトルのステージ情報★__\n"
        content += f"・**{regular_stages[0]}**\n"
        content += f"・**{regular_stages[1]}**\n\n"
        
        content = f"__★ガチマッチのステージ情報（{gachi_rule}）★__\n"
        content += f"・**{gachi_stages[0]}**\n"
        content += f"・**{gachi_stages[1]}**\n\n"
        
        content = f"__★リーグマッチのステージ情報（{league_rule}）★__\n"
        content += f"・**{league_stages[0]}**\n"
        content += f"・**{league_stages[1]}**\n\n"
        
        await ctx.send(content)
        
def setup(bot):
    bot.add_cog(Spla(bot))
