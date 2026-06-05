# Claude Code Skills for DevRev

このディレクトリには、DevRevプラットフォームを操作するためのClaude Codeスキルが含まれています。

## スキル一覧

（準備中）

## スキルの構成

各スキルは以下の構造を持ちます:

```text
skills/[skill-name]/
├── skill.md              # スキル定義（Claude Code用）
├── src/
│   └── index.ts         # メインロジック
├── package.json
└── README.md
```

## 開発ガイド

### 新しいスキルの作成

```bash
# テンプレートからコピー
cp -r templates/skill-template skills/my-new-skill
cd skills/my-new-skill

# 依存関係のインストール
npm install

# 開発
npm run dev
```

### スキルのテスト

```bash
# スキルディレクトリで
npm test
```

### スキルの公開

```bash
# npm publish または GitHub経由で配布
```

## 共通ライブラリの使用

DevRev APIクライアントなど、共通ライブラリは `lib/` ディレクトリにあります:

```typescript
import { DevRevClient } from '../../lib/devrev-client'
import { AuthManager } from '../../lib/auth'
```

## 参考リンク

- [DevRev Developer Docs](https://developer.devrev.ai/about/for-developers)
- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
