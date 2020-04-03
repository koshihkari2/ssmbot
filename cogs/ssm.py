from discord.ext import commands
import discord
import ast
import random
import csv

class SSMCog(commands.Cog,name="SSーM"):
    """
    使用範囲がSSーMに限定される（と思われる）機能の実装。
    """
    def __init__(self, bot):
        self.bot = bot
       
    @commands.Cog.listener()
    async def on_ready(self):
        CH_ID = 693010352568270858
        CH = self.bot.get_channel(CH_ID)
        self.bot.messages = await CH.history(limit=None).flatten()
        
    @commands.command(aliases=["秘情報"])
    async def secret(self,ctx):
        """
        「SSーM㊙情報」チャンネルから㊙情報をランダムで返信します。
        
        https://discord.gg/XYMZkM2 に投稿することで追加できます。
        """
        CH_ID = 693010352568270858
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
            
    @commands.command()
    async def color(self,ctx,color_cord="ffffff"):
        """
        色のついた役職を付与します。
        
        _color ff0000
        
        と送信した場合、カラーコード「#FF0000」に対応する赤色の役職が付与されます。
        """
        color_rgb = int(color_cord,16)
        url = "https://www.colordic.org/"
        
        if color_rgb > 0xffffff:
            await ctx.send(f"正しいカラーコードが指定されませんでした。カラーコードについては {url} などを参照してください。")
            return
        
        before_roles = list(filter(lambda role:role.name.startswith("color:#"),ctx.guild.roles))
        if before_roles:
            # もし、既にcolorコマンドによって何らかの色を取得していれば、それを剥奪する
            await ctx.author.remove_roles(*before_roles,reason="colorコマンド実行に伴う剥奪。")
            
            for role in before_roles:
                if len(role.members) == 0:
                    await role.delete(reason="delcolorコマンドの実行に伴いこの役職を持つメンバー数が0になったため自動削除。")
        
        role_name = f"color:#{color_cord.upper()}"
        new_role = discord.utils.get(ctx.guild.roles,name=role_name)
        
        if new_role is None:
            # もし、まだその色の役職が作成されていなければ、作成する
            new_role = await ctx.guild.create_role(name=role_name,colour=discord.Colour(color_rgb),
                                                   mentionable=False,reason="colorコマンドによる自動生成。")
        
        await ctx.author.add_roles(new_role,reason="colorコマンド実行による自動付与。")
        await ctx.send(f"カラーコード `#{role_name}` の役職を付与しました。delcolorコマンドによってこの役職を剥奪できます。")
        
    @commands.command()
    async def delcolor(self,ctx):
        """
        既にcolorコマンドなどにより色のついた役職が付与されている場合、それを剥奪します。
        """
        roles = list(filter(lambda role:role.name.startswith("color:#"),ctx.author.roles))
        
        if not roles:
            await ctx.send("`color:#カラーコード` の形式の名前の役職があなたには付与されていません。")
            return
        await ctx.author.remove_roles(*roles,reason="delcolorコマンドによる剥奪。")
        
        for role in roles:
            if len(role.members) == 0:
                await role.delete(reason="delcolorコマンドの実行に伴いこの役職を持つメンバー数が0になったため自動削除。")
        await ctx.send("役職の剥奪を完了しました。")
        
    @commands.command(aliases=["randao"])
    async def randomaoao(self,ctx):
        """
        ランダム蒼aoします。
        """
        with open("src/aoaos.csv") as f:
            reader = csv.reader(f)
            elems = [row for row in reader]
            elem = random.choice(elems)
            embed = discord.Embed(title="randomAoao",description=f"画像内容：{elem[0]}",color=0x00ff00)
            embed.set_image(url=elem[1])
            await ctx.send(embed=embed)
                        
def setup(bot):
    bot.add_cog(SSMCog(bot))
