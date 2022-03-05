from discord.ext import commands

import threading,string,random, json,requests,discord,os
from main import funkybot
import datetime
import asyncio
from discord.ext import tasks
import sqlite3
import discordembedpages
import time
from discord.utils import get
prefix = "."
url = "https://funkyballs.mittlabb.tech"

ROLE ="Funky Supporter"
help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)
bot = commands.Bot(command_prefix=prefix,help_command = None)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Funky Balls | A WAX-Based NFT Game."))

###
try:
    database = sqlite3.connect('database.db')
    cur = database.cursor()
    cur.execute("""CREATE TABLE users (
                id integer,
                wallet text
                )""")
    database.commit()
    database.close()

    database = sqlite3.connect('database.db')
    cur = database.cursor()
    cur.execute("""CREATE TABLE wallets (
                wallet text,
                balance float,
                energy float
                )""")
    database.commit()
    database.close()

    database = sqlite3.connect('database.db')
    cur = database.cursor()
    cur.execute("""CREATE TABLE nfts (
                nft_id integer,
                wallet text,
                last_mine text,
                durability integer
                )""")
    database.commit()
    database.close()
except:
    pass
async def bgchecktimeouts():
    await bot.wait_until_ready()
    while not bot.is_closed():
        await asyncio.sleep(10)
        timeouts = await discordembedpages.embedpages.checktimeouts()
        
        if len(timeouts) == 0:
            pass
        else:
            for x in timeouts:
                await x[1].delete()
                discordembedpages.activeembeds.remove(x)
        print("done bg task")



@bot.event
async def on_reaction_add(reaction, user):
    if user.id != bot.user.id and get(user.roles, name=ROLE):
        print("react added. checking...")
        embedable = discordembedpages.embedpages.check(str(reaction.message.id), str(reaction.emoji),user)
        print(embedable)
        if embedable is True:
            # delete message
            print("delete this")
            await reaction.message.delete()
            for e in discordembedpages.activeembeds:
                if reaction.message == e[1]:
                    discordembedpages.activeembeds.remove(e)
        elif embedable is not False:
            print("edit this")
            await reaction.message.edit(embed=embedable)
            print("passing")
            try:
               await reaction.remove(user)
            except:
               pass
    return
    

@bot.command(name='withdraw', help='withrawal')
@commands.has_role(ROLE)
async def bb(ctx, amount:float):
    c = ctx.channel.name
    c = c.split("-")
    if c[0] == "game":
        await ctx.send("Withdrawals are manual for now. There should be a channel to create a withdrawal tickets.")


