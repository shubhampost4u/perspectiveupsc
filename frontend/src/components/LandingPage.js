import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { BookOpen, Clock, Users, CheckCircle, ArrowRight, Menu, X } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LandingPage = () => {
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchPublicTests();
  }, []);

  const fetchPublicTests = async () => {
    try {
      const response = await axios.get(`${API}/public/tests`);
      setTests(response.data);
    } catch (error) {
      console.error('Error fetching tests:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTestClick = (testId) => {
    // Redirect to signup page when user tries to access a test
    navigate('/register', { state: { redirectTo: `/test/${testId}` } });
  };

  const handleGetStarted = () => {
    navigate('/register');
  };

  const handleLogin = () => {
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Navigation Bar */}
      <nav className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <BookOpen className="w-8 h-8 text-blue-600 mr-2" />
              <span className="text-2xl font-bold text-gray-900">Perspective UPSC</span>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-4">
              <a href="#tests" className="text-gray-700 hover:text-blue-600 px-3 py-2">Tests</a>
              <a href="#features" className="text-gray-700 hover:text-blue-600 px-3 py-2">Features</a>
              <a href="#about" className="text-gray-700 hover:text-blue-600 px-3 py-2">About</a>
              <Button variant="outline" onClick={handleLogin}>Login</Button>
              <Button onClick={handleGetStarted}>Get Started</Button>
            </div>

            {/* Mobile menu button */}
            <div className="md:hidden">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="text-gray-700 hover:text-blue-600"
              >
                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>

          {/* Mobile Navigation */}
          {mobileMenuOpen && (
            <div className="md:hidden pb-4 space-y-2">
              <a href="#tests" className="block text-gray-700 hover:text-blue-600 px-3 py-2">Tests</a>
              <a href="#features" className="block text-gray-700 hover:text-blue-600 px-3 py-2">Features</a>
              <a href="#about" className="block text-gray-700 hover:text-blue-600 px-3 py-2">About</a>
              <Button variant="outline" onClick={handleLogin} className="w-full">Login</Button>
              <Button onClick={handleGetStarted} className="w-full">Get Started</Button>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Master UPSC EO/AO & APFC with
            <span className="text-blue-600"> Confidence</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Comprehensive mock tests for UPSC Enforcement Officer/Accounts Officer & APFC examinations. Get detailed analytics and expert-curated content to excel in your exam preparation.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" onClick={handleGetStarted} className="text-lg px-8 py-6">
              Start Your Preparation
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
            <Button size="lg" variant="outline" onClick={() => document.getElementById('tests').scrollIntoView({ behavior: 'smooth' })} className="text-lg px-8 py-6">
              Browse Tests
            </Button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mt-16">
            <div>
              <div className="text-4xl font-bold text-blue-600">{tests.length}+</div>
              <div className="text-gray-600 mt-2">Practice Tests</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-blue-600">1000+</div>
              <div className="text-gray-600 mt-2">Questions</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-purple-600">15% OFF</div>
              <div className="text-gray-600 mt-2">Bundle Savings</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-green-600">₹49</div>
              <div className="text-gray-600 mt-2">Starting Price</div>
            </div>
          </div>
        </div>
      </section>

      {/* Limited Time Offer Banner */}
      <section className="py-8 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-orange-500 via-red-500 to-pink-500">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between text-white gap-6">
            <div className="flex-1 text-center md:text-left">
              <div className="flex items-center justify-center md:justify-start gap-2 mb-3">
                <span className="animate-pulse text-2xl">🎓</span>
                <h3 className="text-2xl md:text-4xl font-extrabold tracking-tight">MEGA SALE ON UPSC EO/AO & APFC TESTS!</h3>
                <span className="animate-pulse text-2xl">🎓</span>
              </div>
              <p className="text-lg md:text-xl font-semibold mb-2">
                🚀 Crack UPSC Enforcement Officer/Accounts Officer & APFC Exams with Confidence
              </p>
              <p className="text-base md:text-lg font-medium opacity-95">
                ⚡ Specially curated mock tests for EO/AO & APFC aspirants | Buy in Bulk & Save Big!
              </p>
              <div className="flex flex-wrap items-center justify-center md:justify-start gap-3 mt-4">
                <div className="bg-white/90 text-red-600 px-4 py-2 rounded-full font-bold text-sm shadow-lg">
                  💰 Starting at just ₹49
                </div>
                <div className="bg-yellow-300 text-gray-900 px-4 py-2 rounded-full font-bold text-sm shadow-lg animate-pulse">
                  🏆 Up to 15% OFF on Multiple Tests
                </div>
              </div>
            </div>
            <div className="flex flex-col sm:flex-row gap-3 items-center">
              <div className="bg-white/20 backdrop-blur-lg rounded-xl px-6 py-4 border-2 border-white/50 shadow-2xl text-center min-w-[160px]">
                <div className="text-3xl font-bold">💰 SAVE BIG</div>
                <div className="text-sm mt-1">Limited Period Offer</div>
                <div className="text-xs mt-1 opacity-90">On EO/AO & APFC Tests</div>
              </div>
              <Button 
                size="lg"
                onClick={handleGetStarted}
                className="bg-white text-red-600 hover:bg-gray-100 font-bold text-lg shadow-2xl animate-bounce px-8 py-6"
              >
                Grab Deal Now! 🎯
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Why Choose Perspective UPSC?</h2>
            <p className="text-xl text-gray-600">Everything you need to ace the UPSC exam</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <Card className="border-2 hover:border-blue-500 transition-colors">
              <CardHeader>
                <CheckCircle className="w-12 h-12 text-blue-600 mb-4" />
                <CardTitle>Comprehensive Tests</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  High-quality mock tests covering the entire UPSC syllabus with expert-curated questions
                </p>
              </CardContent>
            </Card>

            <Card className="border-2 hover:border-blue-500 transition-colors">
              <CardHeader>
                <Clock className="w-12 h-12 text-blue-600 mb-4" />
                <CardTitle>Timed Practice</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Real exam simulation with strict timers to help you manage time effectively during the actual exam
                </p>
              </CardContent>
            </Card>

            <Card className="border-2 hover:border-blue-500 transition-colors">
              <CardHeader>
                <Users className="w-12 h-12 text-blue-600 mb-4" />
                <CardTitle>Detailed Analytics</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  In-depth performance analysis, score tracking, and personalized recommendations for improvement
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Available Tests Section */}
      <section id="tests" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Available Practice Tests</h2>
            <p className="text-xl text-gray-600">Choose from our comprehensive collection of UPSC mock tests</p>
          </div>

          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : tests.length === 0 ? (
            <div className="text-center py-16">
              <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No Tests Available Yet</h3>
              <p className="text-gray-600">Check back soon for new practice tests!</p>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {tests.map((test) => (
                <Card 
                  key={test.id} 
                  className="hover:shadow-xl transition-shadow cursor-pointer border-2 hover:border-blue-500"
                  onClick={() => handleTestClick(test.id)}
                >
                  <CardHeader>
                    <CardTitle className="text-xl">{test.title}</CardTitle>
                    <CardDescription className="line-clamp-2">
                      {test.description || 'Comprehensive practice test for UPSC preparation'}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {/* Test Details */}
                      <div className="flex items-center text-gray-600">
                        <BookOpen className="w-4 h-4 mr-2" />
                        <span>{test.total_questions || test.questions?.length || 0} Questions</span>
                      </div>
                      
                      <div className="flex items-center text-gray-600">
                        <Clock className="w-4 h-4 mr-2" />
                        <span>{test.duration_minutes || test.duration || 0} Minutes</span>
                      </div>

                      {test.subject && (
                        <div className="flex items-center text-gray-600">
                          <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                            {test.subject}
                          </span>
                        </div>
                      )}

                      {/* Price */}
                      <div className="pt-4 border-t">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center text-2xl font-bold text-blue-600">
                            <span>₹{test.price}</span>
                          </div>
                          <Button 
                            onClick={(e) => {
                              e.stopPropagation();
                              handleTestClick(test.id);
                            }}
                            className="bg-blue-600 hover:bg-blue-700"
                          >
                            Take Test
                          </Button>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {/* Bundle Offer Banner */}
          {tests.length > 0 && (
            <div className="mt-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white text-center">
              <h3 className="text-3xl font-bold mb-4">Save More with Bundle Offers!</h3>
              <p className="text-xl mb-6">
                Get up to 15% discount when you purchase multiple tests
              </p>
              <div className="grid md:grid-cols-2 gap-6 max-w-2xl mx-auto mb-6">
                <div className="bg-white/20 backdrop-blur rounded-lg p-6">
                  <div className="text-3xl font-bold">10% OFF</div>
                  <div className="text-base mt-2">Buy 2-4 Tests</div>
                  <div className="text-sm mt-1 opacity-90">Perfect for focused preparation</div>
                </div>
                <div className="bg-white/20 backdrop-blur rounded-lg p-6">
                  <div className="text-3xl font-bold">15% OFF</div>
                  <div className="text-base mt-2">Buy 5+ Tests</div>
                  <div className="text-sm mt-1 opacity-90">Best value for comprehensive practice</div>
                </div>
              </div>
              <Button 
                size="lg" 
                variant="secondary" 
                onClick={handleGetStarted}
                className="bg-white text-blue-600 hover:bg-gray-100"
              >
                Sign Up to Save More
              </Button>
            </div>
          )}
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-6">About Perspective UPSC</h2>
          <p className="text-xl text-gray-600 mb-8">
            We are dedicated to helping UPSC aspirants achieve their dreams through high-quality practice tests, 
            comprehensive analytics, and expert guidance. Our platform is designed by selected candidates and 
            experienced educators who understand the challenges of UPSC preparation.
          </p>
          <Button size="lg" onClick={handleGetStarted}>
            Start Your Journey Today
          </Button>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-6">Ready to Begin Your UPSC Journey?</h2>
          <p className="text-xl mb-8">
            Join thousands of successful UPSC aspirants who trust Perspective UPSC for their preparation
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              size="lg" 
              variant="secondary"
              onClick={handleGetStarted}
              className="bg-white text-blue-600 hover:bg-gray-100 text-lg px-8 py-6"
            >
              Create Free Account
            </Button>
            <Button 
              size="lg" 
              variant="outline"
              onClick={handleLogin}
              className="border-2 border-white text-white hover:bg-white/10 text-lg px-8 py-6"
            >
              Already have an account? Login
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center mb-4">
                <BookOpen className="w-8 h-8 text-blue-400 mr-2" />
                <span className="text-xl font-bold">Perspective UPSC</span>
              </div>
              <p className="text-gray-400">
                Your trusted companion for UPSC Civil Services Examination preparation.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Quick Links</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#tests" className="hover:text-white">Tests</a></li>
                <li><a href="#features" className="hover:text-white">Features</a></li>
                <li><a href="#about" className="hover:text-white">About</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="mailto:admin@perspectiveupsc.com" className="hover:text-white">Contact Us</a></li>
                <li><a href="#" className="hover:text-white">FAQ</a></li>
                <li><a href="#" className="hover:text-white">Help Center</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Legal</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white">Terms of Service</a></li>
                <li><a href="#" className="hover:text-white">Refund Policy</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 Perspective UPSC. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
