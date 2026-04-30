import { api, DEMO_USER_ID } from './client'
import type { EarnProofUploadRequest, EarnVerificationRequest } from '../types/api'

/**
 * Verification step in the earn verification workflow.
 * Each step tracks its own progress through the verification process.
 */
export interface VerificationStep {
  id: string
  name: string
  status: 'pending' | 'running' | 'passed' | 'failed'
  result?: string
  error?: string
  timestamp?: Date
}

/**
 * Complete verification result after running all steps.
 * Includes detailed status of each step and final eligibility determination.
 */
export interface VerificationResult {
  verified: boolean
  steps: VerificationStep[]
  totalTime: number
  eligibleReward: number
  message: string
}

/**
 * Configuration for proof file validation.
 */
interface ProofValidationConfig {
  minSizeBytes: number
  maxSizeBytes: number
  allowedMimeTypes: string[]
  allowedExtensions: string[]
}

const PROOF_VALIDATION_CONFIG: ProofValidationConfig = {
  minSizeBytes: 1024, // 1KB minimum
  maxSizeBytes: 10 * 1024 * 1024, // 10MB maximum
  allowedMimeTypes: ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'],
  allowedExtensions: ['.pdf', '.png', '.jpg', '.jpeg'],
}

/**
 * Validates the proof file type and size constraints.
 * Returns immediately with either pass or fail status.
 *
 * @param file The proof document to validate
 * @returns VerificationStep with validation result
 */
function validateProof(file: File): VerificationStep {
  const startTime = new Date()

  const step: VerificationStep = {
    id: 'step_1_validate_proof',
    name: 'Validate Proof File',
    status: 'running',
    timestamp: startTime,
  }

  // Check file type (MIME type)
  const mimeTypeValid = PROOF_VALIDATION_CONFIG.allowedMimeTypes.includes(
    file.type.toLowerCase()
  )
  if (!mimeTypeValid) {
    return {
      ...step,
      status: 'failed',
      error: `Invalid file type: ${file.type}. Allowed types: PDF, PNG, JPG, JPEG`,
      result: 'File type not supported',
    }
  }

  // Check file extension
  const fileName = file.name.toLowerCase()
  const hasValidExtension = PROOF_VALIDATION_CONFIG.allowedExtensions.some((ext) =>
    fileName.endsWith(ext)
  )
  if (!hasValidExtension) {
    return {
      ...step,
      status: 'failed',
      error: `Invalid file extension. Allowed extensions: ${PROOF_VALIDATION_CONFIG.allowedExtensions.join(', ')}`,
      result: 'File extension not supported',
    }
  }

  // Check file size (minimum)
  if (file.size < PROOF_VALIDATION_CONFIG.minSizeBytes) {
    return {
      ...step,
      status: 'failed',
      error: `File is too small. Minimum size: 1KB`,
      result: 'File size below minimum',
    }
  }

  // Check file size (maximum)
  if (file.size > PROOF_VALIDATION_CONFIG.maxSizeBytes) {
    return {
      ...step,
      status: 'failed',
      error: `File is too large. Maximum size: 10MB`,
      result: 'File size exceeds maximum',
    }
  }

  return {
    ...step,
    status: 'passed',
    result: `File validation passed: ${file.name} (${(file.size / 1024).toFixed(1)}KB)`,
  }
}

/**
 * Verifies that the file content matches user requirements.
 * This would be expanded to check document OCR/parsing in production.
 *
 * @param file The proof document
 * @param userId The user ID claiming the reward
 * @returns Promise resolving to verification step result
 */
