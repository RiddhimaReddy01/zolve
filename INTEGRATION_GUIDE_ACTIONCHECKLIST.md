# ActionChecklist Integration Guide

## Quick Start

The **ActionChecklist** component is now ready for integration into the Earn workflow. It provides a flexible, dark-themed alternative to the existing EarnActionChecklistPage with reusable patterns and animations.

## What Was Created

### 1. Main Component: `ActionChecklist.tsx`
A fully-featured, production-ready component with:
- Dark mode support (z-surface theme)
- Smooth Framer Motion animations
- Step progress tracking
- Error handling
- Time tracking (estimated vs elapsed)
- Expandable details
- Interactive action buttons
- Full accessibility support

**Location:** `frontend/src/components/ActionChecklist.tsx`

### 2. Example Components for Reference
- **ActionChecklist.demo.tsx** - Basic demo showing all features
- **EarnActionExample.tsx** - Full workflow example with API simulation
- **ActionChecklist.usage.md** - Complete documentation

## How to Use

### Step 1: Import the Component

```typescript
import { ActionChecklist, ActionStep } from '../components/ActionChecklist'
import { Upload, CheckCircle2, Zap } from 'lucide-react'
```

### Step 2: Define Your Steps

```typescript
const steps: ActionStep[] = [
  {
    id: 'upload',
    title: 'Upload Proof',
    description: 'Upload your bank statement or document',
    icon: <Upload size={20} />,
    status: 'pending',
    estimatedMinutes: 2,
    action: {
      label: 'Choose File',
      onClick: () => handleFileUpload(),
    }
  },
  {
    id: 'verify',
    title: 'Verify Details',
    description: 'Confirm the extracted information',
    icon: <CheckCircle2 size={20} />,
    status: 'pending',
    estimatedMinutes: 3,
  },
  {
    id: 'claim',
    title: 'Claim Reward',
    description: '150 Z-Coins will be credited',
    icon: <Zap size={20} />,
    status: 'pending',
  }
]
```

### Step 3: Render the Component

```typescript
export function MyEarnAction() {
  const [steps, setSteps] = useState<ActionStep[]>([...])

  const handleStepChange = (stepId: string) => {
    console.log('User progressed to:', stepId)
    // Track analytics, log progress, etc.
  }

  return (
    <div className="rounded-2xl border border-white/10 bg-z-surface p-6">
      <ActionChecklist
        steps={steps}
        onStepChange={handleStepChange}
        showEstimatedTime={true}
      />
    </div>
  )
}
```

## Integration Scenarios

### Scenario 1: Bank Verification Flow
```typescript
const handleUploadFile = async (file: File) => {
  setSteps(prev => prev.map(step =>
    step.id === 'upload' 
      ? { ...step, status: 'active', action: { ...step.action, loading: true } }
      : step
  ))

  try {
    const result = await uploadToAPI(file)
    
    setSteps(prev => prev.map((step, idx) => {
      if (step.id === 'upload') {
        return { 
          ...step, 
          status: 'completed',
          details: `${file.name} uploaded successfully`,
          action: { ...step.action, loading: false }
        }
      }
      if (step.id === 'verify') {
        return { ...step, status: 'active' }
      }
      return step
    }))
  } catch (error) {
    setSteps(prev => prev.map(step =>
      step.id === 'upload' ? { ...step, status: 'error' } : step
    ))
  }
}
```

### Scenario 2: Multi-Step Verification
```typescript
const progressSteps = async () => {
  for (let i = 0; i < steps.length; i++) {
    const step = steps[i]
    
    // Mark as active
    setSteps(prev => prev.map((s, idx) => 
      idx === i ? { ...s, status: 'active', elapsedMinutes: 0 } : s
    ))

    try {
      // Simulate processing
      const result = await verifyStep(step.id)
      
      // Mark as completed
      setSteps(prev => prev.map((s, idx) => 
        idx === i 
          ? { ...s, status: 'completed', elapsedMinutes: Math.floor(result.duration / 60) }
          : s
      ))
    } catch (error) {
      setSteps(prev => prev.map((s, idx) => 
        idx === i ? { ...s, status: 'error' } : s
      ))
      break // Stop on error
    }
  }
}
```

### Scenario 3: With Redux/Zustand State

```typescript
// Using Zustand (example)
const useEarnStore = create((set) => ({
  steps: initialSteps,
  
  updateStep: (stepId: string, updates: Partial<ActionStep>) =>
    set((state) => ({
      steps: state.steps.map(step =>
        step.id === stepId ? { ...step, ...updates } : step
      )
    })),
  
  completeStep: (stepId: string) =>
    set((state) => ({
      steps: state.steps.map((step, idx) => {
        if (step.id === stepId) {
          return { ...step, status: 'completed' }
        }
        // Auto-activate next step
        if (state.steps[idx - 1]?.id === stepId && step.status === 'pending') {
          return { ...step, status: 'active' }
        }
        return step
      })
    })),
  
  markError: (stepId: string, error: string) =>
    set((state) => ({
      steps: state.steps.map(step =>
        step.id === stepId 
          ? { ...step, status: 'error', details: error }
          : step
      )
    }))
}))

// In component:
function MyEarnAction() {
  const { steps, updateStep, completeStep, markError } = useEarnStore()

  return (
    <ActionChecklist
      steps={steps}
      onStepChange={(stepId) => console.log('Step:', stepId)}
    />
  )
}
```

## Customization Guide

### Change Colors
The component uses Tailwind's z-surface theme. To customize:

1. **For all instances** - Update `tailwind.config.ts`:
```typescript
colors: {
  z: {
    accent: '#YOUR_COLOR', // Changes all active/success indicators
  }
}
```

