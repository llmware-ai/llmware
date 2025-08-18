const express = require('express');
const axios = require('axios');
const path = require('path');
const bodyParser = require('body-parser');

const app = express();
const port = 3000;


app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());


app.use(express.static(path.join(__dirname, 'public')));


app.post('/search', async (req, res) => {
    const { query } = req.body;
    try {
        const response = await axios.post('https://api.openai.com/v1/completions', {
            model: 'text-davinci-003', 
            prompt: query,
            max_tokens: 150
        }, {
            headers: {
                'Authorization': 'AIzaSyDcCbEutpObDTjlfJeVeU2sSvbyJML-yh0', 
                'Content-Type': 'application/json'
            }
        });
        const { choices } = response.data;
        const searchResults = choices.map(choice => choice.text.trim());
        res.json(searchResults);
    } catch (error) {
        console.error('Error searching query:', error);
        res.status(500).json({ error: 'Error searching query' });
    }
});


app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
