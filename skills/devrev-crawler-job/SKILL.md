---
name: devrev-crawler-job
version: 1.0.0
description: >
  DevRev Web Crawler Job の作成・一覧表示・制御（pause/resume/abort）を行うスキル。
  Knowledge Base 記事の自動収集に使用。
---

# DevRev Crawler Job Manager

DevRev の Web Crawler Job を管理するスキル。Knowledge Base 記事の自動収集ジョブの作成・一覧表示・制御を行います。

## Path Resolution
`SKILL_DIR` in all commands below = the **absolute path of the directory containing this SKILL.md file**.
- As the AI agent: substitute the actual filesystem path you read this file from.
- Example: if this file is at `/Users/username/.claude/skills/devrev-crawler-job/SKILL.md`, then `SKILL_DIR=/Users/username/.claude/skills/devrev-crawler-job`

## Description
DevRev の Web Crawler Job を管理し、外部サイトから Knowledge Base 記事を自動収集します。ジョブの作成、一覧表示、状態制御（pause/resume/abort）が可能です。

## When to Use
- ユーザーが「クローラージョブを作成して」と言ったとき
- ユーザーが「クローラージョブ一覧を見せて」と言ったとき
- ユーザーが「クローラージョブを停止/再開/中止して」と言ったとき
- Knowledge Base の自動更新を設定したいとき
- 外部ドキュメントサイトを DevRev に取り込みたいとき

## Workflow

### Step 1: PAT 確認
```bash
# devrev-pat-manager スキルで PAT を取得
python3 "${PAT_MANAGER_SKILL}/scripts/pat_manager.py" get "<org>"
```

### Step 2: 目的に応じた操作

#### ジョブ一覧表示
```bash
python3 "${SKILL_DIR}/scripts/list_crawler_jobs.py"
```

#### ジョブ作成
```bash
python3 "${SKILL_DIR}/scripts/create_crawler_job.py" \
  --urls "https://example.com/docs" \
  --part "PROD-1" \
  --frequency 0 \
  --max-depth 4
```

#### ジョブ制御（pause/resume/abort）
```bash
python3 "${SKILL_DIR}/scripts/control_crawler_job.py" \
  --job-id "WCJ-1" \
  --action "pause"
```

## Parameters

### create_crawler_job.py Parameters
- `--urls` (必須): クロール対象URL（カンマ区切りで複数指定可、最大50件）
- `--part` (必須): 適用先パーツのdisplay_id（例: PROD-1）
- `--frequency` (任意): クロール頻度（0=1回のみ、1-12=定期実行、デフォルト: 0）
- `--max-depth` (任意): クロール深度（1-10、デフォルト: 4）
- `--description` (任意): ジョブの説明文

### list_crawler_jobs.py Parameters
- パラメータなし（全ジョブを一覧表示）

### control_crawler_job.py Parameters
- `--job-id` (必須): ジョブIDまたはdisplay_id（例: WCJ-1）
- `--action` (必須): 実行アクション（abort | pause | resume）

## Run Instructions

### Prerequisites

#### Method 1: Direct Python Execution (Recommended for Mac/Linux)

```bash
# Install dependencies
pip3 install requests
```

#### Method 2: Docker (Recommended for Windows or clean environment)

```bash
# Prerequisites: Docker Desktop
# No additional installation needed
```

### ジョブ一覧表示

#### Direct Python

```bash
# 全ジョブを一覧表示
python3 "${SKILL_DIR}/scripts/list_crawler_jobs.py"
```

#### Docker

```bash
cd "${SKILL_DIR}"
docker compose run --rm crawler python3 scripts/list_crawler_jobs.py
```

### ジョブ作成（1回のみ実行）

#### Direct Python

```bash
# 基本的な作成（1回のみクロール）
python3 "${SKILL_DIR}/scripts/create_crawler_job.py" \
  --urls "https://docs.example.com/" \
  --part "PROD-1"

# 複数URL + カスタム深度
python3 "${SKILL_DIR}/scripts/create_crawler_job.py" \
  --urls "https://docs.example.com/,https://help.example.com/" \
  --part "PROD-1" \
  --max-depth 5 \
  --description "公式ドキュメントサイト"
```

#### Docker

```bash
cd "${SKILL_DIR}"

# 基本的な作成
docker compose run --rm crawler python3 scripts/create_crawler_job.py \
  --urls "https://docs.example.com/" \
  --part "PROD-1"

# 複数URL + カスタム深度
docker compose run --rm crawler python3 scripts/create_crawler_job.py \
  --urls "https://docs.example.com/,https://help.example.com/" \
  --part "PROD-1" \
  --max-depth 5 \
  --description "公式ドキュメントサイト"
```

### ジョブ作成（定期実行）

#### Direct Python

