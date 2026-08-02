<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDraftStore } from '../stores/draft'

defineProps<{
  title: string
  subtitle?: string
  showProgress?: boolean
}>()

const route = useRoute()
const router = useRouter()
const draft = useDraftStore()
const saved = ref(false)
const steps = [
  { label: '용도와 크기', path: '/projects/new/purpose' },
  { label: '문구', path: '/projects/new/copy' },
  { label: '사진과 매장', path: '/projects/new/assets' },
  { label: '분위기', path: '/projects/new/style' },
]

const currentIndex = computed(() => {
  const index = steps.findIndex((step) => step.path === route.path)
  return index >= 0 ? index : 0
})

function saveDraft() {
  draft.saveLocalDraft()
  saved.value = true
  window.setTimeout(() => {
    saved.value = false
  }, 1600)
}
</script>

<template>
  <main class="mx-auto max-w-4xl px-6 py-10 sm:py-14">
    <nav v-if="showProgress !== false" class="mx-auto mb-8 max-w-3xl" aria-label="작업 단계">
      <div class="mb-3 flex flex-wrap items-center justify-between gap-3 text-sm">
        <div>
          <span class="font-semibold text-mandrong-primary">{{ currentIndex + 1 }}단계</span>
          <span class="ml-3 text-mandrong-muted">{{ steps[currentIndex].label }}</span>
        </div>
        <div class="flex items-center gap-2">
          <span v-if="saved" class="text-xs text-mandrong-primary">저장됨</span>
          <button class="h-9 rounded-lg border border-mandrong-line px-3 text-xs text-mandrong-muted transition hover:border-mandrong-primary hover:text-mandrong-text" @click="saveDraft">임시 저장</button>
          <button class="h-9 rounded-lg border border-mandrong-line px-3 text-xs text-mandrong-muted transition hover:border-mandrong-danger hover:text-mandrong-danger" @click="router.push('/')">취소</button>
        </div>
      </div>
      <div class="h-2 overflow-hidden rounded-full border border-mandrong-line bg-[#101311]">
        <div class="h-full rounded-full bg-mandrong-primary transition-all" :style="{ width: `${((currentIndex + 1) / steps.length) * 100}%` }" />
      </div>
      <ol class="mt-3 grid grid-cols-4 gap-2 text-center text-xs text-mandrong-muted">
        <li
          v-for="(step, index) in steps"
          :key="step.path"
          class="truncate"
          :class="index === currentIndex ? 'font-semibold text-mandrong-text' : ''"
        >
          {{ step.label }}
        </li>
      </ol>
    </nav>
    <section class="soft-panel page-enter mx-auto max-w-3xl rounded-xl p-6 sm:p-8">
      <div class="mb-8">
        <h1 class="text-[28px] font-semibold leading-tight">{{ title }}</h1>
        <p v-if="subtitle" class="mt-3 text-base leading-7 text-mandrong-muted">{{ subtitle }}</p>
      </div>
      <slot />
    </section>
  </main>
</template>
