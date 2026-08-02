<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api/client'
import { useDraftStore } from '../stores/draft'

const route = useRoute()
const router = useRouter()
const draft = useDraftStore()
const message = ref('홍보물을 만들고 있어요')
const detailIndex = ref(0)
const error = ref('')
let detailTimer = 0

const details = [
  '첨부한 메뉴 사진의 색감과 질감을 읽고 있어요',
  '로고와 매장 정보를 홍보물 안에 배치하고 있어요',
  '문구가 잘 읽히도록 여백과 구도를 정리하고 있어요',
  '완성 이미지를 마지막으로 다듬고 있어요',
]

async function poll(jobId: string) {
  const timer = window.setInterval(async () => {
    try {
      const job = await api.getGenerationJob(jobId)
      if (job.status === 'succeeded' && job.version_id) {
        window.clearInterval(timer)
        router.push(`/projects/${route.params.id}/result/${job.version_id}`)
      }
      if (job.status === 'failed') {
        window.clearInterval(timer)
        error.value = job.error?.message ?? '이미지 생성에 실패했어요.'
      }
    } catch (err) {
      window.clearInterval(timer)
      error.value = err instanceof Error ? err.message : '생성 상태를 확인하지 못했어요.'
    }
  }, 2000)
}

onMounted(async () => {
  detailTimer = window.setInterval(() => {
    detailIndex.value = (detailIndex.value + 1) % details.length
  }, 2600)
  try {
    const projectId = String(route.params.id)
    const job = await api.createGeneration(projectId, draft.menuAssetIds, draft.logoAssetIds, draft.referenceAssetIds)
    await poll(job.job_id)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '생성을 시작하지 못했어요.'
  }
})

onUnmounted(() => {
  window.clearInterval(detailTimer)
})
</script>

<template>
  <main class="mx-auto grid min-h-[calc(100vh-73px)] max-w-6xl items-center gap-10 px-6 py-12 lg:grid-cols-[minmax(0,1fr)_360px]">
    <section class="waiting-card mx-auto w-full max-w-2xl">
      <div class="waiting-frame aspect-[4/5] rounded-xl border border-mandrong-line p-8 shadow-2xl shadow-black/30">
        <div class="flex h-full flex-col justify-between rounded-lg border border-mandrong-line bg-[#0F1210]/82 p-6">
          <div class="space-y-3">
            <div class="h-5 w-28 rounded-full bg-mandrong-primary/70" />
            <div class="h-10 w-3/4 rounded-md bg-[#30382F]" />
            <div class="h-10 w-2/3 rounded-md bg-[#242B25]" />
          </div>
          <div class="grid grid-cols-[1fr_100px] gap-4">
            <div class="h-36 rounded-lg bg-[#202820]" />
            <div class="space-y-3">
              <div class="h-8 rounded-md bg-[#30382F]" />
              <div class="h-8 rounded-md bg-[#242B25]" />
              <div class="h-8 rounded-md bg-[#30382F]" />
            </div>
          </div>
        </div>
      </div>
    </section>
    <section class="page-enter">
      <p class="text-sm font-semibold text-mandrong-primary">생성 중</p>
      <h1 class="mt-3 text-[30px] font-semibold leading-tight">{{ message }}</h1>
      <p class="mt-4 min-h-7 text-mandrong-muted">{{ details[detailIndex] }}</p>
      <div class="mt-8 space-y-3">
        <div v-for="(item, index) in details" :key="item" class="flex items-center gap-3 text-sm" :class="index <= detailIndex ? 'text-mandrong-text' : 'text-mandrong-muted'">
          <span class="h-2.5 w-2.5 rounded-full" :class="index <= detailIndex ? 'bg-mandrong-primary' : 'bg-mandrong-line'" />
          {{ item }}
        </div>
      </div>
      <p v-if="error" class="mt-6 rounded-lg border border-mandrong-danger/40 bg-mandrong-danger/10 p-4 text-mandrong-danger">{{ error }}</p>
    </section>
  </main>
</template>
