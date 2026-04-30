import { useState } from 'react'
import { Check, FileUp, AlertCircle, Loader, Zap } from 'lucide-react'
import {
  runVerification,
  uploadProofFile,
  submitVerificationRequest,
  type VerificationResult,
  type VerificationStep,
} from '../../api/earn-verification'
import { DEMO_USER_ID } from '../../types/api'

/**
 * Complete example component demonstrating the Earn Verification System.
 * Shows a working implementation of the three-step verification workflow.
 *
 * Features:
 * - File selection with type/size hints
 * - Step-by-step progress tracking
 * - Detailed error messages
 * - Successful reward claiming
 * - Loading states
 */
export function EarnVerificationDemo() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [moduleId, setModuleId] = useState<string>('savings')
  const [verifying, setVerifying] = useState(false)
  const [verification, setVerification] = useState<VerificationResult | null>(null)
  const [uploading, setUploading] = useState(false)
  const [uploadId, setUploadId] = useState<string | null>(null)
  const [claiming, setClaiming] = useState(false)
  const [claimed, setClaimed] = useState(false)
  const [claimError, setClaimError] = useState<string | null>(null)

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setVerification(null)
      setUploadId(null)
      setClaimed(false)
      setClaimError(null)
    }
  }

  const handleVerify = async () => {
    if (!selectedFile) return

    setVerifying(true)
    try {
      const result = await runVerification(selectedFile, DEMO_USER_ID)
      setVerification(result)
    } catch (error) {
      setVerification({
        verified: false,
        steps: [],
        totalTime: 0,
        eligibleReward: 0,
        message: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
      })
    } finally {
      setVerifying(false)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile || !verification?.verified) return

    setUploading(true)
    try {
      const result = await uploadProofFile(selectedFile, DEMO_USER_ID, moduleId)
      setUploadId(result.upload_id)
    } catch (error) {
      setClaimError(`Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setUploading(false)
    }
  }

  const handleClaim = async () => {
    if (!uploadId) return

    setClaiming(true)
    setClaimError(null)
    try {
      const result = await submitVerificationRequest(DEMO_USER_ID, moduleId, uploadId)
      if (result.eligible) {
        setClaimed(true)
      } else {
        setClaimError(`Not eligible: ${result.message}`)
      }
    } catch (error) {
      setClaimError(`Claim failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setClaiming(false)
    }
  }

  const moduleOptions = [
    { id: 'savings', label: 'Savings Milestone', reward: 350 },
    { id: 'credit-score', label: 'Credit Score', reward: 400 },
    { id: 'direct-deposit', label: 'Direct Deposit', reward: 200 },
    { id: 'education', label: 'Education Module', reward: 150 },
  ]

  const acceptedFormats = '.pdf, .png, .jpg, .jpeg'
  const maxSize = '10 MB'
  const minSize = '1 KB'

  return (
    <div className="w-full max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Zap className="text-yellow-500" />
            Earn Verification Demo
          </h1>
          <p className="text-gray-600 mt-2">
            Upload proof of financial activity to earn Z-Coins
          </p>
        </div>

        {/* Module Selection */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Select Earn Module
          </label>
          <select
            value={moduleId}
            onChange={(e) => setModuleId(e.target.value)}
            disabled={verifying || uploading || claiming || claimed}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {moduleOptions.map((opt) => (
              <option key={opt.id} value={opt.id}>
                {opt.label} - {opt.reward} coins
              </option>
            ))}
          </select>
        </div>

        {/* File Upload Section */}
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition">
          <div className="flex flex-col items-center gap-3">
            <FileUp className="w-12 h-12 text-gray-400" />
            <div>
              <label htmlFor="file-input" className="text-blue-600 hover:underline cursor-pointer font-semibold">
                Choose proof file
              </label>
              <input
                id="file-input"
                type="file"
                accept={acceptedFormats}
                onChange={handleFileSelect}
                disabled={verifying || uploading || claiming}
                className="hidden"
              />
              <p className="text-sm text-gray-600 mt-1">
                or drag and drop here
              </p>
            </div>
          </div>

          <div className="mt-4 pt-4 border-t text-xs text-gray-500 space-y-1">
            <p>
              <strong>Accepted formats:</strong> {acceptedFormats}
            </p>
            <p>
              <strong>File size:</strong> {minSize} - {maxSize}
            </p>
          </div>

          {selectedFile && (
            <div className="mt-4 pt-4 border-t">
              <p className="text-sm font-semibold text-gray-700">
                Selected: {selectedFile.name}
              </p>
              <p className="text-xs text-gray-600">
                ({(selectedFile.size / 1024).toFixed(1)} KB)
              </p>
            </div>
          )}
        </div>

        {/* Verification Steps */}
        {verification && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">Verification Steps</h2>

            {verification.steps.map((step) => (
              <VerificationStepDisplay key={step.id} step={step} />
            ))}

            {/* Verification Summary */}
            <div className={`p-4 rounded-lg ${
              verification.verified
                ? 'bg-green-50 border border-green-200'
                : 'bg-red-50 border border-red-200'
            }`}>
              <p className={`font-semibold ${
                verification.verified ? 'text-green-900' : 'text-red-900'
              }`}>
                {verification.verified ? '✓ Verification Passed' : '✗ Verification Failed'}
              </p>
              <p className="text-sm mt-1 text-gray-700">
                {verification.message}
              </p>
              <p className="text-xs text-gray-600 mt-2">
                Time: {verification.totalTime}ms | Reward: {verification.eligibleReward} coins
              </p>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3">
          {!verification && (
            <button
              onClick={handleVerify}
              disabled={!selectedFile || verifying}
              className={`flex-1 py-3 px-4 rounded-lg font-semibold flex items-center justify-center gap-2 transition ${
                selectedFile && !verifying
                  ? 'bg-blue-600 hover:bg-blue-700 text-white'
                  : 'bg-gray-200 text-gray-500 cursor-not-allowed'
              }`}
            >
              {verifying && <Loader className="animate-spin w-5 h-5" />}
              {verifying ? 'Verifying...' : 'Verify File'}
            </button>
          )}

          {verification?.verified && !uploadId && (
            <button
              onClick={handleUpload}
              disabled={uploading}
              className={`flex-1 py-3 px-4 rounded-lg font-semibold flex items-center justify-center gap-2 transition ${
                !uploading
                  ? 'bg-green-600 hover:bg-green-700 text-white'
                  : 'bg-gray-200 text-gray-500 cursor-not-allowed'
              }`}
            >
              {uploading && <Loader className="animate-spin w-5 h-5" />}
              {uploading ? 'Uploading...' : 'Upload Proof'}
            </button>
          )}

          {uploadId && !claimed && (
            <button
              onClick={handleClaim}
              disabled={claiming}
              className={`flex-1 py-3 px-4 rounded-lg font-semibold flex items-center justify-center gap-2 transition ${
                !claiming
                  ? 'bg-yellow-600 hover:bg-yellow-700 text-white'
                  : 'bg-gray-200 text-gray-500 cursor-not-allowed'
              }`}
            >
              {claiming && <Loader className="animate-spin w-5 h-5" />}
              {claiming ? 'Claiming...' : 'Claim Reward'}
            </button>
          )}

          {claimed && (
            <button
              onClick={() => {
                setSelectedFile(null)
                setVerification(null)
                setUploadId(null)
                setClaimed(false)
                setClaimError(null)
              }}
              className="flex-1 py-3 px-4 rounded-lg font-semibold bg-gray-200 text-gray-700 hover:bg-gray-300 transition"
            >
              Start Over
            </button>
          )}
        </div>

        {/* Success Message */}
        {claimed && (
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-start gap-3">
              <Check className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-green-900">
                  Reward Claimed Successfully!
                </p>
                <p className="text-sm text-green-800 mt-1">
                  You've earned coins for your verified financial activity.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Error Message */}
        {claimError && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-red-900">Error</p>
                <p className="text-sm text-red-800 mt-1">{claimError}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

/**
 * Component to display a single verification step with its status.
 */
function VerificationStepDisplay({ step }: { step: VerificationStep }) {
  const statusConfig = {
    passed: { icon: Check, color: 'text-green-600', bg: 'bg-green-50' },
    failed: { icon: AlertCircle, color: 'text-red-600', bg: 'bg-red-50' },
    running: { icon: Loader, color: 'text-blue-600', bg: 'bg-blue-50' },
    pending: { icon: FileUp, color: 'text-gray-600', bg: 'bg-gray-50' },
  }

  const config = statusConfig[step.status]
  const Icon = config.icon

  return (
    <div className={`p-4 rounded-lg border ${config.bg}`}>
      <div className="flex items-start gap-3">
        <Icon
          className={`w-5 h-5 ${config.color} ${
            step.status === 'running' ? 'animate-spin' : ''
          } flex-shrink-0 mt-0.5`}
        />
        <div className="flex-1">
          <p className="font-semibold text-gray-900">{step.name}</p>
          <p className="text-sm text-gray-600 mt-1">
            {step.status === 'passed' && 'Verification passed ✓'}
            {step.status === 'failed' && 'Verification failed'}
            {step.status === 'running' && 'Verifying...'}
            {step.status === 'pending' && 'Waiting to run'}
          </p>
          {step.result && (
            <p className="text-sm text-green-700 mt-1">{step.result}</p>
          )}
          {step.error && (
            <p className="text-sm text-red-700 mt-1">{step.error}</p>
          )}
        </div>
      </div>
    </div>
  )
}
