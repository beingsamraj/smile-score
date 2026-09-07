const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export interface User {
  id: string;
  auth_user_id: string | null;
  employee_code: string;
  full_name: string;
  email: string | null;
  phone: string | null;
  role: "worker" | "supervisor" | "manager" | "admin";
  factory_id: string | null;
  factory_name: string | null;
  rfid_uid: string | null;
  status: "active" | "inactive";
  created_at: string;
  updated_at: string;
}

export interface UserListResponse {
  data: User[];
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

export async function getUsers(search?: string, factory_id?: string, role?: string, statusFilter?: string, page: number = 1, limit: number = 10) {
  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (factory_id) params.append('factory_id', factory_id);
  if (role && role !== 'all') params.append('role', role);
  if (statusFilter && statusFilter !== 'all') params.append('status', statusFilter);
  params.append('page', page.toString());
  params.append('limit', limit.toString());
  
  const query = params.toString();
  const url = `${API_URL}/api/users${query ? `?${query}` : ''}`;
  
  const res = await fetch(url, { cache: 'no-store' });
  return handleResponse(res);
}

export async function getUser(id: string) {
  const res = await fetch(`${API_URL}/api/users/${id}`, { cache: 'no-store' });
  return handleResponse(res);
}

export async function createUser(data: Partial<User>) {
  const res = await fetch(`${API_URL}/api/users`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse(res);
}

export async function updateUser(id: string, data: Partial<User>) {
  const res = await fetch(`${API_URL}/api/users/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse(res);
}

export async function deleteUser(id: string) {
  const res = await fetch(`${API_URL}/api/users/${id}`, {
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

export async function validateUsersCsv(file: File): Promise<CsvValidationPreview> {
  const formData = new FormData();
  formData.append('file', file);
  
  const res = await fetch(`${API_URL}/api/users/import/validate`, {
    method: 'POST',
    body: formData,
  });
  return handleResponse(res);
}

export async function importUsersCsv(file: File): Promise<CsvImportResponse> {
  const formData = new FormData();
  formData.append('file', file);
  
  const res = await fetch(`${API_URL}/api/users/import`, {
    method: 'POST',
    body: formData,
  });
  return handleResponse(res);
}

export function downloadUsersCsvTemplate() {
  const headers = ['full_name', 'email', 'phone', 'role', 'factory_code', 'rfid_uid', 'status'];
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
