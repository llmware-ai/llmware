if (process.env.NODE_ENV != "production") {
  require("dotenv").config();
}

const cloudinary = require("cloudinary").v2;
const express = require("express");
const { spawn } = require('child_process'); 
const app = express();
const fs = require("fs");
const mongoose = require("mongoose");
const path = require("path");
const methodOverride = require("method-override");
const ejsMate = require("ejs-mate");
const User = require("./model/user.js");
const Profile = require("./model/profile.js");

const session = require("express-session");
const busboy = require('busboy');
const axios = require('axios');

const bodyParser = require("body-parser");
const MongoStore = require("connect-mongo");
const LocalStrategy = require("passport-local");
const passport = require("passport");
const flash = require("connect-flash");
const { isLoggedIn } = require("./middleware.js");
const multer = require("multer");

const dbUrl = process.env.ATLASDB_URL;
// const { storage } = require("./cloudConfig.js");
if (dbUrl) {
  console.log("DB URL is set");
}

app.locals.AppName = 'Diksha';

async function extractImage(url) {
  try {
    const response = await axios({
      method: 'GET',
      url: url,
      responseType: 'arraybuffer'
    });
    return response.data;
  } catch (error) {
    console.error('Error extracting image:', error);
    throw error;
  }
}


const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, 'uploads/');
  },
  filename: function (req, file, cb) {
    cb(null, file.originalname);
  }
});

const upload1 = multer({ 
  dest: 'uploads/',
  fileFilter: (req, file, cb) => {
      // Only allow PDF files
      if (file.mimetype === 'application/pdf') {
          cb(null, true);
      } else {
          cb(new Error('Only PDF files are allowed'), false);
      }
  }
});

const upload = multer({ storage });

const store = MongoStore.create({
  mongoUrl: process.env.ATLASDB_URL,
  crypto: {
    secret: process.env.SECRET,
  },
  touchAfter: 24 * 60 * 60,
});

store.on("error", (error) => {
  console.log("Error in MONGO SESSION STORE: ", error);
});

const sessionOptions = {
  store,
  secret: process.env.SECRET,
  resave: false,
  saveUninitialized: true,
  cookie: {
    expires: Date.now() + 7 * 24 * 60 * 60 * 1000,
    maxAge: 7 * 24 * 60 * 60 * 1000,
    httpOnly: true,
  },
};

app.use(session(sessionOptions));
app.use(flash());

app.use(bodyParser.urlencoded({ extended: true }));
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "/views"));
app.use(express.static(path.join(__dirname, "public")));
app.use("public/images/", express.static("./public/images"));
app.use(express.urlencoded({ extended: true }));
app.use(methodOverride("_method"));
app.engine("ejs", ejsMate);
app.use(express.json());

async function main() {
  await mongoose.connect(process.env.ATLASDB_URL);
}

main()
  .then(() => {
    console.log("Connection Succeeded");
  })
  .catch((err) => console.log(err));

app.use(passport.initialize());
app.use(passport.session());
passport.use(new LocalStrategy(User.authenticate()));

passport.serializeUser(User.serializeUser());
passport.deserializeUser(User.deserializeUser());

app.use((req, res, next) => {
  res.locals.success = req.flash("success");
  res.locals.error = req.flash("error");
  res.locals.currUser = req.user;
  next();
});

let port = 8080;
app.listen(port, () => {
  console.log("listening to the port " + port);
});

// Routes
app.get("/index", isLoggedIn, (req, res) => {
  res.render("index.ejs");
});

app.get("/about", isLoggedIn, (req, res) => {
  res.render("about.ejs");
});

app.get("/contact", isLoggedIn, (req, res) => {
  res.render("contact.ejs");
});

app.get("/team", isLoggedIn, (req, res) => {
  res.render("team.ejs");
});

app.get("/testimonial", isLoggedIn, (req, res) => {
  res.render("testimonial.ejs");
});

app.get("/courses", isLoggedIn, (req, res) => {
  res.render("courses.ejs");
});

app.get("/form", isLoggedIn, (req, res) => {
  res.render("form.ejs");
});

