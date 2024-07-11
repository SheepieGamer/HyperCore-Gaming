dev = False
import settings
import aiofiles
import discord
import discordbotdash.dash as dbd
from main import bot
from discord.ext import commands
from keep_alive import keep_alive


def main(token):
  
    global bot

    bot.warnings = {
        # guild_id: {member_id: [count, [(admin_id, reason)]]}
    }

    @bot.event
    async def on_ready():
        for guild in bot.guilds:
            async with aiofiles.open(f"guilds/{guild.id}.txt", mode="a") as temp:
                pass

            bot.warnings[guild.id] = {}

        for guild in bot.guilds:
            async with aiofiles.open(f"guilds/{guild.id}.txt", mode="r") as file:
                lines = await file.readlines()

                for line in lines:
                    data = line.split(" ")
                    member_id = int(data[0])
                    admin_id = int(data[1])
                    reason = " ".join(str(data[2:])).strip("\n")

                    try:
                        bot.warnings[guild.id][member_id][0] += 1
                        bot.warnings[guild.id][member_id][1].append((admin_id, reason))
                    
                    except KeyError:
                        bot.warnings[guild.id][member_id] = [1, [(admin_id, reason)]]

        loaded = []
        for cog_file in settings.COGS_DIR.glob("*.py"):
            if cog_file.name != "__init__.py":
                await bot.load_extension(f"cogs.{cog_file.name[:-3]}")
                loaded.append("cogs." + cog_file.name[:-3])
        loaded_str = ""
        for i in loaded:
            loaded_str += f"{i}, "
        print(f"{loaded_str} successfully loaded")
        
        if not dev:
            dbd.openDash(init_bot=bot, port=1234)
            keep_alive()

        bot.tree.copy_global_to(guild=bot.guilds[0])
        await bot.tree.sync(guild=bot.guilds[0])
        print("Tree loaded successfully")
        
        print(f"User: {bot.user} (ID: {bot.user.id})")

    @bot.event
    async def on_guild_join(guild):
        bot.warnings[guild.id] = {}

    @bot.hybrid_command()
    @commands.has_permissions(kick_members=True)
    async def warn(ctx, member: discord.Member, *, reason):
        try:
            first_warning = False
            bot.warnings[ctx.guild.id][member.id][0] += 1
            bot.warnings[ctx.guild.id][member.id][1].append((ctx.author.id, reason))
        except KeyError:
            first_warning = True
            bot.warnings[ctx.guild.id][member.id] = [1, [(ctx.author.id, reason)]]

        count = bot.warnings[ctx.guild.id][member.id][0]

        async with aiofiles.open(f"guilds/{ctx.guild.id}.txt", mode="a") as file:
            await file.write(f"{member.id} {ctx.author.id} {reason}\n")

        await ctx.send(f"{member.mention} has {count} {'warning' if first_warning else 'warnings'}!")

    @bot.hybrid_command()
    @commands.has_permissions(kick_members=True)
    async def warnings(ctx, member: discord.Member):
        embed = discord.Embed(
            title=f"Warnings for {member.name}",
            description="",
            color=discord.Color.red()
        )
        try:
            i = 1
            for admin_id, reason in bot.warnings[ctx.guild.id][member.id][1]:
                admin = ctx.guild.get_member(admin_id)
                embed.description += f"**Warning {i}** given by {admin.mention} because *\"{reason}\"*.\n"
                i += 1
            
            await ctx.send(embed=embed)

        except KeyError:
            await ctx.send("This user has no warnings.")

    bot.run(token)

if __name__ == "__main__":
    main(settings.TOKEN)
    
