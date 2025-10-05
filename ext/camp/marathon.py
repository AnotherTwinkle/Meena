import discord
from discord.ext import commands

import random 

class ProblemCommandFlags(commands.FlagConverter, delimiter = ' ', prefix = '-'):
	d : int

class Marathon(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	def get_thread_problem(self, thread_id):
		thread_id = str(thread_id)

		active = [(key, val)
				  for key, val in
				  self.bot.data['marathon']['problems'].items()
				  if key == thread_id
				  ]

		if len(active) == 0:
			return None

		return active[0][1]

	@commands.command(name = "problem")
	async def mark_problem(self, ctx, difficulty : int = 0, *, s : str = "Nothing yet"):
		if not isinstance(ctx.channel, discord.Thread) and 0:
			await ctx.send("এইটা তো থ্রেড না। থ্রেডের ভিতর মারা লাগবে এই কমান্ড। ")
			return

		prb = self.get_thread_problem(ctx.channel.id)

		if prb:
			if prb['active']:
				await ctx.send("এইহানে ইতিমধ্যেই একখানা প্রব্লেম চলিতেছে।")
			else:
				await ctx.send("এইহানে ইতিমধ্যেই একখানা প্রব্লেম হইয়া গেছে। আপনে অন্যখানে যান আপনার সমস্যা নিয়া।")
			return

		if difficulty == 0:
			await ctx.send("প্রব্লেমের ডিফিকাল্টি না দিলে পাব্লিক কইরে মজা পাইবো কি?")
			return

		entry = {
			"thread" : ctx.channel.id,
			"owner" : ctx.author.id,
			"difficulty" : difficulty,
			"solver" : None,
			"active" : True
		}

		self.bot.data['marathon']['problems'][str(ctx.channel.id)] = entry
		self.bot.data.commit()

		reference = ctx.message.reference
		if reference:
			reference = reference.resolved
			await reference.pin()

		await ctx.message.add_reaction("👌")

	@commands.command(name = "solved")
	async def solved(self, ctx, mem : discord.Member = None):

		prb = self.get_thread_problem(ctx.channel.id)

		if not prb:
			await ctx.send("এই থ্রেডে কোনো প্রব্লেম চলিতেছে না। ?problem এর মাধ্যমে নতুন প্রব্লেম শুরু করন যাইবো। ")
			return

		if not prb['active']:
			await ctx.send("এইখানে যে প্রব্লেম ছিলো তা কে জানি ইতিমধ্যে করিয়া ফেলাইছে। অহন আপনি অন্যখানে যান। ")
			return

		if prb['owner'] != ctx.author.id:
			await ctx.send("অন্যের প্রব্লেমের মালিকানা নিজে জাহির করার চেষ্টা করেন কেন?")
			return

		reference = ctx.message.reference
		reference_author = None

		if (reference):
			reference_author = reference.resolved.author

		if not mem and not reference_author:
			await ctx.send("কে সমাধান করিয়া ফালাইছে সেটা তো কন। ")
			return

		if mem and reference_author and mem.id != reference_author.id:
			await ctx.send("দুইজনকে একজনের কাজের ভুয়া ক্রেডিট দেয়া ভালো কাজ নহে। ")
			return

		solver = mem or reference_author

		# if solver.id == prb['owner']:
		# 	await ctx.send("নিজের প্রব্লেম নিজেই কইরা আমাকে ধোঁকা দেয়া যাইবো না। ")
		# 	return

		self.bot.data['marathon']['problems'][str(ctx.channel.id)]['active'] = False
		self.bot.data['marathon']['problems'][str(ctx.channel.id)]['solver'] = solver.id

		if str(solver.id) not in self.bot.data['marathon']['scores']:
			self.bot.data['marathon']['scores'][str(solver.id)] = prb['difficulty']
		else:
			self.bot.data['marathon']['scores'][str(solver.id)] += prb['difficulty']

		self.bot.data.commit()
		responses = [
			"ঠিকাছে।",
			"পারছে? ভালা তো।",
			"বুঝলাম।", 
			"এম্নে পড়ালেখা চালায় গেলে জীবনে কিছু একটা করা যাইবো।",
		]
		response_points_awarded = f"ওরে {self.bot.data['marathon']['problems'][str(ctx.channel.id)]['difficulty']} পয়েন্ট দিলাম।"
		await ctx.send(random.choice(responses) + " " + response_points_awarded)

		orig = ctx.channel.name
		await ctx.channel.edit(name = "[SOLVED] " + orig)

	@commands.command(name = 'cancel')
	async def cancel_problem(self, ctx):

		prb = self.get_thread_problem(ctx.channel.id)

		if not prb:
			await ctx.send("এই থ্রেডে কোনো প্রব্লেম চলিতেছে না। ?problem এর মাধ্যমে নতুন প্রব্লেম শুরু করন যাইবো। ")
			return

		if not prb['active']:
			await ctx.send("এইখানে যে প্রব্লেম ছিলো তা কে জানি ইতিমধ্যে করিয়া ফেলাইছে। অহন আপনি অন্যখানে যান। ")
			return

		if prb['owner'] != ctx.author.id:
			await ctx.send("অন্যের প্রব্লেমের মালিকানা নিজে জাহির করার চেষ্টা করেন কেন?")
			return

		del self.bot.data['marathon']['problems'][str(ctx.channel.id)]
		await ctx.send("ঠিকাছে। একখানা চলমান প্রব্লেম বন্ধ করা হইলো।")

	@commands.command(name = 'scores')
	async def send_scoreboard(self, ctx):
		scores = self.bot.data['marathon']['scores']

		s = ""
		for user_id_str, score in sorted(scores.items(), key = lambda m : m[1], reverse = True):
			s += f"{self.bot.get_user(int(user_id_str)).display_name} - {score}\n"

		await ctx.send(s)

	@commands.command(name = 'rm')
	async def reload_extension_temporary(self, ctx):
		await self.bot.reload_extension('ext.camp.marathon')
		await ctx.send("👌")

	@commands.command(name = "data")
	async def test_command(self, ctx):
		await ctx.send(self.bot.data.data)

async def setup(bot):
	await bot.add_cog(Marathon(bot))
