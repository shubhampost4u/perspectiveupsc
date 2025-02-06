// src/services/api.service.js
import API_CONFIG from '../config/api.config';

class ApiService {
  static BASE_URL = API_CONFIG.getApiUrl();

  static async fetchQuestions() {
    try {
      const response = await fetch(`${this.BASE_URL}/api/questions`);
      return await response.json();
    } catch (error) {
      console.error('Error fetching questions:', error);
      throw error;
    }
  }
}