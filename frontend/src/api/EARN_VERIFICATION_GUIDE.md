# Earn Verification System - Integration Guide

## Overview

The `earn-verification.ts` module provides comprehensive verification logic for the Earn workflow. It handles:

1. **Local client-side verification** - File validation, content checking, duplicate detection
2. **Backend integration** - Uploading proofs and submitting verification requests
3. **Step-by-step tracking** - Detailed status and error messages at each stage

## Core Interfaces

### VerificationStep

Each verification step has:
- `id`: Unique identifier (step_1_validate_proof, etc.)
- `name`: Human-readable name
- `status`: One of 'pending', 'running', 'passed', 'failed'
- `result`: Success message (only if passed)
- `error`: Error message (only if failed)
- `timestamp`: When the step was processed

### VerificationResult

Complete result after all verification steps:
- `verified`: Boolean indicating overall success
- `steps`: Array of all verification steps taken
- `totalTime`: Total time in milliseconds
- `eligibleReward`: Number of coins user can claim
- `message`: Summary message

## Basic Usage

### 1. Quick Verification (Local Only)

Run local verification on a file without uploading:

```typescript
import { runVerification } from '../api/earn-verification'

const file = event.target.files?.[0]
if (file) {
  const result = await runVerification(file, userId)
  
  if (result.verified) {
    console.log(`Eligible for ${result.eligibleReward} coins`)
    console.log(`Verification took ${result.totalTime}ms`)
  } else {
    console.error(`Verification failed: ${result.message}`)
    result.steps.forEach(step => {
      if (step.error) {
        console.error(`${step.name}: ${step.error}`)
      }
    })
  }
}
```

### 2. Full Workflow (Upload + Verify)

Complete workflow including backend verification:

```typescript
import {
  uploadProofFile,
  submitVerificationRequest,
  runVerification,
} from '../api/earn-verification'

// Step 1: Local validation
const localResult = await runVerification(file, userId)
if (!localResult.verified) {
  throw new Error(localResult.message)
}

// Step 2: Upload to backend
const uploadResult = await uploadProofFile(file, userId, 'savings')
console.log(`Uploaded: ${uploadResult.upload_id}`)

// Step 3: Submit for backend verification
const verifyResult = await submitVerificationRequest(
  userId,
  'savings',
  uploadResult.upload_id,
  uploadResult.file_name,
  { amount: 5000, date: '2024-01-15' }
)

if (verifyResult.eligible) {
  console.log(`Earned ${verifyResult.coins_awarded} coins!`)
}
```

### 3. Individual Verification Steps

You can run verification steps individually:

```typescript
import { earnVerification } from '../api/earn-verification'

// Validate file only
const validationStep = earnVerification.validateProof(file)
if (validationStep.status === 'failed') {
  console.error(validationStep.error)
}

// Check file content
const contentStep = await earnVerification.verifyFileContent(file, userId)
console.log(contentStep.result)

// Check for duplicates
const duplicateStep = await earnVerification.checkDuplicates(userId, fileHash)
console.log(duplicateStep.result)

// Calculate file hash
const hash = await earnVerification.calculateFileHash(file)
console.log(`File hash: ${hash}`)
```

## Verification Rules

### File Validation (Step 1)

- **Supported formats**: PDF, PNG, JPG, JPEG
- **Size limits**: 1KB minimum, 10MB maximum
- **MIME type validation**: Checked against allowed types
- **Extension validation**: Matched to file name

**Failure cases:**
- Invalid file type (e.g., Word doc, Excel file)
- File too small (< 1KB)
- File too large (> 10MB)
- Extension doesn't match MIME type

### Content Verification (Step 2)

- File must be readable and non-empty
- Content is parsed (OCR in production)
- Verified against user account details
- Data extracted and validated

**Failure cases:**
- File cannot be read
- File is empty or corrupted
- Content doesn't match user account
- Parsing/OCR fails

### Duplicate Detection (Step 3)

- Checks for identical files uploaded in last 24 hours
- Uses SHA-256 hash for comparison
- Prevents abuse and reward duplication
- User-specific (same file OK for different users)

**Failure cases:**
- Exact duplicate found (same file hash within 24 hours)
- Multiple similar submissions flagged

## React Component Integration

### Example: File Upload with Verification

```typescript
import { useState } from 'react'
import { runVerification, uploadProofFile } from '../api/earn-verification'

function EarnProofUpload({ moduleId, userId }) {
  const [file, setFile] = useState<File | null>(null)
  const [verifying, setVerifying] = useState(false)
  const [result, setResult] = useState(null)

  const handleVerify = async () => {
    if (!file) return

    setVerifying(true)
    try {
      // Local verification
      const localResult = await runVerification(file, userId)
      
      if (!localResult.verified) {
        setResult({
          success: false,
          message: localResult.message,
          steps: localResult.steps,
        })
        setVerifying(false)
        return
      }

      // Upload to backend
      const upload = await uploadProofFile(file, userId, moduleId)
      setResult({
        success: true,
        upload_id: upload.upload_id,
        message: 'File verified and uploaded successfully',
      })
    } catch (error) {
      setResult({
        success: false,
        message: error.message,
      })
    } finally {
      setVerifying(false)
    }
  }

  return (
    <div>
      <input
        type="file"
        accept=".pdf,.png,.jpg,.jpeg"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
      />
      <button onClick={handleVerify} disabled={!file || verifying}>
        {verifying ? 'Verifying...' : 'Verify & Upload'}
      </button>
      {result && (
        <div className={result.success ? 'success' : 'error'}>
          {result.message}
          {result.steps && (
            <ul>
              {result.steps.map((step) => (
                <li key={step.id}>
                  {step.name}: {step.status}
                  {step.error && ` - ${step.error}`}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}
```

### Example: Progress Indicator

