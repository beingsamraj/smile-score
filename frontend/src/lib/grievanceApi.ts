/* eslint-disable @typescript-eslint/no-explicit-any */
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

async function handleResponse(res: Response) {
  if (!res.ok) {
    throw new Error("API Error: " + res.statusText);
  }
  return res.json();
}


export interface GrievanceMetrics {
  TOTAL: number;
  NEW: number;
  "UNDER REVIEW": number;
  RESOLVED: number;
}

export interface GrievanceRecord {
  grievance_id: string;
  employee_id: string;
  employee_name: string;
  department: string;
  workstation: string;
  grievance_status: string;
  trigger_reason: string;
  detected_at: string;
  latest_feedback: string;
  total_sad_count: number;
  last_sad_time: string;
  risk_level: string;
  risk_score: number;
}

export interface GrievanceDetail {
  grievance: any;
  notes: any[];
  history: any[];
  recent_feedbacks: any[];
}

export async function getGrievanceMetrics(): Promise<GrievanceMetrics> {
  const res = await fetch(`${API_URL}/api/grievances/metrics`, { cache: 'no-store' });
  const json = await handleResponse(res);
  return json.data;
}

export async function getGrievances(
  page = 1,
  limit = 20,
  status?: string,
  department?: string,
  dateFilter?: string,
  sortBy?: string
): Promise<{ data: GrievanceRecord[]; total: number; page: number; limit: number }> {
  const params = new URLSearchParams({
    page: page.toString(),
    limit: limit.toString(),
  });
  if (status && status !== 'ALL') params.append('status', status);
  if (department && department !== 'ALL') params.append('department', department);
  if (dateFilter && dateFilter !== 'all') params.append('date_filter', dateFilter);
  if (sortBy) params.append('sort_by', sortBy);
  
  const res = await fetch(`${API_URL}/api/grievances?${params.toString()}`, { cache: 'no-store' });
  return handleResponse(res);
}

export async function getGrievanceDetails(id: string): Promise<GrievanceDetail> {
  const res = await fetch(`${API_URL}/api/grievances/${id}`, { cache: 'no-store' });
  const json = await handleResponse(res);
  return json.data;
}

export async function updateGrievanceStatus(id: string, status: string, changedBy: string) {
  const res = await fetch(`${API_URL}/api/grievances/${id}/status`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status, changed_by: changedBy })
  });
  return handleResponse(res);
}

export async function addGrievanceNote(id: string, note: string, addedBy: string) {
  const res = await fetch(`${API_URL}/api/grievances/${id}/notes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ note, added_by: addedBy })
  });
  return handleResponse(res);
}

export async function triggerGrievanceDetection() {
  const res = await fetch(`${API_URL}/api/grievances/detect`, { cache: 'no-store' });
  return handleResponse(res);
}
