import discord
from discord.ext import commands
import settings

class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="say", aliases=['repeat'])
    async def say(self, ctx, *, message: str):
        """
        Repeat the provided text.
        """
        await ctx.send(message)

    @commands.hybrid_command(name="announce")
    @commands.has_permissions(manage_messages=True)
    async def announce(self, ctx, channel: discord.TextChannel, anonymous: bool = False, *, message: str):
        """
        Announce something to a channel, anonymously or not anonymously
        """
        embed = discord.Embed(
            title=f"{str(ctx.author) + ' is announcing...' if anonymous == False else 'Someone is anonymously announcing...'}",
            description=f"{'``'+message+'``' if '<@' not in message else message}",
            color=discord.Color.green()
        )
        await channel.send(embed=embed)
        await ctx.send(f"Success! Pop into {channel.mention} to view your message.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(General(bot))