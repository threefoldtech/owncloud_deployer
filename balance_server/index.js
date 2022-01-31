const express = require('express')
const Client = require('tfgrid-api-client')

const app = express()
const port = 3001

const url = "wss://tfchain.dev.grid.tf/ws"
const mnemonic = "talent electric save cabbage write chuckle small only happy resist slight engine"
const scheme = "sr25519"
const client = new Client(url, mnemonic, scheme)


async function getBalance() {
    let balance = 0
    try {
        await client.init()
    } catch (err) {
        return err
    }
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
    console.log(`balance server app listening on port: ${port}`)
})

