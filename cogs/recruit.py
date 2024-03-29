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
        
    summon_users = [ctx.author]
    bye_users = []
    
    stop_flag = False
        
    async def wait_time(seconds):
        await asyncio.sleep(seconds)
            
        if not stop_flag:
            await ctx.send("指定時刻になりました。")
            await msg.unpin()
        
    loop = asyncio.get_event_loop()
    tmp = (start_time - datetime.datetime.now()).total_seconds()
    loop.create_task(wait_time(tmp))
    
    l = ["\N{HEAVY LARGE CIRCLE}","\N{CROSS MARK}","\N{UPWARDS BLACK ARROW}\N{VARIATION SELECTOR-16}",
             "\N{DOWNWARDS BLACK ARROW}\N{VARIATION SELECTOR-16}","\N{WASTEBASKET}\N{VARIATION SELECTOR-16}"]
        
    def check(reaction_,user_):
        return (reaction_.message.id == msg.id) and (not user_.bot) and (str(reaction_.emoji) in l)
        
    while not ctx.bot.is_closed():
        reaction,user = await ctx.bot.wait_for("reaction_add",check=check)
        
        if start_time < datetime.datetime.now():
            return
        
        def create_embed():
            embed = msg.embeds[0]
            
            tmp = "\n".join([str(user) for user in summon_users])
            summon = tmp if tmp else "なし"
            
            tmp = "\n".join([str(user) for user in bye_users])
            bye = tmp if tmp else "なし"
            
            embed.set_field_at(3,name="参加者リスト",value=summon,inline=False)
            embed.set_field_at(4,name="不参加者リスト",value=bye,inline=False)
            
            return embed
                    
        if str(reaction.emoji) == "\N{HEAVY LARGE CIRCLE}":
            # 参加
            if user == ctx.author:
                await ctx.send(f"{user.name} はリーダーなので参加を取り消せません")
                
            elif user in summon_users:
                summon_users.remove(user)
                
                await msg.edit(embed=create_embed())
                await ctx.send(f"{user.name} が参加を取り消しました",delete_after=5.0)
                
            elif user in bye_users:
                bye_users.remove(user)
                summon_users.append(user)
                
                await msg.edit(embed=create_embed())
                await ctx.send(f"{user.name} が不参加から参加に変更しました",delete_after=5.0)
                
            else:
                summon_users.append(user)
                
                await msg.edit(embed=create_embed())
                await ctx.send(f"{user.name} が参加を表明しました（再度「〇」リアクションで取り消せます）",delete_after=5.0)
                
        if str(reaction.emoji) == "\N{CROSS MARK}":
            # 不参加
            if user == ctx.author:
                await ctx.send(f"{user.name} はリーダーなので不参加に変更できません",delete_after=5.0)
                
            elif user in bye_users:
                bye_users.remove(user)
                
                await msg.edit(embed=create_embed())
                await ctx.send(f"{user.name} が不参加を取り消しました",delete_after=5.0)
                
            elif user in summon_users:
                summon_users.remove(user)
                bye_users.append(user)
                
                await msg.edit(embed=create_embed())
                await ctx.send(f"{user.name} が参加から不参加に変更しました",delete_after=5.0)
                
            else:
                bye_users.append(user)
                
                await msg.edit(embed=create_embed())
                await ctx.send(f"{user.name} が不参加を表明しました（再度「×」リアクションで取り消せます）",delete_after=5.0)
            
        if (str(reaction.emoji) == "\N{UPWARDS BLACK ARROW}\N{VARIATION SELECTOR-16}") and (user == ctx.author):
            # 募集人数追加
            await ctx.send("募集人数を1人追加します。",delete_after=5.0)
                
            embed = msg.embeds[0]
                
            tmp = embed.fields[1].value
            embed.set_field_at(1,name="募集人数",value=f"{int(tmp) + 1}")
                
            await msg.edit(embed=embed)
            
        if (str(reaction.emoji) == "\N{DOWNWARDS BLACK ARROW}\N{VARIATION SELECTOR-16}") and (user == ctx.author):
            # 募集人数削減
            await ctx.send("募集人数を1人削減します。",delete_after=5.0)
            embed = msg.embeds[0]
                
            tmp = embed.fields[1].value
            
            if int(tmp) == 0:
                await ctx.send("0人以下に減らすことはできません。",delete_after=5.0)
                continue
                
            embed.set_field_at(1,name="募集人数",value=f"{int(tmp) - 1}")
                
            await msg.edit(embed=embed)
            
        if (str(reaction.emoji) == "\N{WASTEBASKET}\N{VARIATION SELECTOR-16}") and (user == ctx.author):
            # 募集を削除
            await ctx.send("募集を終了します。",delete_after = 5.0)
            await msg.delete()
                
            stop_flag = True
                
            return
        
        await reaction.remove(user)
        
        for emoji in l:
            await msg.add_reaction(emoji)
        

class RecruitCog(commands.Cog,name="募集"):
    def __init__(self,bot):
        self.bot = bot      
                

    @commands.command(aliases=["bosyu"])
    async def recruit(self,ctx,members_num:int,*,start_time_and_comment):
        """
        募集を行います。
        受け取る引数はメンバー数、開始時刻です。
        開始時刻には `年/月/日/時/分`を設定できますが、省略した部分についてはその時刻のものが使用されます。
        あまりにも現在時刻とかけ離れた予約は正常な実行が保証されません。
        
        5人をその日の17時00分に募集する場合。
        `_recruit 5 17時0分`
        
        3人をその月の9日の8時00分に募集する場合。
        `_recruit 3 9日8時0分`
        
        5人をその日の17時00分に募集し、`対戦相手募集`とコメントをつける場合。
        `_recruit 5 17時0分 対戦相手募集`
        """
        
        parsed = parser(start_time_and_comment)
        tmp = " ".join(start_time_and_comment.split(" ")[1:]) 
        comment = tmp if tmp else "なし"
        
        if not parsed:
            await ctx.send("指定された時刻情報が不正です。")
            return
    
        await ctx.send("募集を取り付けました。",delete_after=5.0)
        
        embed = discord.Embed(title=f"{ctx.author} の募集")
        
        time_content = parsed.strftime("%Y年 %m月 %d 日 %H時%M分")
        
        embed.add_field(name="コメント",value=comment,inline=False)
        embed.add_field(name="募集人数",value=members_num,inline=False)
        embed.add_field(name="開始時刻",value=time_content,inline=False)
        embed.add_field(name="参加者リスト",value=ctx.author,inline=False)
        embed.add_field(name="不参加者リスト",value="なし",inline=False)
        
        message = await ctx.send("@everyone",embed=embed)
        
        l = ["\N{HEAVY LARGE CIRCLE}","\N{CROSS MARK}","\N{UPWARDS BLACK ARROW}\N{VARIATION SELECTOR-16}",
             "\N{DOWNWARDS BLACK ARROW}\N{VARIATION SELECTOR-16}","\N{WASTEBASKET}\N{VARIATION SELECTOR-16}"]
        
        await message.pin()
        
        for emoji in l:
            await message.add_reaction(emoji)
        
        await wait_react(ctx,message,parsed)

        
def setup(bot):
    bot.add_cog(RecruitCog(bot))
