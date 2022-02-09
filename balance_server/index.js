const express = require('express')
const Client = require('tfgrid-api-client')

const app = express()
const port = 3001

const url = process.env.CHAIN_URL
const mnemonic = process.env.MNEMONICS 
const scheme = "sr25519"
const client = new Client(url, mnemonic, scheme)

function initClient(client) {
    try {
        client.init()
    } catch (err) {
        return err
    }
}

async function getBalance() {
    let balance = 0
    
    try {
        balance = await client.getBalance()
    } catch (err) {
        return err
    }
    return balance.free / 10 ** 7
}

app.get('/balance', async (req, res) => {
    const b = await getBalance()
    res.status(200).send({ "balance": String(b) })
})

app.listen(port, () => {
    initClient(client);
    console.log(`balance server app listening on port: ${port}`)
})

