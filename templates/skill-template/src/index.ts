import { DevRevClient } from '@devrev-claude/devrev-client'
import { AuthManager } from '@devrev-claude/auth'

export async function execute(args: string[]): Promise<void> {
  // Get authentication
  const auth = new AuthManager()
  const token = await auth.getToken()

  if (!token) {
    throw new Error('No DevRev token found. Please set up authentication first.')
  }

  // Initialize DevRev client
  const client = new DevRevClient({ apiToken: token })

  // Your skill logic here
  console.log('Skill template executed with args:', args)

  // Example: Get current user
  const user = await client.getCurrentUser()
  console.log('Current user:', user)
}

// Main entry point
if (require.main === module) {
  execute(process.argv.slice(2))
    .then(() => process.exit(0))
    .catch(error => {
      console.error('Error:', error)
      process.exit(1)
    })
}
