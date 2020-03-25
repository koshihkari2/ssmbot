from discord.ext import commands
import discord
from googleapiclient.discovery import build

import os
import asyncio
import json

def getService():
    service = build("customsearch", "v1",developerKey=os.environ['API_KEY'])
    return service

class SearchCog(commands.Cog,name="画像検索"):
    def __init__(self,bot):
        self.bot = bot
    @commands.command(aliases=["im"])
    async def image(self,ctx,*,search_word):
        """
        指定されたキーワードでGoogleの画像検索を行い結果を表示します。
        """
        service = getService()
        startIndex = 1
        page_number = 0
        img_list = []
    
        response = service.cse().list(q=search_word,cx=os.environ['CSE_ID'],lr='lang_ja',
                                     searchType='image',start=startIndex*10+1).execute()
        if len(response['items']) > 0:
            for i in response['items']:
                img_list.append(i['link'])

        embed = discord.Embed(title=f"{search_word} の検索結果",color=0x00ffff)
        embed.set_image(url=img_list[page_number])
        embed.set_footer(text=f"{len(img_list)} ページ中 {page_number + 1} ページを参照中")
        message = await ctx.send(embed=embed)

        def check(m):
            return m.content in ["n","N","e","b"] and m.author == ctx.author and m.channel == ctx.channel

        while not self.bot.is_closed():
            try:
                new_msg = await self.bot.wait_for("message",check=check,timeout=20.0)
            except asyncio.TimeoutError:
                await message.edit(content="ページ変更を終了しました。")
                return
            else:
                if new_msg.content == "e":
                    await message.edit(content="ページ変更を終了しました。")
                    return
                if new_msg.content in ["n","N"]:
                    page_number += 1
                    if page_number == len(img_list):
                        # 最後まで参照したら
                        startIndex += 1
                        response = service.cse().list(q=search_word,cx=os.environ['CSE_ID'],
                                                      lr='lang_ja',searchType='image',start=startIndex*10+1).execute()
                        if len(response['items']) > 0:
                            for i in response['items']:
                                img_list.append(i['link'])
                    if page_number == len(img_list):
                        page_number -= 1
    
                    embed.set_image(url=img_list[page_number])
                    embed.set_footer(text=f"{len(img_list)} ページ中 {page_number} ページを参照中")
                    await message.edit(embed=embed)
                    await new_msg.delete()
                if new_msg.content == "e":
                    page_number -= 1
                    if page_number == -1:
                        page_number += 1
                    embed.set_image(url=img_list[page_number])
                    embed.set_footer(text=f"{len(img_list)} ページ中 {page_number} ページを参照中")
                    await message.edit(embed=embed)
                    await new_msg.delete()
                    
def setup(bot):
    bot.add_cog(SearchCog(bot))
