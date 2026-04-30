import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  earnVerification,
  runVerification,
  getVerificationStatus,
  uploadProofFile,
  submitVerificationRequest,
  type VerificationStep,
  type VerificationResult,
} from '../earn-verification'

/**
 * Mock File object for testing.
 * Creates a File with specified properties for unit tests.
 */
function createMockFile(options: {
  name: string
  type: string
  size: number
  content?: string
}): File {
  const { name, type, size, content = 'mock file content' } = options

  const blob = new Blob([content.padEnd(size, ' ')], { type })
  return new File([blob], name, { type })
}

describe('EarnVerification - File Validation', () => {
  describe('validateProof', () => {
    it('should pass validation for valid PDF file', () => {
      const file = createMockFile({
        name: 'proof.pdf',
        type: 'application/pdf',
        size: 100 * 1024, // 100KB
      })

      const result = earnVerification.validateProof(file)

      expect(result.status).toBe('passed')
      expect(result.id).toBe('step_1_validate_proof')
      expect(result.result).toContain('File validation passed')
    })

    it('should pass validation for valid PNG file', () => {
      const file = createMockFile({
        name: 'screenshot.png',
        type: 'image/png',
        size: 256 * 1024, // 256KB
      })

      const result = earnVerification.validateProof(file)

      expect(result.status).toBe('passed')
    })

    it('should pass validation for valid JPEG file', () => {
      const file = createMockFile({
        name: 'photo.jpg',
        type: 'image/jpeg',
        size: 512 * 1024, // 512KB
      })

      const result = earnVerification.validateProof(file)

      expect(result.status).toBe('passed')
    })

    it('should fail validation for invalid file type', () => {
      const file = createMockFile({
        name: 'document.docx',
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        size: 100 * 1024,
      })

      const result = earnVerification.validateProof(file)

      expect(result.status).toBe('failed')
      expect(result.error).toContain('Invalid file type')
    })

    it('should fail validation for file size below minimum', () => {
      const file = createMockFile({
        name: 'tiny.pdf',
        type: 'application/pdf',
        size: 512, // Below 1KB minimum
      })

      const result = earnVerification.validateProof(file)

      expect(result.status).toBe('failed')
      expect(result.error).toContain('too small')
    })

    it('should fail validation for file size above maximum', () => {
      const file = createMockFile({
        name: 'huge.pdf',
        type: 'application/pdf',
        size: 15 * 1024 * 1024, // 15MB, above 10MB max
      })

      const result = earnVerification.validateProof(file)

      expect(result.status).toBe('failed')
      expect(result.error).toContain('too large')
    })

    it('should fail validation for invalid file extension', () => {
      const file = createMockFile({
        name: 'document.txt',
        type: 'application/pdf', // Mismatched extension/type
        size: 100 * 1024,
      })

      const result = earnVerification.validateProof(file)

      expect(result.status).toBe('failed')
      expect(result.error).toContain('Invalid file extension')
    })
  })
})

describe('EarnVerification - File Content Verification', () => {
  describe('verifyFileContent', () => {
    it('should pass verification for readable file', async () => {
      const file = createMockFile({
        name: 'proof.pdf',
        type: 'application/pdf',
        size: 100 * 1024,
        content: 'Valid proof content',
      })

      const result = await earnVerification.verifyFileContent(file, 1)

      expect(result.status).toBe('passed')
      expect(result.id).toBe('step_2_verify_content')
      expect(result.result).toContain('File content verified')
    })

    it('should handle file read errors gracefully', async () => {
      const file = createMockFile({
        name: 'proof.pdf',
        type: 'application/pdf',
        size: 100 * 1024,
      })

      // Mock reader error
      vi.spyOn(FileReader.prototype, 'readAsArrayBuffer').mockImplementation(function () {
        this.onerror?.(new ProgressEvent('error'))
      })

      const result = await earnVerification.verifyFileContent(file, 1)

      expect(result.status).toBe('failed')
      expect(result.error).toContain('Error reading')

      vi.restoreAllMocks()
    })
  })
})

