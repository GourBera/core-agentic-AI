'use client';

import {
  DocumentType,
  PreprocessingStrategy,
  ChunkingStrategy,
  DataSource,
  Document,
  Chunk,
  IngestionResult,
  SearchResult,
  SearchResultSet,
  IngestionStats,
  APIEndpoint,
  CodeSnippet,
  CodeLanguage,
} from '@/types';

// Utility to add delay (simulate network latency)
const delay = (ms: number = 200) => new Promise((resolve) => setTimeout(resolve, ms));

// ============ Mock Data Generators ============

export const generateMockDocument = (index: number): Document => {
  const docTypes = Object.values(DocumentType);
  const type = docTypes[index % docTypes.length];

  return {
    id: `doc-${index}-${Date.now()}`,
    name: `Sample Document ${index + 1}.${type}`,
    type: type as DocumentType,
    size: Math.floor(Math.random() * 5000000) + 100000,
    uploadedAt: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000),
    metadata: {
      title: `Document ${index + 1}`,
      description: `Sample document for testing RAG pipeline`,
      keywords: ['rag', 'testing', 'sample'],
      author: 'Demo User',
      language: 'en',
      wordCount: Math.floor(Math.random() * 5000) + 500,
      pageCount: Math.floor(Math.random() * 50) + 5,
    },
    chunkCount: Math.floor(Math.random() * 200) + 10,
    status: 'completed',
    userId: 'user-demo-001',
  };
};

export const generateMockChunks = (documentId: string, count: number): Chunk[] => {
  const chunks: Chunk[] = [];
  const sampleTexts = [
    'The retrieval-augmented generation (RAG) technique combines language models with information retrieval to enhance response quality.',
    'Document chunking is a critical step in RAG pipelines that affects retrieval performance and context quality.',
    'Preprocessing strategies help normalize text and extract structured information from unstructured documents.',
    'Semantic chunking uses embeddings to create meaningful chunks that preserve context and intent.',
    'The overlap between chunks ensures that important context is not lost during retrieval.',
    'Metadata enrichment adds important context to chunks, improving search relevance and ranking.',
  ];

  for (let i = 0; i < count; i++) {
    chunks.push({
      id: `chunk-${documentId}-${i}`,
      documentId,
      text: sampleTexts[i % sampleTexts.length],
      tokenCount: Math.floor(Math.random() * 500) + 50,
      metadata: {
        startIndex: i * 100,
        endIndex: (i + 1) * 100,
        confidence: Math.random() * 0.3 + 0.7, // 0.7-1.0
        language: 'en',
        keywords: ['rag', 'chunking', 'retrieval'],
        section: `Section ${Math.floor(i / 10) + 1}`,
        pageNumber: Math.floor(i / 5) + 1,
        processingStrategiesApplied: [
          PreprocessingStrategy.TEXT_NORMALIZER,
          PreprocessingStrategy.LANGUAGE_DETECTOR,
        ],
      },
      createdAt: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000),
    });
  }

  return chunks;
};

export const generateMockSearchResults = (query: string, count: number = 5): SearchResult[] => {
  const results: SearchResult[] = [];
  const relevanceScores = Array.from({ length: count }, (_, i) => 1 - i * 0.15);

  for (let i = 0; i < count; i++) {
    results.push({
      chunkId: `chunk-result-${i}`,
      documentId: `doc-${i}`,
      documentName: `Document ${i + 1}.pdf`,
      chunkText: `This chunk contains information about "${query}". The retrieval system found this result relevant based on semantic similarity and keyword matching.`,
      relevanceScore: relevanceScores[i],
      confidence: Math.random() * 0.2 + 0.8,
      section: `Section ${i + 1}`,
      keywords: query.split(' ').filter((w) => w.length > 3),
    });
  }

  return results;
};

// ============ Mock API Functions ============

