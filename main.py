#fetch test

from flask import Flask,render_template,jsonify,request
import bot, json, threading,requests,time
from discord.ext import commands
import sqlite3
app = Flask(__name__)



url = "https://funkyballs.mittlabb.tech"

@app.route("/verify/<id>")
def index(id):
    global url
    e = ""
    try:
        newid = json.load(open("verification.json"))[id]["DISCORD_ID"]
    except Exception as ee:
        e = ee
        newid = "Failed"
    
    return render_template('index.html', id=newid, e=e, hash=id, url=url)


@app.route("/transaction/<arg>/<hash>")
def transaction(arg,hash):
    transactions = json.load(open("transactions.json"))
    for transaction in transactions:
        if transaction == hash:
            user = transactions[transaction]["WAX_WALLET"]
            amount = transactions[transaction]["AMOUNT"]
            info = transactions[transaction]["INFO"]
            return render_template("transaction.html", info=info,hash=hash,amount=amount, user=user)

    newid = "Failed"
    return render_template('index.html', id=newid)


@app.route("/9dwa98sad80dw9a908/<hash>/<wallet>/<transaction_ido>",methods=["POST"])
def payment(hash, wallet, transaction_ido):
    time.sleep(5)
    if request.method == "POST":
        if 1:
            wallet = decrypt(wallet)
            transactions = json.load(open("transactions.json"))
            transaction_ids = json.load(open("transaction_ids.json"))
            transaction_id = decrypt(transaction_ido)
            transaction_amount = float(requests.get("https://wax.greymass.com/v1/history/get_transaction", json={'id':transaction_id}).json()["traces"][0]["act"]["data"]["quantity"].replace(" FTN", ""))
            transaction_sender = str(requests.get("https://wax.greymass.com/v1/history/get_transaction", json={'id':transaction_id}).json()["traces"][0]["act"]["data"]["from"])
            

            
            

            for transaction in transactions:
                if transactions[transaction]["WAX_WALLET"] == wallet:
                    if transaction_sender == wallet:
                        if float(transactions[transaction]["AMOUNT"]) == transaction_amount:
                            for transaction_id1 in transaction_ids:
                                if transaction_id1 == transaction_id:
                                    return jsonify({'success': False})
                            
                            #BOUGHT# GIVE IN-GAME TOKEN
                            ingame_token_amount = float(transaction_amount)*0.95 ## HOW MUCH THEY RECIEVE
                            fee_token_amount = float(transaction_amount)*0.05
                            ########################
                            #UPDATE DATABASE TOKEN WITH ingame_token_amount AMOUNT
                            print("TRANSACTION: "+wallet+" / "+str(transaction_amount))
                            database = sqlite3.connect('database.db')
                            cur = database.cursor()
                            cur.execute(f'SELECT * FROM wallets WHERE wallet=\'{wallet}\'')
                            data = cur.fetchone()  
                            print(data)
                            cur.execute(f'UPDATE wallets SET balance=\'{data[1]+fee_token_amount}\' WHERE wallet=\'roilo.c.wam\'')
                            cur.execute(f'UPDATE wallets SET balance=\'{data[1]+ingame_token_amount}\' WHERE wallet=\'{wallet}\'')
                            database.commit()
                            database.close()


                            transaction_ids[transaction_id] = "THIS ID WAS USED BY: "+wallet
                            json.dump(transaction_ids, open("transaction_ids.json", "w"),indent=4)
                            
                            transactions.pop(hash, None)
                            json.dump(transactions, open("transactions.json", "w"),indent=4)

                            return jsonify({'success': True})
        #except Exception as e:
         #   print(wallet, transaction_id, str(e))
          #  return jsonify({'success': False})
    else:
        return jsonify({'success': False})



@app.route("/239dwkopo321hgfko231321/<hash>/<wallet>",methods=["POST"])
def verifed(hash, wallet):
    if request.method == "POST":
        try:
            wallet = decrypt(wallet)
            j = json.load(open("verification.json"))
            DISCORD_ID = j[hash]["DISCORD_ID"]
            j.pop(hash, None)
            json.dump(j, open("verification.json", "w"),indent=4)

            ###

           
           
            database = sqlite3.connect('database.db')
            cur = database.cursor()
            cur.execute(f'INSERT INTO users VALUES (\'{DISCORD_ID}\',\'{wallet}\')')
            database.commit()
            cur.execute(f'SELECT * FROM wallets WHERE wallet=\'{wallet}\'')
            data = cur.fetchone()
            print("data:")
            print(data)
            if data == None:
                print("none so adding")
                cur.execute(f'INSERT INTO wallets VALUES (\'{wallet}\',\'0\',\'0\')')
                database.commit()
            database.close()
            ######################
            ## USE wallet AND DISCORD_ID to update database!

            #######################
            return jsonify({'success': True})
        except:
            return jsonify({'success': False})
    else:
        return jsonify({'success': False})

def decrypt(obj):
    encrypted = ['n', 'j', 'y', 'q', 'c', 'w', 'b', 'e', 'z', 'f', 'k', 'm', 'x', 'u', 't', 'a', 'v', 'd', 'o', 'r', 'i', 'h', 's', 'p', 'l', 'g', "."]
    letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',"."]
    s = ""
    for x in obj:
        if x in letters:
            s += letters[encrypted.index(x)]
        else:
            s += x
    return s




class funkybot:
    def start():
        t = threading.Thread(target=funkybot.run)
        t.start()

    def run():
        context = ('/etc/letsencrypt/live/funkyballs.mittlabb.tech/fullchain.pem', '/etc/letsencrypt/live/funkyballs.mittlabb.tech/privkey.pem')
        app.run(host="0.0.0.0", port=443, debug=False, ssl_context=context)
