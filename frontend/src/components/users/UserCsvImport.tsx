/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useRef } from 'react';
import { X, Upload, FileText, AlertCircle, CheckCircle2, Download, Loader2 } from 'lucide-react';
import { validateUsersCsv, importUsersCsv, downloadUsersCsvTemplate, CsvValidationPreview } from '@/lib/userApi';

interface UserCsvImportProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function UserCsvImport({ isOpen, onClose, onSuccess }: UserCsvImportProps) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [preview, setPreview] = useState<CsvValidationPreview | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const resetState = () => {
    setFile(null);
    setPreview(null);
    setError('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleClose = () => {
    resetState();
    onClose();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError('');
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    if (!selectedFile.name.endsWith('.csv')) {
      setError('Invalid file type. Please upload a .csv file.');
      return;
    }

    if (selectedFile.size > 5 * 1024 * 1024) {
      setError('CSV file is too large. Maximum allowed size is 5 MB.');
      return;
    }

    setFile(selectedFile);
    setPreview(null);
  };

  const handleValidate = async () => {
    if (!file) return;
    setLoading(true);
    setError('');
    try {
      const result = await validateUsersCsv(file);
      setPreview(result);
    } catch (err: any) {
      setError(err.message || 'Validation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async () => {
    if (!file) return;
    setLoading(true);
    setError('');
    try {
      const result = await importUsersCsv(file);
      alert(result.message);
      onSuccess();
      handleClose();
    } catch (err: any) {
      setError(err.message || 'Import failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh]">
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900">Import Users from CSV</h2>
          <button
            onClick={handleClose}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 overflow-y-auto">
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
              <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 mr-3 flex-shrink-0" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {!preview ? (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <p className="text-sm text-gray-600">Upload workers in bulk using a CSV file.</p>
                <button
                  onClick={downloadUsersCsvTemplate}
                  className="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-700"
                >
                  <Download className="w-4 h-4 mr-1" />
                  Download CSV Template
                </button>
              </div>

              <div 
                className={`border-2 border-dashed rounded-xl p-8 text-center ${
                  file ? 'border-blue-300 bg-blue-50' : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
                } transition-colors cursor-pointer`}
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  accept=".csv"
                  className="hidden"
                />
                
                {file ? (
                  <div className="flex flex-col items-center">
                    <FileText className="w-10 h-10 text-blue-500 mb-3" />
                    <p className="font-medium text-gray-900">{file.name}</p>
                    <p className="text-sm text-gray-500 mt-1">{(file.size / 1024).toFixed(2)} KB</p>
                    <p className="text-xs text-blue-600 mt-3 hover:underline">Click to change file</p>
                  </div>
                ) : (
                  <div className="flex flex-col items-center">
                    <Upload className="w-10 h-10 text-gray-400 mb-3" />
                    <p className="font-medium text-gray-900 mb-1">Click to select CSV File</p>
                    <p className="text-sm text-gray-500">Supported format: .csv | Max size: 5 MB</p>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="bg-gray-50 rounded-xl p-6 border border-gray-100">
                <h3 className="font-semibold text-gray-900 mb-4">CSV Validation Preview</h3>
                <div className="grid grid-cols-3 gap-4 text-center mb-6">
                  <div className="bg-white p-3 rounded-lg border border-gray-200 shadow-sm">
                    <p className="text-sm text-gray-500">Total Rows</p>
                    <p className="text-xl font-bold text-gray-900">{preview.total_rows}</p>
                  </div>
                  <div className="bg-white p-3 rounded-lg border border-gray-200 shadow-sm">
                    <p className="text-sm text-gray-500">Valid Rows</p>
                    <p className="text-xl font-bold text-green-600">{preview.valid_rows}</p>
                  </div>
                  <div className="bg-white p-3 rounded-lg border border-gray-200 shadow-sm">
                    <p className="text-sm text-gray-500">Invalid Rows</p>
                    <p className={`text-xl font-bold ${preview.invalid_rows > 0 ? 'text-red-600' : 'text-gray-900'}`}>
                      {preview.invalid_rows}
                    </p>
                  </div>
                </div>

                {preview.invalid_rows > 0 ? (
                  <div className="space-y-3">
                    <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm font-medium flex items-center">
                      <AlertCircle className="w-4 h-4 mr-2" />
                      {preview.invalid_rows} validation errors found. Please correct the CSV and upload it again.
                    </div>
                    <div className="max-h-48 overflow-y-auto space-y-2">
                      {preview.errors.map((err, i) => (
                        <div key={i} className="bg-white p-3 rounded border border-red-100 text-sm">
                          <p className="font-bold text-red-700 mb-1">Row {err.row}</p>
                          <ul className="list-disc pl-5 text-gray-700 space-y-1">
                            {err.errors.map((msg, j) => (
                              <li key={j}>{msg}</li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-center">
                    <CheckCircle2 className="w-5 h-5 text-green-600 mr-3" />
                    <p className="text-green-800 font-medium">All rows are valid! Ready to import.</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="px-6 py-4 border-t border-gray-100 bg-gray-50 flex justify-end gap-3">
          <button
            type="button"
            onClick={handleClose}
            disabled={loading}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          
          {!preview ? (
            <button
              type="button"
              onClick={handleValidate}
              disabled={!file || loading}
              className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center"
            >
              {loading && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
              Validate CSV
            </button>
          ) : (
            <button
              type="button"
              onClick={preview.valid ? handleImport : resetState}
              disabled={loading}
              className={`px-4 py-2 text-white rounded-lg transition-colors flex items-center ${
                preview.valid 
                  ? 'bg-green-600 hover:bg-green-700' 
                  : 'bg-blue-600 hover:bg-blue-700'
              } disabled:opacity-50`}
            >
              {loading && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
              {preview.valid ? 'Import Valid Rows' : 'Upload New CSV'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
