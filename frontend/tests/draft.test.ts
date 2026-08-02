import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'

import { roundUpToImageStep, useDraftStore } from '../src/stores/draft'

describe('draft store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('builds a creative brief from Korean input fields', () => {
    const draft = useDraftStore()
    draft.promotionText = '오늘 점심은 갈비탕\n평일 점심 한정 9,900원'
    draft.mood_keywords = ['따뜻한']

    expect(draft.brief.primary_copy).toBe('오늘 점심은 갈비탕')
    expect(draft.brief.secondary_copy).toBe('오늘 점심은 갈비탕\n평일 점심 한정 9,900원')
    expect(draft.brief.width).toBe(1080)
    expect(draft.brief.height).toBe(1350)
    expect(draft.brief.mood_keywords).toEqual(['따뜻한'])
  })

  it('rounds custom image sizes up to a 16px step', () => {
    expect(roundUpToImageStep(600)).toBe(608)
    expect(roundUpToImageStep(1800)).toBe(1808)
  })
})
