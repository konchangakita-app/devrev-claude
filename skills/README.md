# DevRev Skills Development Guide

## ⚠️ 重要: スキル開発ルール

**開発場所**: `~/.claude/skills/devrev-xxx/`（マスター）  
**リポジトリ**: `./devrev-xxx/`（コピー・公開用）

### 基本方針

このリポジトリは **公開用・バックアップ用** です。実際の開発は `~/.claude/skills/` で行います。

**なぜこの方針なのか**:
- `~/.claude/skills/` で開発すれば、Claude Code が即座に読み込み、すぐにテスト可能
- リポジトリ側を直接編集すると、マスターとの不整合が発生し混乱の元
- 一元管理でシンプルに保つ

---

## 📋 開発ワークフロー

### Step 1: マスターで開発

```bash
# 作業ディレクトリを確認（MUST）
pwd
# → /Users/username/.claude/skills/devrev-xxx であることを確認

# もし違う場所にいたら即座に移動
cd ~/.claude/skills/devrev-xxx

# 開発・編集・テスト
```

### Step 2: セキュリティチェック（公開前必須）

スキルを公開する前に、以下の項目を必ず確認してください。

#### 2.1 ハードコードされた秘密情報チェック

```bash
# JWT トークンパターンをチェック
grep -r "eyJ" ~/.claude/skills/devrev-xxx/ 2>/dev/null

# API キー、シークレット等をチェック
grep -rE "(api[_-]?key|secret|password|token.*=.*['\"])" \
  ~/.claude/skills/devrev-xxx/ \
  --include="*.py" --include="*.md" --include="*.html" --include="*.js" --include="*.ts"
```

**確認ポイント**:
- ✅ 実際のトークン・APIキーが含まれていないか
- ✅ 検出されたのが例示・サンプルのみか
- ✅ ドキュメント内の例も完全なトークンではないか

#### 2.2 個人情報チェック

```bash
# 個人情報をチェック（ユーザー名、パス等）
grep -rn "skon\|konchangakita\|/Users/[^u]" \
  ~/.claude/skills/devrev-xxx/ 2>/dev/null | grep -v "username"
```

**確認ポイント**:
- ✅ 個人のユーザー名が含まれていないか
- ✅ 固有のパス（`/Users/skon/` 等）が含まれていないか
- ✅ 例示は汎用的な表現（`/Users/username/`）になっているか

#### 2.3 ファイルパーミッションチェック

```bash
# パーミッションを確認
ls -laR ~/.claude/skills/devrev-xxx/
```

**確認ポイント**:
- ✅ スクリプトは 644 または 755（リポジトリでは実行権限不要なので 644 推奨）
- ✅ ディレクトリは 755
- ✅ 機密ファイルは含まれていないか

#### 2.4 依存関係チェック

```bash
# Python の場合
grep -rn "^import\|^from" ~/.claude/skills/devrev-xxx/scripts/*.py | \
  grep -v "^import sys\|^import os\|^import json\|^from pathlib"

# Node.js の場合
cat ~/.claude/skills/devrev-xxx/package.json 2>/dev/null | jq '.dependencies'
```

**確認ポイント**:
- ✅ 外部依存は明示されているか
- ✅ 標準ライブラリのみの場合、その旨を記載しているか
- ✅ requirements.txt または package.json に記載されているか

#### 2.5 セキュリティベストプラクティス確認

**チェックリスト**:
- [ ] トークン・秘密情報は暗号化保存されているか
- [ ] ユーザーローカルディレクトリ（`~/.config/` 等）に保存されているか
- [ ] チャット・ログに秘密情報が露出しない設計か
- [ ] タイムアウト機能があるか（Web GUI等）
- [ ] 適切なエラーハンドリングがあるか

#### 2.6 ドキュメント品質チェック

**チェックリスト**:
- [ ] SKILL.md に frontmatter（name, version, description）があるか
- [ ] 使用例が記載されているか（最低3つ推奨）
- [ ] エラーハンドリングが記載されているか
- [ ] 依存関係が明記されているか
- [ ] トラブルシューティングセクションがあるか

### Step 3: リポジトリへコピー

```bash
# コピー前に差分確認（既存の場合）
diff -r ~/.claude/skills/devrev-xxx \
  ~/DevRev/develop/repo/konchangakita/devrev-claude/skills/devrev-xxx

# コピー実行
cp -r ~/.claude/skills/devrev-xxx \
  ~/DevRev/develop/repo/konchangakita/devrev-claude/skills/

# コピー確認
ls -la ~/DevRev/develop/repo/konchangakita/devrev-claude/skills/devrev-xxx/
```

### Step 4: Git差分確認（CRITICAL）

```bash
cd ~/DevRev/develop/repo/konchangakita/devrev-claude

# Git ステータス確認
git status

# 差分を目視確認（MUST）
git diff skills/devrev-xxx/

# 意図しないファイルチェック
git diff --name-only

# 禁止ファイルパターンチェック
find skills/devrev-xxx/ -type f \( \
  -name ".env*" -o \
  -name "*.log" -o \
  -name "node_modules" -o \
  -name ".DS_Store" -o \
  -name "vault.json" -o \
  -name "deploy.env" \
\) 2>/dev/null
```

**含まれてはいけないもの**:
- ❌ `.env` ファイル（環境変数・秘密情報）
- ❌ `.env.local`, `deploy.env` 等
- ❌ `node_modules/`
- ❌ `.DS_Store`
- ❌ ログファイル（`*.log`）
- ❌ 認証トークン、API キー
- ❌ JWT パターン（`eyJ...` で始まる完全なトークン）
- ❌ vault.json（暗号化されたトークンストレージ）

