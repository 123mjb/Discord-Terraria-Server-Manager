import os
from dotenv import load_dotenv
import subprocess
import discord

from discord.ext import commands
from discord.ext.tasks import loop

load_dotenv("./key.env")

intents: str = discord.Intents.all()
token: str = os.getenv("TOKEN")
GUILD: str = os.getenv("GUILD")
INGAME: str = os.getenv("INGAME")
lf: int = 0

bot: commands.Bot = commands.Bot(command_prefix="/", intents=intents)

def emptyfile():
    open("text.txt", "w", encoding="utf-8").close()

def serviceuptime() -> str:
    if isrunning():
        output = subprocess.run(
            ["service", "terraria", "status"], capture_output=True, text=True
        ).stdout
        lines: str = output.split("\n")
        activeline: str = lines[2]
        r: str = "The server has been running "
        for i in range(30, len(activeline)):
            r += activeline[i]
        return r
        #     Active: active (running)
    else:
        return "Not running"


def isrunning():
    output = subprocess.run(
        ["service", "terraria", "status"], capture_output=True, text=True
    ).stdout
    lines = output.split("\n")
    activeline = lines[2]
    return "active (running)" in activeline


def previous_output(size: int = -1):
    with open("text.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()
        return lines[size]


def countplaying():
    subprocess.run(["terrariad", "playing"], check=False)
    po = previous_output(size=-2)
    fp = po.split()[0]
    if fp == ":":
        fp = po.split()[1]
    if fp == "No":
        return 0
    amountplaying = int(fp)
    return amountplaying


def WhoPlaying() ->list:
    subprocess.run(["terrariad", "playing"])
    amountplaying = countplaying()
    peopleplaying = []
    for i in range(0, amountplaying):
        out = previous_output(-3 - i).split()
        peopleplaying += out[0] if len(out) == 2 else out[1]
    return peopleplaying


@bot.tree.command(
    description="Shows how long the server has been up for.",
    guild=discord.Object(id=GUILD),
)
async def runtime(interaction: discord.Interaction):
    Return = serviceuptime()
    await interaction.response.send_message(Return)


@bot.tree.command(
    description="Shows who and how many players are on the server.",
    guild=discord.Object(id=GUILD),
)
async def playing(interaction: discord.Interaction):
    Return = str(countplaying()) + " Playing:\n" + "\n".join(WhoPlaying())
    await interaction.response.send_message(Return)


@bot.tree.command(
    description="Starts the server if it is down.", guild=discord.Object(id=GUILD)
)
async def start(interaction: discord.Interaction):
    if not isrunning():
        subprocess.run(["sudo", "systemctl", "start", "terraria"])
        await interaction.response.send_message("Starting: May take a sec!")
    else:
        await interaction.response.send_message("Already running!")

@bot.tree.command(
    description="Runs a command on the server.",
    guild=discord.Object(id=GUILD),
)
@commands.has_permissions(manage_guild=True)
async def run(interaction: discord.Interaction, command: str):
    if not interaction.user.roles[1].permissions.manage_guild:
        await interaction.response.send_message("You do not have permission to do that.")
        return
    subprocess.run(["terrariad", "/"+command])
    await interaction.response.send_message("Command ran!")

@bot.tree.command(
    description="Stops the server if no one is on it and it is running.",
    guild=discord.Object(id=GUILD),
)
async def stop(interaction: discord.Interaction):
    if isrunning():
        if countplaying() == 0:
            subprocess.run(["sudo", "systemctl", "stop", "terraria"])
            await interaction.response.send_message("Stopping: May take a sec!")
        else:
            await interaction.response.send_message("Players still active.")
    else:
        await interaction.response.send_message("Not running!")

@bot.tree.command(
    description="Stops the server if you are impatient.",
    guild=discord.Object(id=GUILD),
)
@commands.has_permissions(manage_guild=True)
async def forcestop(interaction: discord.Interaction):
    if isrunning():
        if countplaying() == 0:
            subprocess.run(["sudo", "systemctl", "stop", "terraria"])
            await interaction.response.send_message("Stopping: May take a sec!")
        else:
            subprocess.run(["sudo", "systemctl", "stop", "terraria"])
            await interaction.response.send_message("Players still active. Stopping anyway.")
    else:
        await interaction.response.send_message("Not running! Why would you want to stop it?")


@run.error
async def run_error(error, ctx):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to do that.")
        
@forcestop.error
async def forcestop_error(error, ctx):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to do that.")

def linechecker(line: str) -> bool:
    for phrase in [
        "is connecting...",
        "gpath.c:115",
        "was booted:",
        "player connected.",
        "Settling liquids ",
        "Resetting game objects",
        "No players connected.",
    ]:
        if phrase in line:
            return False
    if len(line) > 60:
        return False
    words = line.split()
    if len(words) == 0:
        return False
    if words[0] == ":":
        del words[0]
        if len(words) == 0:
            return False
    if len(words) == 2:
        if words[1][0] == "(" and words[1][-1] == ")":
            return False
    if words[0] not in ["Saving", "Validating", "Backing", "<Server>"]:
        return True


@loop(seconds=2)
async def ttod(channel: discord.TextChannel):
    global lf
    with open("./text.txt", encoding="utf-8") as file:
        lines: str = file.readlines()
    if len(lines) > lf:
        for i in range(lf, len(lines)):
            if linechecker(lines[i]):
                ld = lines[i].split()
                if ld[0] == ":":
                    del ld[0]
                text = " ".join(ld)
                await channel.send(text[slice(50)])
    lf = len(lines)
    if lf > 100:
        emptyfile()


@bot.event
async def on_ready():
    global lf
    print(f"{bot.user.name} has connected to Discord!")
    with open("./text.txt") as file:
        lf = len(file.readlines())
    channel = bot.get_channel(int(INGAME))
    ttod.start(channel)


@bot.command()
@commands.is_owner()
async def sync(ctx: commands.Context) -> None:
    """Sync commands"""
    guild = discord.Object(id=GUILD)
    synced = await bot.tree.sync(guild=guild)
    await ctx.send(f"Synced {len(synced)} commands globally")


@bot.listen("on_message")
async def sendtoserver(ctx: discord.Message):
    global lf
    if ctx.author == bot.user:
        return
    words = ctx.content
    name = ctx.author.name
    message = "<" + name + "> " + words
    subprocess.run(["terrariad", "say", message])
    return


bot.run(token)
