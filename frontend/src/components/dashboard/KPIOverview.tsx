/* eslint-disable @typescript-eslint/no-explicit-any */
export default function KPIOverview({ data }: { data: any }) {
  if (!data) return <div className="p-4 bg-white rounded shadow animate-pulse">Loading KPIs...</div>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-6">
      <KPICard title="Active Workers" value={data.active_workers} />
      <KPICard title="Smile Score" value={data.overall_smile_score} />
      <KPICard title="Happy %" value={`${data.happy_percentage}%`} color="text-green-600" />
      <KPICard title="OK %" value={`${data.ok_percentage}%`} color="text-yellow-600" />
      <KPICard title="Sad %" value={`${data.sad_percentage}%`} color="text-red-600" />
      <KPICard 
        title="Prod. Risk" 
        value={data.production_risk?.level || "NO_DATA"} 
        color={data.production_risk?.level === 'HIGH' ? 'text-red-600' : 'text-gray-800'}
      />
    </div>
  );
}

function KPICard({ title, value, color = "text-gray-900" }: { title: string, value: any, color?: string }) {
  return (
    <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-center">
      <h3 className="text-sm font-medium text-gray-500 mb-1">{title}</h3>
      <p className={`text-2xl font-bold ${color}`}>{value !== null && value !== undefined ? value : '-'}</p>
    </div>
  );
}
