<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api, apiUrl } from '../api/client'
import FileUploadBox from '../components/FileUploadBox.vue'
import ImagePreview from '../components/ImagePreview.vue'
import PrimaryButton from '../components/PrimaryButton.vue'
import ProcessingOverlay from '../components/ProcessingOverlay.vue'
import { useProjectStore } from '../stores/project'
import type { AnnotationDraft } from '../types/api'

const route = useRoute()
const router = useRouter()
const store = useProjectStore()
const annotations = ref<AnnotationDraft[]>([])
const note = ref('')
const editText = ref('')
const additionalFiles = ref<File[]>([])
const error = ref('')
const submitting = ref(false)
const imageSrc = computed(() => store.currentVersion ? apiUrl(store.currentVersion.image_url) : '')
const canSubmit = computed(() => annotations.value.length > 0 || editText.value.trim().length > 0 || additionalFiles.value.length > 0)

onMounted(() => store.loadVersion(String(route.params.versionId)))

function addNote(event: MouseEvent) {
  const target = event.currentTarget as HTMLElement
  const rect = target.getBoundingClientRect()
  annotations.value.push({
    note: note.value || '이 부분을 자연스럽게 수정해주세요',
    x: Number(((event.clientX - rect.left) / rect.width).toFixed(5)),
    y: Number(((event.clientY - rect.top) / rect.height).toFixed(5)),
    width: null,
    height: null,
    color: 'yellow',
  })
  note.value = ''
}

async function submit() {
  if (!canSubmit.value) {
    error.value = '수정 요청을 입력하거나, 위치 메모 또는 참고 이미지를 추가해주세요.'
    return
  }
  submitting.value = true
  error.value = ''
  try {
    const saved = annotations.value.length
      ? await api.saveAnnotations(String(route.params.versionId), annotations.value)
      : { annotation_ids: [] }
    const additionalAssetIds = []
    for (const file of additionalFiles.value) {
      const asset = await api.uploadAsset(String(route.params.id), 'reference_image', file)
      additionalAssetIds.push(asset.id)
    }
    const job = await api.createEdit(String(route.params.versionId), saved.annotation_ids, editText.value, additionalAssetIds)
    const timer = window.setInterval(async () => {
      const status = await api.getGenerationJob(job.job_id)
      if (status.status === 'succeeded' && status.version_id) {
        window.clearInterval(timer)
        router.push(`/projects/${route.params.id}/compare/${route.params.versionId}/${status.version_id}`)
      }
      if (status.status === 'failed') {
        window.clearInterval(timer)
        error.value = status.error?.message ?? '수정본을 만들지 못했어요.'
      }
    }, 2000)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '수정 요청을 보내지 못했어요.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <main class="mx-auto grid max-w-6xl gap-8 px-6 py-10 lg:grid-cols-[minmax(0,1fr)_360px]">
    <section class="page-enter">
      <div class="relative cursor-crosshair" @click="addNote">
        <ImagePreview v-if="store.currentVersion" :src="imageSrc" alt="수정할 홍보물" />
        <span
          v-for="(item, index) in annotations"
          :key="index"
          class="absolute -translate-x-1/2 -translate-y-1/2 rounded-md bg-mandrong-warning px-3 py-2 text-sm font-semibold text-[#17120A] shadow-lg shadow-black/20"
          :style="{ left: `${item.x * 100}%`, top: `${item.y * 100}%` }"
        >
          {{ index + 1 }}
        </span>
      </div>
    </section>
    <aside class="page-enter rounded-xl border border-mandrong-line bg-mandrong-surface/80 p-5 shadow-2xl shadow-black/20">
      <p class="text-sm font-semibold text-mandrong-primary">수정 단계</p>
      <h1 class="mt-2 text-xl font-semibold">원하는 대로 말해주세요</h1>
      <label class="mt-5 block">
        <span class="mb-2 block font-medium">수정 요청</span>
        <textarea
          v-model="editText"
          class="min-h-32 w-full rounded-lg border border-mandrong-line bg-[#101311] px-4 py-3 leading-7 text-mandrong-text"
          placeholder="예: 메뉴 사진은 그대로 살리고, 문구를 더 크게 넣고, 배경은 고급스럽게 어둡게 바꿔주세요."
        />
      </label>
      <label class="mt-5 block">
        <span class="mb-2 block font-medium">포스트잇 메모</span>
        <textarea v-model="note" class="min-h-24 w-full rounded-lg border border-mandrong-line bg-[#101311] px-4 py-3" placeholder="예: 이 부분의 가격을 더 크게 보여주세요" />
      </label>
      <p class="mt-3 text-sm leading-6 text-mandrong-muted">이미지에서 수정할 위치를 클릭하면 포스트잇이 붙습니다. 위치 지정 없이 요청만 보내도 됩니다.</p>
      <FileUploadBox
        class="mt-5"
        title="추가 참고 이미지"
        description="수정에 반영할 사진이나 시안을 더 붙일 수 있어요"
        multiple
        :max-files="3"
        :files="additionalFiles"
        @change="additionalFiles = $event"
      />
      <ol class="mt-5 space-y-2">
        <li v-for="(item, index) in annotations" :key="index" class="rounded-lg border border-mandrong-line bg-[#101311] p-3 text-sm">
          {{ index + 1 }}. {{ item.note }}
        </li>
      </ol>
      <p v-if="error" class="mt-4 text-mandrong-danger">{{ error }}</p>
      <div class="mt-6 grid grid-cols-2 gap-3">
        <button class="h-12 rounded-lg border border-mandrong-line text-mandrong-muted transition hover:border-mandrong-primary hover:text-mandrong-text" @click="router.back()">취소</button>
        <PrimaryButton :disabled="submitting || !canSubmit" @click="submit">{{ submitting ? '수정본 생성 중' : '수정본 만들기' }}</PrimaryButton>
      </div>
    </aside>
    <ProcessingOverlay
      v-if="submitting"
      title="수정본을 만들고 있어요"
      detail="선택한 기준 이미지와 포스트잇 메모, 추가 참고 이미지를 함께 반영하고 있어요."
    />
  </main>
</template>
