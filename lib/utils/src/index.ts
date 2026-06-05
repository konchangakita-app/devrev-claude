/**
 * Format DevRev Work ID
 */
export function formatWorkId(id: string): string {
  return id.toUpperCase()
}

/**
 * Parse DevRev Work ID
 */
export function parseWorkId(id: string): { prefix: string; number: string } | null {
  const match = id.match(/^([A-Z]+)-(\d+)$/)
  if (!match) return null
  return { prefix: match[1], number: match[2] }
}

/**
 * Validate DevRev Work ID format
 */
export function isValidWorkId(id: string): boolean {
  return /^[A-Z]+-\d+$/.test(id)
}

/**
 * Format date to ISO string
 */
export function formatDate(date: Date | string): string {
  return new Date(date).toISOString()
}

/**
 * Sleep utility
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * Retry utility
 */
export async function retry<T>(
  fn: () => Promise<T>,
  options: {
    maxRetries?: number
    delay?: number
    backoff?: boolean
  } = {}
): Promise<T> {
  const { maxRetries = 3, delay = 1000, backoff = true } = options
  let lastError: Error

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error as Error
      if (i < maxRetries - 1) {
        const waitTime = backoff ? delay * Math.pow(2, i) : delay
        await sleep(waitTime)
      }
    }
  }

  throw lastError!
}

/**
 * Chunk array into smaller arrays
 */
export function chunk<T>(array: T[], size: number): T[][] {
  const chunks: T[][] = []
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size))
  }
  return chunks
}