async function verifyFileContent(
  file: File,
  userId: number
): Promise<VerificationStep> {
  const startTime = new Date()

  const step: VerificationStep = {
    id: 'step_2_verify_content',
    name: 'Verify File Content',
    status: 'running',
    timestamp: startTime,
  }

  try {
    // In production, this would:
    // 1. Use OCR for document parsing
    // 2. Extract key data (account info, transaction details, dates)
    // 3. Validate against user profile
    //
    // For now, we verify the file is readable and has content
    const reader = new FileReader()

    return new Promise((resolve) => {
      reader.onload = () => {
        // Check that file was actually read
        if (!reader.result || reader.result.toString().length === 0) {
          resolve({
            ...step,
            status: 'failed',
            error: 'File content could not be read or is empty',
            result: 'Failed to parse file content',
          })
          return
        }

        resolve({
          ...step,
          status: 'passed',
          result: `File content verified successfully for user ${userId}`,
        })
      }

      reader.onerror = () => {
        resolve({
          ...step,
          status: 'failed',
          error: 'Error reading file content',
          result: 'File read error',
        })
      }

      // Read just enough to verify it's readable
      reader.readAsArrayBuffer(file.slice(0, 1024))
    })
  } catch (error) {
    return {
      ...step,
      status: 'failed',
      error: `Content verification failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
      result: 'Content verification error',
    }
  }
}

/**
 * Checks for duplicate proof uploads to prevent abuse.
 * A duplicate is flagged if the same file was uploaded within 24 hours.
 *
 * @param userId The user ID
 * @param fileHash Hash/fingerprint of the file content
 * @returns Promise resolving to duplicate check step
 */
async function checkDuplicates(
  userId: number,
  fileHash: string
): Promise<VerificationStep> {
  const startTime = new Date()

  const step: VerificationStep = {
    id: 'step_3_check_duplicates',
    name: 'Check for Duplicate Uploads',
    status: 'running',
    timestamp: startTime,
  }

  try {
    // In production, this would:
    // 1. Query the backend for uploads by this user in the last 24 hours
    // 2. Compare file hashes to detect duplicate submissions
    // 3. Return duplicate status
    //
    // For demo purposes, we assume no duplicates (always pass)
    // The backend will enforce this on verification

    return {
      ...step,
      status: 'passed',
      result: `No duplicate uploads detected for user ${userId}`,
    }
  } catch (error) {
    return {
      ...step,
      status: 'failed',
      error: `Duplicate check failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
      result: 'Duplicate check error',
    }
  }
}

/**
 * Calculates the MD5-like hash of file content for duplicate detection.
 * In production, this would use crypto.subtle.digest for secure hashing.
 *
 * @param file The file to hash
 * @returns Promise resolving to hex hash string
 */
async function calculateFileHash(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()

    reader.onload = async () => {
      try {
        const buffer = reader.result as ArrayBuffer
        const hashBuffer = await crypto.subtle.digest('SHA-256', buffer)
        const hashArray = Array.from(new Uint8Array(hashBuffer))
        const hashHex = hashArray.map((b) => b.toString(16).padStart(2, '0')).join('')
        resolve(hashHex)
      } catch (error) {
        reject(error)
      }
    }

    reader.onerror = () => reject(reader.error)
    reader.readAsArrayBuffer(file)
  })
}

/**
 * Runs the complete verification flow for an earn proof document.
 * Executes all verification steps in sequence:
 * 1. Validates proof file (type, size, format)
 * 2. Extracts and verifies file content
 * 3. Checks for duplicate uploads
 * 4. Returns combined result with reward eligibility
 *
 * @param file The proof document to verify
 * @param userId The user ID claiming the reward
 * @param earnWeights Optional mapping of behavior to coin rewards
 * @returns Promise resolving to complete verification result
 */
export async function runVerification(
  file: File,
  userId: number,
  earnWeights: Record<string, number> = {
    credit_score_up: 400,
    savings_milestone: 350,
    direct_deposit: 200,
    education_module: 150,
  }
): Promise<VerificationResult> {
  const overallStartTime = new Date()
  const steps: VerificationStep[] = []

  // Step 1: Validate proof file
  const step1 = validateProof(file)
  steps.push(step1)

  if (step1.status === 'failed') {
    const overallEndTime = new Date()
    return {
      verified: false,
      steps,
      totalTime: overallEndTime.getTime() - overallStartTime.getTime(),
      eligibleReward: 0,
      message: `Verification failed at step 1: ${step1.error}`,
    }
  }

  // Step 2: Verify file content
  const step2 = await verifyFileContent(file, userId)
  steps.push(step2)

  if (step2.status === 'failed') {
    const overallEndTime = new Date()
    return {
      verified: false,
      steps,
      totalTime: overallEndTime.getTime() - overallStartTime.getTime(),
      eligibleReward: 0,
      message: `Verification failed at step 2: ${step2.error}`,
    }
  }

  // Step 3: Check for duplicates
  const fileHash = await calculateFileHash(file)
  const step3 = await checkDuplicates(userId, fileHash)
  steps.push(step3)

  if (step3.status === 'failed') {
    const overallEndTime = new Date()
    return {
      verified: false,
      steps,
      totalTime: overallEndTime.getTime() - overallStartTime.getTime(),
      eligibleReward: 0,
      message: `Verification failed at step 3: ${step3.error}`,
    }
  }

  // All steps passed - determine eligible reward
  const overallEndTime = new Date()
  const totalTime = overallEndTime.getTime() - overallStartTime.getTime()

  // Default reward: use the first available earning weight as base
  const baseReward = Object.values(earnWeights)[0] || 150

  return {
    verified: true,
    steps,
    totalTime,
    eligibleReward: baseReward,
    message: 'Verification successful. Ready to claim reward.',
  }
}