app.get("/search", isLoggedIn, (req, res) => {
  res.render("search.ejs");
});

app.get("/syllabus", isLoggedIn, (req, res) => {
  res.render("syllabus.ejs");
});

app.get("/ask", isLoggedIn, (req, res) => {
  res.render("ask.ejs");
});

app.get("/chat", isLoggedIn, (req, res) => {
  res.render("chat.ejs");
});

app.get("/main", (req, res) => {
  res.render("main.ejs");
});

app.get("/login", (req, res) => {
  res.render("login.ejs");
});
app.get("/grading", isLoggedIn, (req, res) => {
  res.render("grading.ejs");
});

app.post(
  "/login",
  passport.authenticate("local", {
    failureRedirect: "/login",
    failureFlash: true,
  }),
  async (req, res) => {
    let { username } = req.body;
    req.session.user = { username };
    req.flash("success", "Welcome to EduFlex!");
    res.redirect("/user/home");
  }
);

app.get("/signup", (req, res) => {
  res.render("signup.ejs");
});

app.post("/signup", async (req, res) => {
  try {
    let { username, email, phone, password } = req.body;
    req.session.user = { username, email, phone };
    const newUser = new User({ username, email, phone });

    await User.register(newUser, password);

    const newProfile = new Profile({
      user: newUser._id,
      gender: "",
      bio: "",
    });
    await newProfile.save();
    res.redirect("/login");
  } catch (e) {
    res.redirect("/signup");
  }
});

app.post("/syllabus", isLoggedIn, async (req, res) => {
  try {
    let { std, subject } = req.body;
    let result = await syllabusGen(std, subject);
    res.render("syl.ejs", { result });
  } catch (error) {
    console.error("Error:", error);
    res.status(500).send("Internal Server Error");
  }
});


app.post("/ask", isLoggedIn, async (req, res) => {
  try {
    let { question } = req.body;
    let result = await textQuery(question);
    res.render("ask2.ejs", { result });
  } catch (error) {
    console.error("Error:", error);
    res.status(500).send("Internal Server Error");
  }
});


app.post("/chat", isLoggedIn, async (req, res) => {
  try {
    const userInput = req.body.message;

    // Replace Gemini Pro with axios request to your local chat service
    const response = await axios.post('http://localhost:5000/chat', {
      prompt: userInput,
      model: 'llama-2-7b-chat-gguf' // You can change this model as needed
    });

    res.json({ message: response.data.response });
  } catch (error) {
    console.error("Error:", error);
    res.status(500).json({ message: "Internal Server Error" });
  }
});


// Directory for saving uploaded files
const UPLOAD_DIR = path.join(__dirname, 'uploads');
if (!fs.existsSync(UPLOAD_DIR)) {
    fs.mkdirSync(UPLOAD_DIR);
}

const uploadDir = path.join(__dirname, 'uploads');
// const storage = multer.diskStorage({
//   destination: (req, file, cb) => {
//       if (!fs.existsSync(uploadDir)) {
//           fs.mkdirSync(uploadDir);
//       }
//       cb(null, uploadDir);
//   },
//   filename: (req, file, cb) => {
//       cb(null, file.originalname);
//   }
// });


app.get('/analyze-pdf', (req, res) => {
  res.render('pdf.ejs'); // Assumes the EJS file is saved as views/index.ejs
});

app.get("/flashcard", (req, res) => {
  res.render("flashcard.ejs");
})
app.get("/results", (req, res) => {
  res.render("results.ejs");
})
app.get("/newsletter", (req, res) => {
  res.render("newsletter.ejs");
})
app.get("/news", (req, res) => {
  res.render("news.ejs");
})
app.get("/platform", (req, res) => {
  res.render("platform.ejs");
})
app.get("/school", (req, res) => {
  res.render("school.ejs");
})
app.get("/teacher", (req, res) => {
  res.render("teacher.ejs");
})

app.post('/form', isLoggedIn, upload.single('image'), async (req, res) => {
  try {
    const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
    const prompt = '';
    const imageParts = [{
      inlineData: {
        data: fs.readFileSync(req.file.path).toString('base64'),
        mimeType: 'image/jpeg'
      }
    }];

    console.log(req.file.path);

    const result = await model.generateContent([prompt, ...imageParts]);
    const response = await result.response;
    const text = response.text();

    res.json({ result: text }); // Sends JSON response
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'Internal server error' }); // Error response
  }
});


