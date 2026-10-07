import os

with open('frontend/src/lib/grievanceApi.ts', 'r', encoding='utf-8') as f:
    text = f.read()

header = """/* eslint-disable @typescript-eslint/no-explicit-any */
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

async function handleResponse(res: Response) {
  if (!res.ok) {
    throw new Error("API Error: " + res.statusText);
  }
  return res.json();
}
"""

text = text.replace("import { API_URL, handleResponse } from './api';", header)
text = text.replace("/* eslint-disable @typescript-eslint/no-explicit-any */\nexport interface GrievanceDetail {", "export interface GrievanceDetail {")

with open('frontend/lib/grievanceApi.ts', 'w', encoding='utf-8') as f:
    f.write(text)

try:
    os.remove('frontend/src/lib/grievanceApi.ts')
except:
    pass
