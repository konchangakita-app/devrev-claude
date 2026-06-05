import { DevRevClient } from '@devrev-claude/devrev-client'

interface AutomationInput {
  event_type: string
  payload: {
    work?: {
      id: string
      type: string
      title?: string
    }
  }
  context: {
    dev_oid: string
    source_id: string
  }
}

interface AutomationOutput {
  status: 'success' | 'error'
  message?: string
}

export async function run(input: AutomationInput): Promise<AutomationOutput> {
  try {
    const { event_type, payload, context } = input

    console.log('Automation triggered:', event_type)
    console.log('Payload:', payload)
    console.log('Context:', context)

    // Initialize DevRev client
    const token = process.env.DEVREV_SERVICE_ACCOUNT_TOKEN
    if (!token) {
      throw new Error('Service account token not found')
    }

    const client = new DevRevClient({ apiToken: token })

    // Handle different event types
    switch (event_type) {
      case 'work.created':
        await handleWorkCreated(client, payload.work)
        break
      case 'work.updated':
        await handleWorkUpdated(client, payload.work)
        break
      default:
        console.log('Unhandled event type:', event_type)
    }

    return {
      status: 'success',
      message: 'Automation completed',
    }
  } catch (error) {
    console.error('Automation error:', error)
    return {
      status: 'error',
      message: error instanceof Error ? error.message : 'Unknown error',
    }
  }
}

async function handleWorkCreated(client: DevRevClient, work: unknown) {
  console.log('Handling work created:', work)
  // Your logic here
}

async function handleWorkUpdated(client: DevRevClient, work: unknown) {
  console.log('Handling work updated:', work)
  // Your logic here
}
