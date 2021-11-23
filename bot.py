#!/usr/bin/python3
import random
from nextcord.ext import commands
import nextcord
import os

bot = commands.Bot(command_prefix="/", case_insensitive=True)

#Singular function to get random trials

def getTrial():
    ran = random.randint(1, 10)
    trial = ""
    match ran:
        case 1:
            trial = "Hel Ra Citadel"
        case 2:
            trial = "Atherian Archive"
        case 3:
            trial = "Sanctum Ophidia"
        case 4:
            trial = "Maw of Lorkhaj"
        case 5:
            trial = "Halls of Fabrication"
        case 6:
            trial = "Asylum Sanctorium"
        case 7:
            trial = "Cloudrest"
        case 8:
            trial = "Sunspire"
        case 9:
            trial = "Kyne's Aegis"
        case 10:
            trial = "Rockgrove"
    return trial


#Commands

@bot.command(name="welcome")
async def SendMessage(ctx):
    await ctx.send('Winds Of Kyne be with you.')

@bot.command(name="youtube")
async def SendMessage(ctx):
    await ctx.send('https://youtube.com/playlist?list=PL-z7L6gs44NMN_fDzsZY-3RRwaxHzxCBQ')

@bot.command(name="lore")
async def SendMessage(ctx):
    ran = random.randint(1, 4) #Update to account for number of files
    grab = str(ran)
    grab += ".txt"
    with open('Lore/'+ grab,) as l:
        message = l.read();
    await ctx.send(message)

@bot.command(name="joke")
async def SendMessage(ctx):
    ran = random.randint(1, 3) #Update to account for number of files
    grab = str(ran)
    grab += ".txt"
    with open('Jokes/'+ grab,encoding="utf8") as l:
        message = l.read()
    await ctx.send(message)


@bot.command(name="helpme")
async def SendMessage(ctx):
    await ctx.send('Ask Drakador to help you.')

@bot.command(name="lewd")
async def SendMessage(ctx):
    await ctx.send('https://cdn.discordapp.com/attachments/911730032286785536/911776421473550346/interlocking.gif')
#Yeah it is a gif but... meme

@bot.command(name="vka")
async def SendMessage(ctx):
    await ctx.send('https://cdn.discordapp.com/attachments/911730032286785536/911837688141856768/congaline.png')


@bot.command(name="commands")
async def SendMessage(ctx):
    await ctx.send("""
```
Commands:
1)  /welcome         Shows a welcome
2)  /lore            Shows a random lore tidbit
3)  /helpme          Tells you some help
4)  /commands        Tells you the commands
5)  /gimmentrial     Gives you a random normal trial to do
6)  /gimmevtrial     Gives you a random veteran trial to do
7)  /gimmehmtrail    Gives you a random veteran hm trial to do
8)  /youtube         Links you to the BOK Trials Playlist
9)  /lewd            Be wary, very lewd option
10) /joke            Tells a Joke
11) /vka             Something you wanna see for vKA

GIFs:
/arma
/auddy
/lissa
/rng
/vundees
/drak
/fishing
/dance
/logz
/f
/jabs
/facepalm
/hummus
```
""")



# GIFS
#await ctx.send('')
@bot.command(name="arma")
async def SendMessage(ctx):
    #await ctx.send(file=nextcord.File('Gifs/Arma.gif'))
    await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730134044794930/Arma.gif')
    
@bot.command(name="auddy")
async def SendMessage(ctx):
    #await ctx.send(file=nextcord.File('Gifs/Auddy.gif'))
    await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730135034646558/Auddy.gif')

@bot.command(name="lissa")
async def SendMessage(ctx):
    #await ctx.send(file=nextcord.File('Gifs/Lissa.gif'))
    await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730138276855818/Lissa.gif')

@bot.command(name="rng")
async def SendMessage(ctx):
    #await ctx.send(file=nextcord.File('Gifs/RNG.gif'))
    await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730139770019921/RNG.gif')

@bot.command(name="vundees")
async def SendMessage(ctx):
    #await ctx.send(file=nextcord.File('Gifs/Vundees.gif'))
    await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730140604678204/Vundees.gif')

@bot.command(name="drak")
async def SendMessage(ctx):
    #await ctx.send(file=nextcord.File('Gifs/Drak.gif'))
    await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730136628461589/Drak.gif')
    
@bot.command(name="fishing")
async def SendMessage(ctx):
    #await ctx.send(file=nextcord.File('Gifs/Fishing.gif'))
    await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730137450553355/Fishing.gif')

@bot.command(name="dance")
async def SendMessage(ctx):
    #await ctx.send(file=nextcord.File('Gifs/Dance.gif'))
    await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730135919628328/Dance.gif')

@bot.command(name="logz")
async def SendMessage(ctx):
    #await ctx.send(file=nextcord.File('Gifs/Logz.gif'))
    await ctx.send('https://media.discordapp.net/attachments/911730032286785536/911730138935349308/Logz.gif')
    
@bot.command(name="f")
async def SendMessage(ctx):
    await ctx.send('https://tenor.com/view/keyboard-hyperx-rgb-hyperx-family-hyperx-gaming-gif-17743649')
    
@bot.command(name="jabs")
async def SendMessage(ctx):
    await ctx.send('https://cdn.discordapp.com/attachments/911730032286785536/911837712196173824/jabs.gif')

@bot.command(name="facepalm")
async def SendMessage(ctx):
    await ctx.send('https://cdn.discordapp.com/attachments/911730032286785536/912569604973404160/Facepalm.gif')

@bot.command(name="hummus")
async def SendMessage(ctx):
    await ctx.send('https://tenor.com/view/hummus-hummusyes-hummushappy-gif-8630288')


    
    
    
# Get a trial randomly chosen
@bot.command(name="GimmeNTrial")
async def SendMessage(ctx):
    trial = getTrial()
    await ctx.send("Normal " + trial)

@bot.command(name="GimmeVTrial")
async def SendMessage(ctx):
    trial = getTrial()
    await ctx.send("Veteran " + trial)

@bot.command(name="GimmeHMTrial")
async def SendMessage(ctx):
    trial = getTrial()
    await ctx.send("Veteran " + trial + " HM")
    

@bot.command(name="setstat")
async def change_playing(ctx):
    await bot.change_presence(activity=nextcord.Game(name="Several Godslayer Progs"))


#Non-Commmands

@bot.event
async def on_ready():
    print(f"Logged in as: {bot.user.name}")

if __name__ == '__main__':
    with open('Token.txt') as f:
        token = f.readline();
    bot.run(token)
