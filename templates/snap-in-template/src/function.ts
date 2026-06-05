import { DevRevClient } from '@devrev-claude/devrev-client'

interface FunctionInput {
  event: {
    payload: unknown
    context: {
      dev_oid: string
      source_id: string
    }
  }
}

interface FunctionOutput {
  status: 'success' | 'error'
  message?: string
  data?: unknown
}

export async function run(input: FunctionInput): Promise<FunctionOutput> {
  try {
    const { event } = input
    const { payload, context } = event

    console.log('Function triggered with payload:', payload)
    console.log('Context:', context)

    // Your function logic here
    // Example: Initialize DevRev client with service account token
    const token = process.env.DEVREV_SERVICE_ACCOUNT_TOKEN
    if (!token) {
      throw new Error('Service account token not found')
    }

    const client = new DevRevClient({ apiToken: token })

    // Do something with the event
    // ...

    return {
      status: 'success',
      message: 'Function executed successfully',
    }
  } catch (error) {
    console.error('Function error:', error)
    return {
      status: 'error',
      message: error instanceof Error ? error.message : 'Unknown error',
    }
  }
}
