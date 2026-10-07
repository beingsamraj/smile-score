import os

with open('frontend/src/app/grievances/page.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

old_text = """          {departments.map((d: any) /* eslint-disable-line @typescript-eslint/no-explicit-any */ => (
            <option key={d.id || d.name} value={d.name}>{d.name}</option>
          ))}
        </select>
      </div>"""

new_text = """          {departments.map((d: any) /* eslint-disable-line @typescript-eslint/no-explicit-any */ => (
            <option key={d.id || d.name} value={d.name}>{d.name}</option>
          ))}
        </select>

        <select 
          value={dateFilter}
          onChange={e => setDateFilter(e.target.value)}
          className="block w-full sm:w-48 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
        >
          <option value="all">All Time</option>
          <option value="today">Today</option>
          <option value="7d">Last 7 Days</option>
          <option value="30d">Last 30 Days</option>
        </select>
      </div>"""

text = text.replace(old_text, new_text)

with open('frontend/src/app/grievances/page.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