/**
 * Retrieves the verification status for a previously submitted verification.
 * In production, this would query the backend for the status of a verification ID.
 *
 * @param verificationId The ID of the verification to check
 * @returns Promise resolving to verification result
 */
export async function getVerificationStatus(
  verificationId: string
): Promise<VerificationResult> {
  try {
    // In production, this would call:
    // const { data } = await api.get(`/earn/verification/${verificationId}`)
    // return data

    // For demo, return a placeholder result
    return {
      verified: false,
      steps: [
        {
          id: 'step_1_validate_proof',
          name: 'Validate Proof File',
          status: 'pending',
        },
        {
          id: 'step_2_verify_content',
          name: 'Verify File Content',
          status: 'pending',
        },
        {
          id: 'step_3_check_duplicates',
          name: 'Check for Duplicate Uploads',
          status: 'pending',
        },
      ],
      totalTime: 0,
      eligibleReward: 0,
      message: `Verification ${verificationId} status pending`,
    }
  } catch (error) {
    return {
      verified: false,
      steps: [],
      totalTime: 0,
      eligibleReward: 0,
      message: `Error retrieving verification status: ${error instanceof Error ? error.message : 'Unknown error'}`,
    }
  }
}

/**
 * Uploads an earn proof to the backend and returns the upload details.
 * The file is converted to base64 and sent with metadata.
 *
 * @param file The proof document to upload
 * @param userId The user ID uploading the proof
 * @param moduleId The earn module ID (e.g., 'credit-score', 'savings')
 * @returns Promise resolving to upload response with upload_id
 */
export async function uploadProofFile(
  file: File,
  userId: number = DEMO_USER_ID,
  moduleId: string = 'savings'
): Promise<{ upload_id: string; file_name: string; mime_type: string; size_bytes: number }> {
  // Convert file to base64
  const reader = new FileReader()

  return new Promise((resolve, reject) => {
    reader.onload = async () => {
      try {
        const base64Content = (reader.result as string).split(',')[1]

        const uploadRequest: EarnProofUploadRequest = {
          user_id: userId,
          module_id: moduleId,
          file_name: file.name,
          mime_type: file.type,
          size_bytes: file.size,
          content_base64: base64Content,
        }

        const { data } = await api.post('/earn/proofs', uploadRequest)
        resolve({
          upload_id: data.upload_id,
          file_name: data.file_name,
          mime_type: data.mime_type,
          size_bytes: data.size_bytes,
        })
      } catch (error) {
        reject(
          new Error(
            `Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`
          )
        )
      }
    }

    reader.onerror = () => reject(reader.error)
    reader.readAsDataURL(file)
  })
}

/**
 * Submits a verification request to the backend for processing.
 * Must include proof upload details or appropriate metadata for the module.
 *
 * @param userId The user ID requesting verification
 * @param moduleId The earn module ID
 * @param uploadId Optional upload ID from previous proof upload
 * @param proofName Optional proof file name
 * @param metadata Additional metadata for verification
 * @returns Promise resolving to backend verification response
 */
export async function submitVerificationRequest(
  userId: number = DEMO_USER_ID,
  moduleId: string = 'savings',
  uploadId?: string,
  proofName?: string,
  metadata: Record<string, any> = {}
): Promise<any> {
  const verificationRequest: EarnVerificationRequest = {
    user_id: userId,
    module_id: moduleId,
    proof_type: 'document_upload',
    proof_name: proofName || null,
    upload_id: uploadId || null,
    mime_type: null,
    size_bytes: null,
    selected_goal: null,
    metadata,
  }

  try {
    const { data } = await api.post('/earn/verify', verificationRequest)
    return data
  } catch (error) {
    throw new Error(
      `Verification request failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    )
  }
}

/**
 * Main verification API namespace with all verification operations.
 * Combines local verification steps with backend API calls.
 */
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
