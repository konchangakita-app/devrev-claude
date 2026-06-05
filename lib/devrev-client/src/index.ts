import axios, { AxiosInstance } from 'axios'

export interface DevRevClientConfig {
  apiToken: string
  baseURL?: string
}

export class DevRevClient {
  private client: AxiosInstance

  constructor(config: DevRevClientConfig) {
    this.client = axios.create({
      baseURL: config.baseURL || 'https://api.devrev.ai',
      headers: {
        Authorization: `Bearer ${config.apiToken}`,
        'Content-Type': 'application/json',
      },
    })
  }

  // Works API
  async getWork(workId: string) {
    const response = await this.client.get(`/works.get`, {
      params: { id: workId },
    })
    return response.data
  }

  async listWorks(params?: { type?: string; owned_by?: string[] }) {
    const response = await this.client.post('/works.list', params)
    return response.data
  }

  async createWork(data: {
    type: string
    title: string
    body?: string
    owned_by?: string[]
  }) {
    const response = await this.client.post('/works.create', data)
    return response.data
  }

  async updateWork(workId: string, data: { title?: string; body?: string }) {
    const response = await this.client.post('/works.update', {
      id: workId,
      ...data,
    })
    return response.data
  }

  // Dev Users API
  async getCurrentUser() {
    const response = await this.client.get('/dev-users.self')
    return response.data
  }

  // Generic request method
  async request(method: string, endpoint: string, data?: unknown) {
    const response = await this.client.request({
      method,
      url: endpoint,
      data,
    })
    return response.data
  }
}

export default DevRevClient
