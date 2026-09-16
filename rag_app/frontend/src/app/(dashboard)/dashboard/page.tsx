'use client';

import React, { useEffect, useState } from 'react';
import { BarChart3, FileText, Zap, TrendingUp, Plus, ArrowRight } from 'lucide-react';
import { mockAPI } from '@/lib/api/mocks';
import { IngestionStats } from '@/types';
import Link from 'next/link';

export default function DashboardPage() {
  const [stats, setStats] = useState<IngestionStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      setIsLoading(true);
      try {
        const data = await mockAPI.getIngestionStats();
        setStats(data);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, []);

  const statCards = stats
    ? [
        {
          title: 'Total Documents',
          value: stats.totalDocuments,
          icon: <FileText className="w-6 h-6" />,
          color: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600',
          trend: '+12 this month',
        },
        {
          title: 'Total Chunks',
          value: stats.totalChunks,
          icon: <Zap className="w-6 h-6" />,
          color: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600',
          trend: '+250 this month',
        },
        {
          title: 'Avg Chunk Size',
          value: `${stats.averageChunkSize} tokens`,
          icon: <BarChart3 className="w-6 h-6" />,
          color: 'bg-green-100 dark:bg-green-900/30 text-green-600',
          trend: 'Stable',
        },
        {
          title: 'Success Rate',
          value: `${(stats.successRate * 100).toFixed(0)}%`,
          icon: <TrendingUp className="w-6 h-6" />,
          color: 'bg-orange-100 dark:bg-orange-900/30 text-orange-600',
          trend: '+2% vs last month',
        },
      ]
    : [];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Welcome back! Here's your RAG pipeline overview.
          </p>
        </div>
        <Link
          href="/ingest"
          className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition"
        >
          <Plus className="w-5 h-5" />
          New Ingestion
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {isLoading ? (
          // Skeleton Loading
          Array(4)
            .fill(0)
            .map((_, i) => (
              <div
                key={i}
                className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700 animate-pulse"
              >
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-4" />
                <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-2/3 mb-2" />
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/3" />
              </div>
            ))
        ) : (
          statCards.map((card, index) => (
            <div
              key={index}
              className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700 hover:shadow-lg transition"
            >
              <div className={`inline-block p-3 rounded-lg ${card.color} mb-4`}>
                {card.icon}
              </div>
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">{card.title}</h3>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">{card.value}</p>
              <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">{card.trend}</p>
            </div>
          ))
        )}
      </div>

      {/* Recent Ingestions */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Recent Ingestion Jobs
          </h2>
          <Link
            href="/explorer"
            className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            View All
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700">
                <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">
                  Document
                </th>
                <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">
                  Type
                </th>
                <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">
                  Chunks
                </th>
                <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">
                  Status
                </th>
              </tr>
            </thead>
            <tbody>
              {[1, 2, 3, 4, 5].map((i) => (
                <tr key={i} className="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                  <td className="py-3 px-4">
                    <p className="font-medium text-gray-900 dark:text-white">Document {i}.pdf</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">2 days ago</p>
                  </td>
                  <td className="py-3 px-4">
                    <span className="text-gray-600 dark:text-gray-400">PDF</span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="font-medium text-gray-900 dark:text-white">{50 + i * 30}</span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="inline-block px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-medium rounded-full">
                      Completed
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
