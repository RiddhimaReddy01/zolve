import { useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ArrowLeft,
  BadgeCheck,
  CheckCircle2,
  ChevronRight,
  AlertCircle,
  FileUp,
  ShieldCheck,
  Sparkles,
  Upload,
  Zap,
  X,
  Clock,
  Flame,
} from 'lucide-react'
import { useUserStore } from '../store/useUserStore'
import { useUIStore } from '../store/useUIStore'
import { earnActions, earnModuleContent, spendActions } from '../data/zolveContent'
import { zWorldAPI } from '../api/z-world'
import { DEMO_USER_ID } from '../types/api'

type ModuleContent = {
  title: string
  subtitle: string
  steps: string[]
  reward: number
  proof: string
  timeline: string
  verification: string[]
}

type VerificationStep = {
  id: string
  label: string
  status: 'pending' | 'running' | 'passed' | 'failed'
  message: string
  duration: number
}

const spendCopy: Record<string, ModuleContent> = {
  auctions: {
    title: 'Auctions',
    subtitle: 'Bid Z-Coins on premium deals and stay in the loop when someone outbids you.',
    steps: ['Pick a premium deal', 'Place a Z-Coin bid', 'Watch bid status until the timer closes'],
    reward: 0,
    proof: 'No upload needed',
    timeline: 'Live during the auction window',
    verification: ['Balance checked', 'Bid recorded', 'Outbid alert enabled'],
  },
  'flash-deals': {
    title: 'Flash Deals',
    subtitle: 'Quantity-limited drops with Gold, Silver, then Basic access windows.',
    steps: ['Join launch queue', 'Confirm tier access', 'Redeem before inventory runs out'],
    reward: 0,
    proof: 'No upload needed',
    timeline: 'During launch window',
    verification: ['Tier checked', 'Inventory reserved', 'Coins deducted only on redemption'],
  },
}

const DEFAULT_VERIFICATION_STEPS: VerificationStep[] = [
  { id: 'validate-file', label: 'Validating file type', status: 'pending', message: '', duration: 1000 },
  { id: 'check-account', label: 'Checking account eligibility', status: 'pending', message: '', duration: 1200 },
  { id: 'check-duplicates', label: 'Checking for duplicates', status: 'pending', message: '', duration: 1000 },
  { id: 'process-reward', label: 'Processing reward', status: 'pending', message: '', duration: 1500 },
]

