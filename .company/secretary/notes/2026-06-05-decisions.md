---
date: "2026-06-05"
type: decisions
---

# 意思決定ログ - 2026-06-05

## スキル開発の基本方針

**決定事項**: DevRev関連のスキルは何でも作っていく

**背景**:
- 昨日のタスク「基本方針を決定」の結論
- DevRevプラットフォームに特化したスキル集として展開

**含まれる範囲**:
- DevRev API連携
- Snap-in開発支援
- ワークフロー操作
- PAT（Personal Access Token）管理
- Issue/Work管理
- その他DevRevエコシステムに関連するあらゆる機能

**次のアクション**:
1. プロジェクト構造の実装（skills/, lib/, templates/）
2. docker-compose.yml作成
3. 最初のスキル雛形作成

---

## フォルダ構成の決定

**決定事項**: 案A（トップレベルでスキルとSnap-inを分離）を採用

**構成**:

```text
devrev-claude/
├── skills/           # Claude Codeスキル
├── snap-ins/         # DevRev Snap-in
├── lib/              # 共通ライブラリ
├── templates/        # テンプレート（skill/snap-in）
├── docs/             # ドキュメント
└── docker-compose.yml
```

**理由**:

- スキルとSnap-inの責務が明確に分離
- 独立したデプロイ・公開が可能
- 共通ライブラリを両方から参照できる
- シンプルで理解しやすい

**時刻**: 2026-06-05 追記
