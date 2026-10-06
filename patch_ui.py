import os

with open('frontend/src/app/dashboard/page.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('getSmileForecast\n  }', 'getSmileForecast,\n    getFactoryRisk,\n    getRecommendations\n  }')
text = text.replace('const [activityData, setActivityData] = useState<any>(null);', 'const [activityData, setActivityData] = useState<any>(null);\n  const [riskData, setRiskData] = useState<any>(null);\n  const [recommendationsData, setRecommendationsData] = useState<any>(null);')
text = text.replace('const [overview, trend, forecast, emotion, workers, alerts, activity] = await Promise.all([', 'const [overview, trend, forecast, emotion, workers, alerts, activity, risk, recs] = await Promise.all([')
text = text.replace('getRecentActivity()\n        ]);', 'getRecentActivity(),\n          getFactoryRisk(),\n          getRecommendations()\n        ]);')
text = text.replace('setActivityData(activity);', 'setActivityData(activity);\n      setRiskData(risk);\n      setRecommendationsData(recs);')

ui_banner = """
        <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
          
          {riskData && riskData.risk_level && (
            <div className={`mb-6 p-4 rounded-xl shadow-sm border ${riskData.risk_level === 'HIGH' ? 'bg-red-50 border-red-200 text-red-800' : riskData.risk_level === 'MEDIUM' ? 'bg-yellow-50 border-yellow-200 text-yellow-800' : 'bg-green-50 border-green-200 text-green-800'}`}>
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-bold flex items-center space-x-2">
                    <span>AI Production Risk: {riskData.risk_level}</span>
                    <span className="text-xs font-normal opacity-80">(Confidence: {(riskData.confidence * 100).toFixed(0)}%)</span>
                  </h3>
                  <p className="text-sm mt-1 opacity-90">Active Workers: {riskData.features?.active_workers} | Avg Smile: {riskData.features?.average_smile_score}</p>
                </div>
                {recommendationsData && recommendationsData.recommendations && recommendationsData.recommendations.length > 0 && (
                  <div className="text-sm bg-white/50 px-4 py-2 rounded-lg">
                    <strong>AI Recommendation:</strong> {recommendationsData.recommendations[0].action}
                  </div>
                )}
              </div>
            </div>
          )}

          <div className="flex items-center justify-between mb-6">
"""

text = text.replace('<main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">\n          <div className="flex items-center justify-between mb-6">', ui_banner)

with open('frontend/src/app/dashboard/page.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
