import discord
from discord.ext import commands

import os
import traceback


EXT = ["cogs.recruit"]
token = os.environ.get("TOKEN","")

class DiscordBot(commands.Bot):
    def __init__(self,command_prefix):
        super().__init__(command_prefix)

        for cog in EXT:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()

    async def on_message(self,message):
        self.process_commands(message)
        
    async def on_ready(self):
        print("ready")
        
bot = DiscordBot("_")
bot.run(token)