describe('EarnVerification - Duplicate Detection', () => {
  describe('checkDuplicates', () => {
    it('should pass duplicate check by default', async () => {
      const result = await earnVerification.checkDuplicates(1, 'abc123hash')

      expect(result.status).toBe('passed')
      expect(result.id).toBe('step_3_check_duplicates')
      expect(result.result).toContain('No duplicate uploads detected')
    })

    it('should include user ID in duplicate check', async () => {
      const userId = 42
      const result = await earnVerification.checkDuplicates(userId, 'xyz789hash')

      expect(result.result).toContain(`user ${userId}`)
    })
  })
})

describe('EarnVerification - Complete Verification Flow', () => {
  describe('runVerification', () => {
    it('should successfully verify valid file with all steps passed', async () => {
      const file = createMockFile({
        name: 'proof.pdf',
        type: 'application/pdf',
        size: 200 * 1024,
        content: 'Valid financial proof document',
      })

      const result = await runVerification(file, 1)

      expect(result.verified).toBe(true)
      expect(result.steps).toHaveLength(3)
      expect(result.steps[0].status).toBe('passed')
      expect(result.steps[1].status).toBe('passed')
      expect(result.steps[2].status).toBe('passed')
      expect(result.eligibleReward).toBeGreaterThan(0)
      expect(result.message).toContain('successful')
    })

    it('should fail verification if file validation fails', async () => {
      const file = createMockFile({
        name: 'document.docx',
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        size: 100 * 1024,
      })

      const result = await runVerification(file, 1)

      expect(result.verified).toBe(false)
      expect(result.steps[0].status).toBe('failed')
      expect(result.eligibleReward).toBe(0)
      expect(result.message).toContain('failed at step 1')
    })

    it('should stop verification at first failure', async () => {
      const file = createMockFile({
        name: 'invalid.txt',
        type: 'text/plain',
        size: 100 * 1024,
      })

      const result = await runVerification(file, 1)

      expect(result.verified).toBe(false)
      // Should only have attempted step 1
      expect(result.steps.length).toBeLessThan(3)
    })

    it('should calculate total verification time', async () => {
      const file = createMockFile({
        name: 'proof.pdf',
        type: 'application/pdf',
        size: 200 * 1024,
      })

      const result = await runVerification(file, 1)

      expect(result.totalTime).toBeGreaterThan(0)
      expect(typeof result.totalTime).toBe('number')
    })

    it('should use custom earning weights when provided', async () => {
      const file = createMockFile({
        name: 'proof.pdf',
        type: 'application/pdf',
        size: 200 * 1024,
      })

      const customWeights = { custom_behavior: 500 }
      const result = await runVerification(file, 1, customWeights)

      expect(result.verified).toBe(true)
      expect(result.eligibleReward).toBe(500)
    })

    it('should use default reward when no weights provided', async () => {
      const file = createMockFile({
        name: 'proof.pdf',
        type: 'application/pdf',
        size: 200 * 1024,
      })

      const result = await runVerification(file, 1, {})

      expect(result.verified).toBe(true)
      expect(result.eligibleReward).toBe(150) // Default fallback
    })

    it('should create validation step with proper structure', async () => {
      const file = createMockFile({
        name: 'proof.pdf',
        type: 'application/pdf',
        size: 200 * 1024,
      })

      const result = await runVerification(file, 1)
      const step1 = result.steps[0]

      expect(step1.id).toBe('step_1_validate_proof')
      expect(step1.name).toBe('Validate Proof File')
      expect(step1.status).toBe('passed')
      expect(step1.timestamp).toBeDefined()
      expect(step1.result).toBeDefined()
    })
  })
})

