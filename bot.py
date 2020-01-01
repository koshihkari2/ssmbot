import discord
from discord.ext import commands

import os
import traceback


EXT = ["cogs.recruit"]
token = os.environ.get("TOKEN","")

class JapaneseHelpCommand(commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__()
        self.commands_heading = "コマンド:"
        self.no_category = "未分類"
        self.command_attrs["help"] = "ヘルプコマンド"

    def get_ending_note(self):
        return ("各コマンドの説明: _help コマンド名\n各カテゴリの説明: _help カテゴリ名\n")

class DiscordBot(commands.Bot):
    def __init__(self,command_prefix,help_command):
        super().__init__(command_prefix,help_command)

        for cog in EXT:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()

    async def on_message(self,message):
        if self.user in message.mentions:
            await message.channel.send("`_help` でコマンド一覧が確認できます。")
        await self.process_commands(message)
        
    async def on_ready(self):
        print("ready")
        
bot = DiscordBot("_",help_command=JapaneseHelpCommand())
bot.run(token)
