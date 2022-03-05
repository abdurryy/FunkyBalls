import discord
from datetime import datetime, timedelta
import sqlite3
activeembeds = []
timeoutseconds = 10


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


async def getlatestmsgtime(message):
    message= await message.channel.fetch_message(message.id)
    if message.edited_at is None:
        print("created_at")
        return message.created_at
    else:
        print("edited_at")
        return message.edited_at



class embedpages:
    def __init__(self, listitems, user,title, description=None,mode=0,wallet=None, footer=None, inline=True, emojis=None, intochunks=25):
        """
        :param listitems: [[Title,value],[Title2,value2]]
        :param title: Embed title
        :param description: Embed Description
        :param footer: embed footer
        :param emojis: [first page,previous page,next page,last page]
        """
        if emojis is None:
            emojis = ["◀", "⬅", "🟩", "➡", "▶"]
        if len(emojis) != 5:
            print("Wrong number of emojis!")
            emojis = ["◀", "⬅", "🟩", "➡", "▶"]
        self.emojis = emojis
        self.inline = inline
        self._msg = None
        self.user = user
        self.wallet =wallet
        self.title = title
        self.desc = description
        self.footer = footer
        self.mode = mode
        self.embeditems = listitems
        self.page = 0
        self.chunks = intochunks
        self.chunked = None
        self.currentchunk = None
        self.maxpages = None
        self.createpages()
        self.setchunk()

    def createpages(self):
        self.chunked = list(chunks(self.embeditems, self.chunks))
        print("splitted self.embeditems into chunks.")
        self.maxpages = len(self.chunked) - 1

    def setchunk(self):
        self.currentchunk = self.chunked[self.page]

    def setmsg(self, msg):
        self._msg = msg
        self.addtoembed()



    def getembed(self):
        
        c={
        'Legendary': 0x331459,
        'Rare': 0x142159,
        'Uncommon': 0x3B0C0C,
        'Epic': 0x59143B,
	        'Common': 0x0C3B13
        }.get(self.currentchunk[0][1], 0x3b3b3b)  
                
        
        
        if self.mode == 0:
            pageembed = discord.Embed(title=self.title, description=f'**Funky Ball | {self.currentchunk[0][0]}**',color=c)
            if self.footer is not None:
                pageembed.set_footer(text=self.footer)
            pageembed.set_image(url=f'https://ipfs.atomichub.io/ipfs/{self.currentchunk[0][2]}')
            now = int(datetime.utcnow().timestamp())
            c = self.currentchunk[0][4]*60*60
            cooldown = (int(self.currentchunk[0][3][2])+c-now)
            if cooldown <= 0:
                cooldown = 0
                pageembed.add_field(name="Cooldown", value=f"{str(timedelta(seconds=cooldown))}", inline=True)
            else:
                pageembed.add_field(name="Cooldown", value=f"{str(timedelta(seconds=cooldown))}", inline=True)
        
            pageembed.add_field(name="Durability", value=f"{self.currentchunk[0][5]-self.currentchunk[0][3][3]} uses", inline=True)
            pageembed.add_field(name="Reward", value=f"{self.currentchunk[0][6]} Funky Tokens", inline=True)
            return pageembed
        
        else: 
            pageembed = discord.Embed(title=self.title)
            if self.footer is not None:
                pageembed.set_footer(text=self.footer)
            for x in self.currentchunk:
                i={
                'Legendary': '<:legendary:949240231889092638> ',
                'Rare': '<:rare:949240571891957761> ',
                'Uncommon': '<:uncommon:949241157693616188> ',
                'Epic': '<:epic:949241360425299998> ',
                'Common': '<:common:949241540696485918> '
                }.get(x[1], ':black_large_square:')  
                now = int(datetime.utcnow().timestamp())
                c = x[3]*60*60
                cooldown = (int(x[2][2])+c-now)
                if cooldown <= 0:
                    cooldown = 0
                    pageembed.add_field(name=i+x[0], value=str(timedelta(seconds=cooldown)), inline=self.inline)
                else:
                    pageembed.add_field(name=i+x[0], value=str(timedelta(seconds=cooldown)), inline=self.inline)
                    
                
           
        
        
        
            #pageembed.add_field(name="Reward", value=f"10 Funky Tokens", inline=True)
            return pageembed
    def addtoembed(self):
        activeembeds.append([self, self._msg,self.user])

    @staticmethod
    async def checktimeouts():
        now = datetime.utcnow()
        dotimeout = []
        for x in activeembeds:
            if (now - await getlatestmsgtime(x[1])).total_seconds() >= timeoutseconds:
                dotimeout.append(x)
                del x
        return dotimeout

    @staticmethod
    def check(msgid, reaction, user,timeout=False):
        for x in activeembeds:
            print(str(x[2].id))
            print(str(user.id))
            if str(x[1].id) == str(msgid)and str(x[2].id) == str(user.id):
                if timeout:
                    del x
                    return True
                if reaction == x[0].emojis[0]:
                    x[0].firstpage()
                elif reaction == x[0].emojis[1]:
                    x[0].prevpage()
                elif reaction == x[0].emojis[2]:
                    x[0].cooldown()
                elif reaction == x[0].emojis[3]:
                    x[0].nextpage()
                elif reaction == x[0].emojis[4]:
                    x[0].lastpage()
                return x[0].getembed()
        return False
    
    
    def cooldown(self):
        c = self.currentchunk[0][4]*60*60
        now = int(datetime.utcnow().timestamp())
        print(self.wallet)
        if (int(self.currentchunk[0][3][2])+c-now) <= 0 and self.currentchunk[0][5]-self.currentchunk[0][3][3] > 0:
            database = sqlite3.connect('database.db')
            cur = database.cursor()
            cur.execute(f'SELECT * FROM nfts WHERE nft_id={self.currentchunk[0][3][0]}')
            dat = cur.fetchone()  
            cur.execute(f'UPDATE nfts SET last_mine=\'{now}\' WHERE nft_id={self.currentchunk[0][3][0]}')
            cur.execute(f'UPDATE nfts SET durability=\'{dat[3]+1}\' WHERE nft_id={self.currentchunk[0][3][0]}')
            database.commit()
            cur.execute(f'SELECT * FROM wallets WHERE wallet=\'{self.wallet}\'')
            data = cur.fetchone()  
            print(data)
            
            cur.execute(f'UPDATE wallets SET balance=\'{data[1]+self.currentchunk[0][6]}\' WHERE wallet=\'{self.wallet}\'')
            database.commit()
            l = list(self.currentchunk[0][3])
            l[2]=str(now)
            l[3]=int(dat[3]+1)
            self.currentchunk[0][3] = tuple(l)
            
            
            
            database.close()
    
    def nextpage(self):
        if self.page >= self.maxpages:
            self.page = self.maxpages
        else:
            self.page += 1
            self.setchunk()

    def prevpage(self):
        if self.page == 0:
            pass
        else:
            self.page -= 1
            self.setchunk()

    def firstpage(self):
        self.page = 0
        self.setchunk()

    def lastpage(self):
        self.page = self.maxpages
        self.setchunk()


