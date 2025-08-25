import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
  BookOpen, 
  Clock, 
  Trophy, 
  ShoppingCart, 
  LogOut,
  Play,
  CheckCircle2,
  Star,
  TrendingUp,
  Target
} from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '../App';
import PaymentDialog from './PaymentDialog';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const StudentDashboard = () => {
  const { user, logout, token } = useAuth();
  const navigate = useNavigate();
  const [availableTests, setAvailableTests] = useState([]);
  const [purchasedTests, setPurchasedTests] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAvailableTests();
    fetchPurchasedTests();
    fetchResults();
  }, []);

  const axiosConfig = {
    headers: { Authorization: `Bearer ${token}` }
  };

  const fetchAvailableTests = async () => {
    try {
      const response = await axios.get(`${API}/tests`);
      setAvailableTests(response.data);
    } catch (error) {
      console.error('Error fetching available tests:', error);
      toast.error('Failed to fetch available tests');
    }
  };

  const fetchPurchasedTests = async () => {
    try {
      const response = await axios.get(`${API}/my-tests`, axiosConfig);
      setPurchasedTests(response.data);
    } catch (error) {
      console.error('Error fetching purchased tests:', error);
      toast.error('Failed to fetch purchased tests');
    }
  };

  const fetchResults = async () => {
    try {
      const response = await axios.get(`${API}/my-results`, axiosConfig);
      setResults(response.data);
    } catch (error) {
      console.error('Error fetching results:', error);
      toast.error('Failed to fetch results');
    }
  };

  const purchaseTest = async (testId) => {
    setLoading(true);
    try {
      await axios.post(`${API}/tests/${testId}/purchase`, {}, axiosConfig);
      toast.success('Test purchased successfully!');
      fetchPurchasedTests();
      fetchAvailableTests();
    } catch (error) {
      console.error('Error purchasing test:', error);
      toast.error(error.response?.data?.detail || 'Failed to purchase test');
    } finally {
      setLoading(false);
    }
  };

  const startTest = (testId) => {
    navigate(`/test/${testId}`);
  };

  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully');
  };

  const isTestPurchased = (testId) => {
    return purchasedTests.some(test => test.id === testId);
  };

  const isTestCompleted = (testId) => {
    return results.some(result => result.test_id === testId);
  };

  const getTestResult = (testId) => {
    return results.find(result => result.test_id === testId);
  };

  const calculateStats = () => {
    const totalTests = results.length;
    const averageScore = totalTests > 0 
      ? results.reduce((sum, result) => sum + result.percentage, 0) / totalTests 
      : 0;
    const passedTests = results.filter(result => result.percentage >= 70).length;
    
    return { totalTests, averageScore, passedTests };
  };

  const stats = calculateStats();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Student Dashboard</h1>
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
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="card-hover">
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <BookOpen className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{stats.totalTests}</p>
                  <p className="text-gray-600">Tests Completed</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="card-hover">
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <Trophy className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{stats.averageScore.toFixed(1)}%</p>
                  <p className="text-gray-600">Average Score</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="card-hover">
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                  <Target className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{stats.passedTests}</p>
                  <p className="text-gray-600">Tests Passed</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="card-hover">
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                  <ShoppingCart className="w-6 h-6 text-orange-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{purchasedTests.length}</p>
                  <p className="text-gray-600">Tests Purchased</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="browse" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="browse">Browse Tests</TabsTrigger>
            <TabsTrigger value="my-tests">My Tests</TabsTrigger>
            <TabsTrigger value="results">Results</TabsTrigger>
          </TabsList>

          {/* Browse Tests Tab */}
          <TabsContent value="browse" className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">Available Tests</h2>
              <Badge variant="secondary">{availableTests.length} tests available</Badge>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {availableTests.map((test) => (
                <Card key={test.id} className="card-hover">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{test.title}</CardTitle>
                      <Badge variant="outline" className="text-green-600 border-green-600">
                        ${test.price}
                      </Badge>
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
                    
                    <div className="pt-2">
                      {isTestPurchased(test.id) ? (
                        isTestCompleted(test.id) ? (
                          <div className="space-y-2">
                            <Badge variant="default" className="w-full justify-center bg-green-600">
                              <CheckCircle2 className="w-4 h-4 mr-1" />
                              Completed - {getTestResult(test.id)?.percentage}%
                            </Badge>
                            <Button
                              onClick={() => navigate(`/solutions/${test.id}`)}
                              variant="outline"
                              size="sm"
                              className="w-full text-blue-600 border-blue-600 hover:bg-blue-50"
                            >
                              View Solutions
                            </Button>
                          </div>
                        ) : (
                          <Button 
                            onClick={() => startTest(test.id)}
                            className="w-full bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800"
                          >
                            <Play className="w-4 h-4 mr-2" />
                            Start Test
                          </Button>
                        )
                      ) : (
                        <Button
                          onClick={() => purchaseTest(test.id)}
                          disabled={loading}
                          className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800"
                        >
                          <ShoppingCart className="w-4 h-4 mr-2" />
                          {loading ? 'Purchasing...' : 'Purchase Test'}
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* My Tests Tab */}
          <TabsContent value="my-tests" className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">My Tests</h2>
              <Badge variant="secondary">{purchasedTests.length} tests owned</Badge>
            </div>

            {purchasedTests.length === 0 ? (
              <Card>
                <CardContent className="p-8 text-center">
                  <ShoppingCart className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Tests Purchased Yet</h3>
                  <p className="text-gray-600 mb-4">Browse available tests and purchase to start learning!</p>
                  <Button variant="outline">Browse Tests</Button>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {purchasedTests.map((test) => (
                  <Card key={test.id} className="card-hover">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-lg">{test.title}</CardTitle>
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
                      
                      <div className="pt-2">
                        {isTestCompleted(test.id) ? (
                          <div className="space-y-2">
                            <Badge variant="default" className="w-full justify-center bg-green-600">
                              <CheckCircle2 className="w-4 h-4 mr-1" />
                              Completed - {getTestResult(test.id)?.percentage}%
                            </Badge>
                            <p className="text-xs text-gray-500 text-center">
                              Completed on {new Date(getTestResult(test.id)?.completed_at).toLocaleDateString()}
                            </p>
                            <Button
                              onClick={() => navigate(`/solutions/${test.id}`)}
                              variant="outline"
                              size="sm"
                              className="w-full text-blue-600 border-blue-600 hover:bg-blue-50"
                            >
                              View Solutions
                            </Button>
                          </div>
                        ) : (
                          <Button 
                            onClick={() => startTest(test.id)}
                            className="w-full bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800"
                          >
                            <Play className="w-4 h-4 mr-2" />
                            Start Test
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          {/* Results Tab */}
          <TabsContent value="results" className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">Test Results</h2>
              <Badge variant="secondary">{results.length} results</Badge>
            </div>

            {results.length === 0 ? (
              <Card>
                <CardContent className="p-8 text-center">
                  <Trophy className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Results Yet</h3>
                  <p className="text-gray-600 mb-4">Complete some tests to see your results here!</p>
                  <Button variant="outline">Take a Test</Button>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {results.map((result) => (
                  <Card key={result.id} className="card-hover">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-gray-900">{result.test_title}</h3>
                          <p className="text-sm text-gray-600">
                            Completed on {new Date(result.completed_at).toLocaleDateString()}
                          </p>
                        </div>
                        
                        <div className="flex items-center space-x-4">
                          <div className="text-center">
                            <p className="text-2xl font-bold text-gray-900">{result.score}</p>
                            <p className="text-sm text-gray-600">out of {result.total_questions}</p>
                          </div>
                          
                          <div className="text-center">
                            <p className={`text-2xl font-bold ${
                              result.percentage >= 90 ? 'text-green-600' :
                              result.percentage >= 70 ? 'text-blue-600' :
                              result.percentage >= 50 ? 'text-yellow-600' : 'text-red-600'
                            }`}>
                              {result.percentage}%
                            </p>
                            <div className="flex items-center">
                              {result.percentage >= 90 ? (
                                <Star className="w-4 h-4 text-green-600" />
                              ) : result.percentage >= 70 ? (
                                <Trophy className="w-4 h-4 text-blue-600" />
                              ) : result.percentage >= 50 ? (
                                <TrendingUp className="w-4 h-4 text-yellow-600" />
                              ) : (
                                <Target className="w-4 h-4 text-red-600" />
                              )}
                              <span className="text-sm text-gray-600 ml-1">
                                {result.percentage >= 90 ? 'Excellent' :
                                 result.percentage >= 70 ? 'Good' :
                                 result.percentage >= 50 ? 'Fair' : 'Needs Improvement'}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default StudentDashboard;