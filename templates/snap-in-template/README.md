# Snap-in Template

This is a template for creating new DevRev Snap-ins.

## Getting Started

1. Copy this template:
   ```bash
   cp -r templates/snap-in-template snap-ins/my-snap-in
   cd snap-ins/my-snap-in
   ```

2. Update `manifest.yaml`:
   - Change `name` and `description`
   - Define functions and automations
   - Configure event sources

3. Update `package.json`:
   - Change `name` to `@devrev-claude/your-snap-in-name`
   - Update `description`

4. Implement your logic:
   - `src/function.ts` - Custom functions
   - `src/automation.ts` - Event-driven automations

5. Build and deploy:
   ```bash
   npm install
   npm run build
   npm run deploy
   ```

## Structure

```text
snap-in-template/
├── manifest.yaml      # Snap-in definition
├── package.json       # Package configuration
├── src/
│   ├── function.ts   # Function implementation
│   └── automation.ts # Automation implementation
└── README.md         # This file
```

## Development

### Local Testing

```bash
npm run build
npm test
```

### Deployment

```bash
# Deploy to DevRev
npm run deploy

# Or use DevRev CLI directly
devrev snap-in deploy
```

## Configuration

Set environment variables in the DevRev console:
- `DEVREV_SERVICE_ACCOUNT_TOKEN` - Service account token (automatically provided)

## Event Handling

The template includes handlers for:
- `work.created` - When a work item is created
- `work.updated` - When a work item is updated

Add more event handlers in `manifest.yaml` and `src/automation.ts`.

## References

- [DevRev Snap-in Documentation](https://developer.devrev.ai/snapin-development)
- [DevRev API Reference](https://developer.devrev.ai/api-reference)
- [Event Types](https://developer.devrev.ai/snapin-development/event-sources)
