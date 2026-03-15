import axios from 'axios';

const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
});

export const getURLs      = ()           => API.get('/urls');
export const createURL    = (data)       => API.post('/urls', data);
export const deleteURL    = (code)       => API.delete(`/urls/${code}`);
export const getURLStats  = (code)       => API.get(`/urls/${code}/stats`);
