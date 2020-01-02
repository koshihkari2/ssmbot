import discord
from discord.ext import commands

def open_message(message):
    """
    メッセージを展開し、作成した埋め込みに各情報を添付し返す関数
    """

    embed = discord.Embed(title=message.content,description=f"[メッセージリンク]({message.jump_url})",color=0x7fbfff)

    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url) #メッセージ送信者
    embed.set_footer(text=message.guild.name, icon_url=message.guild.icon_url) #メッセージのあるサーバー
    embed.timestamp = message.created_at #メッセージの投稿時間

    if message.attachments:
        embed.set_image(url=message.attachments[0].url) #もし画像があれば、最初の画像を添付する
    return embed

class OpenLink(commands.Cog,name="リンク展開"):
    def __init__(self,bot):
        self.bot = bot
        
    @commands.command(name="open")
    async def open_(self,ctx,*,message):
        
        url_re = r"https://discordapp.com/channels/(\d{18})/(\d{18})/(\d{18})"
        url_list  = re.findall(url_re,message.content)
    
        for url in url_list:
            guild_id,channel_id,message_id = url
            channel = self.bot.get_channel(int(channel_id))

            if channel is not None:
                got_message = await channel.fetch_message(message_id)

                if got_message is not None:
                    await message.channel.send(embed=open_message(got_message))
        

    
def setup(bot):
    bot.add_cog(OpenLink(bot))
