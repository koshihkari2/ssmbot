import discord
from discord.ext import commands
from mee6_py_api import API

class MeeSix(commands.Cog,name="Mee6"):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self,message):
        mee6 = self.bot.get_user(159985870458322944)
        if message.content == "!levels" and mee6 in message.guild.members:
            api = API(message.guild.id)
            result = await api.levels.get_leaderboard_page(0)
            embed = discord.Embed(title=f"{message.guild.name} 詳細順位表 (Top25)")
            
            players = result["players"][:25]
            for i,player in enumerate(players):
                tmp = f"レベル：{player['level']}\nメッセージ数：{player['message_count']}\n経験値：{player['xp']}"
                embed.add_field(name=f"{player.username} ({i + 1} 位)",value=tmp)
                
            await message.channel.send(embed=embed)

def setup(bot):
    bot.add_cog(MeeSix(bot))
