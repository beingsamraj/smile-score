import { API_URL } from './api';
import { getSession } from './auth';

async function fetchApi(endpoint: string, queryParams: Record<string, string | undefined> = {}) {
  const sessionData = await getSession();
  const session = sessionData.data.session;
  
  // Clean up undefined query params
  const params = new URLSearchParams();
  Object.entries(queryParams).forEach(([key, value]) => {
    if (value) params.append(key, value);
  });
  
  const queryString = params.toString() ? `?${params.toString()}` : '';

  try {
    const res = await fetch(`${API_URL}/api/reports${endpoint}${queryString}`, {
      headers: {
        'Authorization': session ? `Bearer ${session.user_id}` : '',
        'Content-Type': 'application/json'
      }
    });
    if (!res.ok) {
      throw new Error('Failed to fetch report data');
    }
    return await res.json();
  } catch (error) {
    console.error(`API Error on /reports${endpoint}:`, error);
    throw error;
  }
}

export async function getReportSummary(filters: any = {}) {
  return fetchApi('/summary', filters);
}

export async function getSmileScoreTrend(filters: any = {}) {
  return fetchApi('/smile-score-trend', filters);
}

export async function getEmotionDistribution(filters: any = {}) {
  return fetchApi('/emotion-distribution', filters);
}

export async function getDepartmentsAnalysis(filters: any = {}) {
  return fetchApi('/departments', filters);
}

export async function getFactoriesAnalysis(filters: any = {}) {
  return fetchApi('/factories', filters);
}

export async function getWorkersAnalysis(filters: any = {}) {
  return fetchApi('/workers', filters);
}

export async function getIndividualWorkerReport(workerId: string, filters: any = {}) {
  return fetchApi(`/workers/${workerId}`, filters);
}

export async function getRiskAnalysis(filters: any = {}) {
  return fetchApi('/risk-analysis', filters);
}

export async function getReportLogs(filters: any = {}) {
  return fetchApi('/logs', filters);
}
