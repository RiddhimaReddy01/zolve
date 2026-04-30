import { ReactNode, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  CheckCircle2,
  Circle,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Clock,
} from 'lucide-react'
import clsx from 'clsx'
import { Button } from './ui/Button'

export interface ActionStep {
  id: string
  title: string
  description: string
  icon: ReactNode
  status: 'pending' | 'active' | 'completed' | 'error'
  details?: string
  action?: {
    label: string
    onClick: () => void
    loading?: boolean
  }
  estimatedMinutes?: number
  elapsedMinutes?: number
}

interface ActionChecklistProps {
  steps: ActionStep[]
  onStepChange?: (stepId: string) => void
  showEstimatedTime?: boolean
}

export function ActionChecklist({
  steps,
  onStepChange,
  showEstimatedTime = true,
}: ActionChecklistProps) {
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set())

  const toggleExpanded = (stepId: string) => {
    const newExpanded = new Set(expandedSteps)
    if (newExpanded.has(stepId)) {
      newExpanded.delete(stepId)
    } else {
      newExpanded.add(stepId)
    }
    setExpandedSteps(newExpanded)
  }

  const getStepNumber = (index: number) => index + 1

  const progressPercentage = (
    (steps.filter((s) => s.status === 'completed').length / steps.length) *
    100
  )

  const activeStepIndex = steps.findIndex((s) => s.status === 'active')
  const hasError = steps.some((s) => s.status === 'error')

  return (
    <div className="w-full space-y-6">
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-white">Progress</h3>
          <span className="text-sm text-z-muted">
            {steps.filter((s) => s.status === 'completed').length} of{' '}
            {steps.length}
          </span>
        </div>

        <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden border border-white/10">
          <motion.div
            className={clsx('h-full rounded-full transition-all duration-500', {
              'bg-z-accent': !hasError,
              'bg-red-500': hasError,
            })}
            initial={{ width: 0 }}
            animate={{ width: `${progressPercentage}%` }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
            style={{
              boxShadow: hasError
                ? '0 10px 24px rgba(239, 68, 68, 0.28)'
                : '0 10px 24px rgba(232, 0, 29, 0.28)',
            }}
          />
        </div>
      </div>

      <div className="relative space-y-4">
        {steps.map((step, index) => {
          const isCompleted = step.status === 'completed'
          const isActive = step.status === 'active'
          const isError = step.status === 'error'
          const isPending = step.status === 'pending'
          const isExpanded = expandedSteps.has(step.id)
          const showConnector = index < steps.length - 1

          return (
            <div key={step.id}>
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1, duration: 0.4 }}
                className={clsx(
                  'relative rounded-lg border transition-all duration-300 cursor-pointer',
                  {
                    'border-z-accent/50 bg-z-accent/5': isActive,
                    'border-white/10 bg-white/5': !isActive && !isError,
                    'border-red-500/50 bg-red-500/5': isError,
                  }
                )}
                onClick={() => toggleExpanded(step.id)}
              >
                <div className="p-4">
                  <div className="flex items-start gap-4">
                    <div className="flex flex-col items-center pt-1">
                      <div className="relative z-10">
                        <motion.div
                          className={clsx(
                            'flex h-10 w-10 items-center justify-center rounded-full border-2 font-semibold',
                            {
                              'border-z-accent bg-z-accent text-white': isActive,
                              'border-z-success bg-z-success text-white':
                                isCompleted,
                              'border-red-500 bg-red-500/20 text-red-500':
                                isError,
                              'border-white/20 bg-white/5 text-white/40':
                                isPending,
                            }
                          )}
                          animate={
                            isActive
                              ? {
                                  boxShadow: [
                                    '0 0 0 0 rgba(232, 0, 29, 0.3)',
                                    '0 0 0 12px rgba(232, 0, 29, 0)',
                                  ],
                                }
                              : {}
                          }
                          transition={
                            isActive
                              ? {
                                  duration: 2,
                                  repeat: Infinity,
                              }
                              : {}
                          }
                        >
                          {isCompleted ? (
                            <CheckCircle2 size={20} className="text-z-success" />
                          ) : isError ? (
                            <AlertCircle size={20} className="text-red-500" />
                          ) : (
                            <span>{getStepNumber(index)}</span>
                          )}
                        </motion.div>
                      </div>

                      {showConnector && (
                        <div className="relative h-12 w-1 mt-2">
                          <div className="absolute inset-0 bg-gradient-to-b from-white/10 to-white/5" />
                          <motion.div
                            className="absolute inset-0 bg-gradient-to-b from-z-accent to-z-accent/20"
                            initial={{ height: 0 }}
                            animate={{
                              height: isCompleted ? '100%' : '0%',
                            }}
                            transition={{ duration: 0.5, ease: 'easeOut' }}
                          />
                        </div>
                      )}
                    </div>

                    <div className="flex-1 pt-1">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4
                            className={clsx(
                              'font-semibold transition-colors',
                              {
                                'text-white': isActive || isCompleted,
                                'text-white/70': isPending,
                                'text-red-500': isError,
                              }
                            )}
                          >
                            {step.title}
                          </h4>
                          <p className="text-sm text-z-muted mt-1">
                            {step.description}
                          </p>
                        </div>

                        <div className="flex items-center gap-2">
                          {showEstimatedTime &&
                            step.estimatedMinutes &&
                            !isExpanded && (
                              <div className="flex items-center gap-1 px-2 py-1 rounded bg-white/5 text-xs text-z-muted">
                                <Clock size={12} />
                                {step.estimatedMinutes}m
                              </div>
                            )}
                          <motion.div
                            animate={{ rotate: isExpanded ? 180 : 0 }}
                            transition={{ duration: 0.2 }}
                          >
                            <ChevronDown
                              size={20}
                              className="text-z-muted"
                            />
                          </motion.div>
                        </div>
                      </div>
                    </div>

                    {step.icon && (
                      <div
                        className={clsx(
                          'flex items-center justify-center p-2 rounded-lg transition-colors',
                          {
                            'bg-z-accent/20 text-z-accent': isActive,
                            'bg-z-success/20 text-z-success': isCompleted,
                            'bg-red-500/20 text-red-500': isError,
                            'bg-white/5 text-white/40': isPending,
                          }
                        )}
                      >
                        <div className="w-6 h-6">{step.icon}</div>
                      </div>
                    )}
                  </div>
                </div>

                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3 }}
                      className="overflow-hidden border-t border-white/10"
                    >
                      <div className="p-4 space-y-4 bg-white/2">
                        {step.details && (
                          <div className="rounded-lg bg-white/5 p-3">
                            <p className="text-sm text-white/70">
                              {step.details}
                            </p>
                          </div>
                        )}

                        {showEstimatedTime &&
                          (step.estimatedMinutes || step.elapsedMinutes) && (
                            <div className="flex items-center gap-4 text-sm">
                              {step.elapsedMinutes !== undefined && (
                                <div className="flex items-center gap-2">
                                  <Clock size={14} className="text-z-accent" />
                                  <span className="text-z-muted">
                                    Elapsed: {step.elapsedMinutes}m
                                  </span>
                                </div>
                              )}
                              {step.estimatedMinutes && (
                                <div className="flex items-center gap-2">
                                  <Clock size={14} className="text-white/40" />
                                  <span className="text-white/50">
                                    Est: {step.estimatedMinutes}m
                                  </span>
                                </div>
                              )}
                            </div>
                          )}

                        {step.action && (
                          <Button
                            onClick={() => {
                              step.action?.onClick()
                              onStepChange?.(step.id)
                            }}
                            variant={isActive ? 'primary' : 'secondary'}
                            size="md"
                            fullWidth
                            loading={step.action.loading}
                          >
                            {step.icon && (
                              <div className="w-4 h-4 flex items-center justify-center">
                                {step.icon}
                              </div>
                            )}
                            {step.action.label}
                          </Button>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                {isError && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="px-4 pb-4 pt-2"
                  >
                    <div className="flex items-center gap-2 rounded-lg bg-red-500/10 border border-red-500/20 px-3 py-2">
                      <AlertCircle size={14} className="text-red-500 flex-shrink-0" />
                      <p className="text-xs text-red-500">
                        This step requires attention. Please review and retry.
                      </p>
                    </div>
                  </motion.div>
                )}
              </motion.div>
            </div>
          )
        })}
      </div>

      {steps.every((s) => s.status === 'completed') && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="rounded-lg border border-z-success/30 bg-z-success/10 p-4 text-center"
        >
          <div className="flex items-center justify-center gap-2 text-z-success font-semibold">
            <CheckCircle2 size={20} />
            All steps completed!
          </div>
        </motion.div>
      )}
    </div>
  )
}
