---
date: 2026-06-08
type: research
---

# 既存DevRevスキル調査結果

## 調査日
2026-06-08 (月)

## 対象
`~/.claude/skills/` 配下の DevRev 関連スキル

---

## 📋 発見したスキル（全3件）

### 1️⃣ devrev-pat-manager
**場所**: `~/.claude/skills/devrev-pat-manager/`  
**役割**: **認証基盤** - 全てのDevRevスキルの土台

**主な機能**:
- 複数org の PAT を暗号化vault保存（`~/.config/`）
- Web GUI（`http://localhost:19847`）でトークン管理
- 自動org検出（slug, URL, 表示名から）
- 有効期限管理
- イベントログ（`~/.config/computer-events/events.jsonl`）

**構成**:
```
devrev-pat-manager/
├── SKILL.md
├── scripts/
│   ├── pat_manager.py          # CLI操作
│   ├── pat_entry_server.py     # Web GUI
│   └── event_log.py
├── templates/
│   └── pat-entry.html          # ダッシュボードUI
├── references/
└── static/
```

**セキュリティ原則**:
- チャットでPATをやり取りしない（常にWeb GUIを使用）
- 環境変数経由で安全に受け渡し（CLI引数に含めない）
- vault は暗号化保存

**ワークフロー**:
1. org 識別
2. 既存PAT チェック（`pat_manager.py get <org>`）
3. なければ Web GUI 起動（`pat_entry_server.py`）
4. 変更検出（event log確認）
5. 後続アクションに使用

---

### 2️⃣ devrev-workflow-action
**場所**: `~/.claude/skills/devrev-workflow-action/`  
**役割**: **Workflow拡張** - カスタムアクション（Snap-in Operation）作成ガイド

**主な機能**:
- Workflow Builder で独自処理を実行
- 入力/出力フィールド定義（text, bool, number, array）
- DevRev API / 外部API 連携
- ローカルテスト環境（fixtures + test-runner）

**実装例**:
- **Article Fetcher** - 本文完全取得（artifact経由、402KB対応）
- **User Group Validator** - メンバーシップ判定
- **Conversation Custom Fields** - Webhook処理

**ディレクトリ構造**:
```
snap-ins/<snap-in-name>/
├── manifest.yaml              # Snap-in定義
├── README.md
├── deploy.sh                  # デプロイスクリプト
├── deploy.env                 # デプロイ設定（Git除外）
├── deploy.env.example
├── .env                       # ローカルテスト用（Git除外）
├── .env.example
└── code/
    ├── package.json
    ├── tsconfig.json
    ├── src/
    │   ├── index.ts
    │   ├── main.ts
    │   ├── function-factory.ts
    │   ├── operations/
    │   │   └── index.ts                    # OperationFactory
    │   ├── functions/
    │   │   └── operation_handler/
    │   │       ├── index.ts                # Operation ルーティング
    │   │       └── <operation_name>.ts     # 実装本体
    │   ├── fixtures/
    │   │   └── <operation_name>_op.json    # テスト用フィクスチャ
    │   ├── test-runner/
    │   │   └── test-runner.ts              # ローカル実行ランナー
    │   └── scripts/
    │       └── run-local-<op>-from-env.ts  # .env からローカル実行
    └── dist/
```

**manifest.yaml の構造**:
```yaml
version: "2"
name: "Your Operation Name"
description: |
  Operation の説明

service_account:
  display_name: Your Operation Bot

functions:
  - name: operation_handler
    description: Routes workflow operations to implementation

operations:
  - name: your_operation_name          # 内部名（snake_case）
    display_name: Your Operation       # Workflow での表示名
    description: 処理内容の説明
    slug: your_operation_name
    function: operation_handler
    type: action                       # Workflow で使えるアクション
    inputs:
      fields:
        - name: input_field_1
          description: 入力フィールドの説明
          field_type: text             # text, bool, number, array
          is_required: true
    outputs:
      fields:
        - name: output_field_1
          description: 出力フィールドの説明
          field_type: text
```

---

### 3️⃣ devrev-presentation-web
**場所**: `~/.claude/skills/devrev-presentation-web/`  
**役割**: **ブランドプレゼン** - DevRevブランドガイドライン準拠のWebプレゼン作成

**主な機能**:
- DevRev公式カラーパレット対応
- タイポグラフィ統一（Noto Sans JP、Courier New）
- レイアウト原則（`justify-start pt-20 md:pt-24`）
- 左下ロゴ配置（Cover以外）
- baseline-ui準拠のクリーンデザイン

**カラーパレット**:
```css
/* メインカラー */
--devrev-purple: #5800E6;    /* ACCENT_1 - メインブランドカラー */
--devrev-yellow: #FFE600;    /* ACCENT_5 - セカンダリカラー（Cover背景） */
--devrev-blue: #3968F6;      /* ACCENT_2 */
--devrev-pink: #FF4570;      /* ACCENT_3 */
--devrev-orange: #FF6C0A;    /* ACCENT_4 */
--devrev-green: #78FF2A;     /* ACCENT_6 */

/* ベースカラー */
--devrev-black: #161616;     /* DARK_1 - 暗色背景 */
--devrev-white: #FFFFFF;     /* LIGHT_1 - 白背景、テキスト */
--devrev-gray-dark: #595959; /* DARK_2 - 本文テキスト */
--devrev-gray-mid: #777777;  /* サブテキスト・ラベル */
--devrev-gray-light: #EEEEEE; /* LIGHT_2 - 薄背景 */
```

**カラー使用原則**:
- **Cover（表紙）**: 黄色背景（#FFE600）
- **コンテンツ**: 白背景（#FFFFFF）
- **セクション区切り**: 黒背景（#161616）
- **アクセント**: 紫、青、ピンク、オレンジ、緑を適宜使用

**禁止事項（baseline-ui準拠）**:
- ❌ グラデーション
- ❌ グローエフェクト
- ❌ カスタムアニメーション
- ❌ 任意のz-index値

**推奨事項**:
- ✅ ソリッドカラー背景
- ✅ Tailwind標準シャドウ（`shadow-lg`, `shadow-xl`）
- ✅ 固定z-indexスケール（`z-1`, `z-10`, `z-20`, `z-30`, `z-40`, `z-50`）
- ✅ `h-dvh`（`h-screen`ではなく）
- ✅ `safe-area-inset` 対応
- ✅ `prefers-reduced-motion` 対応

---

## 📊 依存関係

```
devrev-pat-manager (認証基盤)
        ↓
devrev-workflow-action (Snap-in開発ガイド)

devrev-presentation-web (独立: フロントエンド資料作成)
```

**devrev-pat-manager の重要性**:
- 全てのDevRev API操作の土台
- 他のスキルが認証に依存

---

## 💡 devrev-claudeプロジェクトへの影響

**活用方針**:
1. **pat-manager** → 既存で完成、そのまま利用（スキル開発時の認証に使用）
2. **workflow-action** → テンプレート/参考実装として活用（Snap-in開発時）
3. **presentation-web** → 独立スキル、直接関連なし（プレゼン作成時のみ）

**開発時の注意点**:
- PAT管理は pat-manager に任せる（独自実装不要）
- Snap-in開発時は workflow-action のディレクトリ構造を参考にする
- ローカルテスト環境（fixtures + test-runner）パターンを踏襲する

---

## 次のアクション候補

- [ ] devrev-workflow-action の実装例を詳細調査
- [ ] Article Fetcher のコードを読んで Snap-in 実装パターンを理解
- [ ] pat-manager の実際の使い方をテスト
- [ ] 新規スキルのアイデア出し
