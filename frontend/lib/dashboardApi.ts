import { API_URL } from './api';

async function fetchApi(endpoint: string) {
  try {
    const res = await fetch(`${API_URL}/api/dashboard${endpoint}`, {
      cache: 'no-store', // Always fetch fresh data for the dashboard
    });
    if (!res.ok) throw new Error('Failed to fetch data');
    return await res.json();
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error);
    return null;
  }
}

export async function getDashboardOverview() {
  return fetchApi('/overview');
}

export async function getSmileTrend(period = 'today') {
  return fetchApi(`/smile-trend?period=${period}`);
}

export async function getSmileForecast(hours = 4) {
  return fetchApi(`/smile-forecast?hours=${hours}`);
}

export async function getEmotionDistribution() {
  return fetchApi('/emotion-distribution');
}

export async function getWorkers() {
  return fetchApi('/workers');
}

export async function getAlerts() {
  return fetchApi('/alerts');
}

export async function getProductionRisk() {
  return fetchApi('/production-risk');
}

export async function getDepartments() {
  return fetchApi('/departments');
}

export async function getDevices() {
  return fetchApi('/devices');
}

export async function getRecentActivity() {
  return fetchApi('/recent-activity');
}

export async function getButtonFeedback() {
  return fetchApi('/button-feedback');
}

export async function getAIInsights() {
  return fetchApi('/ai-insights');
}

export async function getShiftAnalysis() {
  return fetchApi('/shifts');
}



export async function getFactoryRisk(factoryId = 'FAC001') {
  try {
    const res = await fetch(`${API_URL}/api/risk/factory/${factoryId}`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to fetch data');
    return await res.json();
  } catch (error) {
    console.error('API Error:', error);
    return null;
  }
}

export async function getRecommendations(factoryId = 'FAC001') {
  try {
    const res = await fetch(`${API_URL}/api/recommendations/factory/${factoryId}`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to fetch data');
    return await res.json();
  } catch (error) {
    console.error('API Error:', error);
    return null;
  }
}
