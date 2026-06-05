# devrev-claude

DevRev platform向けのClaude Code スキル集

## 概要

このリポジトリは、DevRevプラットフォームで使用できるClaude Codeスキルを開発・公開するプロジェクトです。

## DevRev 公式ドキュメント

- **開発者向けドキュメント**: [DevRev Developer Docs](https://developer.devrev.ai/about/for-developers)
- DevRev APIの仕様、Snap-inの開発方法、ベストプラクティスなどはこちらを参照してください

## プロジェクト構成

```text
devrev-claude/
├── README.md
├── package.json            # モノレポ設定
├── tsconfig.json           # TypeScript設定
├── docker-compose.yml      # 開発環境
├── skills/                 # Claude Codeスキル集
│   └── [skill-name]/
├── snap-ins/               # DevRev Snap-in集
│   └── [snap-in-name]/
├── lib/                    # 共通ライブラリ
│   ├── devrev-client/      # DevRev APIクライアント
│   ├── auth/               # 認証・PAT管理
│   └── utils/              # 共通ユーティリティ
├── templates/              # テンプレート
│   ├── skill-template/     # スキル雛形
│   └── snap-in-template/   # Snap-in雛形
└── docs/                   # ドキュメント
    ├── skills.md
    └── snap-ins.md
```

## 開発方針

- **環境**: docker-composeベースの開発環境
- **ポート**: 30xx番台は使用しない
- **公開**: GitHubでpublicリポジトリとして管理
- **ライセンス**: MIT License

## 開発環境のセットアップ

```bash
# リポジトリのクローン
git clone https://github.com/konchangakita/devrev-claude.git
cd devrev-claude

# 依存関係のインストール
npm install

# Docker環境の起動
npm run dev
```

### 新しいスキルの作成

```bash
# テンプレートからコピー
cp -r templates/skill-template skills/my-skill
cd skills/my-skill

# 実装
# - skill.md を編集
# - src/index.ts を実装
# - package.json を更新

npm install
npm run build
```

### 新しいSnap-inの作成

```bash
# テンプレートからコピー
cp -r templates/snap-in-template snap-ins/my-snap-in
cd snap-ins/my-snap-in

# 実装
# - manifest.yaml を編集
# - src/function.ts, src/automation.ts を実装
# - package.json を更新

npm install
npm run build
npm run deploy
```

## スキル一覧

詳細は [docs/skills.md](docs/skills.md) を参照してください。

（準備中）

## Snap-in一覧

詳細は [docs/snap-ins.md](docs/snap-ins.md) を参照してください。

（準備中）

## 共通ライブラリ

- **[@devrev-claude/devrev-client](lib/devrev-client/)** - DevRev APIクライアント
- **[@devrev-claude/auth](lib/auth/)** - 認証・PAT管理
- **[@devrev-claude/utils](lib/utils/)** - 共通ユーティリティ関数

## コントリビューション

Issue、Pull Requestを歓迎します。

## ライセンス

MIT License
