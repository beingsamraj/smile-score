const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export interface Device {
  id: string;
  device_code: string;
  device_name: string;
  device_type: "esp32" | "rfid_reader" | "button_panel" | "camera" | "gateway" | "other";
  factory_id: string | null;
  factory_name: string | null;
  mac_address: string | null;
  location: string | null;
  firmware_version: string | null;
  status: "online" | "offline" | "inactive" | "maintenance";
  last_seen: string | null;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface DeviceListResponse {
  data: Device[];
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

export async function getDevices(search?: string, factory_id?: string, device_type?: string, statusFilter?: string, page: number = 1, limit: number = 10) {
  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (factory_id) params.append('factory_id', factory_id);
  if (device_type && device_type !== 'all') params.append('device_type', device_type);
  if (statusFilter && statusFilter !== 'all') params.append('status', statusFilter);
  params.append('page', page.toString());
  params.append('limit', limit.toString());
  
  const query = params.toString();
  const url = `${API_URL}/api/devices${query ? `?${query}` : ''}`;
  
  const res = await fetch(url, { cache: 'no-store' });
  return handleResponse(res);
}

export async function getDevice(id: string) {
  const res = await fetch(`${API_URL}/api/devices/${id}`, { cache: 'no-store' });
  return handleResponse(res);
}

export async function createDevice(data: Partial<Device>) {
  const res = await fetch(`${API_URL}/api/devices`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse(res);
}

export async function updateDevice(id: string, data: Partial<Device>) {
  const res = await fetch(`${API_URL}/api/devices/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse(res);
}

export async function deleteDevice(id: string) {
  const res = await fetch(`${API_URL}/api/devices/${id}`, {
    method: 'DELETE',
  });
  return handleResponse(res);
}
