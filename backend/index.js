import express from "express"; //simplifies building and managing web servers
import bodyParser from "body-parser"; //simplifies parsing body of incoming requests
import cors from "cors";
import OpenAI from "openai";
import path from "path";
import { fileURLToPath } from "url";
import fs from "fs";
import multer from "multer";

import dotenv from "dotenv";
dotenv.config();

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

const openai = new OpenAI({
  apiKey: OPENAI_API_KEY,
  //apiKey: process.env.OPENAI_API_KEY // This is the default when it stored as an environment variable
});
const app = express(); //create a new express app
const port = 3000; //

app.use(bodyParser.json()); //automatically parse incoming request bodies that are in JSON format
app.use(cors());

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const upload = multer({ dest: "uploads/" });

app.post("/upload", upload.single("file"), (req, res) => {
  console.log("File saved to:", req.file.path);
  res.json({ status: "ok", filename: req.file.originalname });
});

app.post("/hypnosisAudio", async (req, res) => {
  try {
    // Path to the previously saved audio file
    const audioFilePath = path.join(__dirname, "generated_audio.mp3");

    // Check if the file exists
    if (!fs.existsSync(audioFilePath)) {
      return res.status(404).json({ error: "Audio file not found" });
    }

    setTimeout(() => {
      const audioData = fs.readFileSync(audioFilePath);

      // Send the saved audio file
      res.set("Content-Type", "audio/mp3");
      res.send(Buffer.from(audioData));

      console.log("Saved audio file sent successfully:", audioFilePath);
    }, 4000); // 2000 ms = 2 seconds
  } catch (error) {
    console.error("Error sending audio file:", error);
    res
      .status(500)
      .json({ error: "An error occurred while sending the audio file" });
  }
});

app.post("/regular", async (req, res) => {
  const { messages } = req.body; //get the messages from the request body

  const completion = await openai.chat.completions.create({
    //send the messages to GPT
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: "Continue the conversatioon" },
      // {role: "user", content: `${message}`},
      ...messages,
    ],
  });

  res.json({
    //send the completion back to the frontend
    completion: completion.choices[0].message.content,
  });

  console.log("complex reflection api sent result");
});

app.post("/remember", async (req, res) => {
  const { messages } = req.body; //get the messages from the request body

  const completion = await openai.chat.completions.create({
    //send the messages to GPT
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content:
          "Following Bloom's Taxonomy, ask a question that requires remembering infromation. Print only the question.",
      },
      // {role: "user", content: `${message}`},
      ...messages,
    ],
  });

  res.json({
    //send the completion back to the frontend
    completion: completion.choices[0].message.content,
  });

  console.log("hypnotherapy api sent result");
});

app.post("/understand", async (req, res) => {
  const { messages } = req.body; //get the messages from the request body

  const completion = await openai.chat.completions.create({
    //send the messages to GPT
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content:
          "Following Blooms Taxonomy, ask a quesustion that requires understanding. Print only the question.",
      },
      // {role: "user", content: `${message}`},
      ...messages,
    ],
  });

  res.json({
    //send the completion back to the frontend
    completion: completion.choices[0].message.content,
  });

  console.log("hypnotherapy api sent result");
});

app.post("/apply", async (req, res) => {
  const { messages } = req.body; //get the messages from the request body

  const completion = await openai.chat.completions.create({
    //send the messages to GPT
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content:
          "Following Blooms Taxonomy, ask quesustion that requires application. Print only the question.",
      },
      // {role: "user", content: `${message}`},
      ...messages,
    ],
  });

  res.json({
    //send the completion back to the frontend
    completion: completion.choices[0].message.content,
  });

  console.log("hypnotherapy api sent result");
});

app.post("/analyze", async (req, res) => {
  const { messages } = req.body; //get the messages from the request body

  const completion = await openai.chat.completions.create({
    //send the messages to GPT
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content:
          "Following Blooms Taxonomy, ask quesustion that requires analysis. Print only the question.",
      },
      // {role: "user", content: `${message}`},
      ...messages,
    ],
  });

  res.json({
    //send the completion back to the frontend
    completion: completion.choices[0].message.content,
  });

  console.log("hypnotherapy api sent result");
});

app.listen(port, () => {
  //start the server at port 3000
  console.log(`exammple app listening at http://localhost:${port}`);
});
