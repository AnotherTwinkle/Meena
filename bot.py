import discord
from discord.ext import commands
import aiohttp
from config import token

import os
import time

import json

os.environ['JISHAKU_NO_UNDERSCORE'] = "True"
os.environ['JISHAKU_NO_DM_TRACEBACK'] = "True"

CONFIG = {
	"true" : {
		"NATIONAL_CAMP_GUILD_ID" : 1422151919023034400
	},
	"testing" : {
		"NATIONAL_CAMP_GUILD_ID" : 1422151919023034400
	}
}

class DataManager:
	def __init__(self, fp):
		self.fp = fp
		self.data = {}

		self.fetch()
	
	def fetch(self):
		with open(self.fp, 'r') as f:
			self.data = json.load(f)

	def commit(self):
		with open(self.fp, 'w') as f:
			json.dump(self.data, f, indent = 4)

	def __getitem__(self, key):
		return self.data[key]

	def __setitem__(self, key, value):
		self.data[key] = value
		self.commit()

	def __delitem__(self, key):
		del self.data[key]
		self.commit()

	def __contains__(self, key):
		return key in self.data


class Meena(commands.AutoShardedBot):
	def __init__(self, *options):
		super().__init__(intents= discord.Intents.all(), command_prefix= self._prefix_function)

	def _prefix_function(self, bot, message):
		prefixes= (
			"?",
			)

		return commands.when_mentioned_or(*prefixes)(bot, message)
	
	async def start(self, *args, **kwargs):
		self.session = aiohttp.ClientSession(loop= self.loop)
		self.CONFIG = CONFIG
		self.data = DataManager("data.json")
		await super().start(*args, **kwargs)

	async def close(self, *args, **kwargs):
		await self.session.close()
		print(f'[{round(time.time())}]: Shuting down...')
		await super().close(*args, **kwargs)

	async def on_ready(self):
		print(f'{self.user}: Ready. ({self.user.id})')
		print(f'{sum([guild.member_count for guild in self.guilds])} members.')
		extensions = ['jishaku', 'ext.core.admin', 'ext.core.meta', 'ext.camp.marathon']
		
		for ext in extensions:
			try:
				await self.load_extension(ext)
			except commands.ExtensionAlreadyLoaded:
				pass


	async def on_command_error(self, ctx, error):
		if hasattr(ctx.command,'on_error'):
			return

		error = getattr(error, 'original', error)
		ignored = (commands.CommandNotFound)

		if isinstance(error, ignored):
			pass
		
		elif isinstance(error, commands.NotOwner):
			await ctx.reply(content= 'Korbona ki korben')
		else:
			 raise error


if __name__ == "__main__":
	bot= Meena()
	bot.run(token)