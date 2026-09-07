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


