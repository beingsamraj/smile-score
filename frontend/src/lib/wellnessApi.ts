export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export interface WellnessRecord {
  employee_id: string;
  status: string;
  total_alerts: number;
  avg_hr: number;
  avg_spo2: number;
  avg_temp: number;
  detected_at: string;
  employee_name: string;
  department: string;
  workstation: string;
  risk_level: string;
}

export interface WellnessDetail {
  record: WellnessRecord;
  notes: any[];
  readings: any[];
}

async function handleResponse(res: Response) {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json();
}

export async function getWellnessMetrics() {
  const res = await fetch(`${API_URL}/api/wellness/metrics`, { cache: 'no-store' });
  const json = await handleResponse(res);
  return json.data;
}

export async function getWellness(
  page = 1,
  limit = 20,
  status?: string,
  department?: string,
  dateFilter?: string,
  sortBy?: string
): Promise<{ data: WellnessRecord[]; total: number; page: number; limit: number }> {
  const params = new URLSearchParams({
    page: page.toString(),
    limit: limit.toString(),
  });
  if (status && status !== 'ALL') params.append('status', status);
  if (department && department !== 'ALL') params.append('department', department);
  if (dateFilter && dateFilter !== 'all') params.append('date_filter', dateFilter);
  if (sortBy) params.append('sort_by', sortBy);
  
  const res = await fetch(`${API_URL}/api/wellness?${params.toString()}`, { cache: 'no-store' });
  return handleResponse(res);
}

export async function getWellnessDetails(employeeId: string): Promise<WellnessDetail> {
  const res = await fetch(`${API_URL}/api/wellness/${employeeId}`, { cache: 'no-store' });
  const json = await handleResponse(res);
  return json.data;
}

export async function updateWellnessStatus(employeeId: string, status: string, changedBy: string) {
  const res = await fetch(`${API_URL}/api/wellness/${employeeId}/status`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status, changed_by: changedBy })
  });
  return handleResponse(res);
}

export async function addWellnessNote(employeeId: string, note: string, addedBy: string) {
  const res = await fetch(`${API_URL}/api/wellness/${employeeId}/notes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ note, added_by: addedBy })
  });
  return handleResponse(res);
}

export function downloadWellnessReport() {
  window.open(`${API_URL}/api/wellness/export`, '_blank');
}
