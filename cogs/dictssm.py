from discord.ext import commands
import discord
import ast

class DictSSMCog(commands.Cog,name="辞書"):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel()
        msg = await channel.fetch_message()
        tmp = ast.literal_eval(msg.content)
        
        self.pages = [discord.Embed(title=elem.split("\n")[0],description=elem.split("\n")[1:]) for elem in tmp]
        txt = [f"{i+1} : {elem.split('\n')[0]}" for i,elem in enumerate(tmp)]
        self.pages.insert(0,discord.Embed(title="辞書",description="```"+"\n".join(txt)+"```"))
        
    def return_embed(self,page_num=0):
        return self.pages[page_num]
        
    @commands.group(name="dict")
    async def dict_(self,ctx):
        if ctx.invoked_subcommand is not None:
            # もし、サブコマンドを指定されているなら処理しない
            return
            
    @dict_.command()
    async def page(self,ctx,page_num=1):
        if page_num <= 0 or len(self.pages) < page_num:
            await ctx.send(f"ページ数の有効範囲は {1} ～ {len(self.pages)} です。")
        await ctx.send(embed=self.pages[page_num])
        
def setup(bot):
    bot.add_cog(DictSSMCog(bot))
