import discord
from discord.ext import commands
import random
from random import randint
import asyncio
import os
import ast


def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


class _util(commands.Cog):
    """Utility commands to get help, stats, links and more"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Get help with any of my commands", usage="s!help")
    async def help(self, ctx):
        embed = discord.Embed()
        embed.set_author(name='HLL Scoreboard - Help', icon_url=ctx.bot.user.avatar_url, url='https://github.com/timraay/HLLScoreboard')
        oauth = discord.utils.oauth_url(self.bot.user.id, permissions=discord.Permissions(permissions=8))
        embed.description = f"Hello, I am HLL Scoreboard! I display live statistics from ongoing Hell Let Loose matches directly into your server.\n\nFor questions, feedback, bugs, and source code [visit my Github page](https://github.com/timraay/HLLScoreboard). To invite me, [click here]({oauth})."
        embed.add_field(name='✏️ `s!create`', value='Create a new scoreboard')
        embed.add_field(name='📄 `s!list`', value='List all scoreboards')
        embed.add_field(name='📦 `s!invite`', value='Generate my invite link')
        embed.add_field(name='🔧 `s!edit <message> <option>`', value='Edit a property of an existing scoreboard')
        embed.add_field(name='🗑️ `s!delete <message>`', value='Get rid of an existing scoreboard')
        embed.set_footer(text='By Abusify - Made with love ❤️')
        await ctx.send(embed=embed)

    @commands.command()
    async def invite(self, ctx):
        oauth = discord.utils.oauth_url(self.bot.user.id, permissions=discord.Permissions(permissions=8))
        embed = discord.Embed(description=f"[☺️ Click here for an invite link!]({oauth})")
        await ctx.send(embed=embed)
        
    @commands.command(description="View my current latency", usage="r!ping")
    async def ping(self, ctx):
        latency = self.bot.latency * 1000
        color = discord.Color.dark_green()
        if latency > 150: color = discord.Color.green()
        if latency > 200: color = discord.Color.gold()
        if latency > 300: color = discord.Color.orange()
        if latency > 500: color = discord.Color.red()
        if latency > 1000: color = discord.Color(1)
        embed = discord.Embed(description=f'🏓 Pong! {round(latency, 1)}ms', color=color)
        await ctx.send(embed=embed)


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.content in [f'<@!{self.bot.user.id}>', f'<@{self.bot.user.id}>']:
            await message.channel.send('Hello, I am **HLL Scoreboard** 👋\nFor more info, see `s!help`')


    @commands.command(description="Evaluate a python variable or expression", usage="s!eval <cmd>", hidden=True)
    @commands.is_owner()
    async def eval(self, ctx, *, cmd):
        """Evaluates input.
        Input is interpreted as newline seperated statements.
        If the last statement is an expression, that is the return value.
        Usable globals:
        - `bot`: the bot instance
        - `discord`: the discord module
        - `commands`: the discord.ext.commands module
        - `ctx`: the invokation context
        - `__import__`: the builtin `__import__` function
        Such that `>eval 1 + 1` gives `2` as the result.
        The following invokation will cause the bot to send the text '9'
        to the channel of invokation and return '3' as the result of evaluating
        >eval ```
        a = 1 + 2
        b = a * 2
        await ctx.send(a + b)
        a
        ```
        """
        fn_name = "_eval_expr"

        cmd = cmd.strip("` ")
        if cmd.startswith("py"): cmd = cmd.replace("py", "", 1)

        # add a layer of indentation
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

        # wrap in async def body
        body = f"async def {fn_name}():\n{cmd}"

        parsed = ast.parse(body)
        body = parsed.body[0].body

        insert_returns(body)

        env = {
            'self': self,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            '__import__': __import__
        }
        exec(compile(parsed, filename="<ast>", mode="exec"), env)

        result = (await eval(f"{fn_name}()", env))
        try:
            await ctx.send(result)
        except discord.HTTPException:
            pass

    
def setup(bot):
    bot.add_cog(_util(bot))