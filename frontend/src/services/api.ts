/**
 * API client for Smart Lecture Assistant backend
 */
import axios from 'axios';
import type {
  Lecture,
  Topic,
  QueryRequest,
  QueryResponse,
  UploadRequest,
  TopicMap,
  DashboardStats,
} from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health check
export const healthCheck = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};

// Lecture endpoints
export const uploadLecture = async (data: UploadRequest) => {
  const formData = new FormData();
  formData.append('file', data.file);
  formData.append('module_code', data.module_code);
  formData.append('week_number', data.week_number.toString());
  formData.append('lecture_title', data.lecture_title);

  const response = await apiClient.post<Lecture>('/api/lectures/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getLectures = async (moduleCode?: string) => {
  const url = moduleCode ? `/api/lectures?module_code=${moduleCode}` : '/api/lectures';
  const response = await apiClient.get<Lecture[]>(url);
  return response.data;
};

export const getLecture = async (lectureId: string) => {
  const response = await apiClient.get<Lecture>(`/api/lectures/${lectureId}`);
  return response.data;
};

export const deleteLecture = async (lectureId: string) => {
  const response = await apiClient.delete(`/api/lectures/${lectureId}`);
  return response.data;
};

// Topic endpoints
export const detectTopics = async (moduleCode: string) => {
  const response = await apiClient.post<{ status: string; topics: Topic[] }>(
    '/api/topics/detect',
    { module_code: moduleCode }
  );
  return response.data;
};

export const getTopics = async (moduleCode: string) => {
  const response = await apiClient.get<Topic[]>(`/api/topics/${moduleCode}`);
  return response.data;
};

export const getTopicMap = async (moduleCode: string) => {
  const response = await apiClient.get<TopicMap>(`/api/topics/${moduleCode}/map`);
  return response.data;
};

// Query endpoints
export const queryLectures = async (data: QueryRequest) => {
  const response = await apiClient.post<QueryResponse>('/api/query', data);
  return response.data;
};

// Dashboard endpoints
export const getDashboardStats = async () => {
  const response = await apiClient.get<DashboardStats>('/api/dashboard/stats');
  return response.data;
};

export const getModuleDashboard = async (moduleCode: string) => {
  const response = await apiClient.get(`/api/dashboard/${moduleCode}`);
  return response.data;
};

export default apiClient;
