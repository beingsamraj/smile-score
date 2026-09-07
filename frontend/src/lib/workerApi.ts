const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export interface Worker {
  worker_id: string;
  employee_id: string;
  name: string;
  factory_id: string;
  factory_name: string | null;
  department_id: string;
  department_name: string | null;
  rfid_uid: string;
  designation: string | null;
  status: boolean;
  created_at: string;
}

export interface WorkerListResponse {
  data: Worker[];
  total: number;
  page: number;
  limit: number;
}

async function handleResponse(res: Response) {
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'API request failed');
  }
  if (res.status === 204) return null;
  return res.json();
}

export async function getWorkers(search?: string, factory_id?: string, department_id?: string, statusFilter?: string, page: number = 1, limit: number = 10) {
  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (factory_id) params.append('factory_id', factory_id);
  if (department_id) params.append('department_id', department_id);
  if (statusFilter && statusFilter !== 'all') params.append('status', statusFilter);
  params.append('page', page.toString());
  params.append('limit', limit.toString());
  
  const query = params.toString();
  const url = `${API_URL}/api/workers${query ? `?${query}` : ''}`;
  
  const res = await fetch(url, { cache: 'no-store' });
  return handleResponse(res);
}

export async function getWorker(id: string) {
  const res = await fetch(`${API_URL}/api/workers/${id}`, { cache: 'no-store' });
  return handleResponse(res);
}

export async function createWorker(data: Partial<Worker>) {
  const res = await fetch(`${API_URL}/api/workers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse(res);
}

export async function updateWorker(id: string, data: Partial<Worker>) {
  const res = await fetch(`${API_URL}/api/workers/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse(res);
}

export async function deleteWorker(id: string) {
  const res = await fetch(`${API_URL}/api/workers/${id}`, {
    method: 'DELETE',
  });
  return handleResponse(res);
}

export interface CsvRowError {
  row: number;
  errors: string[];
}

export interface CsvValidationPreview {
  valid: boolean;
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  errors: CsvRowError[];
}

export interface CsvImportResponse {
  success: boolean;
  imported_count: number;
  message: string;
}

export async function validateWorkersCsv(file: File): Promise<CsvValidationPreview> {
  const formData = new FormData();
  formData.append('file', file);
  
  const res = await fetch(`${API_URL}/api/workers/import/validate`, {
    method: 'POST',
    body: formData,
  });
  return handleResponse(res);
}

export async function importWorkersCsv(file: File): Promise<CsvImportResponse> {
  const formData = new FormData();
  formData.append('file', file);
  
  const res = await fetch(`${API_URL}/api/workers/import`, {
    method: 'POST',
    body: formData,
  });
  return handleResponse(res);
}

export function downloadWorkersCsvTemplate() {
  const headers = ['name', 'factory_id', 'department_id', 'rfid_uid', 'designation', 'status'];
  const csvContent = headers.join(',') + '\n';
  
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', 'workers_import_template.csv');
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
