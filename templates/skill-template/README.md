# Skill Template

This is a template for creating new DevRev Claude skills.

## Getting Started

1. Copy this template:
   ```bash
   cp -r templates/skill-template skills/my-new-skill
   cd skills/my-new-skill
   ```

2. Update `package.json`:
   - Change `name` to `@devrev-claude/your-skill-name`
   - Update `description`

3. Update `skill.md`:
   - Add skill description
   - Define when to use
   - Document workflow

4. Implement your logic in `src/index.ts`

5. Test your skill:
   ```bash
   npm install
   npm run build
   npm test
   ```

## Structure

```text
skill-template/
├── skill.md           # Skill definition for Claude Code
├── package.json       # Package configuration
├── src/
│   └── index.ts      # Main implementation
└── README.md         # This file
```

## Using Common Libraries

```typescript
import { DevRevClient } from '@devrev-claude/devrev-client'
import { AuthManager } from '@devrev-claude/auth'
import { formatWorkId, retry } from '@devrev-claude/utils'
```

## References

- [DevRev Developer Docs](https://developer.devrev.ai/about/for-developers)
- [Claude Code Skills Guide](https://docs.anthropic.com/claude-code/skills)