```typescript
function VerificationProgress({ result }) {
  const progressPercent = (result.steps.filter(s => s.status !== 'pending').length / result.steps.length) * 100

  return (
    <div>
      <div className="progress-bar" style={{ width: `${progressPercent}%` }} />
      
      {result.steps.map((step) => (
        <div key={step.id} className={`step step-${step.status}`}>
          <span className="step-name">{step.name}</span>
          <span className="step-status">
            {step.status === 'passed' && '✓'}
            {step.status === 'failed' && '✗'}
            {step.status === 'running' && '⏳'}
            {step.status === 'pending' && '○'}
          </span>
          {step.error && <span className="error">{step.error}</span>}
          {step.result && <span className="result">{step.result}</span>}
        </div>
      ))}

      <div className="summary">
        <p>Time: {result.totalTime}ms</p>
        <p>Eligible reward: {result.eligibleReward} coins</p>
        <p>{result.message}</p>
      </div>
    </div>
  )
}
```

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Invalid file type" | Wrong file format | Upload PDF, PNG, JPG, or JPEG |
| "File is too large" | Exceeds 10MB limit | Compress or upload smaller file |
| "File is too small" | Less than 1KB | Ensure file has actual content |
| "File content could not be read" | Corrupted file | Re-download and upload file |
| "No duplicate uploads detected" | Passing duplicate check | OK to proceed to backend |
| "Upload failed: Network error" | Backend unavailable | Retry or check internet connection |

### Retry Strategy

```typescript
async function verifyWithRetry(
  file: File,
  userId: number,
  maxRetries = 3
) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await runVerification(file, userId)
    } catch (error) {
      if (attempt === maxRetries) throw error
      await new Promise(r => setTimeout(r, 1000 * attempt))
    }
  }
}
```

## Performance Considerations

- **Local verification** is instant (< 50ms typically)
- **File hashing** is async but fast for files < 10MB
- **Backend verification** varies (100ms - 1s typically)
- **Total workflow** typically completes in < 2 seconds

### Optimization Tips

1. Validate file locally before showing upload UI
2. Show progress indicators during hashing
3. Cache verification results temporarily
4. Batch multiple verifications if needed

```typescript
// Example: Optimized upload flow
const validateQuickly = (file: File) => {
  const step = earnVerification.validateProof(file)
  return step.status === 'passed'
}

if (validateQuickly(file)) {
  // Safe to show upload UI
  showUploadUI()
}
```

## Backend Integration

The module integrates with these backend endpoints:

### POST /earn/proofs
Uploads a proof file to the backend.

**Request:**
```typescript
{
  user_id: 1,
  module_id: "savings",
  file_name: "proof.pdf",
  mime_type: "application/pdf",
  size_bytes: 102400,
  content_base64: "JVBERi0xLjQKJeLjz9MNCjEgMCBvYmo..."
}
```

**Response:**
```typescript
{
  success: true,
  upload_id: "earn_1_savings_20240115120030123456",
  file_name: "proof.pdf",
  mime_type: "application/pdf",
  size_bytes: 102400,
  stored_path: "/uploads/earn-proofs/1/savings/..."
}
```

### POST /earn/verify
Submits verification request to backend.

**Request:**
```typescript
{
  user_id: 1,
  module_id: "savings",
  proof_type: "document_upload",
  proof_name: "proof.pdf",
  upload_id: "earn_1_savings_20240115120030123456",
  mime_type: "application/pdf",
  size_bytes: 102400,
  metadata: { amount: 5000, date: "2024-01-15" }
}
```

**Response:**
```typescript
{
  success: true,
  event_id: 42,
  transaction_id: 123,
  behavior_id: 456,
  eligible: true,
  module_id: "savings",
  behavior_type: "savings_milestone",
  coins_awarded: 350,
  new_balance: 5350,
  message: "Verified savings_milestone and awarded 350 Z-Coins."
}
```

## Testing

Run the test suite:

```bash
npm test -- earn-verification.test.ts
```

Test cases cover:
- ✓ Valid file passes all steps
- ✓ Invalid file type fails at step 1
- ✓ Wrong user account fails at step 2
- ✓ Duplicate file fails at step 3
- ✓ Successful verification returns reward amount
- ✓ File hashing produces consistent results
- ✓ Custom earning weights are applied
- ✓ Detailed error messages on failure

## Module Exports

```typescript
// Main verification function
export function runVerification(
  file: File,
  userId: number,
  earnWeights?: Record<string, number>
): Promise<VerificationResult>

// Backend integration
export function uploadProofFile(
  file: File,
  userId?: number,
  moduleId?: string
): Promise<UploadResponse>

export function submitVerificationRequest(
  userId?: number,
  moduleId?: string,
  uploadId?: string,
  proofName?: string,
  metadata?: Record<string, any>
): Promise<any>

// Individual steps
export function validateProof(file: File): VerificationStep
export function verifyFileContent(file: File, userId: number): Promise<VerificationStep>
export function checkDuplicates(userId: number, fileHash: string): Promise<VerificationStep>
export function calculateFileHash(file: File): Promise<string>
export function getVerificationStatus(verificationId: string): Promise<VerificationResult>

// Namespace
export const earnVerification = {
  validateProof,
  verifyFileContent,
  checkDuplicates,
  calculateFileHash,
  runVerification,
  getVerificationStatus,
  uploadProofFile,
  submitVerificationRequest,
}
```

## Next Steps

1. **Integrate into EarnActionPage** - Replace manual verification logic
2. **Add to useEarnStore** - Store verification state and results
3. **Create VerificationUI component** - Display step-by-step progress
4. **Handle offline scenarios** - Queue verifications for later
5. **Add analytics** - Track verification success rates
6. **Implement retry logic** - Handle transient failures gracefully
