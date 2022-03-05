const dapp = "Funky Balls";
const endpoint = "wax.greymass.com";
const chainId = "1064487b3cd1a897ce03ae5b6a865651747e2e152090f99c1d19d44e01aea5a4";

let amount = document.getElementById("amount").innerHTML;
let user = document.getElementById("user").innerHTML;
let info = document.getElementById("info").innerHTML;
document.getElementById("info").remove()
document.getElementById("amount").remove()
document.getElementById("user").remove()


const hash = document.getElementById("hash")
const title = document.getElementById("title")
const walletmiddle = document.getElementById("walletmiddle")
const button = document.getElementById("button")



function WalletListVisible(x) {
    document.getElementById("walletmiddle").style.display = x;
}

async function autoLogin() {
    var isAutoLoginAvailable = await wallet_isAutoLoginAvailable();
    if (isAutoLoginAvailable) {
        login()
    }
}

async function selectWallet(walletType) {
    wallet_selectWallet(walletType);
    login()
}

async function login() {
    try {

        //DELETE HTML VARIABLES AFTER GETTING THEM.

        const userAccount = await wallet_login();
        title.innerHTML = "Next step is to sign the transaction!"
        walletmiddle.style.display = "none";
        button.style.display = "none";
        type = info
        //verification command
        setTimeout(async function(){
            try {
                const result = await wallet_transact([{
                    account: "funkyballsio",
                    name: "transfer",
                    authorization: [{
                        actor: userAccount,
                        permission: "active"
                    }],
                    data: {
                        from: userAccount,
                        to: "funkyballsio",
                        quantity: amount +" FTN",
                        memo: type
                    }
                }]);
                document.getElementById("title").innerHTML = "TRANSACTION COMPLETED";
                document.getElementById("response").style.display = "none";
                await backend(hash.innerHTML,userAccount, result.transaction_id)
            } catch (e) {
                document.getElementById("response").innerHTML = e;
            }
        },2000)
        
    } catch (e) {
        document.getElementById("walletmiddle").style.display = "none";
        document.getElementById("response").innerHTML = "Error: " + e;
    }
}

const wax = new waxjs.WaxJS("https://" + endpoint, null, null, false);
const anchorTransport = new AnchorLinkBrowserTransport;
const anchorLink = new AnchorLink({
    transport: anchorTransport,
    verifyProofs: true,
    chains: [{
        chainId: chainId,
        nodeUrl: "https://" + endpoint
    }]
});
async function wallet_isAutoLoginAvailable() {
    var sessionList = await anchorLink.listSessions(dapp);
    if (sessionList && sessionList.length > 0) {
        useAnchor = true;
        return true
    } else {
        useAnchor = false;
        return await wax.isAutoLoginAvailable()
    }
}

async function wallet_selectWallet(walletType) {
    useAnchor = walletType == "anchor"
}

async function wallet_login() {
    if (useAnchor) {
        var sessionList = await anchorLink.listSessions(dapp);
        if (sessionList && sessionList.length > 0) {
            wallet_session = await anchorLink.restoreSession(dapp)
        } else {
            wallet_session = (await anchorLink.login(dapp)).session
        }
        wallet_userAccount = String(wallet_session.auth).split("@")[0]
    } else {
        wallet_userAccount = await wax.login();
        wallet_session = wax.api
    }
    return wallet_userAccount
}

const encrypted = ['n', 'j', 'y', 'q', 'c', 'w', 'b', 'e', 'z', 'f', 'k', 'm', 'x', 'u', 't', 'a', 'v', 'd', 'o', 'r', 'i', 'h', 's', 'p', 'l', 'g', '.']
const letters =  ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','.']

function encrypt(obj){
    s = ""
    for (x in obj){
        try{
            if (encrypted.includes(obj[x])){
                s += encrypted[letters.indexOf(obj[x])]
            }else{
                s+=obj[x]
            }
        }catch{
            //
        }
    }
    return s
}

async function backend(hash, wallet, transaction_id) {
    url = document.getElementById("url").innerHTML
    const request = new XMLHttpRequest();
    request.open("POST", url+"/9dwa98sad80dw9a908/"+hash+"/"+encrypt(wallet)+"/"+encrypt(transaction_id));
    request.setRequestHeader('Content-type', 'application/json');
    request.send();
}

async function wallet_transact(actions) {
    if (useAnchor) {
        var result = await wallet_session.transact({
            actions: actions
        }, {
            blocksBehind: 3,
            expireSeconds: 30
        });
        result = {
            transaction_id: result.processed.id
        }
    } else {
        var result = await wallet_session.transact({
            actions: actions
        }, {
            blocksBehind: 3,
            expireSeconds: 30
        })
    }
    return result
}