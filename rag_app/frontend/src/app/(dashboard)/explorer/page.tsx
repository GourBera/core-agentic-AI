'use client';

import React, { useEffect, useState } from 'react';
import { Document } from '@/types';
import { mockAPI } from '@/lib/api/mocks';
import { FileText, Trash2, Eye, Download, Loader } from 'lucide-react';

export default function ExplorerPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const data = await mockAPI.getDocuments();
        setDocuments(data);
      } catch (error) {
        console.error('Failed to fetch documents:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDocuments();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Document Explorer</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Browse and manage your ingested documents
        </p>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 dark:bg-gray-700/50 border-b border-gray-200 dark:border-gray-700">
                <th className="text-left py-4 px-6 font-medium text-gray-700 dark:text-gray-300">
                  Document
                </th>
                <th className="text-left py-4 px-6 font-medium text-gray-700 dark:text-gray-300">
                  Type
                </th>
                <th className="text-left py-4 px-6 font-medium text-gray-700 dark:text-gray-300">
                  Chunks
                </th>
                <th className="text-left py-4 px-6 font-medium text-gray-700 dark:text-gray-300">
                  Size
                </th>
                <th className="text-left py-4 px-6 font-medium text-gray-700 dark:text-gray-300">
                  Uploaded
                </th>
                <th className="text-left py-4 px-6 font-medium text-gray-700 dark:text-gray-300">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="py-12 px-6 text-center">
                    <Loader className="w-6 h-6 animate-spin mx-auto text-gray-400" />
                    <p className="text-gray-500 dark:text-gray-400 mt-2">Loading documents...</p>
                  </td>
                </tr>
              ) : documents.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 px-6 text-center">
                    <p className="text-gray-500 dark:text-gray-400">No documents found</p>
                  </td>
                </tr>
              ) : (
                documents.map((doc) => (
                  <tr
                    key={doc.id}
                    className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition"
                  >
                    <td className="py-4 px-6">
                      <div className="flex items-center gap-3">
                        <FileText className="w-5 h-5 text-blue-500" />
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">{doc.name}</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {doc.metadata?.language || 'unknown'}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      <span className="inline-block px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-xs font-medium rounded-full">
                        {doc.type.toUpperCase()}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-gray-900 dark:text-white font-medium">
                      {doc.chunkCount}
                    </td>
                    <td className="py-4 px-6 text-gray-600 dark:text-gray-400">
                      {(doc.size / 1024 / 1024).toFixed(2)} MB
                    </td>
                    <td className="py-4 px-6 text-gray-600 dark:text-gray-400">
                      {new Date(doc.uploadedAt).toLocaleDateString()}
                    </td>
                    <td className="py-4 px-6">
                      <div className="flex items-center gap-2">
                        <button
                          title="View chunks"
                          className="p-2 hover:bg-gray-200 dark:hover:bg-gray-600 rounded transition"
                        >
                          <Eye className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                        </button>
                        <button
                          title="Download"
                          className="p-2 hover:bg-gray-200 dark:hover:bg-gray-600 rounded transition"
                        >
                          <Download className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                        </button>
                        <button
                          title="Delete"
                          className="p-2 hover:bg-red-100 dark:hover:bg-red-900/30 rounded transition"
                        >
                          <Trash2 className="w-4 h-4 text-red-600 dark:text-red-400" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
