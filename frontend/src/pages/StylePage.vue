<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/client'
import StepShell from '../components/StepShell.vue'
import PrimaryButton from '../components/PrimaryButton.vue'
import FileUploadBox from '../components/FileUploadBox.vue'
import { useDraftStore } from '../stores/draft'

const router = useRouter()
const draft = useDraftStore()
const loading = ref(false)
const error = ref('')
const moods = ['깔끔한', '따뜻한', '고급스러운', '활기찬', '전통적인', '귀여운', '프리미엄', '가성비 좋은']
const canSubmit = computed(() => draft.mood_keywords.length > 0 || draft.mood_text.trim().length > 0)

function toggleMood(mood: string) {
  draft.mood_keywords = draft.mood_keywords.includes(mood)
    ? draft.mood_keywords.filter((item) => item !== mood)
    : [...draft.mood_keywords, mood]
}

function setReferenceFiles(files: File[]) {
  draft.referenceFiles = files.slice(0, 3)
}

async function submit() {
  loading.value = true
  error.value = ''
  try {
    const project = await api.createProject(draft.title, draft.brief)
    draft.projectId = project.id
    draft.menuAssetIds = []
    draft.logoAssetIds = []
    draft.referenceAssetIds = []
    draft.activeGenerationProjectId = ''
    draft.activeGenerationJobId = ''
    for (const file of draft.menuFiles) {
      const asset = await api.uploadAsset(project.id, 'menu_photo', file)
      draft.menuAssetIds.push(asset.id)
    }
    for (const file of draft.referenceFiles) {
      const asset = await api.uploadAsset(project.id, 'reference_image', file)
      draft.referenceAssetIds.push(asset.id)
    }
    if (draft.useLogo && draft.logoFile) {
      const asset = await api.uploadAsset(project.id, 'reference_image', draft.logoFile)
      draft.logoAssetIds.push(asset.id)
    }
    router.push(`/projects/${project.id}/generate`)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '작업을 만들지 못했어요.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <StepShell title="원하는 분위기를 알려주세요" subtitle="참고 이미지는 선택 사항입니다.">
    <div class="flex flex-wrap gap-2">
      <button
        v-for="mood in moods"
        :key="mood"
        class="rounded-full border px-4 py-2 text-sm font-medium transition hover:border-mandrong-primary"
        :class="draft.mood_keywords.includes(mood) ? 'border-mandrong-primary bg-[#1D2A24] text-mandrong-primary' : 'border-mandrong-line bg-[#111412] text-mandrong-muted'"
        @click="toggleMood(mood)"
      >
        {{ mood }}
      </button>
    </div>
    <label class="mt-6 block">
      <span class="field-label">추가 설명</span>
      <textarea v-model="draft.mood_text" class="min-h-32 w-full rounded-lg border border-mandrong-line bg-[#101311] px-4 py-3 leading-7" placeholder="예: 따뜻한 동네 식당 느낌, 너무 화려하지 않게" />
    </label>
    <FileUploadBox
      class="mt-6"
      title="참고 디자인 이미지"
      description="원하는 분위기의 이미지를 최대 3개까지 선택"
      multiple
      :max-files="3"
      :files="draft.referenceFiles"
      @change="setReferenceFiles"
    />
    <p v-if="error" class="mt-5 text-mandrong-danger">{{ error }}</p>
    <div class="mt-10 flex justify-between">
      <button class="h-12 rounded-lg border border-mandrong-line bg-[#111412] px-5 text-mandrong-muted transition hover:border-mandrong-primary hover:text-mandrong-text" @click="router.back()">이전</button>
      <PrimaryButton :disabled="!canSubmit || loading" @click="submit">{{ loading ? '저장 중' : '홍보물 만들기' }}</PrimaryButton>
    </div>
  </StepShell>
</template>
