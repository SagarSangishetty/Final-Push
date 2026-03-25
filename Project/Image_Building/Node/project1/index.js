const express = require('express')
const app = express()

app.get('/', (req, res) => {
    res.json({ message: 'Hello from Node.js!' })
})

app.get('/health', (req, res) => {
    res.json({ status: 'ok' })
})

app.get('/user', (req, res) => {
    res.json({ name: 'John', age: 30 })
})

app.listen(3000, () => {
    console.log('Server running on port 3000')
})