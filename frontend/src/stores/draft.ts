import { defineStore } from 'pinia'
import type { CreativeBrief, Purpose } from '../types/api'

export const defaultSizes = {
  poster: { width: 1080, height: 1350 },
  banner: { width: 1920, height: 1080 },
  menu_board: { width: 1200, height: 1600 },
  sns_square: { width: 1080, height: 1080 },
  sns_story: { width: 1080, height: 1920 },
  x_banner: { width: 608, height: 1808 },
} satisfies Record<Purpose, { width: number; height: number }>

export const purposeLabels: Record<Purpose, string> = {
  poster: '매장 포스터',
  banner: '가로 배너',
  menu_board: '메뉴판',
  sns_square: 'SNS 정사각형',
  sns_story: 'SNS 스토리',
  x_banner: 'X배너',
}

export const displaySizes = {
  poster: '1080x1350',
  banner: '1920x1080',
  menu_board: '1200x1600',
  sns_square: '1080x1080',
  sns_story: '1080x1920',
  x_banner: '600x1800 기준',
} satisfies Record<Purpose, string>

export function roundUpToImageStep(value: number) {
  const safeValue = Math.min(Math.max(Math.floor(Number(value) || 256), 256), 4096)
  return Math.min(Math.ceil(safeValue / 16) * 16, 4096)
}

export const useDraftStore = defineStore('draft', {
  state: () => ({
    title: '새 홍보물',
    purpose: 'poster' as Purpose,
    sizeMode: 'preset' as 'preset' | 'custom',
    customWidth: 1080,
    customHeight: 1350,
    promotionText: '',
    primary_copy: '',
    secondary_copy: '',
    price_copy: '',
    notice_copy: '',
    store_name: '',
    menu_name: '',
    price: '',
    store_location: '',
    contact: '',
    mood_keywords: [] as string[],
    mood_text: '',
    menuFiles: [] as File[],
    logoFile: null as File | null,
    useLogo: false,
    referenceFiles: [] as File[],
    projectId: '',
    menuAssetIds: [] as string[],
    logoAssetIds: [] as string[],
    referenceAssetIds: [] as string[],
    activeGenerationProjectId: '',
    activeGenerationJobId: '',
  }),
  getters: {
    size(state) {
      if (state.sizeMode === 'custom') {
        return {
          width: roundUpToImageStep(state.customWidth),
          height: roundUpToImageStep(state.customHeight),
        }
      }
      return defaultSizes[state.purpose]
    },
    brief(state): CreativeBrief {
      const size = this.size
      const text = state.promotionText.trim()
      const firstLine = text.split('\n').find((line) => line.trim().length > 0)?.trim() ?? ''
      const primaryCopy = firstLine.slice(0, 80) || text.slice(0, 80)
      return {
        purpose: state.purpose,
        width: size.width,
        height: size.height,
        primary_copy: primaryCopy,
        secondary_copy: text || null,
        price_copy: null,
        notice_copy: null,
        store_name: state.store_name || null,
        menu_name: state.menu_name || null,
        price: state.price || null,
        store_location: state.store_location || null,
        contact: state.contact || null,
        mood_keywords: state.mood_keywords,
        mood_text: state.mood_text || null,
      }
    },
  },
  actions: {
    setPurpose(purpose: Purpose) {
      this.purpose = purpose
      if (this.sizeMode === 'preset') {
        this.customWidth = defaultSizes[purpose].width
        this.customHeight = defaultSizes[purpose].height
      }
    },
    usePresetSize() {
      this.sizeMode = 'preset'
      this.customWidth = defaultSizes[this.purpose].width
      this.customHeight = defaultSizes[this.purpose].height
    },
    useCustomSize() {
      this.sizeMode = 'custom'
    },
    normalizeCustomSize() {
      this.customWidth = roundUpToImageStep(this.customWidth)
      this.customHeight = roundUpToImageStep(this.customHeight)
    },
    saveLocalDraft() {
      const { menuFiles, logoFile, referenceFiles, ...serializable } = this.$state
      localStorage.setItem('mandrong:draft', JSON.stringify(serializable))
    },
    loadLocalDraft() {
      const raw = localStorage.getItem('mandrong:draft')
      if (!raw) return
      const data = JSON.parse(raw) as Partial<Omit<typeof this.$state, 'menuFiles' | 'logoFile' | 'referenceFiles'>>
      this.$patch(data)
    },
    reset() {
      this.$reset()
    },
  },
})
