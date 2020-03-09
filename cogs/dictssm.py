from discord.ext import commands
import discord
import ast
import random

class DictSSMCog(commands.Cog,name="SSーM"):
    def __init__(self, bot):
        self.bot = bot
       
    @commands.Cog.listener()
    async def on_ready(self):
        CH_ID = 606803266218491925
        CH = self.bot.get_channel(CH_ID)
        self.bot.messages = await CH.history(limit=None).flatten()
        
    @commands.command(aliases=["秘情報"])
    async def secret(self,ctx):
        """
        「SSーM㊙情報」チャンネルから㊙情報をランダムで返信します。
        
        https://discord.gg/XYMZkM2 に投稿することで追加できます。
        """
        CH_ID = 606803266218491925
        CH = self.bot.get_channel(CH_ID)
        secret_emoji = "\N{CIRCLED IDEOGRAPH SECRET}\N{VARIATION SELECTOR-16}"
        
        if not self.bot.messages:
            self.bot.messages = await CH.history(limit=None).flatten()
        else:
            tmp = self.bot.messages[-1]
            self.bot.messages += await CH.history(limit=None,after=tmp.created_at).flatten()
        secret_msgs = [msg for msg in self.bot.messages if f"{secret_emoji}情報\n" in msg.content]
        
        while True:
            tmp = random.choice(secret_msgs)
            content = tmp.content.split("\n")
            if len(content) <= 1:
                # 本文が含まれていない
                continue
            embed = discord.Embed(title=content[0],description="\n".join(content[1:]),color=0x00ff00)
            embed.set_author(name=tmp.author.name,icon_url=tmp.author.avatar_url_as(format="png"))
            await ctx.send(embed=embed)
            break
        
    '''
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
    '''
        
def setup(bot):
    bot.add_cog(DictSSMCog(bot))
