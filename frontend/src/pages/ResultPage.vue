<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Download, Expand, History, MessageSquare, Rows3, X } from 'lucide-vue-next'
import { api, apiUrl } from '../api/client'
import PrimaryButton from '../components/PrimaryButton.vue'
import { useProjectStore } from '../stores/project'

const route = useRoute()
const router = useRouter()
const store = useProjectStore()
const exportError = ref('')
const fullView = ref(false)
const imageSrc = computed(() => store.currentVersion ? apiUrl(store.currentVersion.image_url) : '')

onMounted(() => {
  store.loadVersion(String(route.params.versionId))
})

async function download(format: 'png' | 'jpeg' | 'pdf') {
  exportError.value = ''
  try {
    const job = await api.createExport(String(route.params.versionId), format)
    exportError.value = `다운로드 파일을 준비하고 있어요. 작업 ID: ${job.export_job_id}`
  } catch (err) {
    exportError.value = err instanceof Error ? err.message : '다운로드를 준비하지 못했어요.'
  }
}
</script>

<template>
  <main class="mx-auto grid h-[calc(100dvh-73px)] max-w-7xl grid-rows-[minmax(0,1fr)_auto] gap-3 overflow-hidden px-3 py-3 sm:gap-4 sm:px-6 sm:py-5 lg:grid-cols-[minmax(0,1fr)_300px] lg:grid-rows-1 lg:gap-6 lg:py-6">
    <section class="page-enter flex min-h-0 flex-col">
      <p v-if="store.error" class="text-mandrong-danger">{{ store.error }}</p>
      <div v-else-if="store.currentVersion" class="relative flex min-h-0 flex-1 items-center justify-center overflow-hidden rounded-lg border border-mandrong-line bg-[#101311] shadow-2xl shadow-black/25">
        <img :src="imageSrc" alt="생성된 홍보물" class="result-reveal max-h-full max-w-full object-contain" />
        <button class="absolute right-3 top-3 flex h-9 items-center gap-2 rounded-lg border border-mandrong-line bg-[#111412]/90 px-3 text-xs backdrop-blur transition hover:border-mandrong-primary sm:right-4 sm:top-4 sm:h-10 sm:text-sm" @click="fullView = true">
          <Expand class="h-4 w-4" />
          전체보기
        </button>
      </div>
      <div v-else class="min-h-0 flex-1 rounded-lg border border-mandrong-line bg-[#101311]" />
    </section>
    <aside class="page-enter max-h-full space-y-2 overflow-hidden rounded-xl border border-mandrong-line bg-mandrong-surface/80 p-3 shadow-2xl shadow-black/20 sm:space-y-3 sm:p-5">
      <h1 class="text-lg font-semibold sm:text-xl">결과 확인</h1>
      <PrimaryButton class="h-10 w-full gap-2 sm:h-12" @click="router.push(`/projects/${route.params.id}/annotate/${route.params.versionId}`)">
        <MessageSquare class="h-4 w-4" />
        메모로 수정
      </PrimaryButton>
      <button class="flex h-10 w-full items-center justify-center gap-2 rounded-lg border border-mandrong-line bg-[#111412] text-sm transition hover:border-mandrong-primary sm:h-12 sm:text-base" @click="router.push(`/projects/${route.params.id}/reframe/${route.params.versionId}`)">
        <Rows3 class="h-4 w-4" />
        다른 비율로 만들기
      </button>
      <button class="flex h-10 w-full items-center justify-center gap-2 rounded-lg border border-mandrong-line bg-[#111412] text-sm transition hover:border-mandrong-primary sm:h-12 sm:text-base" @click="router.push(`/projects/${route.params.id}/history`)">
        <History class="h-4 w-4" />
        히스토리
      </button>
      <div class="border-t border-mandrong-line pt-3 sm:pt-4">
        <p class="mb-2 font-medium">다운로드</p>
        <div class="grid grid-cols-3 gap-2">
          <button class="rounded-lg border border-mandrong-line bg-[#111412] py-2 text-sm transition hover:border-mandrong-primary" @click="download('png')">PNG</button>
          <button class="rounded-lg border border-mandrong-line bg-[#111412] py-2 text-sm transition hover:border-mandrong-primary" @click="download('jpeg')">JPEG</button>
          <button class="rounded-lg border border-mandrong-line bg-[#111412] py-2 text-sm transition hover:border-mandrong-primary" @click="download('pdf')">PDF</button>
        </div>
        <p v-if="exportError" class="mt-3 text-sm text-mandrong-muted"><Download class="mr-1 inline h-4 w-4" />{{ exportError }}</p>
      </div>
    </aside>
    <Teleport to="body">
      <div v-if="fullView" class="fixed inset-0 z-50 bg-black/88 p-3 backdrop-blur sm:p-6" @click.self="fullView = false">
        <button class="absolute right-4 top-4 flex h-11 w-11 items-center justify-center rounded-lg border border-white/15 bg-white/10 text-white sm:right-6 sm:top-6" @click="fullView = false">
          <X class="h-5 w-5" />
        </button>
        <div class="flex h-full w-full items-center justify-center overflow-auto">
          <img :src="imageSrc" alt="전체 홍보물" class="max-h-none max-w-full rounded-lg" />
        </div>
      </div>
    </Teleport>
  </main>
</template>
