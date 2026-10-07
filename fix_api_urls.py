import os

with open('frontend/lib/dashboardApi.ts', 'r', encoding='utf-8') as f:
    text = f.read()

replacement = """
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
"""

import re
text = re.sub(r'export async function getFactoryRisk.*', replacement, text, flags=re.DOTALL)

with open('frontend/lib/dashboardApi.ts', 'w', encoding='utf-8') as f:
    f.write(text)
