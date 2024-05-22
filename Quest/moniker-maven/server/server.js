const express = require('express');
const { spawn } = require('child_process');
const cors = require('cors');
const app = express();

app.use(cors()); // Enable CORS
app.use(express.json());

app.post('/api/query', (req, res) => {
    const { query, model_name } = req.body;
    const pythonProcess = spawn('python', ['../model/model.py', query || 'Cool names']);

    let data = '';
    let errorOutput = '';

    pythonProcess.stdout.on('data', (chunk) => {
        data += chunk.toString();
    });

    pythonProcess.stderr.on('data', (error) => {
        errorOutput += error.toString();
        console.error(`stderr: ${error}`);
    });

    pythonProcess.on('close', (code) => {
        if (code !== 0) {
            console.error(`Python script exited with code ${code}`);
            console.error(`stderr: ${errorOutput}`);
            return res.status(500).send(`Error executing Python script: ${errorOutput}`);
        }
        try {
            const result = JSON.parse(data);
            console.log("HI there:");
            console.log(result);
            res.json(result);
        } catch (error) {
            console.error('Error parsing JSON response from Python script', error);
            res.status(500).send('Error parsing JSON response from Python script');
        }
    });
});

const PORT = 3001;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
