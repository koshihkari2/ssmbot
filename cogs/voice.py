import discord
from discord.ext import commands

class VoiceCog(commands.Cog,name="音声関連"):
    def __init__(self,bot):
        self.bot = bot
        
    @commands.command()
    async def combine(self,ctx,channel_A_name,channel_B_name):
        """
        2つのボイスチャンネルの参加者を統合します。
        1つめに指定した名前のチャンネルに、2つめのチャンネルの参加者が自動で移動させられます。
        """
        channel_A = discord.utils.get(ctx.guild.voice_channels,name=channel_A_name)
        channel_B = discord.utils.get(ctx.guild.voice_channels,name=channel_B_name)
        
        if channel_A is None:
            await ctx.send("1つめに指定したチャンネルが見つかりませんでした。")
            return
        elif channel_B is None:
            await ctx.send("2つめに指定したチャンネルが見つかりませんでした。")
            return
            
        for member in channel_B.members:
            await member.move_to(channel_A)
        await ctx.send("参加者の移動が完了しました。")
                
def setup(bot):
    bot.add_cog(VoiceCog(bot))
