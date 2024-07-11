import asyncio
import re

import discord
from discord.ext import commands


class HierarchyMember(commands.MemberConverter):
    """
    A member converter that respects Discord's role hierarchy system.
    """
    async def convert(self, ctx, arg):
        member = await super().convert(ctx, arg)

        can_do_action = (ctx.author == ctx.guild.owner or
                         ctx.author.top_role > member.top_role)
        if not can_do_action:
            raise commands.BadArgument("Role hierarchy prevents you from doing this.")
        return member


class HackMember(HierarchyMember):
    """
    A member converter that also allows arbitrary IDs to be passed.
    """
    async def convert(self, ctx, arg):
        try:
            member = await super().convert(ctx, arg)
            return member.id
        except commands.BadArgument:
            try:
                return int(arg)
            except ValueError:
                raise commands.BadArgument(f'"{arg}" is not a valid member or ID.')


class BannedUser(commands.Converter):
    """
    A converter for members who have been banned.
    """
    async def convert(self, ctx, arg):
        bans = [entry.user for entry in await ctx.guild.bans()]

        try:
            user = discord.utils.get(bans, id=int(arg))
        except ValueError:
            if re.match(r"\#\d{4}", arg[-5:]):
                user = discord.utils.find(lambda m: str(m) == arg, bans)
            else:
                possible_users = [user for user in bans if user.name == arg]
                return await ctx.disambiguate(possible_users)

        if user is None:
            raise commands.BadArgument("That user is not banned on this server.")

        return user


class Moderation(commands.Cog):
    """
    Moderation commands to manage your server.
    """
    def __init__(self, bot):
        self.bot = bot


    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: HierarchyMember, *, reason: str = None):
        """
        Kick a member.
        """
        await member.kick(reason=reason)
        await ctx.send('\N{WAVING HAND SIGN} Bye!')

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def softban(self, ctx, member: HierarchyMember, *, reason: str = None):
        """
        Softban a member.

        A softban is equivalent to kicking a member and purging their messages.
        This is done by banning the member and immediately unbanning them.
        """
        await member.ban(reason=reason)
        await member.unban(reason=reason)
        await ctx.send('\N{WAVING HAND SIGN} Bye!')
        unknown_reason = "Unknown reason"
        await member.send(f"You were kicked!\nBy: {ctx.author.username}\nFor: {unknown_reason if reason == None else reason}")

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: HackMember, *, reason: str = None):
        """
        Ban a user.

        You can also ban users who are not in your server by passing in their ID as the argument.
        """
        await ctx.guild.ban(discord.Object(id=user), reason=reason)
        await ctx.send('\N{WAVING HAND SIGN} Goodbye!')

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: BannedUser, *, reason: str = None):
        """
        Unban a user.
        """
        await ctx.guild.unban(user, reason=reason)
        await ctx.send("\N{BABY ANGEL} Welcome back!")
        unknown_reason = "Unknown reason"
        await user.send(f"You were unbanned!\nBy: {ctx.author.username}\nFor: {unknown_reason if reason == None else reason}")


async def setup(bot):
    await bot.add_cog(Moderation(bot))