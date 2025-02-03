// server.js
const express = require('express');
const multer = require('multer');
const xlsx = require('xlsx');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

// MongoDB Question Schema
const questionSchema = new mongoose.Schema({
  question: String,
  options: [String],
  correctAnswer: Number,
  category: String,
  marks: Number
});

const Question = mongoose.model('Question', questionSchema);

// Configure multer for file upload
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// Route to handle Excel file upload
app.post('/api/upload-questions', upload.single('file'), async (req, res) => {
  try {
    const workbook = xlsx.read(req.file.buffer, { type: 'buffer' });
    const sheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[sheetName];
    const questions = xlsx.utils.sheet_to_json(worksheet);

    // Transform and save questions
    const formattedQuestions = questions.map(q => ({
      question: q.Question,
      options: [q.Option1, q.Option2, q.Option3, q.Option4],
      correctAnswer: parseInt(q.CorrectAnswer),
      category: q.Category,
      marks: parseInt(q.Marks) || 1
    }));

    await Question.insertMany(formattedQuestions);
    res.json({ success: true, message: 'Questions uploaded successfully' });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Route to get questions
app.get('/api/questions', async (req, res) => {
  try {
    const questions = await Question.find({});
    res.json(questions);
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