```bash
# 毎日実行（frequency=1）
python3 "${SKILL_DIR}/scripts/create_crawler_job.py" \
  --urls "https://docs.example.com/" \
  --part "PROD-1" \
  --frequency 1 \
  --description "毎日更新チェック"

# 週1回実行（frequency=7）
python3 "${SKILL_DIR}/scripts/create_crawler_job.py" \
  --urls "https://docs.example.com/" \
  --part "PROD-1" \
  --frequency 7 \
  --description "週次更新チェック"
```

#### Docker

```bash
cd "${SKILL_DIR}"

# 毎日実行
docker compose run --rm crawler python3 scripts/create_crawler_job.py \
  --urls "https://docs.example.com/" \
  --part "PROD-1" \
  --frequency 1 \
  --description "毎日更新チェック"

# 週1回実行
docker compose run --rm crawler python3 scripts/create_crawler_job.py \
  --urls "https://docs.example.com/" \
  --part "PROD-1" \
  --frequency 7 \
  --description "週次更新チェック"
```

### ジョブ制御

#### Direct Python

```bash
# ジョブを一時停止
python3 "${SKILL_DIR}/scripts/control_crawler_job.py" \
  --job-id "WCJ-1" \
  --action "pause"

# ジョブを再開
python3 "${SKILL_DIR}/scripts/control_crawler_job.py" \
  --job-id "WCJ-1" \
  --action "resume"

# ジョブを中止
python3 "${SKILL_DIR}/scripts/control_crawler_job.py" \
  --job-id "WCJ-1" \
  --action "abort"
```

#### Docker

```bash
cd "${SKILL_DIR}"

# ジョブを一時停止
docker compose run --rm crawler python3 scripts/control_crawler_job.py \
  --job-id "WCJ-1" \
  --action "pause"

# ジョブを再開
docker compose run --rm crawler python3 scripts/control_crawler_job.py \
  --job-id "WCJ-1" \
  --action "resume"

# ジョブを中止
docker compose run --rm crawler python3 scripts/control_crawler_job.py \
  --job-id "WCJ-1" \
  --action "abort"
```

## Commands Reference

### list_crawler_jobs.py
全 Web Crawler Job を一覧表示します。

**出力形式**:
```
display_id             URL                               frequency  state            created_date
---------------------------------------------------------------------------------------
WCJ-1                  https://docs.example.com/         0          active           2026-06-08 10:00:00
WCJ-2                  https://help.example.com/         1          paused           2026-06-07 15:30:00
```

### create_crawler_job.py
新しい Web Crawler Job を作成します。

**必須パラメータ**:
- `--urls`: クロール対象URL
- `--part`: 適用先パーツ

**オプションパラメータ**:
- `--frequency`: 0=1回のみ、1-12=定期実行（日数）
- `--max-depth`: クロール深度（1-10、デフォルト: 4）
- `--description`: ジョブの説明

**動作**:
1. Before: ジョブ一覧を取得・保存
2. パーツIDを解決（display_id → id）
3. ジョブを作成
4. After: ジョブ一覧を取得・保存

### control_crawler_job.py
既存ジョブの状態を制御します。

**アクション**:
- `abort`: ジョブを中止（完全停止）
- `pause`: ジョブを一時停止
- `resume`: ジョブを再開

**動作**:
1. Before: ジョブ一覧を取得・保存
2. 指定アクションを実行
3. After: ジョブ一覧を取得・保存

## API Reference

### web-crawler-jobs.list
ジョブ一覧を取得します。

**Request**:
```
GET /web-crawler-jobs.list?limit=50&cursor=<cursor>
Authorization: <PAT>
```

**Response**:
```json
{
  "web_crawler_jobs": [
    {
      "id": "don:core:dvrv-us-1:devo/ORG:web_crawler_job/123",
      "display_id": "WCJ-1",
      "urls": ["https://docs.example.com/"],
      "frequency": 0,
      "state": "active",
      "created_date": "2026-06-08T10:00:00Z",
      "max_depth": 4
    }
  ],
  "next_cursor": "..."
}
```

### web-crawler-jobs.create
新しいジョブを作成します。

**Request**:
```
POST /web-crawler-jobs.create
Authorization: <PAT>
Content-Type: application/json

{
  "urls": ["https://docs.example.com/"],
  "applies_to_parts": ["don:core:dvrv-us-1:devo/ORG:product/1"],
  "frequency": 0,
  "max_depth": 4,
  "description": "公式ドキュメント"
}
```

**Response**:
```json
{
  "web_crawler_job": {
    "id": "don:core:dvrv-us-1:devo/ORG:web_crawler_job/123",
    "display_id": "WCJ-1",
    "state": "active"
  }
}
```

