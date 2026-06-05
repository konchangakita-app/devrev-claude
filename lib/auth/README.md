# @devrev-claude/auth

DevRev認証とPAT（Personal Access Token）管理ライブラリ

## 特徴

- セキュアストレージ（keytar）を使用した安全なトークン保存
- 複数トークンの管理
- デフォルトトークンの設定

## インストール

```bash
npm install @devrev-claude/auth
```

## 使い方

```typescript
import { AuthManager } from '@devrev-claude/auth'

const auth = new AuthManager()

// トークンを保存
await auth.saveToken('my-token', 'your-pat-token-here', true)

// トークンを取得
const token = await auth.getToken() // デフォルトトークン
const namedToken = await auth.getToken('my-token') // 名前付きトークン

// トークンをリスト表示
const tokens = auth.listTokens()
console.log(tokens)

// デフォルトトークンを変更
auth.setDefaultToken('another-token')

// トークンを削除
await auth.deleteToken('my-token')
```

## API

### `saveToken(name, token, setDefault?)`

トークンを保存します。

- `name`: トークン名
- `token`: PAT トークン文字列
- `setDefault`: デフォルトトークンとして設定するか（オプション）

### `getToken(name?)`

トークンを取得します。

- `name`: トークン名（省略時はデフォルトトークン）

### `listTokens()`

保存されているトークンのリストを返します（トークン値自体は含まれません）。

### `deleteToken(name)`

指定したトークンを削除します。

### `setDefaultToken(name)`

デフォルトトークンを設定します。

## セキュリティ

- トークンはOSのセキュアストレージ（macOS Keychain、Windows Credential Manager、Linux Secret Service）に保存されます
- 設定ファイル（`~/.devrev/config.json`）にはトークン値は保存されません
