'use client';

import React, { useState } from 'react';
import { Search, ArrowRight, Loader, ChevronDown } from 'lucide-react';
import { mockAPI } from '@/lib/api/mocks';
import { SearchResultSet } from '@/types';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResultSet | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [expandedResults, setExpandedResults] = useState<Set<string>>(new Set());
  const [searchHistory, setSearchHistory] = useState<string[]>([]);

  const handleSearch = async (e: React.FormEvent | string) => {
    if (typeof e === 'string') {
      setQuery(e);
    } else {
      e.preventDefault();
    }

    const searchQuery = typeof e === 'string' ? e : query;
    if (!searchQuery.trim()) return;

    setIsLoading(true);
    try {
      const data = await mockAPI.searchChunks(searchQuery, 10);
      setResults(data);
      setSearchHistory((prev) => [searchQuery, ...prev.filter((q) => q !== searchQuery)].slice(0, 5));
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleExpanded = (resultId: string) => {
    const newExpanded = new Set(expandedResults);
    if (newExpanded.has(resultId)) {
      newExpanded.delete(resultId);
    } else {
      newExpanded.add(resultId);
    }
    setExpandedResults(newExpanded);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">RAG Search & Test</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Test your RAG pipeline by searching across ingested documents
        </p>
      </div>

      {/* Search Box */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="flex-1 relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search documents..."
            className="w-full px-4 py-3 pl-4 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={isLoading || !query.trim()}
            className="absolute right-3 top-1/2 -translate-y-1/2 p-2 text-gray-400 hover:text-blue-600 disabled:opacity-50"
          >
            <Search className="w-5 h-5" />
          </button>
        </div>
      </form>

      {/* Search History */}
      {searchHistory.length > 0 && !results && (
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-900/50 rounded-lg p-4">
          <p className="text-sm font-medium text-blue-900 dark:text-blue-300 mb-3">
            Recent Searches
          </p>
          <div className="flex flex-wrap gap-2">
            {searchHistory.map((item, idx) => (
              <button
                key={idx}
                onClick={() => handleSearch(item)}
                className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 hover:bg-blue-200 dark:hover:bg-blue-900/50 text-blue-700 dark:text-blue-300 text-sm rounded-full transition"
              >
                {item}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <Loader className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-3" />
            <p className="text-gray-600 dark:text-gray-400">Searching...</p>
          </div>
        </div>
      )}

      {/* Results */}
      {results && !isLoading && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Results ({results.totalResults})
            </h2>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Found in {results.processingTimeMs}ms
            </p>
          </div>

          {results.results.length === 0 ? (
            <div className="py-12 px-6 text-center bg-gray-50 dark:bg-gray-800 rounded-lg">
              <p className="text-gray-500 dark:text-gray-400">
                No results found for "{results.query}"
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {results.results.map((result, idx) => (
                <div
                  key={idx}
                  className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden hover:shadow-lg transition"
                >
                  <button
                    onClick={() => toggleExpanded(result.chunkId)}
                    className="w-full p-4 text-left flex items-start justify-between gap-4 hover:bg-gray-50 dark:hover:bg-gray-700/50"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <p className="font-medium text-gray-900 dark:text-white">
                          {result.documentName}
                        </p>
                        {result.section && (
                          <span className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 px-2 py-1 rounded">
                            {result.section}
                          </span>
                        )}
                      </div>
                      <p className="text-gray-600 dark:text-gray-400 text-sm line-clamp-2">
                        {result.chunkText}
                      </p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-gray-500 dark:text-gray-500">
                        <span>
                          Relevance:{' '}
                          <span className="font-medium text-gray-700 dark:text-gray-300">
                            {(result.relevanceScore * 100).toFixed(0)}%
                          </span>
                        </span>
                        <span>
                          Confidence:{' '}
                          <span className="font-medium text-gray-700 dark:text-gray-300">
                            {(result.confidence * 100).toFixed(0)}%
                          </span>
                        </span>
                      </div>
                    </div>
                    <ChevronDown
                      className={`w-5 h-5 text-gray-400 flex-shrink-0 transition ${
                        expandedResults.has(result.chunkId) ? 'rotate-180' : ''
                      }`}
                    />
                  </button>

                  {expandedResults.has(result.chunkId) && (
                    <div className="px-4 py-4 bg-gray-50 dark:bg-gray-700/50 border-t border-gray-200 dark:border-gray-700">
                      <p className="text-sm text-gray-700 dark:text-gray-300 mb-4">
                        {result.chunkText}
                      </p>
                      <button className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-700 text-sm font-medium">
                        Copy Text
                        <ArrowRight className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
