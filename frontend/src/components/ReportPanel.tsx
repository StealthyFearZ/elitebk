import { useState } from 'react';
import type { ReportState } from '../types/report';

interface ReportPanelProps {
  reportState: ReportState;
  onDownload: () => void;
}

export default function ReportPanel({ reportState, onDownload }: ReportPanelProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  // Add loading state display--> should show a waiting bubble thingy
  if (reportState.loading) {
    return (
      <div className="w-full rounded-xl bg-white border border-gray-200 shadow-sm px-4 py-3">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
          EliteBK Report
        </p>
        <div className="flex space-x-2 items-center">
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
          <span className="text-xs text-gray-400 ml-1">Generating report…</span>
        </div>
      </div>
    );
  }

  //error catching
  if (reportState.error) {
    return (
      <div className="w-full rounded-xl bg-white border border-red-200 shadow-sm px-4 py-3">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">
          EliteBK Report
        </p>
        <p className="text-xs text-red-500">{reportState.error}</p>
      </div>
    );
  }

  if (!reportState.preview) return null;

  const { overview, key_statistics } = reportState.preview;

  // We want to display a preview that they can then download 

  return (
    <div className="w-full rounded-xl bg-white border border-gray-200 shadow-sm px-4 py-3">
      {/* header*/}
      <div className="flex items-center justify-between">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
          EliteBK Report
        </p>
        <div className="flex items-center gap-2">
          {/* option to expand / collapse */ }
          <button
            onClick={() => setIsExpanded(prev => !prev)}
            className="text-gray-400 hover:text-gray-600 transition-colors text-xs"
            aria-label={isExpanded ? 'Collapse report' : 'Expand report'}
          >
            {isExpanded ? '▲ Collapse' : '▼ Expand'}
          </button>
          {/* option to download */ }
          <button
            onClick={onDownload}
            className="bg-gray-800 hover:bg-gray-700 text-white text-xs px-3 py-1 rounded transition-colors"
          >
            Download PDF
          </button>
        </div>
      </div>

      {/* collapsed body */}
      {isExpanded && (
        <div className="mt-3 space-y-4">
          {/* Overview */}
          <div>
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
              Overview
            </p>
            <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
              {overview}
            </p>
          </div>

          {/* stats */}
          {key_statistics.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                Key Statistics
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {key_statistics.map((stat, idx) => (
                  <div key={idx} className="bg-gray-50 rounded-lg px-3 py-2">
                    <p className="text-xs text-gray-500">{stat.label}</p>
                    <p className="text-base font-bold text-orange-500">{stat.value}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{stat.context}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* option to download text */}
          <p className="text-xs text-gray-400 italic">
            Download the full PDF for detailed analysis, context, comparisons, and conclusion.
          </p>
        </div>
      )}
    </div>
  );
}
