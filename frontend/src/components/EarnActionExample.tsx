/**
 * Example integration of ActionChecklist for an Earn action workflow.
 * This shows how to use the component with real API calls and state management.
 */

import { useState } from 'react'
import { Upload, CheckCircle2, Zap, DollarSign, AlertCircle } from 'lucide-react'
import { ActionChecklist, ActionStep } from './ActionChecklist'
import { Button } from './ui/Button'

interface EarnActionExampleProps {
  actionId: string
  onComplete?: (reward: number) => void
}

export function EarnActionExample({ actionId, onComplete }: EarnActionExampleProps) {
  const [steps, setSteps] = useState<ActionStep[]>([
    {
      id: 'upload',
      title: 'Upload Proof of Purchase',
      description: 'Upload your bank statement, invoice, or receipt',
      icon: <Upload size={20} />,
      status: 'active',
      details:
        'Accepted formats: PDF, JPG, PNG. Maximum file size: 10MB. Make sure the transaction amount and date are clearly visible.',
      estimatedMinutes: 2,
      action: {
        label: 'Upload Document',
        onClick: () => handleUpload(),
      },
    },
    {
      id: 'extract',
      title: 'Extract Transaction Details',
      description: 'Verify the extracted information from your document',
      icon: <DollarSign size={20} />,
      status: 'pending',
      details:
        'Our system automatically extracts key details. Please review and correct any errors before proceeding.',
      estimatedMinutes: 3,
    },
    {
      id: 'verify',
      title: 'Verify by Bank',
      description: 'Bank verification using secure connection',
      icon: <CheckCircle2 size={20} />,
      status: 'pending',
      details:
        'We securely connect to your bank to verify the transaction. This is encrypted and safe.',
      estimatedMinutes: 5,
    },
    {
      id: 'claim',
      title: 'Claim Your Reward',
      description: '150 Z-Coins will be credited to your wallet',
      icon: <Zap size={20} />,
      status: 'pending',
      details:
        'Once verified, your coins are immediately available. You can use them in the marketplace or games.',
      estimatedMinutes: 1,
    },
  ])

  const [isLoading, setIsLoading] = useState(false)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)

  const handleUpload = async () => {
    // In a real app, this would show a file picker
    setIsLoading(true)
    try {
      // Simulate file upload and extraction
      await new Promise((resolve) => setTimeout(resolve, 2000))

      // Move to extract step
      setSteps((prev) =>
        prev.map((step) => {
          if (step.id === 'upload') {
            return {
              ...step,
              status: 'completed',
              details: 'statement_2024.pdf uploaded successfully',
              elapsedMinutes: 1,
            }
          }
          if (step.id === 'extract') {
            return {
              ...step,
              status: 'active',
              elapsedMinutes: 0,
              action: {
                label: 'Verify Details',
                onClick: () => handleExtractVerify(),
              },
            }
          }
          return step
        })
      )
    } catch (error) {
      setSteps((prev) =>
        prev.map((step) =>
          step.id === 'upload' ? { ...step, status: 'error' } : step
        )
      )
    } finally {
      setIsLoading(false)
    }
  }

  const handleExtractVerify = async () => {
    setIsLoading(true)
    try {
      // Simulate verification
      await new Promise((resolve) => setTimeout(resolve, 1500))

      setSteps((prev) =>
        prev.map((step) => {
          if (step.id === 'extract') {
            return {
              ...step,
              status: 'completed',
              details: 'Amount: $500, Date: 2024-04-20, Status: Valid',
              elapsedMinutes: 2,
            }
          }
          if (step.id === 'verify') {
            return {
              ...step,
              status: 'active',
              elapsedMinutes: 0,
              action: {
                label: 'Verify with Bank',
                onClick: () => handleBankVerify(),
                loading: isLoading,
              },
            }
          }
          return step
        })
      )
    } catch (error) {
      setSteps((prev) =>
        prev.map((step) =>
          step.id === 'extract' ? { ...step, status: 'error' } : step
        )
      )
    } finally {
      setIsLoading(false)
    }
  }

  const handleBankVerify = async () => {
    setIsLoading(true)
    try {
      // Simulate bank verification
      await new Promise((resolve) => setTimeout(resolve, 3000))

      setSteps((prev) =>
        prev.map((step) => {
          if (step.id === 'verify') {
            return {
              ...step,
              status: 'completed',
              details:
                'Transaction verified via secure bank connection. Status: Approved',
              elapsedMinutes: 4,
            }
          }
          if (step.id === 'claim') {
            return {
              ...step,
              status: 'active',
              elapsedMinutes: 0,
              action: {
                label: 'Claim 150 Z-Coins',
                onClick: () => handleClaim(),
              },
            }
          }
          return step
        })
      )
    } catch (error) {
      setSteps((prev) =>
        prev.map((step) =>
          step.id === 'verify' ? { ...step, status: 'error' } : step
        )
      )
    } finally {
      setIsLoading(false)
    }
  }

  const handleClaim = async () => {
    setIsLoading(true)
    try {
      // Simulate coin claim
      await new Promise((resolve) => setTimeout(resolve, 1000))

      setSteps((prev) =>
        prev.map((step) =>
          step.id === 'claim'
            ? {
                ...step,
                status: 'completed',
                details: '150 Z-Coins credited to your wallet',
                elapsedMinutes: 1,
              }
            : step
        )
      )

      // Notify parent component
      onComplete?.(150)
    } catch (error) {
      setSteps((prev) =>
        prev.map((step) =>
          step.id === 'claim' ? { ...step, status: 'error' } : step
        )
      )
    } finally {
      setIsLoading(false)
    }
  }

  const handleRetry = (stepId: string) => {
    setSteps((prev) =>
      prev.map((step) =>
        step.id === stepId ? { ...step, status: 'active' } : step
      )
    )
  }

  const activeStep = steps.find((s) => s.status === 'active')
  const hasError = steps.some((s) => s.status === 'error')

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">Earn Z-Coins</h2>
        <p className="text-z-muted text-sm">
          Complete your bank transaction verification to earn 150 Z-Coins
        </p>
      </div>

      <div className="rounded-2xl border border-white/10 bg-z-surface p-6">
        <ActionChecklist
          steps={steps}
          onStepChange={(stepId) => {
            console.log('Step changed to:', stepId)
          }}
          showEstimatedTime={true}
        />
      </div>

      {hasError && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4">
          <div className="flex gap-3">
            <AlertCircle size={20} className="text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-red-500 mb-1">
                Error in verification process
              </p>
              <p className="text-sm text-red-400 mb-3">
                Please review the step details and try again. If the issue
                persists, contact our support team.
              </p>
              <Button
                onClick={() => {
                  const errorStep = steps.find((s) => s.status === 'error')
                  if (errorStep) handleRetry(errorStep.id)
                }}
                variant="primary"
                size="sm"
              >
                Retry Step
              </Button>
            </div>
          </div>
        </div>
      )}

      {steps.every((s) => s.status === 'completed') && (
        <div className="rounded-lg border border-z-success/30 bg-z-success/10 p-6 text-center">
          <div className="flex justify-center mb-4">
            <Zap size={32} className="text-z-success" />
          </div>
          <h3 className="text-xl font-bold text-z-success mb-2">
            Congratulations!
          </h3>
          <p className="text-z-muted mb-4">
            You have successfully earned 150 Z-Coins. Check your wallet to see
            your new balance.
          </p>
          <Button variant="success" size="md">
            View Wallet
          </Button>
        </div>
      )}
    </div>
  )
}
