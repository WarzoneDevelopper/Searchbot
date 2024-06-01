import os
import discord
from discord.ext import commands
import json
import asyncio
from datetime import datetime, timedelta

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)


allowed_channel_id = 1246525821603024947  


def load_credits():
    if not os.path.exists("credits.json"):
        return {}
    with open("credits.json", "r") as f:
        return json.load(f)


def save_credits(credits):
    with open("credits.json", "w") as f:
        json.dump(credits, f, indent=4)


def load_daily_claims():
    if not os.path.exists("daily_claims.json"):
        return {}
    with open("daily_claims.json", "r") as f:
        return json.load(f)


def save_daily_claims(daily_claims):
    with open("daily_claims.json", "w") as f:
        json.dump(daily_claims, f, indent=4)

@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user}')

@bot.command()
async def lookup(ctx, id: str):
    """Recherche un ID dans les fichiers texte du répertoire spécifié."""
   
    if ctx.channel.id != allowed_channel_id:
        await ctx.send("Use this command in <#1246525821603024947>")
        return

    
    if not id:
        await ctx.send("Please, send a correct ID or key word.")
        return

   
    credits = load_credits()
    user_id = str(ctx.author.id)
    if user_id not in credits or credits[user_id] <= 0:
        await ctx.send("You have 0 credits, Please buy some credits.")
        return

    
    credits[user_id] -= 1
    save_credits(credits)

    
    directory = "C:/Users/softw/Desktop/dumper/dump"
    if not os.path.isdir(directory):
        await ctx.send(f"Erreur de code '{directory}' ")
        return

    found = False
    result = ""
    loop = asyncio.get_event_loop()
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if not os.path.isfile(filepath):
            continue
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = await loop.run_in_executor(None, f.readlines)
            for line in lines:
                if str(id) in line:
                    result += line
                    found = True
                    break
        if found:
            break

   
    if not found:
        await ctx.send(f"L'ID {id} is not available in the database. Search another discord ID.")
        return

   
    embed = discord.Embed(title="Lithium Bot", description=f"Result for: {id}:", color=0xffd700)
    embed.add_field(name="Informations:", value=f"```{result}```", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def balance(ctx, member: discord.Member = None):
    """Affiche le solde de crédits d'un utilisateur."""
    member = member or ctx.author
    credits = load_credits()
    user_id = str(member.id)
    embed = discord.Embed(title="Total credits:", color=0x09ff93)
    embed.add_field(name="Member - ", value=member.mention)
    embed.add_field(name="Number - ", value=credits.get(user_id, 0))
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def add(ctx, member: discord.Member, amount: int):
    """Ajoute des crédits à un utilisateur (admin uniquement)."""
    if amount <= 0:
        await ctx.send("Le montant doit être supérieur à zéro.")
        return
    credits = load_credits()
    user_id = str(member.id)
    credits[user_id] = credits.get(user_id, 0) + amount
    save_credits(credits)
    await ctx.send(f"{amount} credits added to {member.mention}.")

@bot.command()
@commands.has_permissions(administrator=True)
async def remove(ctx, member: discord.Member, amount: int):
    """Retire des crédits à un utilisateur (admin uniquement)."""
    if amount <= 0:
        await ctx.send("Le montant doit être supérieur à zéro.")
        return
    credits = load_credits()
    user_id = str(member.id)
    if user_id not in credits or credits[user_id] < amount:
        await ctx.send(f"{member.mention} n'a pas assez de crédits.")
        return
    credits[user_id] -= amount
    save_credits(credits)
    await ctx.send(f"{amount} credits removed from {member.mention}.")

@bot.command()
async def daily(ctx):
    """Permet aux utilisateurs de réclamer 10 crédits toutes les 24 heures."""
    user_id = str(ctx.author.id)
    daily_claims = load_daily_claims()

    
    last_claim_time = daily_claims.get(user_id)
    if last_claim_time:
        last_claim_time = datetime.strptime(last_claim_time, "%Y-%m-%d %H:%M:%S")
        if datetime.now() - last_claim_time < timedelta(days=1):
            next_claim_time = last_claim_time + timedelta(days=1)
            await ctx.send(f"You have already claimed your daily credits. Next claim available at {next_claim_time.strftime('%Y-%m-%d %H:%M:%S')}.")
            return


    credits = load_credits()
    credits[user_id] = credits.get(user_id, 0) + 10
    save_credits(credits)

    
    daily_claims[user_id] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_daily_claims(daily_claims)

    await ctx.send(f"10 daily credits have been added to your account, {ctx.author.mention}.")


bot.run('your_bot_token_here')
