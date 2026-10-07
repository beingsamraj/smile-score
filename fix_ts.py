import os

with open('frontend/lib/dashboardApi.ts', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("return fetchApi(/risk/factory/);", "return fetchApi(`/risk/factory/${factoryId}`);")
text = text.replace("return fetchApi(/recommendations/factory/);", "return fetchApi(`/recommendations/factory/${factoryId}`);")

with open('frontend/lib/dashboardApi.ts', 'w', encoding='utf-8') as f:
    f.write(text)
