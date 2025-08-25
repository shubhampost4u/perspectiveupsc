import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { 
  ArrowLeft, 
  CheckCircle2, 
  XCircle, 
  BookOpen, 
  Clock,
  Target,
  Award
} from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '../App';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TestSolutions = () => {
  const { testId } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();
  
  const [solutions, setSolutions] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSolutions();
  }, [testId]);

  const axiosConfig = {
    headers: { Authorization: `Bearer ${token}` }
  };

  const fetchSolutions = async () => {
    try {
      const response = await axios.get(`${API}/test-solutions/${testId}`, axiosConfig);
      setSolutions(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching solutions:', error);
      toast.error(error.response?.data?.detail || 'Failed to load solutions');
      navigate('/dashboard');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading solutions...</p>
        </div>
      </div>
    );
  }

  if (!solutions) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50">
        <Card className="max-w-md mx-auto text-center p-6">
          <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">Solutions Not Available</h2>
          <p className="text-gray-600 mb-4">Complete the test first to view solutions.</p>
          <Button onClick={() => navigate('/dashboard')}>
            Back to Dashboard
          </Button>
        </Card>
      </div>
    );
  }

  const getScoreColor = (percentage) => {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-blue-600';
    if (percentage >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreIcon = (percentage) => {
    if (percentage >= 80) return <Award className="w-8 h-8 text-green-600" />;
    if (percentage >= 60) return <Target className="w-8 h-8 text-blue-600" />;
    return <BookOpen className="w-8 h-8 text-orange-600" />;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <Button
                onClick={() => navigate('/dashboard')}
                variant="outline"
                size="sm"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Button>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Test Solutions</h1>
                <p className="text-sm text-gray-600">{solutions.test_title}</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Score Summary */}
        <Card className="mb-8">
          <CardContent className="p-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                {getScoreIcon(solutions.percentage)}
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Your Performance</h2>
                  <p className="text-gray-600">Test completed on {new Date(solutions.completed_at).toLocaleDateString()}</p>
                </div>
              </div>
              
              <div className="text-right">
                <div className={`text-4xl font-bold ${getScoreColor(solutions.percentage)}`}>
                  {solutions.percentage}%
                </div>
                <p className="text-gray-600">
                  {solutions.student_score} out of {solutions.total_questions} correct
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Solutions */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">Detailed Solutions</h2>
            <div className="flex items-center space-x-4">
              <Badge variant="outline" className="text-green-600 border-green-600">
                <CheckCircle2 className="w-4 h-4 mr-1" />
                {solutions.solutions.filter(s => s.is_correct).length} Correct
              </Badge>
              <Badge variant="outline" className="text-red-600 border-red-600">
                <XCircle className="w-4 h-4 mr-1" />
                {solutions.solutions.filter(s => !s.is_correct).length} Incorrect
              </Badge>
            </div>
          </div>

          {solutions.solutions.map((solution, index) => (
            <Card key={index} className={`border-l-4 ${
              solution.is_correct ? 'border-l-green-500' : 'border-l-red-500'
            }`}>
              <CardHeader className="pb-4">
                <div className="flex items-start justify-between">
                  <CardTitle className="text-lg">
                    Question {solution.question_number}
                  </CardTitle>
                  <Badge 
                    variant={solution.is_correct ? "success" : "destructive"}
                    className={solution.is_correct ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}
                  >
                    {solution.is_correct ? (
                      <>
                        <CheckCircle2 className="w-3 h-3 mr-1" />
                        Correct
                      </>
                    ) : (
                      <>
                        <XCircle className="w-3 h-3 mr-1" />
                        Incorrect
                      </>
                    )}
                  </Badge>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-6">
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">{solution.question_text}</h3>
                  
                  <div className="space-y-2">
                    {solution.options.map((option, optIndex) => {
                      const isCorrect = optIndex === solution.correct_answer;
                      const isStudentAnswer = optIndex === solution.student_answer;
                      
                      return (
                        <div
                          key={optIndex}
                          className={`p-3 rounded-lg border-2 transition-all ${
                            isCorrect 
                              ? 'border-green-500 bg-green-50' 
                              : isStudentAnswer && !isCorrect
                              ? 'border-red-500 bg-red-50'
                              : 'border-gray-200 bg-gray-50'
                          }`}
                        >
                          <div className="flex items-center space-x-3">
                            <span className={`w-6 h-6 rounded-full flex items-center justify-center text-sm font-medium ${
                              isCorrect 
                                ? 'bg-green-600 text-white'
                                : isStudentAnswer && !isCorrect
                                ? 'bg-red-600 text-white'
                                : 'bg-gray-400 text-white'
                            }`}>
                              {String.fromCharCode(65 + optIndex)}
                            </span>
                            <span className="flex-1">{option}</span>
                            <div className="flex items-center space-x-2">
                              {isCorrect && (
                                <Badge variant="outline" className="text-green-600 border-green-600 text-xs">
                                  Correct Answer
                                </Badge>
                              )}
                              {isStudentAnswer && (
                                <Badge variant="outline" className={`text-xs ${
                                  isCorrect ? 'text-green-600 border-green-600' : 'text-red-600 border-red-600'
                                }`}>
                                  Your Answer
                                </Badge>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {solution.explanation && (
                  <div className="border-t pt-4">
                    <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                      <BookOpen className="w-4 h-4 mr-2" />
                      Explanation
                    </h4>
                    <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                      <p className="text-gray-700 leading-relaxed">{solution.explanation}</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Back Button */}
        <div className="text-center mt-8">
          <Button
            onClick={() => navigate('/dashboard')}
            className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>
        </div>
      </div>
    </div>
  );
};

export default TestSolutions;