export default function EarnActionChecklistPage() {
  const navigate = useNavigate()
  const { actionId, spendId } = useParams()
  const addToast = useUIStore((s) => s.addToast)
  const addCoinAnimation = useUIStore((s) => s.addCoinAnimation)
  const addCoins = useUserStore((s) => s.addCoins)
  const setDashboard = useUserStore((s) => s.setDashboard)
  const key = actionId || spendId || 'savings'

  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [filePreview, setFilePreview] = useState<string | null>(null)
  const [uploadedProof, setUploadedProof] = useState<{
    upload_id: string
    file_name: string
    mime_type: string
    size_bytes: number
  } | null>(null)
  const [selectedGoal, setSelectedGoal] = useState('')
  const [uploadProgress, setUploadProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState(0)
  const [expandedStep, setExpandedStep] = useState<number | null>(null)
  const [verifying, setVerifying] = useState(false)
  const [verificationSteps, setVerificationSteps] = useState<VerificationStep[]>(
    DEFAULT_VERIFICATION_STEPS
  )
  const [verified, setVerified] = useState(false)
  const [verificationError, setVerificationError] = useState<string | null>(null)
  const [showSuccessAnimation, setShowSuccessAnimation] = useState(false)

  const action = useMemo(
    () =>
      earnActions.find((item) => item.route.endsWith(key)) ||
      spendActions.find((item) => item.route.endsWith(key)),
    [key]
  )

  const content: ModuleContent = earnModuleContent[key] || spendCopy[key] || {
    title: action?.title || 'Reward action',
    subtitle: action?.detail || 'Complete this module to move your Zolve loop forward.',
    reward: 150,
    steps: ['Review module requirements', 'Upload or confirm proof', 'Verify and claim reward'],
    proof: 'Module proof',
    timeline: 'Instant demo verification',
    verification: ['Proof received', 'Rule checked', 'Reward eligible'],
  }

  const Icon = action?.icon || Sparkles
  const heroMedia =
    action && 'media' in action && typeof action.media === 'string'
      ? action.media
      : 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1200&h=700&fit=crop'
  const uploadLabel = String(
    action && 'uploadLabel' in action ? (action as any).uploadLabel : content.proof
  )
  const requiresUpload = !/No document|Automatic/i.test(uploadLabel || '')
  const canVerify = verified || !requiresUpload || selectedFile || selectedGoal

  const handleFileSelected = (file: File | null) => {
    if (!file) {
      setSelectedFile(null)
      setFilePreview(null)
      return
    }

    setSelectedFile(file)
    setUploadedProof(null)

    if (file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setFilePreview(e.target?.result as string)
      }
      reader.readAsDataURL(file)
    } else {
      setFilePreview(null)
    }
  }

  const readFileAsBase64 = (file: File) =>
    new Promise<string>((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => {
        const result = String(reader.result || '')
        resolve(result.includes(',') ? result.split(',')[1] : result)
      }
      reader.onerror = () => reject(reader.error)
      reader.readAsDataURL(file)
    })

  const runVerificationSteps = async () => {
    const steps = [...DEFAULT_VERIFICATION_STEPS]
    setVerificationSteps(steps)

    for (let i = 0; i < steps.length; i++) {
      setVerificationSteps((prev) =>
        prev.map((step, idx) =>
          idx === i ? { ...step, status: 'running' as const } : step
        )
      )

      await new Promise((resolve) => setTimeout(resolve, steps[i].duration))

      const isLastStep = i === steps.length - 1
      setVerificationSteps((prev) =>
        prev.map((step, idx) =>
          idx === i ? { ...step, status: 'passed' as const } : step
        )
      )
    }

    setShowSuccessAnimation(true)
    await new Promise((resolve) => setTimeout(resolve, 800))
  }

  const handleVerify = async () => {
    if (!canVerify) {
      addToast('Upload proof or complete the required confirmation first', 'info')
      return
    }

    setVerifying(true)
    setVerificationError(null)

    try {
      let proof = uploadedProof

      if (requiresUpload && selectedFile && !proof) {
        const contentBase64 = await readFileAsBase64(selectedFile)
        const upload = await zWorldAPI.uploadEarnProof({
          user_id: DEMO_USER_ID,
          module_id: key,
          file_name: selectedFile.name,
          mime_type: selectedFile.type || 'application/octet-stream',
          size_bytes: selectedFile.size,
          content_base64: contentBase64,
        })
        proof = upload
        setUploadedProof(upload)
      }

      await runVerificationSteps()

      const response = await zWorldAPI.verifyEarnModule({
        user_id: DEMO_USER_ID,
        module_id: key,
        proof_type: selectedFile ? 'upload' : 'self_confirmed',
        proof_name: proof?.file_name || selectedFile?.name || null,
        upload_id: proof?.upload_id || null,
        mime_type: proof?.mime_type || selectedFile?.type || null,
        size_bytes: proof?.size_bytes || selectedFile?.size || null,
        selected_goal: selectedGoal || null,
        metadata: {
          module_title: content.title,
          proof_required: requiresUpload,
        },
      })

      if (!response.success || !response.eligible) {
        setVerificationError(response.message || 'Verification did not pass')
        setVerificationSteps((prev) =>
          prev.map((step) =>
            step.status === 'running'
              ? { ...step, status: 'failed' }
              : step
          )
        )
        addToast(response.message || 'Verification did not pass', 'error')
        return
      }

      setVerified(true)
      if (response.dashboard) setDashboard(response.dashboard)
      if (!response.dashboard && response.coins_awarded > 0) addCoins(response.coins_awarded)
      addToast(`Verified: +${response.coins_awarded} Z-Coins`, 'success')
    } catch (error: any) {
      const errorMessage =
        error?.response?.data?.detail || 'Verification failed'
      setVerificationError(errorMessage)
      setVerificationSteps((prev) =>
        prev.map((step) =>
          step.status === 'running' ? { ...step, status: 'failed' } : step
        )
      )
      addToast(errorMessage, 'error')
    } finally {
      setVerifying(false)
    }
  }

  const handleClaimReward = () => {
    navigate('/dashboard')
  }

  const progressPercentage = Math.min(
    ((currentStep + 1) / content.steps.length) * 100,
    100
  )

  return (
    <div className="min-h-screen bg-[#F6F7FB] pb-24 text-z-surface">
      <div className="max-w-7xl mx-auto">
        <div className="relative min-h-[360px] overflow-hidden bg-z-surface text-white">
          <img
            src={heroMedia}
            alt=""
            className="absolute inset-0 h-full w-full object-cover opacity-45"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-black/15 via-black/45 to-black/90" />

          <div className="relative p-5 sm:p-8">
            <button
              onClick={() => navigate('/dashboard')}
              className="mb-16 rounded-full bg-white/15 p-3 backdrop-blur hover:bg-white/25 transition-colors"
            >
              <ArrowLeft size={22} />
            </button>

            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
              <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-white/15 px-3 py-1 text-sm font-semibold">
                <Icon size={16} /> Earn module
              </div>
              <h1 className="max-w-2xl text-4xl font-black">{content.title}</h1>
              <p className="mt-3 max-w-xl text-sm text-white/75">{content.subtitle}</p>
            </motion.div>
          </div>
        </div>

        <div className="grid gap-6 p-5 lg:grid-cols-[1.2fr_1fr] lg:p-8">
          <section className="space-y-6">
            <div className="rounded-2xl border border-z-border bg-white p-6 shadow-sm">
              <div className="mb-6 flex items-center justify-between">
                <h2 className="text-lg font-black">Action checklist</h2>
                <span className="rounded-full bg-z-accent/10 px-3 py-1 text-sm font-black text-z-accent">
                  {content.reward > 0 ? `+${content.reward} Z-Coins` : 'Spend module'}
                </span>
              </div>

              <div className="mb-6 h-2 overflow-hidden rounded-full bg-gray-100">
                <motion.div
                  className="h-full bg-z-accent"
                  initial={{ width: 0 }}
                  animate={{ width: `${progressPercentage}%` }}
                  transition={{ duration: 0.6, ease: 'easeOut' }}
                />
              </div>

              <div className="space-y-3">
                {content.steps.map((step, index) => (
                  <motion.button
                    key={step}
                    onClick={() =>
                      setExpandedStep(expandedStep === index ? null : index)
                    }
                    className={`w-full rounded-xl border p-4 text-left transition-all ${
                      index < currentStep
                        ? 'border-z-success bg-z-success/5'
                        : index === currentStep
                          ? 'border-z-accent bg-z-accent/5 ring-2 ring-z-accent/20'
                          : 'border-z-border bg-[#FAFBFC]'
                    }`}
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    whileHover={{ y: -2 }}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`flex h-10 w-10 items-center justify-center rounded-full text-sm font-black ${
                          index < currentStep
                            ? 'bg-z-success text-white'
                            : 'bg-z-accent text-white'
                        }`}
                      >
                        {index < currentStep ? (
                          <CheckCircle2 size={20} />
                        ) : (
                          index + 1
                        )}
                      </div>
                      <div className="flex-1">
                        <span className="font-semibold">{step}</span>
                        {index === currentStep && (
                          <div className="mt-1 inline-block rounded-full bg-z-accent px-2 py-0.5 text-xs font-bold text-white">
                            Current step
                          </div>
                        )}
                      </div>
                      {expandedStep === index && (
                        <ChevronRight size={18} className="rotate-90" />
                      )}
                    </div>

                    <AnimatePresence>
                      {expandedStep === index && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          className="mt-4 border-t border-z-border pt-4"
                        >
                          <p className="text-sm text-z-muted">
                            {getStepGuidance(key, index)}
                          </p>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.button>
                ))}
              </div>
            </div>

            <div className="rounded-2xl border border-z-border bg-white p-6 shadow-sm">
              <h2 className="mb-4 flex items-center gap-2 text-lg font-black">
                <FileUp className="text-z-accent" /> Proof upload
              </h2>
              {requiresUpload ? (
                <div className="space-y-4">
                  <label className="flex min-h-[200px] cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-z-border bg-[#FAFBFC] p-6 text-center transition-colors hover:border-z-accent hover:bg-z-accent/5">
                    <Upload className="mb-3 text-z-accent" size={40} />
                    <b className="text-base">
                      {uploadedProof
                        ? `${uploadedProof.file_name} uploaded`
                        : selectedFile
                          ? selectedFile.name
                          : uploadLabel}
                    </b>
                    <span className="mt-2 text-sm text-z-muted">
                      PDF, PNG, JPG, or screenshot accepted for demo verification
                    </span>
                    <input
                      type="file"
                      className="hidden"
                      accept=".pdf,.png,.jpg,.jpeg"
                      onChange={(event) =>
                        handleFileSelected(event.target.files?.[0] || null)
                      }
                    />
                  </label>

                  {filePreview && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="relative overflow-hidden rounded-lg border border-z-border"
                    >
                      <img
                        src={filePreview}
                        alt="File preview"
                        className="max-h-64 w-full object-contain"
                      />
                      <button
                        onClick={() => handleFileSelected(null)}
                        className="absolute top-2 right-2 rounded-full bg-black/50 p-1 text-white hover:bg-black/70"
                      >
                        <X size={18} />
                      </button>
                    </motion.div>
                  )}

                  {selectedFile && !uploadedProof && (
                    <div className="rounded-lg bg-blue-50 p-3 text-sm">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-semibold text-blue-900">
                          {selectedFile.name}
                        </span>
                        <span className="text-xs text-blue-700">
                          {(selectedFile.size / 1024).toFixed(1)} KB
                        </span>
                      </div>
                      <div className="h-1.5 rounded-full bg-blue-200 overflow-hidden">
                        <motion.div
                          className="h-full bg-blue-500"
                          initial={{ width: 0 }}
                          animate={{ width: '100%' }}
                          transition={{ duration: 2 }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="rounded-2xl border border-z-border bg-[#FAFBFC] p-4">
                  <p className="mb-4 text-sm font-bold text-z-muted">{uploadLabel}</p>
                  <div className="grid gap-2 sm:grid-cols-3">
                    {['Pay down card', 'Save $25', 'Review spending'].map((goal) => (
                      <button
                        key={goal}
                        onClick={() => setSelectedGoal(goal)}
                        className={`rounded-xl border px-3 py-3 text-sm font-black transition-all ${
                          selectedGoal === goal
                            ? 'border-z-accent bg-z-accent text-white'
                            : 'border-z-border bg-white hover:border-z-accent'
                        }`}
                      >
                        {goal}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </section>

          <aside className="space-y-6">
            <div className="rounded-2xl border border-z-border bg-white p-6 shadow-sm">
              <h2 className="mb-4 flex items-center gap-2 text-lg font-black">
                <ShieldCheck className="text-z-accent" /> Live verification
              </h2>

              <div className="space-y-3">
                {verificationSteps.map((step) => (
                  <motion.div
                    key={step.id}
                    className={`flex items-center gap-3 rounded-lg p-3 transition-all ${
                      step.status === 'passed'
                        ? 'bg-z-success/10'
                        : step.status === 'failed'
                          ? 'bg-red-50'
                          : step.status === 'running'
                            ? 'bg-z-accent/10'
                            : 'bg-gray-50'
                    }`}
                    initial={{ opacity: 0, x: -4 }}
                    animate={{ opacity: 1, x: 0 }}
                  >
                    {step.status === 'passed' && (
                      <CheckCircle2 className="text-z-success flex-shrink-0" size={18} />
                    )}
                    {step.status === 'failed' && (
                      <AlertCircle className="text-red-500 flex-shrink-0 animate-pulse" size={18} />
                    )}
                    {step.status === 'running' && (
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                        className="flex-shrink-0"
                      >
                        <Zap className="text-z-accent" size={18} />
                      </motion.div>
                    )}
                    {step.status === 'pending' && (
                      <div className="h-5 w-5 rounded-full border-2 border-gray-300 flex-shrink-0" />
                    )}

                    <span className="text-sm font-semibold flex-1">{step.label}</span>
                  </motion.div>
                ))}
              </div>

              {verificationError && (
                <motion.div
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 rounded-lg bg-red-50 p-4 border border-red-200"
                >
                  <p className="text-sm font-semibold text-red-900">
                    Verification failed
                  </p>
                  <p className="text-sm text-red-700 mt-1">{verificationError}</p>
                </motion.div>
              )}

              {showSuccessAnimation && !verificationError && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="mt-4 rounded-lg bg-z-success/10 p-4 border border-z-success"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <motion.div
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 0.6, repeat: Infinity }}
                    >
                      <BadgeCheck className="text-z-success" size={20} />
                    </motion.div>
                    <p className="font-bold text-z-success">Verification complete!</p>
                  </div>
                  <p className="text-sm text-z-success/80">
                    You've earned {content.reward} Z-Coins
                  </p>
                </motion.div>
              )}

              <button
                onClick={handleVerify}
                disabled={verifying || verified || (verificationError && !showSuccessAnimation)}
                className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-z-accent px-4 py-3 font-black text-white hover:bg-red-700 disabled:opacity-60 transition-all"
              >
                {verified ? (
                  <>
                    <BadgeCheck size={18} /> Reward claimed
                  </>
                ) : verifying ? (
                  <>
                    <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity }}>
                      <Zap size={18} />
                    </motion.div>
                    Running verification...
                  </>
                ) : verificationError ? (
                  <>
                    <AlertCircle size={18} /> Retry verification
                  </>
                ) : (
                  <>
                    <Zap size={18} /> Verify & claim reward
                  </>
                )}
              </button>

              {verified && (
                <button
                  onClick={handleClaimReward}
                  className="mt-3 w-full rounded-xl border border-z-accent bg-z-accent/5 px-4 py-3 font-black text-z-accent hover:bg-z-accent/10 transition-all"
                >
                  Return to dashboard
                </button>
              )}
            </div>

            <div className="rounded-2xl border border-z-border bg-white p-6 shadow-sm">
              <h2 className="mb-4 flex items-center gap-2 text-lg font-black">
                <Flame className="text-z-coin" /> Reward details
              </h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center pb-4 border-b border-z-border">
                  <span className="text-sm text-z-muted">Action title</span>
                  <span className="font-bold">{content.title}</span>
                </div>
                <div className="flex justify-between items-center pb-4 border-b border-z-border">
                  <span className="text-sm text-z-muted">Reward amount</span>
                  <div className="flex items-center gap-2">
                    <Zap size={18} className="text-z-coin" />
                    <span className="font-black text-lg text-z-coin">
                      {content.reward}
                    </span>
                  </div>
                </div>
                <div className="flex justify-between items-center pb-4 border-b border-z-border">
                  <span className="text-sm text-z-muted">Estimated time</span>
                  <div className="flex items-center gap-2">
                    <Clock size={16} className="text-z-muted" />
                    <span className="font-semibold">{content.timeline}</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-z-muted">Proof type</span>
                  <span className="font-semibold">{uploadLabel}</span>
                </div>
              </div>

              <div className="mt-6 rounded-lg bg-z-accent/10 p-4">
                <p className="text-xs text-z-muted mb-2">VERIFICATION STEPS</p>
                <div className="space-y-2">
                  {content.verification.map((item) => (
                    <div key={item} className="flex items-center gap-2">
                      <CheckCircle2 size={14} className="text-z-success flex-shrink-0" />
                      <span className="text-sm font-semibold">{item}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <button
              onClick={() => navigate('/rewards')}
              className="flex w-full items-center justify-between rounded-2xl border border-z-border bg-white p-5 text-left shadow-sm hover:border-z-accent transition-all"
            >
              <span className="flex items-center gap-3 font-black">
                <CheckCircle2 className="text-z-accent" /> Reward history
              </span>
              <ChevronRight />
            </button>
          </aside>
        </div>
      </div>
    </div>
  )
}

function getStepGuidance(moduleId: string, stepIndex: number): string {
  const guidance: Record<string, string[]> = {
    bills: [
      'Review the credit card statement requirements. Make sure to have the latest statement or payment confirmation ready.',
      'Upload a clear screenshot or PDF of your recent payment. The file should show the payment date and amount.',
      'Submit your proof and we\'ll verify your on-time payment automatically.',
    ],
    savings: [
      'Check your current savings account balance and ensure it meets the milestone requirement.',
      'Prepare a screenshot of your latest account statement showing the total savings.',
      'Upload your savings proof for instant verification.',
    ],
    'credit-score': [
      'Get your latest credit score from any of the major bureaus or your bank.',
      'Make sure you have proof of the score improvement compared to last month.',
      'Upload your credit report or score screenshot showing the improvement.',
    ],
    education: [
      'Complete the financial education module by reviewing all the content.',
      'Take the short quiz at the end to demonstrate understanding.',
      'Upload your completion certificate for verification.',
    ],
    'direct-deposit': [
      'Contact your HR or payroll department for the direct deposit form.',
      'Fill out the form with your Zolve bank account details.',
      'Upload the signed form or confirmation email from your employer.',
    ],
  }

  const steps = guidance[moduleId] || [
    'Complete this step as required.',
    'Provide proof or confirmation of completion.',
    'Submit for verification.',
  ]

  return steps[stepIndex] || 'Complete this action step.'
}
