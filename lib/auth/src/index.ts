import * as keytar from 'keytar'
import { homedir } from 'os'
import { join } from 'path'
import { readFileSync, writeFileSync, existsSync } from 'fs'

const SERVICE_NAME = 'devrev-claude'
const CONFIG_FILE = join(homedir(), '.devrev', 'config.json')

export interface TokenConfig {
  name: string
  token: string
  default?: boolean
  createdAt: string
}

export class AuthManager {
  /**
   * トークンを保存（セキュアストレージ使用）
   */
  async saveToken(name: string, token: string, setDefault = false): Promise<void> {
    await keytar.setPassword(SERVICE_NAME, name, token)

    const config = this.loadConfig()
    const existing = config.tokens.findIndex(t => t.name === name)

    if (existing >= 0) {
      config.tokens[existing] = {
        ...config.tokens[existing],
        token,
        default: setDefault || config.tokens[existing].default,
      }
    } else {
      config.tokens.push({
        name,
        token,
        default: setDefault || config.tokens.length === 0,
        createdAt: new Date().toISOString(),
      })
    }

    this.saveConfig(config)
  }

  /**
   * トークンを取得
   */
  async getToken(name?: string): Promise<string | null> {
    const config = this.loadConfig()

    if (!name) {
      const defaultToken = config.tokens.find(t => t.default)
      name = defaultToken?.name
    }

    if (!name) {
      return null
    }

    return await keytar.getPassword(SERVICE_NAME, name)
  }

  /**
   * トークンをリスト表示
   */
  listTokens(): Omit<TokenConfig, 'token'>[] {
    const config = this.loadConfig()
    return config.tokens.map(({ token, ...rest }) => rest)
  }

  /**
   * トークンを削除
   */
  async deleteToken(name: string): Promise<boolean> {
    await keytar.deletePassword(SERVICE_NAME, name)

    const config = this.loadConfig()
    config.tokens = config.tokens.filter(t => t.name !== name)
    this.saveConfig(config)

    return true
  }

  /**
   * デフォルトトークンを設定
   */
  setDefaultToken(name: string): void {
    const config = this.loadConfig()
    config.tokens.forEach(t => {
      t.default = t.name === name
    })
    this.saveConfig(config)
  }

  private loadConfig(): { tokens: TokenConfig[] } {
    if (!existsSync(CONFIG_FILE)) {
      return { tokens: [] }
    }

    try {
      const data = readFileSync(CONFIG_FILE, 'utf-8')
      return JSON.parse(data)
    } catch {
      return { tokens: [] }
    }
  }

  private saveConfig(config: { tokens: TokenConfig[] }): void {
    const dir = join(homedir(), '.devrev')
    if (!existsSync(dir)) {
      require('fs').mkdirSync(dir, { recursive: true })
    }
    writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2), 'utf-8')
  }
}

export default AuthManager
