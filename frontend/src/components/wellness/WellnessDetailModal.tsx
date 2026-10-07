import { useState, useEffect } from 'react';
import { X, Activity, User, MessageCircle, Heart, Thermometer } from 'lucide-react';
import { getWellnessDetails, updateWellnessStatus, addWellnessNote, WellnessDetail } from '@/lib/wellnessApi';

interface ModalProps {
  employeeId: string;
  onClose: () => void;
  onUpdated: () => void;
}

export default function WellnessDetailModal({ employeeId, onClose, onUpdated }: ModalProps) {
  const [data, setData] = useState<WellnessDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [note, setNote] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);

  const fetchDetails = async () => {
    setLoading(true);
    try {
      const res = await getWellnessDetails(employeeId);
      setData(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetails(); // eslint-disable-line
  }, [employeeId]);

  const handleStatusChange = async (newStatus: string) => {
    setIsUpdating(true);
    try {
      await updateWellnessStatus(employeeId, newStatus, 'Admin User');
      await fetchDetails(); // eslint-disable-line
      onUpdated();
    } catch (e) {
      console.error(e);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleAddNote = async () => {
    if (!note.trim()) return;
    setIsUpdating(true);
    try {
      await addWellnessNote(employeeId, note, 'Nurse');
      setNote('');
      await fetchDetails(); // eslint-disable-line
    } catch (e) {
      console.error(e);
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 transition-opacity" aria-hidden="true" onClick={onClose}>
          <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
        </div>

        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

        <div className="relative z-10 inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl w-full">
          {loading || !data ? (
            <div className="p-8 text-center text-gray-500">Loading details...</div>
          ) : (
            <div className="bg-white">
              {/* Header */}
              <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center bg-blue-50">
                <h3 className="text-lg leading-6 font-medium text-blue-900 flex items-center">
                  <Activity className="w-5 h-5 mr-2" />
                  Medical & Wellness Details
                </h3>
                <button onClick={onClose} className="text-gray-400 hover:text-gray-500">
                  <X className="w-6 h-6" />
                </button>
              </div>

              <div className="px-6 py-4 grid grid-cols-1 md:grid-cols-3 gap-6">
                
                {/* Left Column: Employee Info & Actions */}
                <div className="md:col-span-1 space-y-6">
                  <div>
                    <h4 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-2 flex items-center">
                      <User className="w-4 h-4 mr-2 text-gray-500" />
                      Employee
                    </h4>
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <div className="font-medium text-gray-900">{data.record.employee_name}</div>
                      <div className="text-sm text-gray-500">{data.record.employee_id}</div>
                      <div className="text-sm text-gray-500 mt-1">{data.record.department} | {data.record.workstation}</div>
                    </div>
                  </div>

                  <div>
                    <h4 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-2 flex items-center">
                      <Activity className="w-4 h-4 mr-2 text-gray-500" />
                      Current Status
                    </h4>
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        data.record.status === 'REFERRED TO NURSE' ? 'bg-orange-100 text-orange-800' :
                        data.record.status === 'TREATED' ? 'bg-green-100 text-green-800' :
                        data.record.status === 'SENT TO HOSPITAL' ? 'bg-red-100 text-red-800' :
                        'bg-red-50 text-red-700'
                      }`}>
                        {data.record.status}
                      </span>

                      <div className="space-y-2 mt-4">
                        {data.record.status !== 'REFERRED TO NURSE' && (
                          <button 
                            disabled={isUpdating}
                            onClick={() => handleStatusChange('REFERRED TO NURSE')}
                            className="w-full text-center text-sm bg-orange-100 text-orange-800 hover:bg-orange-200 py-2 rounded-md font-medium transition-colors"
                          >
                            Refer to Nurse
                          </button>
                        )}
                        {data.record.status !== 'TREATED' && (
                          <button 
                            disabled={isUpdating}
                            onClick={() => handleStatusChange('TREATED')}
                            className="w-full text-center text-sm bg-green-100 text-green-800 hover:bg-green-200 py-2 rounded-md font-medium transition-colors"
                          >
                            Mark as Treated
                          </button>
                        )}
                        {data.record.status !== 'SENT TO HOSPITAL' && (
                          <button 
                            disabled={isUpdating}
                            onClick={() => handleStatusChange('SENT TO HOSPITAL')}
                            className="w-full text-center text-sm bg-red-100 text-red-800 hover:bg-red-200 py-2 rounded-md font-medium transition-colors"
                          >
                            Send to Hospital
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Right Column: Readings & Notes */}
                <div className="md:col-span-2 space-y-6">
                  
                  <div>
                    <h4 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-2">
                      Recent Anomalous Vitals
                    </h4>
                    <div className="bg-gray-50 rounded-lg p-4 max-h-48 overflow-y-auto">
                      <table className="min-w-full text-sm">
                        <thead>
                          <tr className="text-left text-gray-500">
                            <th className="pb-2">Time</th>
                            <th className="pb-2"><Heart className="w-4 h-4 inline" /> HR</th>
                            <th className="pb-2"><Activity className="w-4 h-4 inline" /> SpO2</th>
                            <th className="pb-2"><Thermometer className="w-4 h-4 inline" /> Temp</th>
                          </tr>
                        </thead>
                        <tbody>
                          {data.readings.map((r: any, i: number) => (
                            <tr key={i} className="border-t border-gray-200">
                              <td className="py-2">{new Date(r.timestamp).toLocaleString()}</td>
                              <td className={`py-2 ${(r.heart_rate > 100 || r.heart_rate < 60) ? 'text-red-600 font-bold' : ''}`}>{Math.round(r.heart_rate)} bpm</td>
                              <td className={`py-2 ${r.spo2 < 95 ? 'text-red-600 font-bold' : ''}`}>{Math.round(r.spo2)}%</td>
                              <td className={`py-2 ${r.skin_temperature > 37.5 ? 'text-red-600 font-bold' : ''}`}>{r.skin_temperature.toFixed(1)}°C</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  <div>
                    <h4 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-2 flex items-center">
                      <MessageCircle className="w-4 h-4 mr-2 text-gray-500" />
                      Medical Notes
                    </h4>
                    
                    <div className="space-y-3 mb-4 max-h-40 overflow-y-auto pr-2">
                      {data.notes.length === 0 ? (
                        <p className="text-sm text-gray-500 italic">No notes added yet.</p>
                      ) : (
                        data.notes.map((n: any) => (
                          <div key={n.id} className="bg-blue-50 p-3 rounded-lg border border-blue-100">
                            <div className="flex justify-between items-center mb-1">
                              <span className="text-xs font-semibold text-blue-900">{n.added_by}</span>
                              <span className="text-xs text-blue-500">{new Date(n.created_at).toLocaleString()}</span>
                            </div>
                            <p className="text-sm text-gray-800 whitespace-pre-wrap">{n.note}</p>
                          </div>
                        ))
                      )}
                    </div>

                    <div className="flex flex-col space-y-2">
                      <textarea
                        value={note}
                        onChange={(e) => setNote(e.target.value)}
                        placeholder="Add a medical note or triage observation..."
                        className="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                        rows={2}
                      />
                      <div className="flex justify-end">
                        <button 
                          onClick={handleAddNote}
                          disabled={isUpdating || !note.trim()}
                          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 text-sm font-medium"
                        >
                          Add Note
                        </button>
                      </div>
                    </div>
                  </div>

                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
