'use client';

import React, { useEffect, useState } from 'react';
import { Code, Copy, Download, Grid3x3, Loader } from 'lucide-react';
import { mockAPI } from '@/lib/api/mocks';
import { CodeLanguage, APIEndpoint } from '@/types';

export default function IntegrationPage() {
  const [activeTab, setActiveTab] = useState<'endpoints' | 'code'>('endpoints');
  const [endpoints, setEndpoints] = useState<APIEndpoint[]>([]);
  const [selectedLanguage, setSelectedLanguage] = useState(CodeLanguage.PYTHON);
  const [generatedCode, setGeneratedCode] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const endpointsData = await mockAPI.getAPIEndpoints();
        setEndpoints(endpointsData);

        const codeSnippet = await mockAPI.generateCodeSnippet(
          selectedLanguage,
          endpointsData[1]?.path || '/api/search'
        );
        setGeneratedCode(codeSnippet.code);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [selectedLanguage]);

  const handleCopyCode = () => {
    navigator.clipboard.writeText(generatedCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">API Integration</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Integrate RAG API endpoints and use code examples
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-200 dark:border-gray-700">
        <button
          onClick={() => setActiveTab('endpoints')}
          className={`px-4 py-3 font-medium border-b-2 transition ${
            activeTab === 'endpoints'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-300'
          }`}
        >
          <Grid3x3 className="w-4 h-4 inline mr-2" />
          API Endpoints
        </button>
        <button
          onClick={() => setActiveTab('code')}
          className={`px-4 py-3 font-medium border-b-2 transition ${
            activeTab === 'code'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-300'
          }`}
        >
          <Code className="w-4 h-4 inline mr-2" />
          Code Examples
        </button>
      </div>

      {/* Endpoints Tab */}
      {activeTab === 'endpoints' && (
        <div className="space-y-4">
          {isLoading ? (
            <div className="flex justify-center py-12">
              <Loader className="w-6 h-6 animate-spin text-blue-500" />
            </div>
          ) : (
            endpoints.map((endpoint, idx) => (
              <div
                key={idx}
                className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="inline-block px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-sm font-mono font-medium rounded">
                        {endpoint.method}
                      </span>
                      <span className="font-mono text-gray-600 dark:text-gray-400">
                        {endpoint.path}
                      </span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {endpoint.name}
                    </h3>
                  </div>
                </div>

                <p className="text-gray-600 dark:text-gray-400 mb-4">{endpoint.description}</p>

                {endpoint.example && (
                  <div className="bg-gray-50 dark:bg-gray-700/50 rounded p-4 font-mono text-sm text-gray-700 dark:text-gray-300">
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">Example Response:</p>
                    <pre className="overflow-x-auto">
                      {JSON.stringify(endpoint.example, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Code Examples Tab */}
      {activeTab === 'code' && (
        <div className="space-y-4">
          {/* Language Selector */}
          <div className="flex gap-2">
            {[CodeLanguage.PYTHON, CodeLanguage.JAVASCRIPT, CodeLanguage.TYPESCRIPT, CodeLanguage.CURL].map(
              (lang) => (
                <button
                  key={lang}
                  onClick={() => setSelectedLanguage(lang)}
                  className={`px-4 py-2 rounded-lg font-medium transition ${
                    selectedLanguage === lang
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                  }`}
                >
                  {lang.charAt(0).toUpperCase() + lang.slice(1)}
                </button>
              )
            )}
          </div>

          {/* Code Block */}
          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
            {/* Header */}
            <div className="bg-gray-50 dark:bg-gray-700/50 px-4 py-3 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                {selectedLanguage.charAt(0).toUpperCase() + selectedLanguage.slice(1)} Example
              </p>
              <button
                onClick={handleCopyCode}
                className="flex items-center gap-2 px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition"
              >
                <Copy className="w-4 h-4" />
                {copied ? 'Copied!' : 'Copy'}
              </button>
            </div>

            {/* Code */}
            <div className="p-6 bg-gray-900 text-gray-100 font-mono text-sm overflow-x-auto">
              <pre>{generatedCode}</pre>
            </div>
          </div>

          {/* Download Button */}
          <button className="inline-flex items-center gap-2 px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-900 dark:text-white font-medium rounded-lg transition">
            <Download className="w-4 h-4" />
            Download Code
          </button>
        </div>
      )}
    </div>
  );
}
