import { API_URL } from './api';

export async function login(username: string, password: string) {
  try {
    const res = await fetch(`${API_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (!res.ok) {
      const errorData = await res.json();
      return { data: null, error: new Error(errorData.detail || 'Login failed') };
    }

    const data = await res.json();
    
    // Store simple custom session in localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('custom_session', JSON.stringify(data.user));
    }
    
    return { data: { session: data.user }, error: null };
  } catch (error) {
    return { data: null, error };
  }
}

export async function logout() {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('custom_session');
  }
  return { error: null };
}

export async function getSession() {
  if (typeof window !== 'undefined') {
    const sessionStr = localStorage.getItem('custom_session');
    if (sessionStr) {
      try {
        const session = JSON.parse(sessionStr);
        return { data: { session }, error: null };
      } catch {
        return { data: { session: null }, error: null };
      }
    }
  }
  return { data: { session: null }, error: null };
}

export async function getCurrentUser() {
  return getSession();
}
