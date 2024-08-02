import discord
import os 
import random as r
from dotenv import load_dotenv 
import subprocess

from discord.ext import commands


load_dotenv("./key.env") 

intents= discord.Intents.all()
token = os.getenv('TOKEN')
GUILD = os.getenv('GUILD')


bot = commands.Bot(command_prefix='/',intents=intents)

def emptyfile():
    if r.randrange(0,10) > 7:
        open('file.txt', 'w').close()

def serviceuptime():
    if isrunning():
        output = subprocess.run(["service","terraria","status"],capture_output=True,text=True).stdout
        lines = output.split("\n")
        activeline = lines[2]
        r="The server has been running "
        for i in range(30,len(activeline)):
            r+=activeline[i]
        return r
        #     Active: active (running) 
    else:
        return "Not running"

def isrunning():
    output = subprocess.run(["service","terraria","status"],capture_output=True,text=True).stdout
    lines = output.split("\n")
    activeline = lines[2]
    return "active (running)" in activeline

def previous_output(size: int = -1):
    with open("text.txt","r") as file:
        lines = file.readlines()
        return lines[size]
    
def countplaying():
    subprocess.run(["terrariad","playing"])
    po = previous_output(size=-2)
    fp = po.split()[0]
    if fp == ":": fp = po.split()[1]
    if fp == "No": return 0
    amountplaying = int(fp)
    return amountplaying

def WhoPlaying():
    subprocess.run(["terrariad","playing"])
    amountplaying = countplaying()
    peopleplaying = []
    for i in range(0,amountplaying):
        out = previous_output(-3-i).split()
        peopleplaying += out[0] if len(out) == 2 else out[1]
    return peopleplaying 


@bot.tree.command(description="Shows how long the server has been up for.",guild=discord.Object(id=GUILD))
async def runtime(interaction: discord.Interaction):
    Return = serviceuptime()
    emptyfile()
    await interaction.response.send_message(Return)
    
@bot.tree.command(description="Shows who and how many players are on the server.",guild=discord.Object(id=GUILD))
async def playing(interaction: discord.Interaction):
    Return=str(countplaying())+" Playing:\n" + "\n".join(WhoPlaying())
    emptyfile()
    await interaction.response.send_message(Return)

@bot.tree.command(description="Starts the server if it is down.",guild=discord.Object(id=GUILD))
async def start(interaction: discord.Interaction):
    if not isrunning():
        subprocess.run(["sudo","systemctl","start","terraria"])
        await interaction.response.send_message("Starting: May take a sec!")
    else:
        await interaction.response.send_message("Already running!")
        
@bot.tree.command(description="Stops the server if no one is on it and it is running.",guild=discord.Object(id=GUILD))
async def stop(interaction: discord.Interaction):
    if isrunning():
        if countplaying()==0:
            subprocess.run(["sudo","systemctl","stop","terraria"])
            await interaction.response.send_message("Stopping: May take a sec!")
        else:
            await interaction.response.send_message("Players still active.")
    else:
        await interaction.response.send_message("Not running!")

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    guild = bot.get_guild(GUILD)

    print(
        f'{bot.user.name} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')
    
@bot.command()
@commands.is_owner()
async def sync(ctx: commands.Context) -> None:
    """Sync commands"""
    guild = discord.Object(id=GUILD)
    synced = await bot.tree.sync(guild=guild)
    await ctx.send(f"Synced {len(synced)} commands globally")

bot.run(token)