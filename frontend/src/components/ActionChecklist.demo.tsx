import { useState } from 'react'
import { Upload, CheckCircle2, Zap, DollarSign, Clock } from 'lucide-react'
import { ActionChecklist, ActionStep } from './ActionChecklist'
import { Button } from './ui/Button'

export function ActionChecklistDemo() {
  const [steps, setSteps] = useState<ActionStep[]>([
    {
      id: 'upload',
      title: 'Upload Proof',
      description: 'Upload your bank statement or document',
      icon: <Upload size={20} />,
      status: 'completed',
      details: 'statement_2024.pdf uploaded successfully',
      estimatedMinutes: 2,
      elapsedMinutes: 1,
    },
    {
      id: 'verify',
      title: 'Verify Details',
      description: 'Confirm transaction amount and date',
      icon: <CheckCircle2 size={20} />,
      status: 'active',
      details:
        'Please review the extracted data and confirm it matches your document.',
      estimatedMinutes: 3,
      elapsedMinutes: 0,
      action: {
        label: 'Verify Now',
        onClick: () => handleVerify(),
      },
    },
    {
      id: 'review',
      title: 'Review Details',
      description: 'Our team will review the information',
      icon: <Clock size={20} />,
      status: 'pending',
      details:
        'This usually takes 24-48 hours. We will notify you once the review is complete.',
      estimatedMinutes: 1440,
    },
    {
      id: 'claim',
      title: 'Claim Reward',
      description: '150 Z-Coins will be credited',
      icon: <Zap size={20} />,
      status: 'pending',
      details:
        'Your Z-Coins will be available immediately in your wallet after verification.',
    },
  ])

  const handleVerify = () => {
    setSteps((prev) =>
      prev.map((step) => {
        if (step.id === 'verify') {
          return { ...step, status: 'completed', elapsedMinutes: 2 }
        }
        if (step.id === 'review') {
          return { ...step, status: 'active', elapsedMinutes: 0 }
        }
        return step
      })
    )
  }

  const handleReset = () => {
    setSteps([
      {
        id: 'upload',
        title: 'Upload Proof',
        description: 'Upload your bank statement or document',
        icon: <Upload size={20} />,
        status: 'pending',
        estimatedMinutes: 2,
      },
      {
        id: 'verify',
        title: 'Verify Details',
        description: 'Confirm transaction amount and date',
        icon: <CheckCircle2 size={20} />,
        status: 'active',
        estimatedMinutes: 3,
        action: {
          label: 'Upload Document',
          onClick: () => handleVerify(),
        },
      },
      {
        id: 'review',
        title: 'Review Details',
        description: 'Our team will review the information',
        icon: <Clock size={20} />,
        status: 'pending',
        estimatedMinutes: 1440,
      },
      {
        id: 'claim',
        title: 'Claim Reward',
        description: '150 Z-Coins will be credited',
        icon: <Zap size={20} />,
        status: 'pending',
      },
    ])
  }

  return (
    <div className="w-full max-w-2xl mx-auto p-6 bg-z-surface rounded-2xl">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">
            Action Checklist Demo
          </h2>
          <p className="text-z-muted">
            Example of the ActionChecklist component for the Earn workflow
          </p>
        </div>

        <ActionChecklist
          steps={steps}
          onStepChange={(stepId) => {
            console.log('Step changed:', stepId)
          }}
          showEstimatedTime={true}
        />

        <div className="flex gap-2 pt-4">
          <Button onClick={handleReset} variant="secondary" size="md">
            Reset
          </Button>
        </div>
      </div>
    </div>
  )
}
