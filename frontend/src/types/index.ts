/**
 * TypeScript type definitions for Smart Lecture Assistant
 */

export interface Lecture {
  id: string;
  module_code: string;
  week_number: number;
  title: string;
  filename: string;
  upload_date: string;
  num_pages?: number;
}

export interface Topic {
  id: string;
  name: string;
  description?: string;
  module_code: string;
  appearances: TopicAppearance[];
}

export interface TopicAppearance {
  lecture_id: string;
  week_number: number;
  lecture_title: string;
  frequency: number;
  first_appearance_slide?: number;
}

export interface Chunk {
  id: string;
  lecture_id: string;
  content: string;
  slide_number: number;
  embedding?: number[];
}

export interface QueryRequest {
  query: string;
  module_code: string;
  top_k?: number;
  temporal_filter?: boolean;
}

export interface QueryResponse {
  answer: string;
  sources: Source[];
  processing_time: number;
}

export interface Source {
  lecture_title: string;
  week_number: number;
  slide_number: number;
  content: string;
  similarity_score: number;
}

export interface UploadRequest {
  file: File;
  module_code: string;
  week_number: number;
  lecture_title: string;
}

export interface TopicMap {
  nodes: TopicNode[];
  edges: TopicEdge[];
}

export interface TopicNode {
  id: string;
  label: string;
  size: number;
  color?: string;
}

export interface TopicEdge {
  source: string;
  target: string;
  type: 'prerequisite' | 'related';
}

export interface DashboardStats {
  total_lectures: number;
  total_topics: number;
  modules: string[];
  recent_uploads: Lecture[];
}
