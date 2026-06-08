---
date: 2026-06-08
type: decisions
---

# 意思決定ログ

## 2026-06-08 (月)

### DevRevスキル開発ルール

**決定内容**:
DevRevスキル開発時は、以下のワークフローを厳守する。

**ルール**:
1. **`~/.claude/skills/` を正（マスター）とする**
   - 開発・編集は `~/.claude/skills/devrev-xxx/` で行う
   - Claude Code が実際に読み込む場所なので、すぐにテスト可能

2. **完成したらリポジトリにコピー**
   - `~/.claude/skills/devrev-xxx/` → `このリポジトリ/skills/devrev-xxx/`
   - リポジトリは公開用・バックアップ用として機能

3. **命名規則**:
   - スキル名は `devrev-` プレフィックスを付ける
   - 例: `devrev-pat-manager`, `devrev-workflow-action`

**理由**:
- `~/.claude/skills/` で開発すれば即座にテストできる
- リポジトリは成果物の公開・共有用
- 一元管理が容易（混乱を避ける）

**ワークフロー例**:
```bash
# 1. ~/.claude/skills/ で開発
cd ~/.claude/skills/devrev-new-skill
# 編集・テスト

# 2. 完成したらリポジトリにコピー
cp -r ~/.claude/skills/devrev-new-skill ~/DevRev/develop/repo/konchangakita/devrev-claude/skills/

# 3. コミット・公開
cd ~/DevRev/develop/repo/konchangakita/devrev-claude
git add skills/devrev-new-skill
git commit -m "feat: add devrev-new-skill"
git push
```

**注意事項**:
- リポジトリ側を直接編集しない（混乱の元）
- コピー時は `-r`（再帰的）を使う
- 既存スキル（pat-manager等）は参考実装として活用

---

### DevRevスキル開発ルール（詳細版） - 17:17 追記

#### 1. 禁止事項（MUST NOT）

- ❌ リポジトリ側（`~/DevRev/develop/repo/konchangakita/devrev-claude/skills/`）を直接編集しない
- ❌ リポジトリからスキルを読み込まない（常に `~/.claude/skills/` から読む）
- ❌ 双方向同期しない（片方向コピーのみ）
- ❌ スキル名の `devrev-` プレフィックスを省略しない

#### 2. 作業前の確認（MUST CHECK）

```bash
# スキル編集前に必ず実行
pwd
# 結果が /Users/skon/.claude/skills/devrev-xxx であることを確認

# もし間違った場所にいたら即座に移動
cd ~/.claude/skills/devrev-xxx
```

#### 3. 同期のタイミング

以下の場合にのみ、`~/.claude/skills/` → リポジトリへコピー:
- ✅ スキルが完成した（動作確認済み）
- ✅ 重要な変更をコミットする前
- ✅ 公開・共有する前
- ❌ 開発途中での頻繁な同期は不要

#### 4. ファイルパス記載ルール

ドキュメント・コメントでパスを記載する際:

```markdown
# ✅ 正しい
マスター: ~/.claude/skills/devrev-xxx/
リポジトリ: ~/DevRev/develop/repo/konchangakita/devrev-claude/skills/devrev-xxx/

# ❌ 間違い
skills/devrev-xxx/  ← どちらか不明
```

#### 5. バージョン管理

- リポジトリ側は Git 管理（コミット履歴あり）
- `~/.claude/skills/` 側は Git 管理しない（ワーキングディレクトリ）
- バージョン番号は SKILL.md の frontmatter に記載:

```yaml
---
name: devrev-xxx
version: 1.0.0  ← 更新時にインクリメント
---
```

#### 6. コピーコマンドの標準化

```bash
# 単一スキルをコピー（標準）
cp -r ~/.claude/skills/devrev-xxx ~/DevRev/develop/repo/konchangakita/devrev-claude/skills/

# 全DevRevスキルを一括コピー（リリース前）
cp -r ~/.claude/skills/devrev-* ~/DevRev/develop/repo/konchangakita/devrev-claude/skills/

# コピー後は必ず確認
ls -la ~/DevRev/develop/repo/konchangakita/devrev-claude/skills/
```

#### 7. コミット前の必須チェック（CRITICAL）

```bash
# ステップ1: コピー前に両者の差分を確認
diff -r ~/.claude/skills/devrev-xxx \
  ~/DevRev/develop/repo/konchangakita/devrev-claude/skills/devrev-xxx

# ステップ2: コピー実行
cp -r ~/.claude/skills/devrev-xxx \
  ~/DevRev/develop/repo/konchangakita/devrev-claude/skills/

# ステップ3: Gitステータス確認
cd ~/DevRev/develop/repo/konchangakita/devrev-claude
git status

# ステップ4: Git差分を確認（MUST）
git diff skills/devrev-xxx/

# ステップ5: 意図しないファイルが含まれていないか確認
git diff --name-only

# ステップ6: ステージング
git add skills/devrev-xxx/

# ステップ7: ステージング後も再確認
git diff --cached

# ステップ8: コミット
git commit -m "feat: update devrev-xxx"
```

#### 8. 差分チェックで確認すべき項目

**✅ 含まれるべきもの:**
- SKILL.md の変更
- 新規/更新されたスクリプト
- templates/, references/, static/ の変更
- README.md の更新

**❌ 含まれてはいけないもの:**
- `.env` ファイル（環境変数・秘密情報）
- `.env.local`, `deploy.env` 等
- `node_modules/`
- `.DS_Store`
- 個人的な設定ファイル
- テスト時の一時ファイル
- ログファイル（`*.log`）
- 認証トークン、API キー
- JWT パターン（`eyJ...`）

#### 9. README.md への明記

リポジトリの `skills/README.md` に以下を記載:

```markdown
## ⚠️ 重要: スキル開発ルール

**開発場所**: `~/.claude/skills/devrev-xxx/`（マスター）
**リポジトリ**: `./skills/devrev-xxx/`（コピー・公開用）

### 開発ワークフロー
1. `~/.claude/skills/` で開発・テスト
2. 完成後にリポジトリへコピー
3. Git コミット・プッシュ

**⚠️ リポジトリ側を直接編集しないこと！**
```

#### 10. チェックリスト（新規スキル作成・更新時）

**開発フェーズ:**

- [ ] `~/.claude/skills/devrev-xxx/` で開発
- [ ] SKILL.md に frontmatter 記載（name, version, description）
- [ ] 動作確認完了（実際にスキルを実行してテスト）

**コピー・コミット前フェーズ:**

- [ ] 作業ディレクトリ確認 (`pwd` が `~/.claude/skills/devrev-xxx` であること)
- [ ] コピー前に差分確認 (`diff -r ...`)
- [ ] リポジトリへコピー (`cp -r ...`)
- [ ] Git ステータス確認 (`git status`)
- [ ] **Git 差分を目視確認** (`git diff skills/devrev-xxx/`)
- [ ] 禁止ファイルが含まれていないか確認（.env, トークン, node_modules 等）
- [ ] ステージング (`git add skills/devrev-xxx/`)
- [ ] **ステージング後も差分確認** (`git diff --cached`)
- [ ] コミットメッセージ作成（Conventional Commits 形式）
- [ ] コミット (`git commit -m "..."`)
- [ ] README.md にスキル追加を記載（新規の場合）
- [ ] プッシュ (`git push`)

**関連ドキュメント**:

- 既存スキル調査: `2026-06-08-devrev-skills-survey.md`
