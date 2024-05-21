const express = require("express");
const app = express();
const cors = require("cors");
const paper = require("./routes/paper");

app.use(cors());
app.use(express.json());
app.use(express.text());

require("dotenv").config();

const port = process.env.PORT || 3000;

app.use("/api/v1", paper);

const start = () => {
  app.listen(port, () => {
    console.log(`server is listening on port ${port}`);
  });
};

start();
