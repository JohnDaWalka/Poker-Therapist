import axios from 'axios';

const API_URL = 'https://api.example.com/poker-hand-analysis';

export const getHandDetails = async () => {
  const response = await axios.get(`${API_URL}/hand-details`);
  return response.data;
};

export const getHandStrength = async () => {
  const response = await axios.get(`${API_URL}/hand-strength`);
  return response.data;
};

export const getHandRank = async () => {
  const response = await axios.get(`${API_URL}/hand-rank`);
  return response.data;
};

export const getWinningProbability = async () => {
  const response = await axios.get(`${API_URL}/winning-probability`);
  return response.data;
};

export const getSuggestedActions = async () => {
  const response = await axios.get(`${API_URL}/suggested-actions`);
  return response.data;
};

export const getOpponentAnalysis = async () => {
  const response = await axios.get(`${API_URL}/opponent-analysis`);
  return response.data;
};

export const getHistoricalData = async () => {
  const response = await axios.get(`${API_URL}/historical-data`);
  return response.data;
};

export const getVisualElements = async () => {
  const response = await axios.get(`${API_URL}/visual-elements`);
  return response.data;
};
