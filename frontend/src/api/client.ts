import type { AnnotationDraft, Asset, CreativeBrief, GenerationJob, Project, Version } from '../types/api'

export const DEPLOYED_API_BASE = 'https://mandrong.onrender.com'
const configuredApiBase = import.meta.env.VITE_API_BASE as string | undefined
export const API_BASE = configuredApiBase
  || (typeof window !== 'undefined' && window.location.hostname.includes('vercel.app') ? DEPLOYED_API_BASE : '')

export function apiUrl(path: string | null | undefined) {
  if (!path) return ''
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  return `${API_BASE}${path}`
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: options.body instanceof FormData ? undefined : { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!response.ok) {
    const payload = await response.json().catch(() => null)
    const message = payload?.error?.message ?? '요청을 처리하지 못했어요.'
    throw new Error(message)
  }
  if (response.status === 204) {
    return undefined as T
  }
  return response.json() as Promise<T>
}

export const api = {
  listProjects() {
    return request<Project[]>('/api/v1/projects')
  },
  createProject(title: string, brief: CreativeBrief) {
    return request<Project>('/api/v1/projects', {
      method: 'POST',
      body: JSON.stringify({ title, brief }),
    })
  },
  renameProject(projectId: string, title: string) {
    return request<Project>(`/api/v1/projects/${projectId}`, {
      method: 'PATCH',
      body: JSON.stringify({ title }),
    })
  },
  deleteProject(projectId: string) {
    return request<void>(`/api/v1/projects/${projectId}`, { method: 'DELETE' })
  },
  uploadAsset(projectId: string, type: 'menu_photo' | 'reference_image', file: File) {
    const form = new FormData()
    form.append('type', type)
    form.append('file', file)
    return request<Asset>(`/api/v1/projects/${projectId}/assets`, { method: 'POST', body: form })
  },
  createGeneration(projectId: string, menuAssetIds: string[], logoAssetIds: string[], referenceAssetIds: string[]) {
    return request<{ job_id: string; status: string }>(`/api/v1/projects/${projectId}/generations`, {
      method: 'POST',
      body: JSON.stringify({ menu_asset_ids: menuAssetIds, logo_asset_ids: logoAssetIds, reference_asset_ids: referenceAssetIds }),
    })
  },
  getGenerationJob(jobId: string) {
    return request<GenerationJob>(`/api/v1/generation-jobs/${jobId}`)
  },
  getVersion(versionId: string) {
    return request<Version>(`/api/v1/versions/${versionId}`)
  },
  listVersions(projectId: string) {
    return request<Version[]>(`/api/v1/projects/${projectId}/versions`)
  },
  saveAnnotations(versionId: string, annotations: AnnotationDraft[]) {
    return request<{ annotation_ids: string[] }>(`/api/v1/versions/${versionId}/annotations`, {
      method: 'POST',
      body: JSON.stringify({ annotations }),
    })
  },
  createEdit(versionId: string, annotationIds: string[], editText = '', additionalAssetIds: string[] = []) {
    return request<{ job_id: string; status: string }>(`/api/v1/versions/${versionId}/edits`, {
      method: 'POST',
      body: JSON.stringify({ annotation_ids: annotationIds, edit_text: editText, additional_asset_ids: additionalAssetIds }),
    })
  },
  applyVersion(versionId: string) {
    return request<{ project_id: string; current_version_id: string }>(`/api/v1/versions/${versionId}/apply`, {
      method: 'POST',
    })
  },
  createReframe(versionId: string, target: { purpose: string; width: number; height: number }) {
    return request<{ job_id: string; status: string }>(`/api/v1/versions/${versionId}/reframes`, {
      method: 'POST',
      body: JSON.stringify({ target, keep: { copy: true, menu_photo: true, price: true, mood: true } }),
    })
  },
  createExport(versionId: string, format: 'png' | 'jpeg' | 'pdf') {
    return request<{ export_job_id: string; status: string }>(`/api/v1/versions/${versionId}/exports`, {
      method: 'POST',
      body: JSON.stringify({ format, quality: 90 }),
    })
  },
}