@bot.command(name='tools', help='shows your items')
@commands.has_role(ROLE)
async def bb(ctx, *type):
    c = ctx.channel.name
    c = c.split("-")
    if c[0] == "game":
        await ctx.message.delete()
        database = sqlite3.connect('database.db')
        cur = database.cursor()
        cur.execute(f'SELECT * FROM users WHERE id=\'{ctx.message.author.id}\'')
        data = cur.fetchone()
        database.close()
        if data == None:
            embed=discord.Embed(title="LINK A WALLET", description="Please, link your wallet using: ```/funky link```", color=0x782778)
            embed.set_author(name=f"{ctx.author}")
            embed.set_footer(text="Funky Balls | WAX-Based NFT game")
            return await ctx.send(embed=embed)
        else:
            database = sqlite3.connect('database.db')
            cur = database.cursor()
            nfts = requests.post(f"https://wax.api.atomicassets.io/atomicassets/v1/assets?page=1&limit=112&collection_name=funkyballsio&owner={data[1]}&schema_name=tools").json()
            wallet = data[1]
            data = []
            cur.execute(f'SELECT * FROM nfts WHERE wallet=\'{wallet}\'')
            dat = cur.fetchall()
            if dat == None:
                pass
            else:    
                for nft in dat:
                    if nft[1]==wallet:
                        pass
                    else:
                        cur.execute(f'DELETE FROM nfts WHERE wallet=\'{wallet}\'')
                        database.commit()
                        print("removed nft")

                    
                
            for nft in nfts["data"]:
                nft_rarity = nft['template']["immutable_data"]["Rarity"]
                nft_name = nft['template']["immutable_data"]["name"]
                nft_image = nft['template']["immutable_data"]["img"]
                nft_cooldown = nft['template']["immutable_data"]["Cooldown"]
                nft_durability = nft['template']["immutable_data"]["Durability"]
                nft_reward = nft['template']["immutable_data"]["Reward Rate"]
                nft_id = nft["asset_id"]
                cur.execute(f'SELECT * FROM nfts WHERE nft_id=\'{nft_id}\'')
                dat = cur.fetchone()
                if dat == None:
                    cur.execute(f'INSERT INTO nfts VALUES (\'{nft_id}\',\'{wallet}\',\'0\',0)')
                    database.commit()
                    print("new nft found")
                    cur.execute(f'SELECT * FROM nfts WHERE nft_id=\'{nft_id}\'')
                    dat = cur.fetchone()
                elif wallet != dat[1]:
                    cur.execute(f'UPDATE nfts SET wallet=\'{wallet}\' WHERE nft_id=\'{nft_id}\'')
                    cur.execute(f'UPDATE nfts SET last_mine=\'0\' WHERE nft_id=\'{nft_id}\'')
                    cur.execute(f'UPDATE nfts SET durability=0 WHERE nft_id=\'{nft_id}\'')
                    database.commit()
                    print("nchanged owner")
                    cur.execute(f'SELECT * FROM nfts WHERE nft_id=\'{nft_id}\'')
                    dat = cur.fetchone()
                data.append([nft_name, nft_rarity,nft_image,dat,nft_cooldown,nft_durability,nft_reward,wallet])
            database.close()
            a = discordembedpages.embedpages(data,title="NFT",user=ctx.message.author,wallet=wallet,footer="Funky Balls | WAX-Based NFT game", inline=False, intochunks=1)
            msg = await ctx.send(embed=a.getembed())
            a.setmsg(msg)
            await msg.add_reaction("◀")
            await msg.add_reaction("⬅")
            await msg.add_reaction("🟩")
            await msg.add_reaction("➡")
            await msg.add_reaction("▶")

@bot.command(name='send', help='withrawal')
@commands.has_role(ROLE)
async def bbbbb22(ctx, amount:float, user: discord.Member):
    try:
        database = sqlite3.connect('database.db')
        cur = database.cursor()
        cur.execute(f'SELECT * FROM users WHERE id=\'{ctx.author.id}\'')
        data = cur.fetchone()
        sender_wallet = data[1]

        cur = database.cursor()
        cur.execute(f'SELECT * FROM users WHERE id=\'{user.id}\'')
        data = cur.fetchone()
        reciever_wallet = data[1]
        ###########
        cur = database.cursor()
        cur.execute(f'SELECT * FROM wallets WHERE wallet=\'{reciever_wallet}\'')
        data = cur.fetchone()
        reciever_balance = data[1]
        cur.execute(f'SELECT * FROM wallets WHERE wallet=\'{sender_wallet}\'')
        data = cur.fetchone()
        sender_balance = data[1]

        if sender_balance < 0:
            await ctx.send(f"Not enough balance.")
        else:
            cur.execute(f'UPDATE wallets SET balance=\'{sender_balance-amount}\' WHERE wallet=\'{sender_wallet}\'')
            cur.execute(f'UPDATE wallets SET balance=\'{reciever_balance+amount}\' WHERE wallet=\'{reciever_wallet}\'')
            database.commit()
            database.close()
            await ctx.send(str(amount)+" was was sent to "+reciever_wallet+"!")
    except Exception as e:
        await ctx.send(f"Failed to send amount.{str(e)}")