### web-crawler-jobs.control
ジョブの状態を変更します。

**Request**:
```
POST /web-crawler-jobs.control
Authorization: <PAT>
Content-Type: application/json

{
  "id": "WCJ-1",
  "action": "pause"
}
```

**Response**:
```json
{
  "web_crawler_job": {
    "id": "don:core:dvrv-us-1:devo/ORG:web_crawler_job/123",
    "display_id": "WCJ-1",
    "state": "paused"
  }
}
```

## Dependencies
- Python 3.8+
- `requests` library (`pip install requests`)
- devrev-pat-manager スキル（PAT 認証用）

## Security Model
- PAT は devrev-pat-manager 経由で取得（暗号化vault）
- コマンドライン引数にトークンを含めない（環境変数経由）
- 出力ファイルにトークンを記録しない

## Error Handling

### 環境変数エラー
- **When**: `DEVREV_PAT` が未設定
- **Handling**: エラーメッセージを表示して終了
- **User Impact**: PAT Manager でトークンを設定するよう促す

### API エラー
- **When**: API 呼び出しが 200 以外を返す
- **Handling**: ステータスコードとエラー内容を表示
- **User Impact**: エラー内容に基づいて修正を促す

### パラメータエラー
- **When**: 必須パラメータが未指定、または不正な値
- **Handling**: 使用例を表示して終了
- **User Impact**: 正しいパラメータで再実行

### パーツ解決エラー
- **When**: 指定したパーツの display_id が見つからない
- **Handling**: パーツ一覧を表示して確認を促す
- **User Impact**: 正しいパーツ ID を確認して再実行

## File Structure
```
devrev-crawler-job/
├── SKILL.md                          # このファイル
├── scripts/
│   ├── list_crawler_jobs.py          # ジョブ一覧表示
│   ├── create_crawler_job.py         # ジョブ作成
│   └── control_crawler_job.py        # ジョブ制御
├── references/
│   └── devrev-crawler-api.md         # DevRev Crawler API リファレンス
└── templates/
    └── job_config_template.json      # ジョブ設定テンプレート
```

## Examples

### Example 1: ドキュメントサイトを1回クロール
```
User: "https://docs.example.com/ をクロールしてKBに追加して。PROD-1に適用。"

Agent:
→ pat_manager.py get "example-org"
→ create_crawler_job.py --urls "https://docs.example.com/" --part "PROD-1"
→ "クローラージョブ WCJ-1 を作成しました。1回のみ実行します。"
```

### Example 2: 毎日更新チェックする定期ジョブ
```
User: "https://help.example.com/ を毎日クロールして最新情報を取り込みたい。"

Agent:
→ create_crawler_job.py --urls "https://help.example.com/" --part "PROD-1" --frequency 1
→ "クローラージョブ WCJ-2 を作成しました。毎日自動実行します。"
```

### Example 3: ジョブ一覧を確認
```
User: "現在のクローラージョブを見せて"

Agent:
→ list_crawler_jobs.py
→ 一覧を表示（display_id, URL, frequency, state, created_date）
```

### Example 4: ジョブを一時停止
```
User: "WCJ-1 を一時停止して"

Agent:
→ control_crawler_job.py --job-id "WCJ-1" --action "pause"
→ "ジョブ WCJ-1 を一時停止しました。"
```

### Example 5: 複数URLを一括クロール
```
User: "公式サイトとヘルプサイトの両方をクロールして"

Agent:
→ create_crawler_job.py --urls "https://docs.example.com/,https://help.example.com/" --part "PROD-1" --max-depth 5
→ "2つのURLをクロールするジョブ WCJ-3 を作成しました。"
```

## Frequency Values

| Value | Meaning |
|-------|---------|
| 0 | 1回のみ実行（デフォルト） |
| 1 | 毎日実行 |
| 2 | 2日ごと |
| 3 | 3日ごと |
| 7 | 週1回 |
| 14 | 2週間に1回 |
| 30 | 月1回 |

最大値: 12（12日ごと）

## State Values

| State | Meaning |
|-------|---------|
| active | 実行中 |
| paused | 一時停止中 |
| completed | 完了 |
| aborted | 中止 |
| failed | 失敗 |

## Version History

### v1.0.0 (2026-06-08)
**Initial Release**

Core Features:
- ジョブ一覧表示（全ジョブをcursorでページング取得）
- ジョブ作成（1回のみ / 定期実行）
- ジョブ制御（pause / resume / abort）
- パーツID自動解決（display_id → id）
- Before/After 差分保存

Security:
- PAT Manager 連携（暗号化vault経由）
- トークンをコマンドライン引数に含めない
- 出力ファイルにトークンを記録しない

Documentation:
- 完全なAPIリファレンス
- 5つの使用例
- エラーハンドリング documented
