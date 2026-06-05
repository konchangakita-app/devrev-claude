# @devrev-claude/utils

共通ユーティリティ関数集

## インストール

```bash
npm install @devrev-claude/utils
```

## 使い方

```typescript
import { formatWorkId, isValidWorkId, retry } from '@devrev-claude/utils'

// Work ID操作
const formatted = formatWorkId('work-123') // 'WORK-123'
const valid = isValidWorkId('WORK-123') // true

// リトライ処理
const result = await retry(
  async () => {
    return await someApiCall()
  },
  { maxRetries: 3, delay: 1000, backoff: true }
)
```

## API

### Work ID関連

- `formatWorkId(id: string)`: Work IDを大文字フォーマットに変換
- `parseWorkId(id: string)`: Work IDをprefix/numberに分解
- `isValidWorkId(id: string)`: Work IDの形式検証

### ユーティリティ

- `formatDate(date: Date | string)`: 日付をISO文字列に変換
- `sleep(ms: number)`: 指定時間待機
- `retry(fn, options)`: リトライ処理
- `chunk(array, size)`: 配列を指定サイズに分割