2. **For specific instances** - Wrap in div with custom classes:
```typescript
<div className="[--z-accent:#FF0000]">
  <ActionChecklist steps={steps} />
</div>
```

### Change Icons
Replace lucide-react icons with any icon library:

```typescript
import { CustomIcon } from 'your-icon-library'

const steps: ActionStep[] = [
  {
    id: 'step1',
    icon: <CustomIcon />, // Any React component
    // ...
  }
]
```

### Change Animations
Modify animation speeds in the component (lines 105-106):

```typescript
// Faster animations
transition={{ delay: index * 0.05, duration: 0.2 }}

// Slower animations
transition={{ delay: index * 0.15, duration: 0.6 }}
```

### Change Layout
The component is 100% width. Wrap with container as needed:

```typescript
<div className="max-w-2xl mx-auto">
  <ActionChecklist steps={steps} />
</div>
```

## Common Patterns

### Auto-Progress (No User Action)
```typescript
useEffect(() => {
  const timer = setInterval(() => {
    const activeStep = steps.find(s => s.status === 'active')
    if (activeStep) {
      const nextIdx = steps.findIndex(s => s.id === activeStep.id) + 1
      if (nextIdx < steps.length) {
        // Auto-progress
        completeStep(activeStep.id)
      }
    }
  }, 5000) // Every 5 seconds
  
  return () => clearInterval(timer)
}, [steps])
```

### Timed Steps (Auto-Complete)
```typescript
const handleActiveStep = (stepId: string) => {
  const step = steps.find(s => s.id === stepId)
  const duration = step?.estimatedMinutes || 1
  
  setTimeout(() => {
    completeStep(stepId)
  }, duration * 60 * 1000)
}
```

### Conditional Step Visibility
```typescript
const visibleSteps = steps.filter(step => {
  if (step.id === 'optional-step' && !userHasCondition) {
    return false
  }
  return true
})

<ActionChecklist steps={visibleSteps} />
```

### Error Retry with Reset
```typescript
const handleRetry = (stepId: string) => {
  setSteps(prev => prev.map((step, idx) => {
    if (step.id === stepId) {
      return {
        ...step,
        status: 'active',
        details: undefined,
        elapsedMinutes: 0,
        action: {
          ...step.action,
          loading: false
        }
      }
    }
    return step
  }))
}
```

## Comparison: ActionChecklist vs EarnActionChecklistPage

| Feature | ActionChecklist | EarnActionChecklistPage |
|---------|-----------------|------------------------|
| Theme | Dark (z-surface) | Light (white) |
| Reusable | Yes | Page-specific |
| Animation Library | Framer Motion | Framer Motion |
| Dependencies | Minimal | More integrated |
| Customization | Easy | Requires page edit |
| File Upload | No (actions only) | Integrated |
| Verification Steps | No | Yes (sidebar) |
| Use Case | General workflows | Specific earn actions |

## Migration Guide

If you want to replace EarnActionChecklistPage with ActionChecklist:

1. **Extract steps from content:**
```typescript
const steps = content.steps.map((title, idx) => ({
  id: `step-${idx}`,
  title: title,
  description: getDescription(title),
  icon: getIcon(title),
  status: idx < currentStep ? 'completed' : idx === currentStep ? 'active' : 'pending'
}))
```

2. **Move verification logic to action buttons:**
```typescript
action: {
  label: idx === currentStep ? 'Next' : 'View',
  onClick: () => {
    if (idx === currentStep) {
      handleVerification(step.id)
    }
  }
}
```

3. **Handle file upload as separate component:**
```typescript
<FileUploadArea onFileSelected={handleFileSelected} />
<ActionChecklist steps={steps} />
<VerificationDisplay verification={verificationSteps} />
```

## Testing Integration

### Example Test
```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { ActionChecklist } from './ActionChecklist'

test('completes step on action click', () => {
  const handleClick = jest.fn()
  const steps = [
    {
      id: 'test',
      title: 'Test Step',
      description: 'Test',
      icon: null,
      status: 'active',
      action: { label: 'Test', onClick: handleClick }
    }
  ]

  render(<ActionChecklist steps={steps} />)
  
  const button = screen.getByText('Test')
  fireEvent.click(button)
  
  expect(handleClick).toHaveBeenCalled()
})
```

## Troubleshooting

### Component not showing
- Check that z-surface theme colors are in tailwind.config.ts
- Ensure parent has `text-white` class for dark mode
- Check browser console for React errors

### Animations not working
- Verify framer-motion is installed: `npm list framer-motion`
- Check if prefers-reduced-motion is disabled in browser
- Inspect component with DevTools (Framer Motion tab)

### Styling issues
- Ensure Tailwind CSS is loaded
- Check tailwind.config.ts includes component path
- Verify clsx is installed

### Icons not appearing
- Check lucide-react is installed
- Verify icon imports are correct
- Inspect element to see if icon is rendered but hidden

## Performance Optimization

For long lists of steps:
```typescript
import { memo } from 'react'

const MemoizedChecklist = memo(ActionChecklist, (prev, next) => {
  // Only re-render if steps actually changed
  return JSON.stringify(prev.steps) === JSON.stringify(next.steps)
})
```

## Accessibility Notes

The component includes:
- Semantic HTML structure
- Proper heading hierarchy
- High contrast colors
- Keyboard navigation (click-based)
- Clear status indicators
- Loading states for async operations

## Next Steps

1. ✅ Component created and tested
2. → Import into your Earn action page
3. → Define your specific workflow steps
4. → Connect to your API/state management
5. → Test with real data
6. → Deploy to production

## Support

For detailed documentation, see: `ActionChecklist.usage.md`
For examples, see: `EarnActionExample.tsx` and `ActionChecklist.demo.tsx`

All files are located in: `frontend/src/components/`
