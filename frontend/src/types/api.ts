export type Purpose = 'poster' | 'banner' | 'menu_board' | 'sns_square' | 'sns_story' | 'x_banner'

export interface CreativeBrief {
  purpose: Purpose
  width: number
  height: number
  primary_copy: string
  secondary_copy?: string | null
  price_copy?: string | null
  notice_copy?: string | null
  store_name?: string | null
  menu_name?: string | null
  price?: string | null
  store_location?: string | null
  contact?: string | null
  mood_keywords: string[]
  mood_text?: string | null
}

export interface Project {
  id: string
  title: string
  status: string
  current_version_id: string | null
  current_image_url?: string | null
  created_at: string
}

export interface Asset {
  id: string
  type: string
  original_filename: string | null
  mime_type: string
  size_bytes: number
  width: number | null
  height: number | null
  url: string
}

export interface GenerationJob {
  id: string
  project_id: string
  type: string
  status: string
  version_id: string | null
  error: { code: string; message: string } | null
}

export interface ExportJob {
  id: string
  status: string
  asset_id: string | null
  download_url: string | null
  error: { code: string; message: string } | null
}

export interface Version {
  id: string
  project_id: string
  image_asset_id: string
  image_url: string
  version_number: number
  width: number
  height: number
  summary: string | null
  is_applied: boolean
  created_at: string
}

export interface AnnotationDraft {
  note: string
  x: number
  y: number
  width?: number | null
  height?: number | null
  color: string
}
