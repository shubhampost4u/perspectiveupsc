import React, { useState, useEffect } from 'react';
import ApiService from '../services/api.service';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const TestInterface = () => {
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadQuestions = async () => {
      try {
        setLoading(true);
        const data = await ApiService.fetchQuestions();
        setQuestions(data);
      } catch (error) {
        console.error('Failed to load questions');
        setError('Failed to load questions. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    loadQuestions();
  }, []);

  const handleAnswer = (questionIndex, optionIndex) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [questionIndex]: optionIndex
    }));
  };

  if (loading) return <div>Loading questions...</div>;
  if (error) return <div>{error}</div>;
  if (questions.length === 0) return <div>No questions available.</div>;

  return (
    <div className="max-w-4xl mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle>
            Question {currentQuestion + 1} of {questions.length}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <p className="text-lg font-medium">{questions[currentQuestion].question}</p>
          </div>
          <div className="space-y-2">
            {questions[currentQuestion].options.map((option, idx) => (
              <Button
                key={idx}
                className={`w-full text-left justify-start ${
                  selectedAnswers[currentQuestion] === idx ? 'bg-blue-100' : ''
                }`}
                variant="outline"
                onClick={() => handleAnswer(currentQuestion, idx)}
              >
                {option}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>
      
      <div className="flex justify-between mt-4">
        <Button
          onClick={() => setCurrentQuestion(prev => Math.max(0, prev - 1))}
          disabled={currentQuestion === 0}
        >
          Previous
        </Button>
        <Button
          onClick={() => setCurrentQuestion(prev => Math.min(questions.length - 1, prev + 1))}
          disabled={currentQuestion === questions.length - 1}
        >
          Next
        </Button>
      </div>
    </div>
  );
};

export default TestInterface;