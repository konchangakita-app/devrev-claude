# DevRev Snap-ins

このディレクトリには、DevRevプラットフォーム上で動作するSnap-inが含まれています。

## Snap-in一覧

（準備中）

## Snap-inの構成

各Snap-inは以下の構造を持ちます:

```text
snap-ins/[snap-in-name]/
├── manifest.yaml        # Snap-in定義
├── src/
│   ├── function.ts     # 関数実装
│   └── automation.ts   # 自動化ロジック
├── package.json
└── README.md
```

## 開発ガイド

### 新しいSnap-inの作成

```bash
# テンプレートからコピー
cp -r templates/snap-in-template snap-ins/my-snap-in
cd snap-ins/my-snap-in

# 依存関係のインストール
npm install

# 開発
npm run dev
```

### Snap-inのテスト

```bash
# Snap-inディレクトリで
npm test
```

### Snap-inのデプロイ

```bash
# DevRev CLIを使用
devrev snap-in deploy
```

## 共通ライブラリの使用

DevRev APIクライアントなど、共通ライブラリは `lib/` ディレクトリにあります:

```typescript
import { DevRevClient } from '../../lib/devrev-client'
import { AuthManager } from '../../lib/auth'
```

## Snap-inの種類

### Custom Functions

カスタム関数として実装するSnap-in。

### Automations

イベント駆動の自動化処理。

### Workflow Actions

ワークフロー内で実行されるアクション。

## 参考リンク

- [DevRev Snap-in Documentation](https://developer.devrev.ai/snapin-development)
- [DevRev API Reference](https://developer.devrev.ai/api-reference)