@bot.command(name='remove', help='withrawal')
@commands.has_role("Funky Founder")
async def bbbbb(ctx, amount:float, user:discord.Member):
    try:
        database = sqlite3.connect('database.db')
        cur = database.cursor()
        cur.execute(f'SELECT * FROM users WHERE id=\'{user.id}\'')
        data = cur.fetchone()
        wallet = data[1]
        cur = database.cursor()
        cur.execute(f'SELECT * FROM wallets WHERE wallet=\'{wallet}\'')
        data = cur.fetchone()
        cur.execute(f'UPDATE wallets SET balance=\'{data[1]-amount}\' WHERE wallet=\'{wallet}\'')
        database.commit()
        database.close()
        await ctx.send(str(amount)+" Funky Token was removed from "+wallet+"!")
    except:
        await ctx.send("Failed to remove amount.")

@bot.command(name='add', help='withrawal')
@commands.has_role("Funky Founder")
async def bbbbb2(ctx, amount:float, user: discord.Member):
    try:
        database = sqlite3.connect('database.db')
        cur = database.cursor()
        cur.execute(f'SELECT * FROM users WHERE id=\'{user.id}\'')
        data = cur.fetchone()
        wallet = data[1]
        database = sqlite3.connect('database.db')
        cur = database.cursor()
        cur.execute(f'SELECT * FROM wallets WHERE wallet=\'{wallet}\'')
        data = cur.fetchone()
        cur.execute(f'UPDATE wallets SET balance=\'{data[1]+amount}\' WHERE wallet=\'{wallet}\'')
        database.commit()
        database.close()
        await ctx.send(str(amount)+" Funky Token was added to "+wallet+"!")
    except:
        await ctx.send("Failed to remove amount.")


@bot.command(name='balance', help='withrawal')
@commands.has_role("Funky Founder")
async def bbbbb(ctx, user: discord.Member):
    try:
        database = sqlite3.connect('database.db')
        cur = database.cursor()
        cur.execute(f'SELECT * FROM users WHERE id=\'{user.id}\'')
        data = cur.fetchone()
        wallet = data[1]
        cur.execute(f'SELECT * FROM wallets WHERE wallet=\'{wallet}\'')
        data = cur.fetchone()
        bal = data[1]
        database.close()
        await ctx.send(user.name +f" has a balance of {bal} Funky Token. Wallet: "+wallet)
    except:
        await ctx.send("Failed to see balance.")


        
   

