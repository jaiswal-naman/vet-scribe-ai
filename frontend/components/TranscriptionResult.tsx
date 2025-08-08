import { useState } from 'react'

interface TranscriptionResultProps {
  result: any
}

export default function TranscriptionResult({ result }: TranscriptionResultProps) {
  const [activeTab, setActiveTab] = useState('transcript')

  const tabs = [
    { id: 'transcript', label: 'Original Transcript', icon: '📝' },
    { id: 'entities', label: 'Medical Entities', icon: '🏥' },
    { id: 'security', label: 'Compliance & Security', icon: '🔒' }
  ]

  return (
    <div className="space-y-6">
      {/* Header with metadata */}
      <div className="flex items-center justify-between p-4 bg-white/50 rounded-xl border border-gray-200/50">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-blue-500 rounded-xl flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Veterinary Clinical Note</h3>
            <p className="text-sm text-gray-500">Generated on {new Date().toLocaleDateString()}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-200">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
            Completed
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 transition-colors duration-200 ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-[200px]">
        {activeTab === 'transcript' && (
          <div className="space-y-4">
            <div className="bg-white/50 p-6 rounded-xl border border-gray-200/50">
              <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                <svg className="w-4 h-4 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                Original Audio Transcript
              </h4>
              <div className="bg-gray-50 p-4 rounded-lg border-l-4 border-blue-500">
                <p className="text-gray-800 text-lg leading-relaxed">
                  "{result.transcript || 'No transcript available'}"
                </p>
              </div>
              <div className="mt-4 flex items-center justify-between text-sm text-gray-500">
                <span>Confidence: {result.confidence ? `${(result.confidence * 100).toFixed(1)}%` : 'N/A'}</span>
                <span>Duration: {result.duration ? `${result.duration.toFixed(1)}s` : 'N/A'}</span>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'entities' && (
          <div className="space-y-4">
            <div className="bg-white/50 p-6 rounded-xl border border-gray-200/50">
              <h4 className="text-sm font-semibold text-gray-700 mb-4 flex items-center">
                <svg className="w-4 h-4 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
                Extracted Medical Entities
              </h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-3">
                  <h5 className="text-sm font-medium text-gray-700 flex items-center">
                    <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
                    Diagnoses
                  </h5>
                  <div className="space-y-2">
                    {result.diagnoses && result.diagnoses.length > 0 ? (
                      result.diagnoses.map((diagnosis: string, index: number) => (
                        <span key={index} className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-red-100 text-red-800 border border-red-200">
                          {diagnosis}
                        </span>
                      ))
                    ) : (
                      <p className="text-sm text-gray-500 italic">No diagnoses identified</p>
                    )}
                  </div>
                </div>

                <div className="space-y-3">
                  <h5 className="text-sm font-medium text-gray-700 flex items-center">
                    <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
                    Treatments
                  </h5>
                  <div className="space-y-2">
                    {result.treatments && result.treatments.length > 0 ? (
                      result.treatments.map((treatment: string, index: number) => (
                        <span key={index} className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800 border border-blue-200">
                          {treatment}
                        </span>
                      ))
                    ) : (
                      <p className="text-sm text-gray-500 italic">No treatments identified</p>
                    )}
                  </div>
                </div>
              </div>

              <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200/50">
                <p className="text-sm text-blue-700">
                  <strong>Note:</strong> Medical entity extraction uses BioBERT model for clinical terminology recognition.
                </p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'security' && (
          <div className="space-y-4">
            <div className="bg-white/50 p-6 rounded-xl border border-gray-200/50">
              <h4 className="text-sm font-semibold text-gray-700 mb-4 flex items-center">
                <svg className="w-4 h-4 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                Compliance & Security Information
              </h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <h5 className="text-sm font-semibold text-gray-700">Security Features</h5>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-sm text-gray-600">100% Offline Processing</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-sm text-gray-600">No Data Transmission</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-sm text-gray-600">Local AI Models</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-sm text-gray-600">End-to-End Encryption</span>
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  <h5 className="text-sm font-semibold text-gray-700">Compliance Standards</h5>
                  <div className="space-y-2">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800 border border-purple-200">
                      WCAG 2.2 Compliant
                    </span>
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 border border-blue-200">
                      HIPAA Ready
                    </span>
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-200">
                      Self-Hosted
                    </span>
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800 border border-orange-200">
                      Zero-Cost Stack
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200/50">
                <p className="text-sm text-green-700">
                  <strong>Security Status:</strong> All processing completed locally with no external data transmission. 
                  Your veterinary notes remain completely private and secure.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer with technical details */}
      <div className="bg-gray-50/50 p-4 rounded-xl border border-gray-200/50">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center space-x-4">
            <span>Task ID: {result.task_id || 'N/A'}</span>
            <span>Processing Time: {result.processing_time ? `${result.processing_time.toFixed(2)}s` : 'N/A'}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span>Vosk Model: v0.22</span>
            <span>BioBERT: Clinical</span>
          </div>
        </div>
      </div>
    </div>
  )
}