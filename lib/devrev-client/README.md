# @devrev-claude/devrev-client

DevRev APIクライアントライブラリ

## インストール

```bash
npm install @devrev-claude/devrev-client
```

## 使い方

```typescript
import { DevRevClient } from '@devrev-claude/devrev-client'

const client = new DevRevClient({
  apiToken: process.env.DEVREV_API_TOKEN,
})

// Workの取得
const work = await client.getWork('WORK-123')

// Workの作成
const newWork = await client.createWork({
  type: 'issue',
  title: 'New Issue',
  body: 'Issue description',
})
```

## API

### `new DevRevClient(config)`

- `config.apiToken`: DevRev API token (必須)
- `config.baseURL`: API base URL (オプション、デフォルト: `https://api.devrev.ai`)

### Works API

- `getWork(workId: string)`: Workを取得
- `listWorks(params?)`: Workリストを取得
- `createWork(data)`: Workを作成
- `updateWork(workId, data)`: Workを更新

### Dev Users API

- `getCurrentUser()`: 現在のユーザー情報を取得

### Generic

- `request(method, endpoint, data?)`: 任意のAPIリクエスト

## 参考

- [DevRev API Documentation](https://developer.devrev.ai/api-reference)
