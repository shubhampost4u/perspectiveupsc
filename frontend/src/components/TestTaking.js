import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { 
  Clock, 
  CheckCircle2, 
  ArrowLeft, 
  ArrowRight,
  Flag,
  Timer,
  BookOpen,
  AlertTriangle
} from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '../App';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TestTaking = () => {
  const { testId } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();
  
  const [test, setTest] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [testStarted, setTestStarted] = useState(false);

  useEffect(() => {
    fetchTest();
  }, [testId]);

  useEffect(() => {
    let timer;
    if (testStarted && timeRemaining > 0) {
      timer = setInterval(() => {
        setTimeRemaining((prev) => {
          if (prev <= 1) {
            handleAutoSubmit();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [testStarted, timeRemaining]);

  const axiosConfig = {
    headers: { Authorization: `Bearer ${token}` }
  };

  const fetchTest = async () => {
    try {
      const response = await axios.get(`${API}/tests/${testId}/take`, axiosConfig);
      setTest(response.data);
      setTimeRemaining(response.data.duration_minutes * 60);
      setAnswers(new Array(response.data.questions.length).fill(-1));
      setLoading(false);
    } catch (error) {
      console.error('Error fetching test:', error);
      toast.error(error.response?.data?.detail || 'Failed to load test');
      navigate('/dashboard');
    }
  };

  const startTest = () => {
    setTestStarted(true);
    toast.success('Test started! Good luck!');
  };

  const selectAnswer = (questionIndex, optionIndex) => {
    const newAnswers = [...answers];
    newAnswers[questionIndex] = optionIndex;
    setAnswers(newAnswers);
  };

  const goToQuestion = (index) => {
    setCurrentQuestionIndex(index);
  };

  const nextQuestion = () => {
    if (currentQuestionIndex < test.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const previousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleAutoSubmit = async () => {
    toast.warning('Time up! Submitting test automatically...');
    await submitTest();
  };

  const submitTest = async () => {
    setSubmitting(true);
    try {
      const response = await axios.post(
        `${API}/tests/${testId}/submit`,
        { 
          answers,
          time_taken_minutes: Math.ceil((test.duration_minutes * 60 - timeRemaining) / 60)
        },
        axiosConfig
      );

      toast.success('Test submitted successfully!');
      
      // Show results immediately
      const result = response.data;
      navigate('/dashboard', { 
        state: { 
          showResult: true, 
          result: {
            score: result.score,
            total: result.total_questions,
            percentage: result.percentage,
            testTitle: test.title
          }
        }
      });
      
    } catch (error) {
      console.error('Error submitting test:', error);
      toast.error('Failed to submit test');
    } finally {
      setSubmitting(false);
    }
  };

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getAnsweredCount = () => {
    return answers.filter(answer => answer !== -1).length;
  };

  const getProgressPercentage = () => {
    return (getAnsweredCount() / test.questions.length) * 100;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading test...</p>
        </div>
      </div>
    );
  }

  if (!testStarted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center p-4">
        <Card className="max-w-2xl mx-auto glass-card shadow-2xl">
          <CardHeader className="text-center pb-4">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <BookOpen className="w-8 h-8 text-white" />
            </div>
            <CardTitle className="text-3xl font-bold text-gray-900">{test.title}</CardTitle>
            <p className="text-gray-600 mt-2">{test.description}</p>
          </CardHeader>
          
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 rounded-lg bg-blue-50 border border-blue-200">
                <Clock className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                <p className="font-semibold text-blue-900">Duration</p>
                <p className="text-blue-700">{test.duration_minutes} minutes</p>
              </div>
              
              <div className="text-center p-4 rounded-lg bg-green-50 border border-green-200">
                <BookOpen className="w-8 h-8 text-green-600 mx-auto mb-2" />
                <p className="font-semibold text-green-900">Questions</p>
                <p className="text-green-700">{test.questions.length} questions</p>
              </div>
              
              <div className="text-center p-4 rounded-lg bg-purple-50 border border-purple-200">
                <Flag className="w-8 h-8 text-purple-600 mx-auto mb-2" />
                <p className="font-semibold text-purple-900">Type</p>
                <p className="text-purple-700">Multiple Choice</p>
              </div>
            </div>

            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
                <div className="text-sm text-amber-800">
                  <p className="font-medium mb-2">Important Instructions:</p>
                  <ul className="list-disc list-inside space-y-1">
                    <li>You have {test.duration_minutes} minutes to complete this test</li>
                    <li>Each question has multiple choice answers</li>
                    <li>You can navigate between questions and change your answers</li>
                    <li>The test will auto-submit when time runs out</li>
                    <li>Make sure you have a stable internet connection</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="flex space-x-4">
              <Button
                onClick={() => navigate('/dashboard')}
                variant="outline"
                className="flex-1"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Button>
              
              <Button
                onClick={startTest}
                className="flex-1 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800"
              >
                Start Test
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const currentQuestion = test.questions[currentQuestionIndex];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-bold text-gray-900">{test.title}</h1>
              <Badge variant="outline">
                Question {currentQuestionIndex + 1} of {test.questions.length}
              </Badge>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className={`flex items-center space-x-2 px-3 py-1 rounded-lg ${
                timeRemaining < 300 ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'
              }`}>
                <Timer className={`w-4 h-4 ${timeRemaining < 300 ? 'timer-warning' : ''}`} />
                <span className="font-mono font-semibold">
                  {formatTime(timeRemaining)}
                </span>
              </div>
              
              <Button
                onClick={submitTest}
                disabled={submitting}
                className="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800"
              >
                {submitting ? 'Submitting...' : 'Submit Test'}
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Question Navigation Sidebar */}
          <div className="lg:col-span-1">
            <Card className="sticky top-24">
              <CardHeader className="pb-4">
                <CardTitle className="text-lg">Progress</CardTitle>
                <Progress value={getProgressPercentage()} className="mt-2" />
                <p className="text-sm text-gray-600 mt-1">
                  {getAnsweredCount()} of {test.questions.length} answered
                </p>
              </CardHeader>
              
              <CardContent className="space-y-4">
                <div className="grid grid-cols-5 gap-2">
                  {test.questions.map((_, index) => (
                    <button
                      key={index}
                      onClick={() => goToQuestion(index)}
                      className={`w-10 h-10 rounded-lg text-sm font-medium transition-all ${
                        index === currentQuestionIndex
                          ? 'bg-blue-600 text-white'
                          : answers[index] !== -1
                          ? 'bg-green-100 text-green-700 border border-green-300'
                          : 'bg-gray-100 text-gray-600 border border-gray-300 hover:bg-gray-200'
                      }`}
                    >
                      {index + 1}
                    </button>
                  ))}
                </div>
                
                <div className="text-xs space-y-1">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-blue-600 rounded"></div>
                    <span>Current</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-green-100 border border-green-300 rounded"></div>
                    <span>Answered</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-gray-100 border border-gray-300 rounded"></div>
                    <span>Not answered</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Question Area */}
          <div className="lg:col-span-3">
            <Card className="question-container">
              <CardHeader className="pb-6">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-xl">
                    Question {currentQuestionIndex + 1}
                  </CardTitle>
                  {answers[currentQuestionIndex] !== -1 && (
                    <Badge variant="default" className="bg-green-600">
                      <CheckCircle2 className="w-3 h-3 mr-1" />
                      Answered
                    </Badge>
                  )}
                </div>
              </CardHeader>
              
              <CardContent className="space-y-6">
                <div className="text-lg text-gray-900 leading-relaxed">
                  {currentQuestion.question_text}
                </div>
                
                <div className="space-y-3">
                  {currentQuestion.options.map((option, optionIndex) => (
                    <button
                      key={optionIndex}
                      onClick={() => selectAnswer(currentQuestionIndex, optionIndex)}
                      className={`option-button w-full p-4 text-left rounded-lg transition-all ${
                        answers[currentQuestionIndex] === optionIndex
                          ? 'selected'
                          : ''
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                          answers[currentQuestionIndex] === optionIndex
                            ? 'border-white bg-white'
                            : 'border-gray-300'
                        }`}>
                          {answers[currentQuestionIndex] === optionIndex && (
                            <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
                          )}
                        </div>
                        <span className="font-medium">
                          {String.fromCharCode(65 + optionIndex)}.
                        </span>
                        <span className="flex-1">{option}</span>
                      </div>
                    </button>
                  ))}
                </div>
                
                {/* Navigation Buttons */}
                <div className="flex items-center justify-between pt-6 border-t">
                  <Button
                    onClick={previousQuestion}
                    disabled={currentQuestionIndex === 0}
                    variant="outline"
                  >
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Previous
                  </Button>
                  
                  <div className="text-sm text-gray-600">
                    {currentQuestionIndex + 1} of {test.questions.length}
                  </div>
                  
                  <Button
                    onClick={nextQuestion}
                    disabled={currentQuestionIndex === test.questions.length - 1}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    Next
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TestTaking;