### Step 5: ステージング

```bash
# ステージング
git add skills/devrev-xxx/

# ステージング後も差分確認（MUST）
git diff --cached --stat
git diff --cached skills/devrev-xxx/SKILL.md | head -50
```

### Step 6: コミット

```bash
# Conventional Commits 形式でコミット
git commit -m "$(cat <<'EOF'
feat: add devrev-xxx skill

スキルの概要（1-2行）

主な機能:
- 機能1
- 機能2
- 機能3

セキュリティ:
- セキュリティ対策1
- セキュリティ対策2

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

### Step 7: プッシュ

```bash
# プッシュ前の最終確認
git log --oneline -1
git show --stat

# プッシュ
git push
```

---

## 🚫 禁止事項（MUST NOT）

1. ❌ リポジトリ側（`./skills/devrev-xxx/`）を直接編集しない
2. ❌ リポジトリからスキルを読み込まない（常に `~/.claude/skills/` から読む）
3. ❌ 双方向同期しない（片方向コピーのみ）
4. ❌ スキル名の `devrev-` プレフィックスを省略しない
5. ❌ セキュリティチェックをスキップしない

---

## 📐 命名規則

### スキル名
- **必須プレフィックス**: `devrev-`
- **形式**: `devrev-<機能名>`
- **例**: `devrev-pat-manager`, `devrev-workflow-action`, `devrev-presentation-web`

### ファイル名
- Python スクリプト: `snake_case.py`
- Markdown ドキュメント: `kebab-case.md`
- 設定ファイル: `.env.example`, `config.yaml`

---

## 🔄 同期のタイミング

以下の場合にのみ、`~/.claude/skills/` → リポジトリへコピー:
- ✅ スキルが完成した（動作確認済み）
- ✅ 重要な変更をコミットする前
- ✅ 公開・共有する前
- ❌ 開発途中での頻繁な同期は不要

---

## 📝 バージョン管理

### バージョン番号
SKILL.md の frontmatter に記載:

```yaml
---
name: devrev-xxx
version: 1.0.0  # セマンティックバージョニング
description: >
  スキルの説明
---
```

### バージョン更新ルール
- **Major (1.0.0 → 2.0.0)**: 破壊的変更
- **Minor (1.0.0 → 1.1.0)**: 機能追加（後方互換性あり）
- **Patch (1.0.0 → 1.0.1)**: バグ修正

---

## 📚 ファイル構造例

```
devrev-xxx/
├── SKILL.md                    # スキル定義（必須）
├── README.md                   # 使い方ガイド（任意）
├── scripts/                    # 実行スクリプト
│   ├── main.py
│   └── utils.py
├── templates/                  # テンプレートファイル
│   └── template.html
├── static/                     # 静的ファイル（CSS, JS等）
│   ├── style.css
│   └── script.js
├── references/                 # 参考資料
│   └── api-reference.md
├── tests/                      # テスト（推奨）
│   └── test_main.py
├── .env.example                # 環境変数テンプレート
├── requirements.txt            # Python依存関係（該当する場合）
├── package.json                # Node.js依存関係（該当する場合）
└── evaluation_results.json     # 評価結果（任意）
```

---

## 🔍 トラブルシューティング

### スキルが読み込まれない

```bash
# スキルの場所を確認
ls -la ~/.claude/skills/devrev-xxx/

# SKILL.md の frontmatter を確認
head -10 ~/.claude/skills/devrev-xxx/SKILL.md

# Claude Code を再起動
# （IDEの場合は拡張機能をリロード）
```

### リポジトリとマスターの不整合

```bash
# マスターを正として、リポジトリ側を削除して再コピー
rm -rf ~/DevRev/develop/repo/konchangakita/devrev-claude/skills/devrev-xxx
cp -r ~/.claude/skills/devrev-xxx \
  ~/DevRev/develop/repo/konchangakita/devrev-claude/skills/
```

---

## 📖 参考リンク

- [DevRev API ドキュメント](https://docs.devrev.ai/)
- [Claude Code ドキュメント](https://docs.anthropic.com/claude/docs/claude-code)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## ✅ チェックリスト（新規スキル作成・更新時）

### 開発フェーズ
- [ ] `~/.claude/skills/devrev-xxx/` で開発
- [ ] SKILL.md に frontmatter 記載（name, version, description）
- [ ] 動作確認完了（実際にスキルを実行してテスト）

### セキュリティチェックフェーズ
- [ ] ハードコードされた秘密情報チェック（JWT, API key等）
- [ ] 個人情報チェック（ユーザー名、パス等）
- [ ] ファイルパーミッションチェック
- [ ] 依存関係チェック
- [ ] セキュリティベストプラクティス確認
- [ ] ドキュメント品質チェック

### コピー・コミット前フェーズ
- [ ] 作業ディレクトリ確認（`pwd` が `~/.claude/skills/devrev-xxx` であること）
- [ ] コピー前に差分確認（`diff -r ...`）
- [ ] リポジトリへコピー（`cp -r ...`）
- [ ] Git ステータス確認（`git status`）
- [ ] **Git 差分を目視確認**（`git diff skills/devrev-xxx/`）
- [ ] 禁止ファイルが含まれていないか確認（.env, トークン, node_modules 等）
- [ ] ステージング（`git add skills/devrev-xxx/`）
- [ ] **ステージング後も差分確認**（`git diff --cached`）
- [ ] コミットメッセージ作成（Conventional Commits 形式）
- [ ] コミット（`git commit -m "..."`）
- [ ] プッシュ（`git push`）

---

## 📧 サポート

質問・問題があれば、Issue を作成してください。
