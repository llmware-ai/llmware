const { PythonShell } = require("python-shell");
const fs = require("fs").promises;

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const Model = async (req, res) => {
  // console.log(req.body);
  let options = {
    scriptPath: "../model",
  };

  try {
    await fs.writeFile("../media/paper.txt", req.body);
    console.log("Starting Point...");
    const pythonRes = await PythonShell.run("model.py", options);
    console.log(pythonRes);

    let jsonData;
    while (true) {
      try {
        const data = await fs.readFile("../media/response.json", "utf8");
        console.log(data);
        jsonData = JSON.parse(data);
        res.json(jsonData);
        break;
      } catch (error) {
        console.error("File not found. Retrying...");
        await wait(5000);
      }
    }
  } catch (error) {
    console.error(error);
    res.status(500).json({
      error: "Internal Server Error",
    });
  }
};

const testing = async (req, res) => {
  res.send("Hello Baba!");
};

const qna = async (req, res) => {
  try {
    let question = req.body.question;
    let options = {
      scriptPath: "../model",
      args: [question],
    };
    const pythonRes = await PythonShell.run("qna.py", options);
    res.send(pythonRes);
  } catch (error) {
    console.error("Error in qna function:", error);
    res.status(500).json({
      error: error.message || "Internal Server Error",
    });
  }
};

module.exports = { testing, Model, qna };
