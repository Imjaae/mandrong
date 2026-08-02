<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api, apiUrl } from '../api/client'
import PrimaryButton from '../components/PrimaryButton.vue'
import type { Version } from '../types/api'

const route = useRoute()
const router = useRouter()
const before = ref<Version | null>(null)
const after = ref<Version | null>(null)
const selected = ref<'before' | 'after'>('after')
const error = ref('')
const selectedVersion = computed(() => selected.value === 'after' ? after.value : before.value)

onMounted(async () => {
  try {
    before.value = await api.getVersion(String(route.params.beforeId))
    after.value = await api.getVersion(String(route.params.afterId))
  } catch (err) {
    error.value = err instanceof Error ? err.message : '비교 이미지를 불러오지 못했어요.'
  }
})

async function apply() {
  if (!selectedVersion.value) return
  await api.applyVersion(selectedVersion.value.id)
  router.push(`/projects/${route.params.id}/result/${selectedVersion.value.id}`)
}

function editSelected() {
  if (!selectedVersion.value) return
  router.push(`/projects/${route.params.id}/annotate/${selectedVersion.value.id}`)
}
</script>

<template>
  <main class="page-enter mx-auto flex h-[calc(100dvh-73px)] max-w-7xl flex-col overflow-hidden px-3 py-3 sm:px-6 sm:py-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <p class="text-sm font-semibold text-mandrong-primary">버전 선택</p>
        <h1 class="text-[24px] font-semibold sm:text-[28px]">어떤 결과를 이어갈까요?</h1>
      </div>
      <button class="h-10 rounded-lg border border-mandrong-line px-4 text-sm text-mandrong-muted transition hover:border-mandrong-primary hover:text-mandrong-text" @click="router.back()">이전</button>
    </div>
    <p v-if="error" class="mt-4 text-mandrong-danger">{{ error }}</p>
    <div class="mt-4 grid min-h-0 flex-1 gap-3 sm:mt-6 lg:grid-cols-2 lg:gap-5">
      <button
        class="grid min-h-0 grid-rows-[auto_minmax(0,1fr)] rounded-xl border bg-mandrong-surface/72 p-3 text-left transition hover:border-mandrong-primary"
        :class="selected === 'before' ? 'border-mandrong-primary ring-2 ring-mandrong-primary/20' : 'border-mandrong-line'"
        @click="selected = 'before'"
      >
        <span class="mb-3 flex items-center justify-between">
          <span>
            <strong class="block">수정 전</strong>
            <span class="text-sm text-mandrong-muted">이 버전을 기준으로 다시 수정할 수 있어요</span>
          </span>
          <span v-if="selected === 'before'" class="rounded-full bg-mandrong-primary/10 px-3 py-1 text-xs font-semibold text-mandrong-primary">선택됨</span>
        </span>
        <span class="flex min-h-0 items-center justify-center overflow-hidden rounded-lg bg-[#101311]">
          <img v-if="before" :src="apiUrl(before.image_url)" alt="수정 전" class="max-h-full max-w-full object-contain" />
        </span>
      </button>
      <button
        class="grid min-h-0 grid-rows-[auto_minmax(0,1fr)] rounded-xl border bg-mandrong-surface/72 p-3 text-left transition hover:border-mandrong-primary"
        :class="selected === 'after' ? 'border-mandrong-primary ring-2 ring-mandrong-primary/20' : 'border-mandrong-line'"
        @click="selected = 'after'"
      >
        <span class="mb-3 flex items-center justify-between">
          <span>
            <strong class="block">수정 후</strong>
            <span class="text-sm text-mandrong-muted">새로 만든 결과를 이어서 수정할 수 있어요</span>
          </span>
          <span v-if="selected === 'after'" class="rounded-full bg-mandrong-primary/10 px-3 py-1 text-xs font-semibold text-mandrong-primary">선택됨</span>
        </span>
        <span class="flex min-h-0 items-center justify-center overflow-hidden rounded-lg bg-[#101311]">
          <img v-if="after" :src="apiUrl(after.image_url)" alt="수정 후" class="max-h-full max-w-full object-contain" />
        </span>
      </button>
    </div>
    <div class="mt-4 grid gap-3 sm:flex sm:justify-end">
      <button class="h-12 rounded-lg border border-mandrong-line bg-[#111412] px-5 transition hover:border-mandrong-primary" @click="editSelected">선택한 결과 수정</button>
      <PrimaryButton @click="apply">선택한 결과 적용</PrimaryButton>
    </div>
  </main>
</template>
