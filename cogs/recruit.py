import discord
from discord.ext import commands

import re
import datetime
import asyncio

def parser(time_str):
    """
    時刻情報文字列 time_str を受け取り、省略された部分は現在の時刻を参照して、datetime.datetimeに変換する。
    """
    units = ["年","月","日","時","分"]
    data = []
        
    now = datetime.datetime.now()
    tmp = [now.year, now.month, now.day, now.hour, now.minute]
    now_data = [str(datum) for datum in tmp]
        
    for i,unit in enumerate(units):
        tmp = re.search(f"(\d+){unit}",time_str)
        if tmp:
           data.append(tmp.group(1))
        else:
           data.append(now_data[i])
    
    try:
        result = datetime.datetime.strptime("-".join(data),"%Y-%m-%d-%H-%M")
    except ValueError:
        result = None
            
    return result

async def wait_react(ctx,msg,start_time):
    """
    リアクションを待機する。
    """
        
    users = []
    stop_flag = False
        
    async def wait_time(seconds):
        await asyncio.sleep(seconds)
            
        if not stop_flag:
                await ctx.send("指定時刻になりました。")
        
    loop = asyncio.get_event_loop()
    tmp = (start_time - datetime.datetime.now()).total_seconds()
    loop.create_task(wait_time(tmp))
        
    def check(reation_,user_):
        return (reaction.message.id == msg.id) and (not user_.bot) and (str(reaction_.emoji) in [""])
        
    while not self.bot.is_closed():
        rection,user = await self.bot.wait_for("reaction_add",check=check)
            
        if str(reaction.emoji) == "\N{HEAVY LARGE CIRCLE}":
            # 参加
            if user in users:
                await ctx.send(f"{user.name} は既に参加しています",delete_after=5.0)
            else:
                await ctx.send(f"{user.name} が参加を表明しました（「×リアクションで取り消せます」）",delete_after=5.0)
                users.append(user)
                
        if str(reaction.emoji) == "\N{CROSS MARK}":
            # 取り消し
            if user not in users:
                await ctx.send(f"{user.name} はまだ参加していません",delete_after=5.0)
            else:
                await ctx.send(f"{user.name} が参加を取り消しました",delete_after=5.0)
                users.remove(user)
            
        if (str(reaction.emoji) == "\N{UPWARDS BLACK ARROW}") and (user == ctx.author):
            # 募集人数追加
            await ctx.send("募集人数を1人追加します。",delete_after=5.0)
                
            embed = msg.embeds[0]
                
            tmp = embed.fields[0].value
            embed.set_field_at(0,name="募集人数",value=tmp + 1)
                
            await msg.edit(embed=embed)
            
        if (str(reaction.emoji) == "\N{DOWNWARDS BLACK ARROW}") and (user == ctx.author):
            # 募集人数削減
            await ctx.send("募集人数を1人削減します。",delete_after=5.0)
            embed = msg.embeds[0]
                
            tmp = embed.fields[0].value
            embed.set_field_at(0,name="募集人数",value=tmp + 1)
                
            await msg.edit(embed=embed)
            
        if (str(reaction.emoji) == "\N{WASTEBASKET}") and (user == ctx.author):
            # 募集を削除
            await ctx.send("募集を終了します。",delete_after = 5.0)
            await msg.delete()
                
            stop_flag = True
                
            return

class RecruitCog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot      
                

    @commands.command(aliases=["bosyu"])
    async def recruit(self,ctx,members_num:int,*,start_time):
        """
        募集を行います。
        受け取る引数はメンバー数、開始時刻です。
        開始時刻には `年/月/日/時/分`を設定できますが、省略した部分についてはその時刻のものが使用されます。
        あまりにも現在時刻とかけ離れた予約は正常な実行が保証されません。
        
        5人をその日の17時00分に募集する場合。
        `_recruit 5 17時0分`
        
        3人をその月の9日の8時00分に募集する場合。
        `_recruit 3 9日8時0分`
        """
        
        parsed = parser(start_time)
        
        if not parsed:
            await ctx.send("指定された時刻情報が不正です。")
            return
    
        await ctx.send("募集を取り付けました。",delete_after=5.0)
        
        description = f"・募集人数 : **{members_num}**人\n・開始時刻 : **{start_time}**"
        
        embed = discord.Embed(title=f"{ctx.author} の募集",description=description)
        embed.add_field(name="募集人数",value=members_num)
        embed.add_field(name="開始時刻",value=start_time)
        
        message = await ctx.send(embed=embed)
        
        await wait_react(ctx,message,parsed)

        
def setup(bot):
    bot.add_cog(RecruitCog(bot))
