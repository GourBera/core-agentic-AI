'use client';

import React, { useState } from 'react';
import { Upload, FileUp, CheckCircle, AlertCircle } from 'lucide-react';
import { DocumentType, ChunkingStrategy, PreprocessingStrategy, DataSource } from '@/types';
import { mockAPI } from '@/lib/api/mocks';

export default function IngestPage() {
  const [step, setStep] = useState<1 | 2 | 3 | 4>(1);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const [config, setConfig] = useState({
    documentType: DocumentType.PDF,
    dataSource: DataSource.LOCAL_UPLOAD,
    preprocessingStrategies: [PreprocessingStrategy.TEXT_NORMALIZER],
    chunkingStrategy: ChunkingStrategy.HYBRID,
    chunkSize: 512,
    overlapPercentage: 20,
  });

  const handleFileSelect = (e: React.DragEvent | React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    const files =
      'dataTransfer' in e ? e.dataTransfer.files : e.currentTarget.files;
    if (files && files[0]) {
      setSelectedFile(files[0]);
      setError('');
    }
  };

  const handleProcess = async () => {
    if (!selectedFile) {
      setError('Please select a file');
      return;
    }

    setIsProcessing(true);
    setError('');

    try {
      const ingestionResult = await mockAPI.ingestDocument(selectedFile, config);
      setResult(ingestionResult);
      setStep(4);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Processing failed');
    } finally {
      setIsProcessing(false);
    }
  };

  // Step 1: File Selection
  if (step === 1) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold">Document Ingestion</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Upload your document and configure ingestion parameters
        </p>

        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-8">
          {/* File Upload Area */}
          <div
            onDrop={handleFileSelect}
            onDragOver={(e) => e.preventDefault()}
            className="border-2 border-dashed border-blue-300 dark:border-blue-600 rounded-lg p-12 text-center cursor-pointer hover:bg-blue-50 dark:hover:bg-blue-900/10 transition"
          >
            <input
              type="file"
              onChange={handleFileSelect}
              accept=".pdf,.docx,.pptx,.xlsx,.html,.jpg,.png,.eml,.msg"
              className="hidden"
              id="file-input"
            />
            <label htmlFor="file-input" className="cursor-pointer">
              <FileUp className="w-12 h-12 text-blue-400 mx-auto mb-4" />
              <p className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                {selectedFile ? selectedFile.name : 'Drag & drop your document here'}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                or click to browse files
              </p>
            </label>
          </div>

          {selectedFile && (
            <div className="mt-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-900/50 rounded-lg flex gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
              <div>
                <p className="font-medium text-green-800 dark:text-green-300">{selectedFile.name}</p>
                <p className="text-sm text-green-700 dark:text-green-400">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
          )}

          {error && (
            <div className="mt-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-900/50 rounded-lg flex gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
              <p className="text-sm text-red-800 dark:text-red-300">{error}</p>
            </div>
          )}

          <div className="mt-8 flex gap-3">
            <button
              onClick={() => setStep(2)}
              disabled={!selectedFile}
              className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition"
            >
              Next: Configure
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Step 2: Configuration
  if (step === 2) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold">Configure Ingestion</h1>

        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 space-y-6">
          {/* Document Type */}
          <div>
            <label className="block text-sm font-medium mb-3">Document Type</label>
            <select
              value={config.documentType}
              onChange={(e) =>
                setConfig({ ...config, documentType: e.target.value as DocumentType })
              }
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {Object.entries(DocumentType).map(([key, value]) => (
                <option key={key} value={value}>
                  {key}
                </option>
              ))}
            </select>
          </div>

          {/* Chunking Strategy */}
          <div>
            <label className="block text-sm font-medium mb-3">Chunking Strategy</label>
            <select
              value={config.chunkingStrategy}
              onChange={(e) =>
                setConfig({ ...config, chunkingStrategy: e.target.value as ChunkingStrategy })
              }
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {Object.entries(ChunkingStrategy).map(([key, value]) => (
                <option key={key} value={value}>
                  {key}
                </option>
              ))}
            </select>
          </div>

          {/* Chunk Size */}
          <div>
            <label className="block text-sm font-medium mb-2">Chunk Size: {config.chunkSize}</label>
            <input
              type="range"
              min="256"
              max="2048"
              step="256"
              value={config.chunkSize}
              onChange={(e) => setConfig({ ...config, chunkSize: parseInt(e.target.value) })}
              className="w-full"
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
              Recommended: 512 tokens for optimal retrieval
            </p>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              onClick={() => setStep(1)}
              className="flex-1 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 font-medium py-2 px-4 rounded-lg transition"
            >
              Back
            </button>
            <button
              onClick={() => setStep(3)}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition"
            >
              Review & Process
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Step 3: Review
  if (step === 3) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold">Review & Process</h1>

        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div className="space-y-4">
            <div className="flex justify-between items-center py-3 border-b border-gray-200 dark:border-gray-700">
              <span className="text-gray-600 dark:text-gray-400">Document:</span>
              <span className="font-medium">{selectedFile?.name}</span>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-gray-200 dark:border-gray-700">
              <span className="text-gray-600 dark:text-gray-400">Type:</span>
              <span className="font-medium">{config.documentType.toUpperCase()}</span>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-gray-200 dark:border-gray-700">
              <span className="text-gray-600 dark:text-gray-400">Chunking Strategy:</span>
              <span className="font-medium">{config.chunkingStrategy}</span>
            </div>
            <div className="flex justify-between items-center py-3">
              <span className="text-gray-600 dark:text-gray-400">Chunk Size:</span>
              <span className="font-medium">{config.chunkSize} tokens</span>
            </div>
          </div>

          <div className="mt-8 flex gap-3">
            <button
              onClick={() => setStep(2)}
              className="flex-1 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 font-medium py-2 px-4 rounded-lg transition"
            >
              Back
            </button>
            <button
              onClick={handleProcess}
              disabled={isProcessing}
              className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition"
            >
              {isProcessing ? 'Processing...' : 'Process Document'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Step 4: Results
  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold">Ingestion Complete!</h1>

      {result && (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center gap-3 mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-900/50 rounded-lg">
            <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0" />
            <div>
              <p className="font-medium text-green-800 dark:text-green-300">Processing Successful</p>
              <p className="text-sm text-green-700 dark:text-green-400">
                Document has been ingested and chunked successfully
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex justify-between items-center py-3 border-b border-gray-200 dark:border-gray-700">
              <span className="text-gray-600 dark:text-gray-400">Total Chunks:</span>
              <span className="text-2xl font-bold text-blue-600">{result.totalChunks}</span>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-gray-200 dark:border-gray-700">
              <span className="text-gray-600 dark:text-gray-400">Total Tokens:</span>
              <span className="font-medium">{result.totalTokens}</span>
            </div>
            <div className="flex justify-between items-center py-3">
              <span className="text-gray-600 dark:text-gray-400">Processing Time:</span>
              <span className="font-medium">{result.processingTimeMs}ms</span>
            </div>
          </div>

          <div className="mt-8 flex gap-3">
            <button
              onClick={() => {
                setStep(1);
                setSelectedFile(null);
                setResult(null);
              }}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition"
            >
              Ingest Another
            </button>
            <a
              href="/explorer"
              className="flex-1 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-900 dark:text-white font-medium py-2 px-4 rounded-lg transition text-center"
            >
              View Documents
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
