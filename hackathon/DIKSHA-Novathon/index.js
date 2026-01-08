const { GoogleGenerativeAI } = require("@google/generative-ai");
const fs = require("fs");


const dotenv = require("dotenv");
dotenv.config();

// Access your API key as an environment variable (see "Set up your API key" above)
const genAI = new GoogleGenerativeAI(process.env.API_KEY);

const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

function fileToGenerativePart(path, mimeType) {
    return {
      inlineData: {
        data: Buffer.from(fs.readFileSync(path)).toString("base64"),
        mimeType
      },
    };
  }
  
  async function problemSolving() {
    // For text-and-image input (multimodal), use the gemini-pro-vision model
    const model = genAI.getGenerativeModel({ model: "gemini-pro-vision" });
  
    const prompt = "";
  
    const imageParts = [
      fileToGenerativePart("prob.jpg", "image/jpeg"),
    //   fileToGenerativePart("image2.jpeg", "image/jpeg"),
    ];
  
    const result = await model.generateContent([prompt, ...imageParts]);
    const response = await result.response;
    const text = response.text();
    console.log(text);
  }
  
  // problemSolving();

async function textQuery() {
    // For text-only input, use the gemini-pro model
    const model = genAI.getGenerativeModel({ model: "gemini-pro"});
  
    const prompt = "What is Newton's First Law ?"
  
    const result = await model.generateContent(prompt);
    const response = await result.response;
    const text = response.text();
    console.log(text);
  }
  
  // textQuery();


async function chatBot() {
  // For text-only input, use the gemini-pro model
  const model = genAI.getGenerativeModel({ model: "gemini-pro"});

  const chat = model.startChat({
    history: [],
    generationConfig: {
      maxOutputTokens: 100,
    },
  });

  async function askAndRespond(){
    rl.question("You: ", async(msg)=>{
      if(msg.toLowerCase() === "exit"){
        rl.close();
      }
      else{
        const result = await model.generateContent(msg);
        const response = await result.response;
        const text = await response.text();
        console.log("AI: ", text);
        askAndRespond();
      }
    });
  }
  askAndRespond();
}

chatBot();
