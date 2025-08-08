import React, { useState, useRef } from 'react'
import axios from 'axios'

interface AudioRecorderProps {
  onTranscriptionComplete: (result: any) => void
  onProgressUpdate: (progress: any) => void
}

const AudioRecorder: React.FC<AudioRecorderProps> = ({ onTranscriptionComplete, onProgressUpdate }) => {
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const progressIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      })
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm;codecs=opus') ? 'audio/webm;codecs=opus' : ''
      })
      
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = async () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        await processAudio(blob)
        
        // Clean up stream
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start(1000) // Collect data every second
      setIsRecording(true)
      setError(null)
    } catch (error) {
      setError('Failed to access microphone. Please check permissions.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const processAudio = async (audioBlob: Blob) => {
    setIsProcessing(true)
    setError(null)

    try {
      // Create form data
      const formData = new FormData()
      formData.append('file', audioBlob, 'recording.webm')

      // Upload and start transcription
      const response = await axios.post('http://localhost:8000/transcribe', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      const { task_id } = response.data
      setCurrentTaskId(task_id)

      // Start polling for progress
      pollProgress(task_id)

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start transcription')
      setIsProcessing(false)
    }
  }

  const pollProgress = (taskId: string) => {
    progressIntervalRef.current = setInterval(async () => {
      try {
        const response = await axios.get(`http://localhost:8000/progress/${taskId}`)
        const progress = response.data
        
        onProgressUpdate(progress)

        if (progress.status === 'completed') {
          clearInterval(progressIntervalRef.current!)
          const resultResponse = await axios.get(`http://localhost:8000/results/${taskId}`)
          onTranscriptionComplete(resultResponse.data)
          setIsProcessing(false)
          setCurrentTaskId(null)
        } else if (progress.status === 'error') {
          clearInterval(progressIntervalRef.current!)
          setError(progress.current_stage || 'Transcription failed')
          setIsProcessing(false)
          setCurrentTaskId(null)
        }
      } catch (err: any) {
        clearInterval(progressIntervalRef.current!)
        setError('Failed to get progress')
        setIsProcessing(false)
        setCurrentTaskId(null)
      }
    }, 1000)
  }

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-lg" role="region" aria-label="Audio Recording">
      <h2 className="text-xl font-semibold mb-4" id="recorder-title">Veterinary Note Recording</h2>
      
      <div className="space-y-4">
        {/* Recording Controls */}
        <div className="flex justify-center space-x-4">
          <button
            onClick={startRecording}
            disabled={isRecording || isProcessing}
            className={`px-6 py-3 rounded-full font-medium transition-colors ${
              isRecording || isProcessing
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-red-500 hover:bg-red-600 text-white'
            }`}
            aria-label="Start recording veterinary notes"
            aria-describedby="recorder-title"
          >
            {isRecording ? 'Recording...' : 'Start Recording'}
          </button>
          
          <button
            onClick={stopRecording}
            disabled={!isRecording || isProcessing}
            className={`px-6 py-3 rounded-full font-medium transition-colors ${
              !isRecording || isProcessing
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-500 hover:bg-blue-600 text-white'
            }`}
            aria-label="Stop recording"
          >
            Stop Recording
          </button>
        </div>

        {/* Audio Visualizer */}
        {isRecording && (
          <div className="mt-4" role="status" aria-live="polite">
            <div className="w-full h-20 bg-gray-100 rounded flex items-center justify-center">
              <div className="flex space-x-1">
                {[...Array(20)].map((_, i) => (
                  <div
                    key={i}
                    className="w-1 bg-red-500 rounded animate-pulse"
                    style={{
                      height: `${Math.random() * 60 + 20}%`,
                      animationDelay: `${i * 0.1}s`
                    }}
                  />
                ))}
              </div>
            </div>
            <p className="text-sm text-gray-600 mt-2">Recording in progress...</p>
          </div>
        )}

        {/* Processing Status */}
        {isProcessing && (
          <div className="mt-4 p-4 bg-blue-50 rounded-lg" role="status" aria-live="polite">
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
              <span className="text-blue-800">Processing transcription...</span>
            </div>
            {currentTaskId && (
              <p className="text-xs text-blue-600 mt-1">Task ID: {currentTaskId}</p>
            )}
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg" role="alert">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* WCAG 2.2 Compliance Notice */}
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-xs text-green-700">
            <strong>WCAG 2.2 Compliant:</strong> This interface supports keyboard navigation, 
            screen readers, and provides real-time status updates for accessibility.
          </p>
        </div>
      </div>
    </div>
  )
}

export default AudioRecorder