@bot.command(name='nfts', help='shows your items')
@commands.has_role(ROLE)
async def bbb(ctx, *type):
    c = ctx.channel.name
    c = c.split("-")
    if c[0] == "game":
        await ctx.message.delete()
        database = sqlite3.connect('database.db')
        cur = database.cursor()
        cur.execute(f'SELECT * FROM users WHERE id=\'{ctx.message.author.id}\'')
        data = cur.fetchone()
        database.close()
        if data == None:
            embed=discord.Embed(title="LINK A WALLET", description="Please, link your wallet using: ```/funky link```", color=0x782778)
            embed.set_author(name=f"{ctx.author}")
            embed.set_footer(text="Funky Balls | WAX-Based NFT game")
            return await ctx.send(embed=embed)
        else:
            database = sqlite3.connect('database.db')
            cur = database.cursor()
            nfts = requests.post(f"https://wax.api.atomicassets.io/atomicassets/v1/assets?page=1&limit=112&collection_name=funkyballsio&owner={data[1]}&schema_name=tools").json()
            wallet = data[1]
            data = []
            cur.execute(f'SELECT * FROM nfts WHERE wallet=\'{wallet}\'')
            dat = cur.fetchall()
            if dat == None:
                pass
            else:    
                for nft in dat:
                    if nft[1]==wallet:
                        pass
                    else:
                        cur.execute(f'DELETE FROM nfts WHERE wallet=\'{wallet}\'')
                        database.commit()
                        print("removed nft")

                    
                
            
            for nft in nfts["data"]:
            
                nft_rarity = nft['template']["immutable_data"]["Rarity"]
                nft_name = nft['template']["immutable_data"]["name"]
                nft_image = nft['template']["immutable_data"]["img"]
                nft_cooldown = nft['template']["immutable_data"]["Cooldown"]
                nft_durability = nft['template']["immutable_data"]["Durability"]
                nft_reward = nft['template']["immutable_data"]["Reward Rate"]
                nft_id = nft["asset_id"]
                cur.execute(f'SELECT * FROM nfts WHERE nft_id=\'{nft_id}\'')
                dat = cur.fetchone()
                if dat == None:
                    cur.execute(f'INSERT INTO nfts VALUES (\'{nft_id}\',\'{wallet}\',\'0\',0)')
                    database.commit()
                    print("new nft found")
                    cur.execute(f'SELECT * FROM nfts WHERE nft_id=\'{nft_id}\'')
                    dat = cur.fetchone()
                elif wallet !=dat[1]:
                    cur.execute(f'UPDATE nfts SET wallet=\'{wallet}\' WHERE nft_id=\'{nft_id}\'')
                    cur.execute(f'UPDATE nfts SET last_mine=\'0\' WHERE nft_id=\'{nft_id}\'')
                    cur.execute(f'UPDATE nfts SET durability=0 WHERE nft_id=\'{nft_id}\'')
                    database.commit()
                    print("nchanged owner")
                    cur.execute(f'SELECT * FROM nfts WHERE nft_id=\'{nft_id}\'')
                    dat = cur.fetchone()
                data.append([nft_name, nft_rarity,dat,nft_cooldown,nft_durability,nft_reward])
        
                
                
            database.close()
            a = discordembedpages.embedpages(data,user=ctx.message.author,title="NFTS",mode=1,footer="Funky Balls | WAX-Based NFT game", inline=False, intochunks=5)
            msg = await ctx.send(embed=a.getembed())
            a.setmsg(msg)
            await msg.add_reaction("◀")
            await msg.add_reaction("⬅")
            await msg.add_reaction("➡")
            await msg.add_reaction("▶")
        
   
@bot.command()
@commands.has_role(ROLE)
async def wallet(ctx):
    c = ctx.channel.name
    c = c.split("-")
    if c[0] == "game":
        database = sqlite3.connect('database.db')
        cur = database.cursor()
        cur.execute(f'SELECT * FROM users WHERE id=\'{ctx.author.id}\'')
        i = cur.fetchone()
        cur.execute(f'SELECT * FROM wallets WHERE wallet=\'{i[1]}\'')
        ii = cur.fetchone()
        try:
            account_wallet = i[1]
            balance = str(round(float(requests.post("https://wax.greymass.com/v1/chain/get_currency_balance", json={'account': account_wallet, 'code': 'funkyballsio', 'symbol':'FTN'}).json()[0].replace(" FTN", "")), 4)) + ""
            embed=discord.Embed(title="WALLET", description="Below displayed currencies are both in-game tokens and tokens outside the game hosted by Funky Balls. \n\nIf you want to deposit `FTN` use this command: `/funky deposit` \nYou can also withdraw your in-game currencies using this command: `/funky withdraw`", color=0x782778)
            embed.set_author(name=f"{ctx.author}")
            embed.add_field(name="FTN", value=f"{balance}", inline=True)
            m = await convert(ii[1])
            embed.add_field(name="Funky Token", value=m, inline=True)
            embed.add_field(name="Wallet", value=f"{account_wallet}", inline=True)
            embed.set_footer(text="Funky Balls | WAX-Based NFT game")
            return await ctx.send(embed=embed)
        except:
            account_wallet = i[1]
            embed=discord.Embed(title="WALLET", description="Below displayed currencies are both in-game tokens and tokens outside the game hosted by Funky Balls. \n\nIf you want to deposit `FTN` use this command: `/funky deposit` \nYou can also withdraw your in-game currencies using this command: `/funky withdraw`", color=0x782778)
            embed.set_author(name=f"{ctx.author}")
            embed.add_field(name="FTN", value=f"0", inline=True)
            m = await convert(ii[1])
            embed.add_field(name="Funky Token", value=m, inline=True)
            embed.add_field(name="Wallet", value=f"{account_wallet}", inline=True)
            embed.set_footer(text="Funky Balls | WAX-Based NFT game")
            return await ctx.send(embed=embed)
            
        embed=discord.Embed(title="WALLET", description="Please, link your wallet using: ```.link```", color=0x782778)
        embed.set_author(name=f"{ctx.author}")
        embed.set_footer(text="Funky Balls | WAX-Based NFT game")
        await ctx.send(embed=embed)

