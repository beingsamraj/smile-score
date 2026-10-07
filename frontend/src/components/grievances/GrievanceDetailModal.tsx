import { useState, useEffect } from 'react';
import { X, Clock, AlertTriangle, User, MessageCircle } from 'lucide-react';
import { getGrievanceDetails, updateGrievanceStatus, addGrievanceNote, GrievanceDetail } from '@/lib/grievanceApi';

interface ModalProps {
  grievanceId: string;
  onClose: () => void;
  onUpdated: () => void;
}

export default function GrievanceDetailModal({ grievanceId, onClose, onUpdated }: ModalProps) {
  const [data, setData] = useState<GrievanceDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [note, setNote] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);

  const fetchDetails = async () => {
    setLoading(true);
    try {
      const res = await getGrievanceDetails(grievanceId);
      setData(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetails(); // eslint-disable-line
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [grievanceId]);

  const handleStatusChange = async (newStatus: string) => {
    setIsUpdating(true);
    try {
      await updateGrievanceStatus(grievanceId, newStatus, 'Admin User');
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
      await addGrievanceNote(grievanceId, note, 'Admin User');
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

        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl w-full">
          {loading || !data ? (
            <div className="p-8 text-center text-gray-500">Loading details...</div>
          ) : (
            <div className="bg-white">
              {/* Header */}
              <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  Wellbeing Concern Details
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
                      <User className="w-4 h-4 mr-2" /> Employee
                    </h4>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <p className="font-bold text-gray-900">{data.grievance.employee_name}</p>
                      <p className="text-sm text-gray-500">{data.grievance.employee_id}</p>
                      <p className="text-sm text-gray-500 mt-2">{data.grievance.department} | {data.grievance.workstation}</p>
                    </div>
                  </div>

                  <div>
                    <h4 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-2 flex items-center">
                      <AlertTriangle className="w-4 h-4 mr-2" /> Current Status
                    </h4>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full mb-3 ${
                        data.grievance.status === 'NEW' ? 'bg-red-100 text-red-800' : 
                        data.grievance.status === 'UNDER REVIEW' ? 'bg-yellow-100 text-yellow-800' : 
                        'bg-green-100 text-green-800'
                      }`}>
                        {data.grievance.status}
                      </span>
                      <div className="space-y-2 mt-2">
                        {data.grievance.status !== 'UNDER REVIEW' && (
                          <button 
                            disabled={isUpdating}
                            onClick={() => handleStatusChange('UNDER REVIEW')}
                            className="w-full text-center text-sm bg-yellow-100 text-yellow-800 hover:bg-yellow-200 py-2 rounded-md font-medium transition-colors"
                          >
                            Mark Under Review
                          </button>
                        )}
                        {data.grievance.status !== 'RESOLVED' && (
                          <button 
                            disabled={isUpdating}
                            onClick={() => handleStatusChange('RESOLVED')}
                            className="w-full text-center text-sm bg-green-100 text-green-800 hover:bg-green-200 py-2 rounded-md font-medium transition-colors"
                          >
                            Resolve Concern
                          </button>
                        )}
                        {data.grievance.status === 'RESOLVED' && (
                          <button 
                            disabled={isUpdating}
                            onClick={() => handleStatusChange('UNDER REVIEW')}
                            className="w-full text-center text-sm bg-gray-100 text-gray-800 hover:bg-gray-200 py-2 rounded-md font-medium transition-colors"
                          >
                            Reopen
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Right Column: Timeline & Notes */}
                <div className="md:col-span-2 space-y-6">
                  
                  {/* Trigger Reason */}
                  <div className="bg-red-50 p-4 rounded-lg border border-red-100">
                    <h4 className="text-sm font-semibold text-red-800 mb-1">Trigger Reason</h4>
                    <p className="text-sm text-red-700">{data.grievance.trigger_reason}</p>
                    <p className="text-xs text-red-600 mt-1">Detected on: {new Date(data.grievance.detected_at).toLocaleString()}</p>
                  </div>

                  {/* Recent Feedback Timeline */}
                  <div>
                    <h4 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-2 flex items-center">
                      <Clock className="w-4 h-4 mr-2" /> Recent Feedback Pattern
                    </h4>
                    <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 flex overflow-x-auto space-x-2">
                      {data.recent_feedbacks.map((fb, idx) => (
                        <div key={idx} className="flex-shrink-0 flex flex-col items-center">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                            fb.feedback === 'HAPPY' ? 'bg-green-100 text-green-800' :
                            fb.feedback === 'OK' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {fb.feedback.substring(0, 1)}
                          </div>
                          <div className="text-[10px] text-gray-500 mt-1">
                            {new Date(fb.timestamp).toLocaleDateString(undefined, {month: 'short', day: 'numeric'})}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Notes Section */}
                  <div>
                    <h4 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-2 flex items-center">
                      <MessageCircle className="w-4 h-4 mr-2" /> Management Notes
                    </h4>
                    <div className="space-y-3 mb-4 max-h-40 overflow-y-auto pr-2">
                      {data.notes.length === 0 ? (
                        <p className="text-sm text-gray-500 italic">No notes added yet.</p>
                      ) : (
                        data.notes.map((n) => (
                          <div key={n.id} className="bg-gray-50 p-3 rounded-lg text-sm border border-gray-100">
                            <p className="text-gray-800">{n.note}</p>
                            <p className="text-xs text-gray-400 mt-1">- {n.added_by} on {new Date(n.created_at).toLocaleString()}</p>
                          </div>
                        ))
                      )}
                    </div>
                    <div className="flex space-x-2">
                      <input 
                        type="text" 
                        value={note}
                        onChange={e => setNote(e.target.value)}
                        placeholder="Add a note about this wellbeing concern..."
                        className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
                      />
                      <button 
                        onClick={handleAddNote}
                        disabled={isUpdating || !note.trim()}
                        className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50 text-sm font-medium"
                      >
                        Add
                      </button>
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
