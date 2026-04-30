# ActionChecklist Component Usage Guide

## Overview

The `ActionChecklist` component displays a step-by-step progress checklist for completing earn actions in the Z-World platform. It provides visual feedback on progress, allows users to expand steps for more details, and enables interactive actions at each step.

## File Location

- Component: `src/components/ActionChecklist.tsx`
- Types: Exported `ActionStep` and component props interfaces
- Demo: `src/components/ActionChecklist.demo.tsx`

## Import

```typescript
import { ActionChecklist, ActionStep } from '../components/ActionChecklist'
```

## Component Props

```typescript
interface ActionChecklistProps {
  steps: ActionStep[]           // Array of step definitions
  onStepChange?: (stepId: string) => void  // Callback when step changes
  showEstimatedTime?: boolean   // Show estimated/elapsed time (default: true)
}
```

## Step Structure

Each step in the `steps` array is an `ActionStep` object:

```typescript
interface ActionStep {
  id: string                    // Unique identifier for the step
  title: string                 // Step title (e.g., "Upload Proof")
  description: string           // Short description of what to do
  icon: ReactNode               // Icon to display (from lucide-react)
  status: 'pending' | 'active' | 'completed' | 'error'
  details?: string              // Extended details (shown when expanded)
  action?: {                    // Optional action button
    label: string               // Button label
    onClick: () => void         // Callback when clicked
    loading?: boolean            // Show loading state
  }
  estimatedMinutes?: number     // Estimated time to complete
  elapsedMinutes?: number       // Time already spent
}
```

## Basic Example

```typescript
import { Upload, CheckCircle2, Zap } from 'lucide-react'
import { ActionChecklist } from './components/ActionChecklist'

function MyComponent() {
  const steps = [
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
      details: 'Please review the extracted data and confirm it matches your document.',
      estimatedMinutes: 3,
      elapsedMinutes: 0,
      action: {
        label: 'Verify Now',
        onClick: () => handleVerify(),
      },
    },
    {
      id: 'claim',
      title: 'Claim Reward',
      description: '150 Z-Coins will be credited',
      icon: <Zap size={20} />,
      status: 'pending',
      details: 'Your Z-Coins will be available immediately after verification.',
    },
  ]

  const handleVerify = () => {
    // Handle verification logic
  }

  return (
    <ActionChecklist
      steps={steps}
      onStepChange={(stepId) => console.log('Step:', stepId)}
      showEstimatedTime={true}
    />
  )
}
```

## Status Styling

The component automatically applies different styling based on step status:

### Completed
- Icon: CheckCircle2 with green checkmark
- Color: Green border and background
- Connector: Animated fill from previous step
- Action: Disabled or not shown

### Active
- Icon: Step number with pulsing glow
- Color: Red/accent border and background
- Connector: Being filled
- Action: Highlighted and clickable

### Pending
- Icon: Step number (grayed out)
- Color: Light gray/muted colors
- Connector: Empty
- Action: Not shown

### Error
- Icon: AlertCircle with red indicator
- Color: Red border and background
- Error message: Displayed below step
- Action: May show retry button

## Features

### 1. Progress Bar
Displays overall progress as a percentage of completed steps. Shows:
- Step count (e.g., "2 of 4")
- Animated fill bar
- Color change to red if any step has an error

### 2. Step Expansion
Click anywhere on a step to expand/collapse details:
- Extended description in `details` field
- Time information (elapsed vs estimated)
- Action button (if available)

### 3. Visual Progression
- Connected line showing step progression
- Animated fill as steps complete
- Icons highlighting current and completed steps
- Checkmark for completed steps

### 4. Time Tracking
When `showEstimatedTime` is true:
- Displays estimated time per step
- Shows elapsed time during active step
- Includes clock icon for quick recognition
- Hidden when step is not expanded (saves space)