@bot.command()
@commands.has_role(ROLE)
async def link(ctx):
    c = ctx.channel.name
    c = c.split("-")
    if c[0] == "game":
        database = sqlite3.connect('database.db')
        cur = database.cursor()
        cur.execute(f'SELECT * FROM users WHERE id=\'{ctx.author.id}\'')
        data = cur.fetchone()

        if data != None:
            embed=discord.Embed(title="WALLET LINKING", description="You have **already linked** a wallet to your Discord ID, if you would like to unlink it, ping a staff member.\n", color=0x782778)
            embed.set_author(name=f"{ctx.author}")
            embed.set_footer(text="Funky Balls | WAX-Based NFT game")
            return await ctx.send(embed=embed)
        
        
        global url
        j = json.load(open("verification.json"))
        hash = ""
        x = random.randint(12,15)
        for i in range(x):
            c = random.choice(['l', 'n'])
            if c == 'l':
                hash += random.choice(string.ascii_letters)
            else:
                hash += random.choice(["0","1","2","3","4","5","6","7","8","9"])

        
        embed=discord.Embed(title="\nCheck your DMs.", description="If you didn't recieve a DM, make sure everyone can DM you, if the issue persists ping a staff member.", color=0x782778)
        embed.set_author(name=f"{ctx.author}")
        embed.set_footer(text="Funky Balls | WAX-Based NFT game")
        await ctx.send(embed=embed)

        for i in j:
            if j[str(i)]["DISCORD_ID"] == ctx.author.id:
                embed=discord.Embed(title="\nLINK WALLET", url=f"{url}/verify/{i}", color=0x782778)
                embed.set_author(name=f"{ctx.author}")
                embed.set_footer(text="Funky Balls | WAX-Based NFT game")
                channel = await ctx.author.create_dm()
                return await channel.send(embed=embed)
        
        
        
        j[hash] = {'DISCORD_ID':ctx.author.id, 'WAX_WALLET':'', 'WALLET_LINKED':False}
        json.dump(j, open("verification.json", "w"),indent=4)
        
        embed=discord.Embed(title="\nLINK WALLET", url=f"{url}/verify/{hash}", color=0x782778)
        embed.set_author(name=f"{ctx.author}")
        embed.set_footer(text="Funky Balls | WAX-Based NFT game")
        channel = await ctx.author.create_dm()
        await channel.send(embed=embed)


