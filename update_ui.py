import os

with open('frontend/src/app/grievances/page.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

old_ui = """        <select 
          value={dateFilter}
          onChange={e => setDateFilter(e.target.value)}
          className="block w-full sm:w-48 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
        >
          <option value="all">All Time</option>
          <option value="today">Today</option>
          <option value="7d">Last 7 Days</option>
          <option value="30d">Last 30 Days</option>
        </select>"""

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
        </div>"""

text = text.replace(old_ui, new_ui)

with open('frontend/src/app/grievances/page.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
