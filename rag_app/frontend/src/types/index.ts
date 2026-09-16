/**
 * Core TypeScript Types and Enums for RAG Application
 */

// ============ User & Authentication ============
export type UserRole = 'admin' | 'user' | 'viewer';

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  avatar?: string;
  createdAt: Date;
}

export interface Session {
  user: User;
  token: string;
  expiresAt: Date;
}

// ============ Document Types & Enums ============
export enum DocumentType {
  PDF = 'pdf',
  DOCX = 'docx',
  PPTX = 'pptx',
  XLSX = 'xlsx',
  HTML = 'html',
  IMAGE = 'image',
  EMAIL = 'email',
  WEBPAGE = 'webpage',
  SCANNED_DOC = 'scanned_doc',
}

export enum DataSource {
  LOCAL_UPLOAD = 'local_upload',
  CLOUD_STORAGE = 'cloud_storage',
  WEB_URL = 'web_url',
  EMAIL = 'email',
}

export enum PreprocessingStrategy {
  TEXT_NORMALIZER = 'text_normalizer',
  LANGUAGE_DETECTOR = 'language_detector',
  METADATA_ENRICHER = 'metadata_enricher',
  STRUCTURE_PRESERVER = 'structure_preserver',
  BOILERPLATE_REMOVER = 'boilerplate_remover',
  TABLE_EXTRACTOR = 'table_extractor',
}

export enum ChunkingStrategy {
  OVERLAP = 'overlap',
  SEMANTIC = 'semantic',
  HYBRID = 'hybrid',
  STRUCTURAL = 'structural',
  TABLE = 'table',
  LINEAGE = 'lineage',
  SLIDE = 'slide',
}

// ============ Document & Chunk Models ============
export interface DocumentMetadata {
  title?: string;
  description?: string;
  keywords?: string[];
  author?: string;
  createdAt?: Date;
  modifiedAt?: Date;
  language?: string;
  wordCount?: number;
  pageCount?: number;
}

export interface Document {
  id: string;
  name: string;
  type: DocumentType;
  size: number;
  uploadedAt: Date;
  metadata: DocumentMetadata;
  chunkCount: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  userId: string;
}

export interface Chunk {
  id: string;
  documentId: string;
  text: string;
  tokenCount: number;
  metadata: {
    startIndex: number;
    endIndex: number;
    confidence?: number;
    language?: string;
    keywords?: string[];
    section?: string;
    pageNumber?: number;
    processingStrategiesApplied: PreprocessingStrategy[];
  };
  createdAt: Date;
}

export interface ChunkMetadata {
  chunkId: string;
  documentId: string;
  confidence: number;
  language: string;
  keywords: string[];
  section: string;
  relevanceScore?: number;
}

// ============ Ingestion Models ============
export interface IngestionConfig {
  documentType: DocumentType;
  dataSource: DataSource;
  preprocessingStrategies: PreprocessingStrategy[];
  chunkingStrategy: ChunkingStrategy;
  chunkSize?: number;
  overlapPercentage?: number;
  similarityThreshold?: number;
}

export interface IngestionJob {
  id: string;
  documentId: string;
  documentName: string;
  config: IngestionConfig;
  status: 'pending' | 'loading' | 'preprocessing' | 'chunking' | 'completed' | 'failed';
  progress: number;
  totalChunks: number;
  processedChunks: number;
  startedAt: Date;
  completedAt?: Date;
  error?: string;
  processingTimeMs?: number;
}

export interface IngestionResult {
  documentId: string;
  totalChunks: number;
  averageChunkSize: number;
  totalTokens: number;
  processingTimeMs: number;
  chunks: Chunk[];
}

// ============ Search Models ============
export interface SearchQuery {
  query: string;
  limit?: number;
  filters?: {
    documentType?: DocumentType;
    dateRange?: { from: Date; to: Date };
    confidenceThreshold?: number;
  };
}

export interface SearchResult {
  chunkId: string;
  documentId: string;
  documentName: string;
  chunkText: string;
  relevanceScore: number;
  confidence: number;
  section?: string;
  keywords: string[];
}

export interface SearchResultSet {
  query: string;
  results: SearchResult[];
  totalResults: number;
  processingTimeMs: number;
  timestamp: Date;
}

// ============ Code Generation Models ============
export enum CodeLanguage {
  PYTHON = 'python',
  JAVASCRIPT = 'javascript',
  TYPESCRIPT = 'typescript',
  CURL = 'curl',
}

export interface CodeSnippet {
  language: CodeLanguage;
  code: string;
  description: string;
}

export interface APIEndpoint {
  name: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  path: string;
  description: string;
  requestSchema?: Record<string, unknown>;
  responseSchema?: Record<string, unknown>;
  example?: Record<string, unknown>;
}

// ============ Statistics Models ============
export interface IngestionStats {
  totalDocuments: number;
  totalChunks: number;
  averageChunkSize: number;
  averageProcessingTimeMs: number;
  successRate: number;
  lastIngestionAt?: Date;
}

export interface SearchStats {
  totalSearches: number;
  averageResponseTimeMs: number;
  topQueries: string[];
  lastSearchAt?: Date;
}

// ============ UI State Models ============
export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
  duration?: number;
}

export interface ModalState {
  isOpen: boolean;
  title?: string;
  message?: string;
  onConfirm?: () => void;
  onCancel?: () => void;
}
