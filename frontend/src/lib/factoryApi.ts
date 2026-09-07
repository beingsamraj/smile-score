const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export interface Factory {
  factory_id: string;
  factory_name: string;
  factory_address: string | null;
  no_of_employees: number | null;
  status: boolean;
  created_at: string;
}

async function handleResponse(res: Response) {
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'API request failed');
  }
  if (res.status === 204) return null;
  return res.json();
}

export async function getFactories(search?: string, statusFilter?: string) {
  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (statusFilter && statusFilter !== 'all') params.append('status', statusFilter);
  
  const query = params.toString();
  const url = `${API_URL}/api/factories${query ? `?${query}` : ''}`;
  
  const res = await fetch(url, { cache: 'no-store' });
  return handleResponse(res);
}

export async function getFactory(id: string) {
  const res = await fetch(`${API_URL}/api/factories/${id}`, { cache: 'no-store' });
  return handleResponse(res);
}

export async function createFactory(data: Partial<Factory>) {
  const res = await fetch(`${API_URL}/api/factories`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse(res);
}

export async function updateFactory(id: string, data: Partial<Factory>) {
  const res = await fetch(`${API_URL}/api/factories/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse(res);
}

export async function deleteFactory(id: string) {
  const res = await fetch(`${API_URL}/api/factories/${id}`, {
    method: 'DELETE',
  });
  return handleResponse(res);
}