### 5. Action Buttons
Optional action buttons can be added to any step:
- Primary styling for active steps
- Secondary styling for pending steps
- Loading state support
- Click triggers `action.onClick()` callback

### 6. Error Handling
Steps with `status: 'error'` show:
- Red icon indicator
- Error message box with AlertCircle icon
- Red border styling
- Prompts user to review and retry

## Animations

The component includes smooth animations for:
- Step entry (fade and slide)
- Progress bar fill
- Step expansion/collapse
- Connector line animation
- Pulsing glow on active step
- Completion feedback

All animations respect system motion preferences.

## Theming

Uses the z-surface design system colors:
- `z-accent` (#E8001D) - Primary actions and highlights
- `z-success` (#16A34A) - Completed states
- `z-muted` - Subtle text
- `z-surface` - Dark background (assumed)
- `white/opacity` - Light variants

## Example Integration with State Management

```typescript
import { useState } from 'react'
import { ActionChecklist } from './components/ActionChecklist'

function EarnAction() {
  const [steps, setSteps] = useState<ActionStep[]>([
    // Initial steps...
  ])

  const handleVerify = async () => {
    try {
      // Call API to verify
      const response = await verifyAPI.verify(data)
      
      // Update steps
      setSteps(prev => prev.map(step => 
        step.id === 'verify' 
          ? { ...step, status: 'completed' }
          : step.id === 'next'
          ? { ...step, status: 'active' }
          : step
      ))
    } catch (error) {
      setSteps(prev => prev.map(step =>
        step.id === 'verify'
          ? { ...step, status: 'error' }
          : step
      ))
    }
  }

  return (
    <ActionChecklist
      steps={steps}
      onStepChange={(stepId) => {
        // Track step changes for analytics
        console.log('User progressed to:', stepId)
      }}
    />
  )
}
```

## Customization

### Icons
Use any lucide-react icon:
```typescript
import { Upload, CheckCircle2, Zap, Clock, DollarSign } from 'lucide-react'

icon: <Upload size={20} />
```

### Colors
The component uses Tailwind classes. Modify colors by:
1. Changing Tailwind config in `tailwind.config.ts`
2. Using custom className props if needed
3. Z-surface design tokens are pre-configured

### Animation Speed
Adjust `transition` props in the code:
- `duration: 0.3` to 0.6 for standard animations
- `ease: 'easeOut'` for progress fills
- `repeat: Infinity` for pulsing effects

## Accessibility

- Semantic HTML with proper heading hierarchy
- Icon descriptions in titles
- High contrast colors
- Clear visual feedback for all states
- Keyboard navigable (clickable step headers)
- Time information reduces cognitive load

## Performance Notes

- Uses `AnimatePresence` from framer-motion for efficient animations
- Step expansion is local state only
- Re-renders only affected steps on prop changes
- Suitable for 5-10 steps per checklist

## Common Patterns

### Sequential Workflow
Update status progressively as user completes each step:
```typescript
setSteps(prev => prev.map((step, idx) => {
  if (idx < completedIndex) return { ...step, status: 'completed' }
  if (idx === completedIndex) return { ...step, status: 'active' }
  return { ...step, status: 'pending' }
}))
```

### With Loading States
Show loading while processing:
```typescript
{
  id: 'verify',
  status: 'active',
  action: {
    label: 'Verify',
    onClick: handleVerify,
    loading: isVerifying,  // Set based on async operation
  }
}
```

### Error Recovery
Allow retry on error:
```typescript
{
  id: 'verify',
  status: 'error',
  action: {
    label: 'Retry',
    onClick: handleRetry,
  }
}
```

## Demo Component

A complete demo is available in `ActionChecklist.demo.tsx`. It shows:
- All step statuses
- Progression through steps
- Time tracking
- Action button interaction
- Reset functionality

## Browser Support

Works with modern browsers (Chrome, Firefox, Safari, Edge).
Requires CSS Grid and Flexbox support.
