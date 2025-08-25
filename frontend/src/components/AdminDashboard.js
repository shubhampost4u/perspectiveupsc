import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { 
  Plus, 
  BookOpen, 
  Users, 
  BarChart3, 
  Settings, 
  LogOut,
  Edit,
  Trash2,
  Clock,
  DollarSign,
  CheckCircle2,
  Upload,
  Download,
  FileSpreadsheet,
  AlertCircle,
  Info
} from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '../App';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminDashboard = () => {
  const { user, logout, token } = useAuth();
  const [tests, setTests] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateTest, setShowCreateTest] = useState(false);

  const [testForm, setTestForm] = useState({
    title: '',
    description: '',
    price: '',
    duration_minutes: '',
    questions: []
  });

  const [currentQuestion, setCurrentQuestion] = useState({
    question_text: '',
    options: ['', '', '', ''],
    correct_answer: 0,
    explanation: ''
  });

  useEffect(() => {
    fetchTests();
    fetchStudents();
  }, []);

  const axiosConfig = {
    headers: { Authorization: `Bearer ${token}` }
  };

  const fetchTests = async () => {
    try {
      const response = await axios.get(`${API}/admin/tests`, axiosConfig);
      setTests(response.data);
    } catch (error) {
      console.error('Error fetching tests:', error);
      toast.error('Failed to fetch tests');
    }
  };

  const fetchStudents = async () => {
    try {
      const response = await axios.get(`${API}/admin/students`, axiosConfig);
      setStudents(response.data);
    } catch (error) {
      console.error('Error fetching students:', error);
      toast.error('Failed to fetch students');
    }
  };

  const handleTestFormChange = (e) => {
    setTestForm({
      ...testForm,
      [e.target.name]: e.target.value
    });
  };

  const handleQuestionChange = (e) => {
    const { name, value } = e.target;
    if (name.startsWith('option_')) {
      const index = parseInt(name.split('_')[1]);
      const newOptions = [...currentQuestion.options];
      newOptions[index] = value;
      setCurrentQuestion({
        ...currentQuestion,
        options: newOptions
      });
    } else {
      setCurrentQuestion({
        ...currentQuestion,
        [name]: value
      });
    }
  };

  const addQuestion = () => {
    if (!currentQuestion.question_text || currentQuestion.options.some(opt => !opt.trim())) {
      toast.error('Please fill in all question fields');
      return;
    }

    setTestForm({
      ...testForm,
      questions: [...testForm.questions, { ...currentQuestion }]
    });

    setCurrentQuestion({
      question_text: '',
      options: ['', '', '', ''],
      correct_answer: 0,
      explanation: ''
    });

    toast.success('Question added successfully');
  };

  const removeQuestion = (index) => {
    const newQuestions = testForm.questions.filter((_, i) => i !== index);
    setTestForm({
      ...testForm,
      questions: newQuestions
    });
    toast.success('Question removed');
  };

  const createTest = async () => {
    if (!testForm.title || !testForm.description || testForm.questions.length === 0) {
      toast.error('Please fill in all required fields and add at least one question');
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API}/admin/tests`, {
        ...testForm,
        price: parseFloat(testForm.price),
        duration_minutes: parseInt(testForm.duration_minutes)
      }, axiosConfig);

      toast.success('Test created successfully!');
      setShowCreateTest(false);
      setTestForm({
        title: '',
        description: '',
        price: '',
        duration_minutes: '',
        questions: []
      });
      fetchTests();
    } catch (error) {
      console.error('Error creating test:', error);
      toast.error('Failed to create test');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Admin Dashboard</h1>
                <p className="text-sm text-gray-600">Welcome back, {user?.name}</p>
              </div>
            </div>
            <Button
              onClick={handleLogout}
              variant="outline"
              className="text-gray-600 hover:text-gray-900"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="tests">Tests</TabsTrigger>
            <TabsTrigger value="students">Students</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="card-hover">
                <CardContent className="p-6">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                      <BookOpen className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-gray-900">{tests.length}</p>
                      <p className="text-gray-600">Total Tests</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="card-hover">
                <CardContent className="p-6">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                      <Users className="w-6 h-6 text-green-600" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-gray-900">{students.length}</p>
                      <p className="text-gray-600">Active Students</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="card-hover">
                <CardContent className="p-6">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                      <BarChart3 className="w-6 h-6 text-purple-600" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-gray-900">
                        ${tests.reduce((sum, test) => sum + test.price, 0).toFixed(2)}
                      </p>
                      <p className="text-gray-600">Total Value</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Dialog open={showCreateTest} onOpenChange={setShowCreateTest}>
                  <DialogTrigger asChild>
                    <Button className="h-20 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800">
                      <Plus className="w-5 h-5 mr-2" />
                      Create New Test
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
                    <DialogHeader>
                      <DialogTitle>Create New Test</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-6">
                      {/* Test Details */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <Label>Test Title</Label>
                          <Input
                            name="title"
                            value={testForm.title}
                            onChange={handleTestFormChange}
                            placeholder="Enter test title"
                          />
                        </div>
                        <div>
                          <Label>Price ($)</Label>
                          <Input
                            name="price"
                            type="number"
                            step="0.01"
                            value={testForm.price}
                            onChange={handleTestFormChange}
                            placeholder="Enter price"
                          />
                        </div>
                      </div>

                      <div>
                        <Label>Description</Label>
                        <Textarea
                          name="description"
                          value={testForm.description}
                          onChange={handleTestFormChange}
                          placeholder="Enter test description"
                          rows={3}
                        />
                      </div>

                      <div>
                        <Label>Duration (minutes)</Label>
                        <Input
                          name="duration_minutes"
                          type="number"
                          value={testForm.duration_minutes}
                          onChange={handleTestFormChange}
                          placeholder="Enter duration in minutes"
                        />
                      </div>

                      {/* Questions Section */}
                      <div className="border-t pt-6">
                        <h3 className="text-lg font-semibold mb-4">Add Questions</h3>
                        
                        {/* Current Questions */}
                        {testForm.questions.length > 0 && (
                          <div className="mb-6 space-y-4">
                            <h4 className="font-medium">Added Questions ({testForm.questions.length})</h4>
                            {testForm.questions.map((q, index) => (
                              <Card key={index} className="p-4">
                                <div className="flex justify-between items-start">
                                  <div className="flex-1">
                                    <p className="font-medium">{index + 1}. {q.question_text}</p>
                                    <div className="mt-2 space-y-1">
                                      {q.options.map((option, optIndex) => (
                                        <p key={optIndex} className={`text-sm ${optIndex === q.correct_answer ? 'text-green-600 font-medium' : 'text-gray-600'}`}>
                                          {String.fromCharCode(65 + optIndex)}. {option}
                                          {optIndex === q.correct_answer && ' ✓'}
                                        </p>
                                      ))}
                                    </div>
                                  </div>
                                  <Button
                                    onClick={() => removeQuestion(index)}
                                    variant="outline"
                                    size="sm"
                                    className="text-red-600 hover:text-red-700"
                                  >
                                    <Trash2 className="w-4 h-4" />
                                  </Button>
                                </div>
                              </Card>
                            ))}
                          </div>
                        )}

                        {/* Add New Question */}
                        <Card className="p-4">
                          <div className="space-y-4">
                            <div>
                              <Label>Question Text</Label>
                              <Textarea
                                name="question_text"
                                value={currentQuestion.question_text}
                                onChange={handleQuestionChange}
                                placeholder="Enter the question"
                                rows={2}
                              />
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              {currentQuestion.options.map((option, index) => (
                                <div key={index}>
                                  <Label>Option {String.fromCharCode(65 + index)}</Label>
                                  <Input
                                    name={`option_${index}`}
                                    value={option}
                                    onChange={handleQuestionChange}
                                    placeholder={`Enter option ${String.fromCharCode(65 + index)}`}
                                  />
                                </div>
                              ))}
                            </div>

                            <div>
                              <Label>Correct Answer</Label>
                              <select
                                name="correct_answer"
                                value={currentQuestion.correct_answer}
                                onChange={(e) => setCurrentQuestion({
                                  ...currentQuestion,
                                  correct_answer: parseInt(e.target.value)
                                })}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                              >
                                {currentQuestion.options.map((_, index) => (
                                  <option key={index} value={index}>
                                    Option {String.fromCharCode(65 + index)}
                                  </option>
                                ))}
                              </select>
                            </div>

                            <div>
                              <Label>Explanation (Optional)</Label>
                              <Textarea
                                name="explanation"
                                value={currentQuestion.explanation}
                                onChange={handleQuestionChange}
                                placeholder="Enter explanation for the correct answer"
                                rows={2}
                              />
                            </div>

                            <Button onClick={addQuestion} variant="outline" className="w-full">
                              <Plus className="w-4 h-4 mr-2" />
                              Add Question
                            </Button>
                          </div>
                        </Card>
                      </div>

                      {/* Create Test Button */}
                      <div className="flex justify-end space-x-4 pt-4 border-t">
                        <Button
                          variant="outline"
                          onClick={() => setShowCreateTest(false)}
                        >
                          Cancel
                        </Button>
                        <Button
                          onClick={createTest}
                          disabled={loading || testForm.questions.length === 0}
                          className="bg-gradient-to-r from-blue-600 to-blue-700"
                        >
                          {loading ? 'Creating...' : 'Create Test'}
                        </Button>
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Tests Tab */}
          <TabsContent value="tests" className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">Manage Tests</h2>
              <Dialog open={showCreateTest} onOpenChange={setShowCreateTest}>
                <DialogTrigger asChild>
                  <Button className="bg-gradient-to-r from-blue-600 to-blue-700">
                    <Plus className="w-4 h-4 mr-2" />
                    Create Test
                  </Button>
                </DialogTrigger>
              </Dialog>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {tests.map((test) => (
                <Card key={test.id} className="card-hover">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{test.title}</CardTitle>
                      <Badge variant="secondary">${test.price}</Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-gray-600 text-sm">{test.description}</p>
                    
                    <div className="flex items-center justify-between text-sm text-gray-500">
                      <div className="flex items-center space-x-1">
                        <Clock className="w-4 h-4" />
                        <span>{test.duration_minutes} mins</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <BookOpen className="w-4 h-4" />
                        <span>{test.questions_count} questions</span>
                      </div>
                    </div>
                    
                    <div className="flex space-x-2">
                      <Button variant="outline" size="sm" className="flex-1">
                        <Edit className="w-4 h-4 mr-1" />
                        Edit
                      </Button>
                      <Button variant="outline" size="sm" className="text-red-600 hover:text-red-700">
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Students Tab */}
          <TabsContent value="students" className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Students</h2>
            
            <Card>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b">
                      <tr>
                        <th className="px-6 py-4 text-left text-sm font-medium text-gray-900">Name</th>
                        <th className="px-6 py-4 text-left text-sm font-medium text-gray-900">Email</th>
                        <th className="px-6 py-4 text-left text-sm font-medium text-gray-900">Status</th>
                        <th className="px-6 py-4 text-left text-sm font-medium text-gray-900">Joined</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {students.map((student) => (
                        <tr key={student.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 text-sm font-medium text-gray-900">{student.name}</td>
                          <td className="px-6 py-4 text-sm text-gray-600">{student.email}</td>
                          <td className="px-6 py-4">
                            <Badge variant={student.is_active ? "default" : "secondary"} className="status-badge">
                              <CheckCircle2 className="w-3 h-3 mr-1" />
                              {student.is_active ? 'Active' : 'Inactive'}
                            </Badge>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600">
                            {new Date(student.created_at).toLocaleDateString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Analytics</h2>
            <Card>
              <CardContent className="p-8 text-center">
                <BarChart3 className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Analytics Dashboard</h3>
                <p className="text-gray-600">Detailed analytics and reporting features coming soon!</p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default AdminDashboard;