// Set up a route for logging out
app.get('/logout', (req, res, next) => {
  req.logout(function (err) {
    if (err) {
      console.error("Error logging out:", err);
      return next(err); // Forward the error to the error handler
    }
    res.redirect('/login'); // Only one response
  });
});


async function quizGenerator(topic) {
  const model = genAI.getGenerativeModel({ model: "gemini-pro" });
  const prompt = `Based on the topic of ${topic} in the context of Engineering, create a multiple-choice quiz with 8 questions. Please format the response only in JSON (no extra things) with the following structure:
{
  "title": "MCQ Quiz on ${topic}",
  "questions": [
    {
      "question": "Question text here",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correctAnswer": "Correct answer text here"
    },
    {
      "question": "Next question text here",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correctAnswer": "Correct answer text here"
    }
    // Repeat for all 10 questions
  ]
}
Make sure that:
- Strictly Do not include any preamble.
- Each question has 4 answer options.
- Provide the correct answer for each question under "correctAnswer".
`;
  const result = await model.generateContent(prompt);
  const response = await result.response;
  const text = response.text();

  return text;
}



app.get("/practice", (req, res) => {
  res.render("practice.ejs");
});

app.post("/practice", async (req, res) => {
  try {
    const { topic } = req.body;
    const generatedQuiz = await quizGenerator(topic);
    // Log the raw generated quiz

    // Attempt to parse the generated quiz string into an object
    const quiz = JSON.parse(generatedQuiz);
    req.session.quiz = quiz; // Store the generated quiz in the session

    res.render("quiz.ejs", { quiz }); // Render the quiz page with the generated quiz
  } catch (err) {
    console.error("Error generating quiz:", err);
    res.status(500).send("Error generating quiz. Please try again.");
  }
});

app.post("/submit-quiz", (req, res) => {


  const userAnswers = req.body.userAnswers;
  const quiz = req.session.quiz;

  if (!quiz) {
    console.error("Quiz not found in session");
    return res.status(400).json({ error: "Quiz not found in session." });
  }

  let correctCount = 0;
  const results = quiz.questions.map((question, index) => {
    const correctAnswer = question.correctAnswer;
    const userAnswer = userAnswers[`q${index}`];
    const isCorrect = userAnswer === correctAnswer;
    if (isCorrect) correctCount++;
    return {
      question: question.question,
      userAnswer,
      correctAnswer,
      isCorrect,
    };
  });

  res.json({
    correctCount,
    totalQuestions: quiz.questions.length,
    results,
  });
});



app.all("*", (req, res) => {
  res.redirect("/index");
});



const { GoogleGenerativeAI } = require("@google/generative-ai");

const dotenv = require("dotenv");
dotenv.config();

const genAI = new GoogleGenerativeAI(process.env.API_KEY);

function fileToGenerativePart(path, mimeType) {
  return {
    inlineData: {
      data: Buffer.from(fs.readFileSync(path)).toString("base64"),
      mimeType
    },
  };
}


async function problemSolving() {
  const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
  const prompt = "";
  const imageParts = [
    fileToGenerativePart("prob.jpg", "image/jpeg"),
  ];
  const result = await model.generateContent([prompt, ...imageParts]);
  const response = await result.response;
  const text = response.text();
  console.log(text);
  return text;
}

async function textQuery(query) {
  const model = genAI.getGenerativeModel({ model: "gemini-pro" });
  const result = await model.generateContent(query);
  const response = await result.response;
  const text = response.text();
  return text;
}

async function syllabusGen(std, sub) {
  const model = genAI.getGenerativeModel({ model: "gemini-pro" });
  const prompt = `Generate the Syllabus of ${std} for the subject ${sub} based on current National Educational Policy and always keep in mind the class of a student.Only generate the syllabus according the class age.`;
  const result = await model.generateContent(prompt);
  const response = await result.response;
  const text = response.text();
  return text;
}
