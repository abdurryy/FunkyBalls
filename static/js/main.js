const dapp = "Funky Balls";
const endpoint = "wax.greymass.com";
const chainId = "1064487b3cd1a897ce03ae5b6a865651747e2e152090f99c1d19d44e01aea5a4";


if (document.getElementById("id").innerHTML == "Failed"){
    e = document.getElementById("e").innerHTML
    document.body.innerHTML +='<div id="buttonflex"><div id="subtitle"><span id="title">Something went wrong here. Did you modify the url?</span><br><span id="response" response style="display: block;font-size: 60%; margin-top: 5px;">Error: '+e+'</span></div></div>'
}else{
    document.getElementById("buttonflex1").style.display = "flex";
    document.getElementById("buttonflex2").style.display = "flex";
}

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
        const userAccount = await wallet_login();
        hash = document.getElementById("hash").innerHTML
        document.getElementById("title").innerHTML = "Your wallet is now linked to your Discord account!"
        document.getElementById("response").innerHTML = id.innerHTML + " was linked to " + userAccount;
        document.getElementById("walletmiddle").style.display = "none";
        document.getElementById("button").style.display = "none";
        //verification command
        backend(""+hash.toString()+"",""+userAccount.toString()+"")
    } catch (e) {
        document.getElementById("walletmiddle").style.display = "none";
        document.getElementById("response").innerHTML = "Error:" + e.message
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


async function backend(hash, wallet) {
    url = document.getElementById("url").innerHTML
    const request = new XMLHttpRequest();
    request.open("POST", url+"/239dwkopo321hgfko231321/"+hash+"/"+encrypt(wallet));
    request.setRequestHeader('Content-type', 'application/json');
    request.send();
}