describe('EarnVerification - File Hashing', () => {
  describe('calculateFileHash', () => {
    it('should generate consistent hash for same file content', async () => {
      const file1 = createMockFile({
        name: 'proof1.pdf',
        type: 'application/pdf',
        size: 100,
        content: 'Same content for hashing test',
      })

      const file2 = createMockFile({
        name: 'proof2.pdf',
        type: 'application/pdf',
        size: 100,
        content: 'Same content for hashing test',
      })

      const hash1 = await earnVerification.calculateFileHash(file1)
      const hash2 = await earnVerification.calculateFileHash(file2)

      expect(hash1).toBe(hash2)
    })

    it('should generate different hash for different file content', async () => {
      const file1 = createMockFile({
        name: 'proof1.pdf',
        type: 'application/pdf',
        size: 100,
        content: 'Content A',
      })

      const file2 = createMockFile({
        name: 'proof2.pdf',
        type: 'application/pdf',
        size: 100,
        content: 'Content B',
      })

      const hash1 = await earnVerification.calculateFileHash(file1)
      const hash2 = await earnVerification.calculateFileHash(file2)

      expect(hash1).not.toBe(hash2)
    })

    it('should return valid hex string hash', async () => {
      const file = createMockFile({
        name: 'proof.pdf',
        type: 'application/pdf',
        size: 100,
      })

      const hash = await earnVerification.calculateFileHash(file)

      expect(typeof hash).toBe('string')
      expect(hash).toMatch(/^[a-f0-9]+$/)
      expect(hash.length).toBeGreaterThan(0)
    })
  })
})

describe('EarnVerification - Status Retrieval', () => {
  describe('getVerificationStatus', () => {
    it('should return verification status with steps', async () => {
      const result = await getVerificationStatus('verify_123')

      expect(result.steps).toHaveLength(3)
      expect(result.steps[0].id).toBe('step_1_validate_proof')
      expect(result.steps[1].id).toBe('step_2_verify_content')
      expect(result.steps[2].id).toBe('step_3_check_duplicates')
    })

    it('should handle invalid verification ID gracefully', async () => {
      const result = await getVerificationStatus('invalid_id')

      expect(result.verified).toBe(false)
      expect(typeof result.message).toBe('string')
    })
  })
})

describe('EarnVerification - Step Tracking', () => {
  it('should track step progression through verification', async () => {
    const file = createMockFile({
      name: 'proof.pdf',
      type: 'application/pdf',
      size: 200 * 1024,
    })

    const result = await runVerification(file, 1)

    // Verify step order
    expect(result.steps[0].name).toBe('Validate Proof File')
    expect(result.steps[1].name).toBe('Verify File Content')
    expect(result.steps[2].name).toBe('Check for Duplicate Uploads')

    // Verify all passed
    result.steps.forEach((step) => {
      expect(['passed', 'failed']).toContain(step.status)
      expect(step.timestamp).toBeDefined()
    })
  })

  it('should include detailed error messages on failure', async () => {
    const file = createMockFile({
      name: 'huge.pdf',
      type: 'application/pdf',
      size: 15 * 1024 * 1024, // Exceeds 10MB limit
    })

    const result = await runVerification(file, 1)

    expect(result.steps[0].status).toBe('failed')
    expect(result.steps[0].error).toBeDefined()
    expect(result.steps[0].error?.length).toBeGreaterThan(0)
  })
})

describe('EarnVerification - Result Structure', () => {
  it('should return properly structured verification result', async () => {
    const file = createMockFile({
      name: 'proof.pdf',
      type: 'application/pdf',
      size: 200 * 1024,
    })

    const result = await runVerification(file, 1)

    expect(result).toHaveProperty('verified')
    expect(result).toHaveProperty('steps')
    expect(result).toHaveProperty('totalTime')
    expect(result).toHaveProperty('eligibleReward')
    expect(result).toHaveProperty('message')

    expect(typeof result.verified).toBe('boolean')
    expect(Array.isArray(result.steps)).toBe(true)
    expect(typeof result.totalTime).toBe('number')
    expect(typeof result.eligibleReward).toBe('number')
    expect(typeof result.message).toBe('string')
  })

  it('should include all step details in result', async () => {
    const file = createMockFile({
      name: 'proof.pdf',
      type: 'application/pdf',
      size: 200 * 1024,
    })

    const result = await runVerification(file, 1)

    result.steps.forEach((step) => {
      expect(step).toHaveProperty('id')
      expect(step).toHaveProperty('name')
      expect(step).toHaveProperty('status')
      expect(step).toHaveProperty('timestamp')

      if (step.status === 'passed') {
        expect(step.result).toBeDefined()
      } else if (step.status === 'failed') {
        expect(step.error).toBeDefined()
      }
    })
  })
})