export const mockAPI = {
  // Ingestion APIs
  async ingestDocument(
    file: File,
    config: any,
  ): Promise<IngestionResult> {
    await delay(2000); // Simulate file upload and processing

    const chunkCount = Math.floor(Math.random() * 200) + 50;
    const chunks = generateMockChunks(`doc-${Date.now()}`, chunkCount);

    return {
      documentId: `doc-${Date.now()}`,
      totalChunks: chunkCount,
      averageChunkSize: Math.floor(Math.random() * 200) + 100,
      totalTokens: chunks.reduce((sum, c) => sum + c.tokenCount, 0),
      processingTimeMs: Math.floor(Math.random() * 5000) + 1000,
      chunks,
    };
  },

  async getIngestionStats(): Promise<IngestionStats> {
    await delay(300);

    return {
      totalDocuments: Math.floor(Math.random() * 50) + 10,
      totalChunks: Math.floor(Math.random() * 5000) + 500,
      averageChunkSize: 250,
      averageProcessingTimeMs: 2500,
      successRate: 0.95,
      lastIngestionAt: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000),
    };
  },

  async getDocuments(): Promise<Document[]> {
    await delay(500);

    return Array.from({ length: 8 }, (_, i) => generateMockDocument(i));
  },

  async getDocumentChunks(documentId: string): Promise<Chunk[]> {
    await delay(600);

    const chunkCount = Math.floor(Math.random() * 150) + 20;
    return generateMockChunks(documentId, chunkCount);
  },

  // Search APIs
  async searchChunks(query: string, limit: number = 10): Promise<SearchResultSet> {
    await delay(800);

    const results = generateMockSearchResults(query, limit);

    return {
      query,
      results,
      totalResults: results.length,
      processingTimeMs: Math.floor(Math.random() * 500) + 100,
      timestamp: new Date(),
    };
  },

  // Code Generation APIs
  async generateCodeSnippet(language: CodeLanguage, endpoint: string): Promise<CodeSnippet> {
    await delay(400);

    const snippets: Record<CodeLanguage, string> = {
      [CodeLanguage.PYTHON]: `import requests
import json

url = "http://localhost:8000/api/search"
headers = {"Authorization": "Bearer YOUR_API_KEY"}

payload = {
    "query": "Your search query here",
    "limit": 10,
    "filters": {"document_type": "pdf"}
}

response = requests.post(url, json=payload, headers=headers)
results = response.json()

for result in results['results']:
    print(f"Score: {result['relevanceScore']}")
    print(f"Text: {result['chunkText']}")`,

      [CodeLanguage.JAVASCRIPT]: `const axios = require('axios');

const url = 'http://localhost:8000/api/search';
const headers = { Authorization: 'Bearer YOUR_API_KEY' };

const payload = {
  query: 'Your search query here',
  limit: 10,
  filters: { documentType: 'pdf' }
};

axios.post(url, payload, { headers })
  .then(response => {
    const results = response.data.results;
    results.forEach(result => {
      console.log(\`Score: \${result.relevanceScore}\`);
      console.log(\`Text: \${result.chunkText}\`);
    });
  })
  .catch(error => console.error('Error:', error));`,

      [CodeLanguage.TYPESCRIPT]: `import axios from 'axios';
import { SearchResult } from '@/types';

interface SearchResponse {
  results: SearchResult[];
  totalResults: number;
  processingTimeMs: number;
}

async function searchRAG(query: string): Promise<SearchResponse> {
  const response = await axios.post<SearchResponse>(
    'http://localhost:8000/api/search',
    { query, limit: 10 },
    { headers: { Authorization: 'Bearer YOUR_API_KEY' } }
  );
  return response.data;
}`,

      [CodeLanguage.CURL]: `curl -X POST http://localhost:8000/api/search \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -d '{
    "query": "Your search query here",
    "limit": 10,
    "filters": {
      "document_type": "pdf"
    }
  }'`,
    };

    return {
      language,
      code: snippets[language],
      description: `Example code for searching the RAG API using ${language}`,
    };
  },

  async getAPIEndpoints(): Promise<APIEndpoint[]> {
    await delay(400);

    return [
      {
        name: 'Ingest Document',
        method: 'POST',
        path: '/api/ingest',
        description: 'Upload and process a document for RAG ingestion',
        requestSchema: {
          file: 'File',
          documentType: 'DocumentType',
          preprocessingStrategies: 'PreprocessingStrategy[]',
          chunkingStrategy: 'ChunkingStrategy',
        },
        responseSchema: {
          documentId: 'string',
          totalChunks: 'number',
          processingTimeMs: 'number',
        },
        example: {
          documentId: 'doc-12345',
          totalChunks: 150,
          processingTimeMs: 2500,
        },
      },
      {
        name: 'Search',
        method: 'POST',
        path: '/api/search',
        description: 'Search ingested documents and retrieve relevant chunks',
        requestSchema: {
          query: 'string',
          limit: 'number',
          filters: 'SearchFilters',
        },
        responseSchema: {
          results: 'SearchResult[]',
          totalResults: 'number',
          processingTimeMs: 'number',
        },
        example: {
          results: [
            {
              chunkId: 'chunk-123',
              documentId: 'doc-456',
              relevanceScore: 0.92,
              chunkText: '...',
            },
          ],
          totalResults: 42,
          processingTimeMs: 500,
        },
      },
      {
        name: 'List Documents',
        method: 'GET',
        path: '/api/documents',
        description: 'Retrieve list of all ingested documents',
        responseSchema: {
          documents: 'Document[]',
        },
        example: {
          documents: [
            {
              id: 'doc-123',
              name: 'example.pdf',
              type: 'pdf',
              chunkCount: 150,
            },
          ],
        },
      },
      {
        name: 'Get Chunk Details',
        method: 'GET',
        path: '/api/chunks/{chunkId}',
        description: 'Retrieve detailed information about a specific chunk',
        responseSchema: {
          id: 'string',
          documentId: 'string',
          text: 'string',
          metadata: 'ChunkMetadata',
        },
        example: {
          id: 'chunk-123',
          documentId: 'doc-456',
          text: 'Lorem ipsum dolor sit amet...',
          metadata: {
            confidence: 0.92,
            keywords: ['lorem', 'ipsum'],
          },
        },
      },
    ];
  },
};

export default mockAPI;
