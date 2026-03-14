import { useState } from 'react';
import { uploadEvidence } from '../utils/api';

export default function EvidenceViewer({ refundId, existingAnalysis }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [analysis, setAnalysis] = useState(existingAnalysis || null);
  const [error, setError] = useState(null);

  const handleUpload = async () => {
    if (!file || !refundId) return;
    setUploading(true);
    setError(null);
    try {
      const res = await uploadEvidence(refundId, file);
      setAnalysis(res.data.analysis);
    } catch (err) {
      setError('Failed to upload evidence');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
      <h2 className="text-lg font-semibold text-white mb-4">📸 Evidence Upload & AI Analysis</h2>

      {/* Upload area */}
      <div className="mb-4">
        <label className="block text-sm text-gray-400 mb-2">Upload damage photo (include barcode/tag)</label>
        <div className="flex gap-3">
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setFile(e.target.files[0])}
            className="flex-1 text-sm text-gray-400 file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-blue-600 file:text-white file:cursor-pointer"
          />
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="px-4 py-2 rounded-lg bg-blue-600 text-white text-sm disabled:opacity-50"
          >
            {uploading ? 'Analyzing...' : 'Upload'}
          </button>
        </div>
        {error && <p className="text-red-400 text-xs mt-2">{error}</p>}
      </div>

      {/* Analysis results */}
      {analysis && (
        <div className="space-y-3">
          {/* EXIF */}
          <div className="p-3 rounded-lg bg-gray-800/50 border border-gray-700">
            <h3 className="text-sm font-medium text-gray-300 mb-2">📋 EXIF Metadata</h3>
            <div className="flex items-center gap-2">
              <span className={analysis.exif?.suspicious ? 'text-red-400' : 'text-green-400'}>
                {analysis.exif?.suspicious ? '🚩' : '✅'}
              </span>
              <span className="text-sm text-gray-400">{analysis.exif?.detail}</span>
            </div>
            {analysis.exif?.device && (
              <p className="text-xs text-gray-500 mt-1">Device: {analysis.exif.device}</p>
            )}
          </div>

          {/* Vision */}
          <div className="p-3 rounded-lg bg-gray-800/50 border border-gray-700">
            <h3 className="text-sm font-medium text-gray-300 mb-2">🔍 Vision Analysis</h3>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-gray-500">Damaged:</span>
                <span className={`ml-2 ${analysis.vision?.is_damaged ? 'text-yellow-400' : 'text-green-400'}`}>
                  {analysis.vision?.is_damaged ? 'Yes' : 'No'}
                </span>
              </div>
              <div>
                <span className="text-gray-500">Matches order:</span>
                <span className={`ml-2 ${analysis.vision?.matches_order ? 'text-green-400' : 'text-red-400'}`}>
                  {analysis.vision?.matches_order ? 'Yes' : 'No'}
                </span>
              </div>
              <div>
                <span className="text-gray-500">Stock photo:</span>
                <span className={`ml-2 ${analysis.vision?.is_stock_photo ? 'text-red-400' : 'text-green-400'}`}>
                  {analysis.vision?.is_stock_photo ? 'Yes ⚠️' : 'No'}
                </span>
              </div>
              <div>
                <span className="text-gray-500">Severity:</span>
                <span className="ml-2 text-gray-300">{analysis.vision?.severity || 'N/A'}</span>
              </div>
            </div>
            {analysis.vision?.simulated && (
              <p className="text-xs text-yellow-600 mt-2">⚠ Simulated — Bedrock Vision not connected</p>
            )}
          </div>

          {/* Recommendation */}
          <div className={`p-3 rounded-lg border ${
            analysis.overall?.recommendation?.includes('GENUINE') ? 'border-green-500/30 bg-green-500/10' :
            analysis.overall?.recommendation?.includes('SUSPICIOUS') || analysis.overall?.recommendation?.includes('STOCK') ? 'border-red-500/30 bg-red-500/10' :
            'border-yellow-500/30 bg-yellow-500/10'
          }`}>
            <h3 className="text-sm font-medium text-gray-300 mb-1">📋 Recommendation</h3>
            <p className="text-sm text-gray-300">{analysis.overall?.recommendation}</p>
          </div>
        </div>
      )}
    </div>
  );
}
