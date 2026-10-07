import os

with open('frontend/src/app/grievances/page.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    "const [dateFilter, setDateFilter] = useState('all');",
    "const [dateFilter, setDateFilter] = useState('all');\n  const [riskFilter, setRiskFilter] = useState('ALL');"
)

text = text.replace(
    "getGrievances(page, 20, statusFilter, deptFilter, dateFilter),",
    "getGrievances(page, 20, statusFilter, deptFilter, dateFilter, riskFilter),"
)

text = text.replace(
    "}, [page, statusFilter, deptFilter, dateFilter]);",
    "}, [page, statusFilter, deptFilter, dateFilter, riskFilter]);"
)

old_ui = """        <div className="flex items-center space-x-2">
          <input 
            type="date"
            value={dateFilter === 'all' ? '' : dateFilter}
            onChange={e => setDateFilter(e.target.value || 'all')}
            className="block w-full sm:w-48 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
          />
          {dateFilter !== 'all' && (
            <button 
              onClick={() => setDateFilter('all')}
              className="text-xs text-gray-500 hover:text-gray-700 underline"
            >
              Clear
            </button>
          )}
        </div>
      </div>"""

new_ui = """        <div className="flex items-center space-x-2">
          <input 
            type="date"
            value={dateFilter === 'all' ? '' : dateFilter}
            onChange={e => setDateFilter(e.target.value || 'all')}
            className="block w-full sm:w-48 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
          />
          {dateFilter !== 'all' && (
            <button 
              onClick={() => setDateFilter('all')}
              className="text-xs text-gray-500 hover:text-gray-700 underline"
            >
              Clear
            </button>
          )}
        </div>

        <select 
          value={riskFilter}
          onChange={e => setRiskFilter(e.target.value)}
          className="block w-full sm:w-48 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
        >
          <option value="ALL">All Risk Levels</option>
          <option value="LOW">Low Risk</option>
          <option value="MODERATE">Moderate Risk</option>
          <option value="HIGH">High Risk</option>
          <option value="CRITICAL">Critical Risk</option>
        </select>
      </div>"""

text = text.replace(old_ui, new_ui)

with open('frontend/src/app/grievances/page.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
