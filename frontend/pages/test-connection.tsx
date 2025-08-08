import { useState, useEffect } from 'react'

export default function TestConnection() {
  const [backendStatus, setBackendStatus] = useState<string>('checking')
  const [testResults, setTestResults] = useState<any>(null)

  useEffect(() => {
    const testConnection = async () => {
      try {
        console.log('Testing backend connection...')
        
        // Test 1: Health endpoint
        const healthResponse = await fetch('http://localhost:8000/health')
        const healthData = await healthResponse.json()
        console.log('Health check result:', healthData)
        
        if (healthResponse.ok) {
          setBackendStatus('connected')
          
          // Test 2: Test endpoint
          const testResponse = await fetch('http://localhost:8000/test')
          const testData = await testResponse.json()
          console.log('Test endpoint result:', testData)
          
          setTestResults({
            health: healthData,
            test: testData,
            timestamp: new Date().toISOString()
          })
        } else {
          setBackendStatus('error')
        }
      } catch (error) {
        console.error('Connection test failed:', error)
        setBackendStatus('error')
      }
    }

    testConnection()
  }, [])

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">🔍 Backend Connection Test</h1>
      
      <div className="space-y-6">
        {/* Connection Status */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Connection Status</h2>
          <div className="flex items-center space-x-3">
            {backendStatus === 'checking' && (
              <>
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                <span className="text-blue-600">Checking connection...</span>
              </>
            )}
            {backendStatus === 'connected' && (
              <>
                <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm">✓</span>
                </div>
                <span className="text-green-600 font-semibold">Backend Connected</span>
              </>
            )}
            {backendStatus === 'error' && (
              <>
                <div className="w-6 h-6 bg-red-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm">✗</span>
                </div>
                <span className="text-red-600 font-semibold">Connection Failed</span>
              </>
            )}
          </div>
        </div>

        {/* Test Results */}
        {testResults && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Test Results</h2>
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-green-600">Health Endpoint</h3>
                <pre className="bg-gray-100 p-3 rounded text-sm overflow-auto">
                  {JSON.stringify(testResults.health, null, 2)}
                </pre>
              </div>
              <div>
                <h3 className="font-semibold text-blue-600">Test Endpoint</h3>
                <pre className="bg-gray-100 p-3 rounded text-sm overflow-auto">
                  {JSON.stringify(testResults.test, null, 2)}
                </pre>
              </div>
              <div>
                <h3 className="font-semibold text-gray-600">Timestamp</h3>
                <p className="text-sm text-gray-600">{testResults.timestamp}</p>
              </div>
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="bg-blue-50 rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">What This Means</h2>
          <ul className="space-y-2 text-sm">
            <li>✅ <strong>Connected:</strong> Frontend can communicate with backend</li>
            <li>✅ <strong>Health Check:</strong> Backend services are running</li>
            <li>✅ <strong>Test Endpoint:</strong> Backend API is responding</li>
            <li>⚠️ <strong>If you see errors:</strong> Check that both servers are running</li>
          </ul>
        </div>

        {/* Navigation */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Next Steps</h2>
          <div className="space-y-2">
            <a 
              href="/" 
              className="block w-full bg-blue-600 text-white text-center py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors"
            >
              ← Back to Main App
            </a>
            <p className="text-sm text-gray-600 text-center">
              If connection is working, try recording audio on the main page
            </p>
          </div>
        </div>
      </div>
    </div>
  )
} 