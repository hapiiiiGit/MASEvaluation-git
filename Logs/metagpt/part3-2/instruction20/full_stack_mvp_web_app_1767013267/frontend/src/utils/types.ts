/**
 * TypeScript types for Metric and Report used in the dashboard components.
 * These types are based on the system design class diagram and backend data models.
 */

export interface Metric {
  id: string; // UUID
  name: string;
  value: number;
  timestamp: string; // ISO date string
  user_id: string; // UUID
}

export interface Report {
  id: string; // UUID
  title: string;
  data: { [key: string]: string | number | boolean | null }; // Flat object for report data
  created_by: string; // UUID
  created_at: string; // ISO date string
}