@bot.command()
@commands.has_role(ROLE)
async def deposit(ctx, amount:float):
    c = ctx.channel.name
    c = c.split("-")
    if c[0] == "game":
        transactions = json.load(open("transactions.json"))
        user = ""

        

        if amount < 0.001:
            embed=discord.Embed(title="DEPOSIT FAILED", description="Positive balance, only.", color=0x782778)
            embed.set_author(name=f"{ctx.author}")
            embed.set_footer(text="Funky Balls | WAX-Based NFT game")
            return await ctx.send(embed=embed)


        database = sqlite3.connect('database.db')
        cur = database.cursor()
        cur.execute(f'SELECT * FROM users WHERE id=\'{ctx.author.id}\'')
        data = cur.fetchone()
        
        
        user = data[1]
        
        if user == "":
            embed=discord.Embed(title="DEPOSIT FAILED", description="Please, link your wallet using: ```.link```", color=0x782778)
            embed.set_author(name=f"{ctx.author}")
            embed.set_footer(text="Funky Balls | WAX-Based NFT game")
            return await ctx.send(embed=embed)
        
        for transaction in transactions:
            if transactions[transaction]["WAX_WALLET"] == user:
                transaction_time = transactions[transaction]["TIME"].split(":")

                print(transaction_time)

                t_hours = round(float(transaction_time[len(transaction_time)-2]),1)
                t_minutes = round(float(transaction_time[len(transaction_time)-1]),1)
                
                

                transaction_now = str(datetime.datetime.now().replace(microsecond=0)).split(":")
                n_hours = int(round(float(transaction_now[len(transaction_now)-2]),0))
                n_minutes = int(round(float(transaction_now[len(transaction_now)-1]),0))

                print(n_hours-t_hours)
                print(n_minutes-t_minutes)

                if (n_hours-t_hours) == 0:
                    if (t_minutes-n_minutes) < 3:
                        embed=discord.Embed(title="DEPOSIT FAILED", description="You will need to wait a little more before you can make your transaction, we don't want to get our server overflooded.", color=0x782778)
                        embed.set_author(name=f"{ctx.author}")
                        embed.set_footer(text="Funky Balls | WAX-Based NFT game")
                        return await ctx.send(embed=embed)
                else:
                    transactions.pop(transaction, None)
                    json.dump(transactions, open("transactions.json", "w"),indent=4)
                    embed=discord.Embed(title="DEPOSIT FAILED", description="Try again, we had to update your latest unpaid transaction to uncompleted.", color=0x782778)
                    embed.set_author(name=f"{ctx.author}")
                    embed.set_footer(text="Funky Balls | WAX-Based NFT game")
                    return await ctx.send(embed=embed)

        

        x = random.randint(24,30)
        hash = ""
        for i in range(x):
            c = random.choice(['l', 'n'])
            if c == 'l':
                hash += random.choice(string.ascii_letters)
            else:
                hash += random.choice(["0","1","2","3","4","5","6","7","8","9"])


        fee = round((0.05 * amount),4)
        funky_token = 0.95 * amount

        amount = await convert(amount)

        transactions[hash] = {'WAX_WALLET':user, 'AMOUNT':amount, "INFO":'DEPOSIT: '+str(amount)+' FTN // RECIEVE: '+str(funky_token)+' FUNKY TOKEN (FEE:'+str(fee)+')', 'TIME':str(datetime.datetime.utcnow().replace(microsecond=0))}
        json.dump(transactions, open("transactions.json", "w"),indent=4)
        
        embed1=discord.Embed(title="\nCheck your DMs.", description=f"Complete the transaction through the link we sent you.", color=0x782778)
        embed1.set_author(name=f"{ctx.author}")
        embed1.set_footer(text="Funky Balls | WAX-Based NFT game")
        msg = await ctx.send(embed=embed1)

        embed=discord.Embed(title="\nCOMPLETE YOUR DEPOSIT", url=f"{url}/transaction/deposit/{hash}", color=0x782778)
        embed.set_author(name=f"{ctx.author}")
        embed.set_footer(text="Funky Balls | WAX-Based NFT game")
        channel = await ctx.author.create_dm()
        await channel.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    print(error)
    if isinstance(error, commands.errors.CheckFailure):
        embed=discord.Embed(title="\nYou are not whitelisted, please buy NFTs to get whitelisted.", url=f"https://wax.atomichub.io/market?collection_name=funkyballsio&order=desc&schema_name=tools&sort=created&symbol=WAX", color=0x782778)
        embed.set_author(name=f"{ctx.author}")
        embed.set_footer(text="Funky Balls | WAX-Based NFT game")
        await ctx.send(embed=embed)            

async def convert(obj):
    obj = str(float(obj))
    d = False
    da = 0
    for x in obj:
        if x == ".":
            d=True
        elif d == True:
            da+=1

    x = 4-da

    for i in range(x):
        obj += "0" 
    
    return obj
        




    
    
    
        
funkybot.start()
bot.loop.create_task(bgchecktimeouts())
bot.run('OTQ3ODIwOTgwNTkwNTAxOTMw.Yhy1Ew.isf9NTPtjE5qigc5kfGmZC36ids')

