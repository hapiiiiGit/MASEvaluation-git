/**
 * API utility for the dashboard.
 * Handles fetching metrics, reports, subscribing to real-time metrics, and exporting reports.
 * Uses TypeScript and fetch API.
 */

import { Metric, Report } from './types';

// Backend API base URL (adjust for your deployment)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:4000/api';

// Fetch metrics for the current user (requires JWT token in localStorage)
export async function fetchMetrics(): Promise<Metric[]> {
  const token = localStorage.getItem('token');
  const res = await fetch(`${API_BASE_URL}/dashboard/metrics`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token || ''}`,
      'Content-Type': 'application/json',
    },
  });
  if (!res.ok) {
    throw new Error('Failed to fetch metrics');
  }
  const data = await res.json();
  return data.metrics as Metric[];
}

// Fetch reports for the current user (requires JWT token)
export async function fetchReports(): Promise<Report[]> {
  const token = localStorage.getItem('token');
  const res = await fetch(`${API_BASE_URL}/dashboard/reports`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token || ''}`,
      'Content-Type': 'application/json',
    },
  });
  if (!res.ok) {
    throw new Error('Failed to fetch reports');
  }
  const data = await res.json();
  return data.reports as Report[];
}

// Subscribe to real-time metric updates using WebSocket
export function subscribeToRealtimeMetrics(
  onMetric: (metric: Metric) => void
): () => void {
  const token = localStorage.getItem('token');
  // Use native WebSocket API
  const wsUrl = API_BASE_URL.replace(/^http/, 'ws') + '/dashboard/metrics/realtime';
  const ws = new WebSocket(wsUrl + `?token=${token}`);

  ws.onmessage = (event) => {
    try {
      const metric: Metric = JSON.parse(event.data);
      onMetric(metric);
    } catch (err) {
      // Ignore malformed messages
    }
  };

  ws.onerror = () => {
    // Optionally handle error
  };

  // Return unsubscribe function
  return () => {
    ws.close();
  };
}

// Export a report in the specified format (CSV or PDF)
export async function exportReport(reportId: string, format: 'csv' | 'pdf'): Promise<Blob> {
  const token = localStorage.getItem('token');
  const res = await fetch(`${API_BASE_URL}/report/export/${reportId}?format=${format}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token || ''}`,
    },
  });
  if (!res.ok) {
    throw new Error('Failed to export report');
  }
  const blob = await res.blob();
  return blob;
}