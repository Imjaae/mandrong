<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api/client'
import PrimaryButton from '../components/PrimaryButton.vue'
import ProcessingOverlay from '../components/ProcessingOverlay.vue'
import StepShell from '../components/StepShell.vue'
import { defaultSizes, displaySizes, purposeLabels, roundUpToImageStep } from '../stores/draft'
import type { Purpose } from '../types/api'

const route = useRoute()
const router = useRouter()
const selected = ref<Purpose>('sns_story')
const sizeMode = ref<'preset' | 'custom'>('preset')
const customWidth = ref(1080)
const customHeight = ref(1920)
const error = ref('')
const submitting = ref(false)

function selectPurpose(purpose: Purpose) {
  selected.value = purpose
  if (sizeMode.value === 'preset') {
    customWidth.value = defaultSizes[purpose].width
    customHeight.value = defaultSizes[purpose].height
  }
}

async function submit() {
  submitting.value = true
  error.value = ''
  try {
    const size = sizeMode.value === 'custom'
      ? { width: roundUpToImageStep(customWidth.value), height: roundUpToImageStep(customHeight.value) }
      : defaultSizes[selected.value]
    const job = await api.createReframe(String(route.params.versionId), { purpose: selected.value, ...size })
    const timer = window.setInterval(async () => {
      const status = await api.getGenerationJob(job.job_id)
      if (status.status === 'succeeded' && status.version_id) {
        window.clearInterval(timer)
        router.push(`/projects/${route.params.id}/result/${status.version_id}`)
      }
      if (status.status === 'failed') {
        window.clearInterval(timer)
        submitting.value = false
        error.value = status.error?.message ?? '다른 비율로 만들지 못했어요.'
      }
    }, 2000)
  } catch (err) {
    submitting.value = false
    error.value = err instanceof Error ? err.message : '요청을 보내지 못했어요.'
  }
}
</script>

<template>
  <StepShell title="다른 비율로 다시 구성해요" subtitle="기존 내용을 유지하면서 새 크기에 맞게 배치합니다." :show-progress="false">
    <div class="grid gap-3 sm:grid-cols-2">
      <button
        v-for="(label, key) in purposeLabels"
        :key="key"
        class="rounded-lg border px-5 py-5 text-left"
        :class="selected === key ? 'border-mandrong-primary bg-[#1D2A24]' : 'border-mandrong-line bg-[#111412]'"
        @click="selectPurpose(key)"
      >
        <strong>{{ label }}</strong>
        <span class="mt-2 block text-sm text-mandrong-muted">{{ displaySizes[key] }}</span>
        <span v-if="key === 'x_banner'" class="mt-1 block text-xs text-mandrong-muted">생성 크기 608x1808</span>
      </button>
    </div>
    <section class="mt-8 border-t border-mandrong-line pt-6">
      <div class="flex rounded-lg border border-mandrong-line bg-[#0F1210] p-1">
        <button class="h-10 flex-1 rounded-md text-sm font-medium" :class="sizeMode === 'preset' ? 'bg-mandrong-primary text-[#0E100F]' : 'text-mandrong-muted'" @click="sizeMode = 'preset'; selectPurpose(selected)">
          기본 크기
        </button>
        <button class="h-10 flex-1 rounded-md text-sm font-medium" :class="sizeMode === 'custom' ? 'bg-mandrong-primary text-[#0E100F]' : 'text-mandrong-muted'" @click="sizeMode = 'custom'">
          직접 지정
        </button>
      </div>
      <div v-if="sizeMode === 'custom'" class="mt-5 grid gap-4 sm:grid-cols-2">
        <label class="block">
          <span class="mb-2 block font-medium">가로 크기</span>
          <div class="flex h-12 items-center rounded-lg border border-mandrong-line bg-[#101311] px-4">
            <input v-model.number="customWidth" type="number" min="256" max="4096" step="16" class="w-full bg-transparent outline-none" @blur="customWidth = roundUpToImageStep(customWidth)" />
            <span class="text-sm text-mandrong-muted">px</span>
          </div>
        </label>
        <label class="block">
          <span class="mb-2 block font-medium">세로 크기</span>
          <div class="flex h-12 items-center rounded-lg border border-mandrong-line bg-[#101311] px-4">
            <input v-model.number="customHeight" type="number" min="256" max="4096" step="16" class="w-full bg-transparent outline-none" @blur="customHeight = roundUpToImageStep(customHeight)" />
            <span class="text-sm text-mandrong-muted">px</span>
          </div>
        </label>
      </div>
      <p v-if="sizeMode === 'custom'" class="mt-3 text-sm text-mandrong-muted">16px 단위로 자동 조정됩니다. 현재 생성 크기: {{ roundUpToImageStep(customWidth) }}x{{ roundUpToImageStep(customHeight) }}</p>
    </section>
    <p v-if="error" class="mt-5 text-mandrong-danger">{{ error }}</p>
    <div class="mt-10 flex justify-end">
      <PrimaryButton :disabled="submitting" @click="submit">{{ submitting ? '재구성 중' : '새 비율로 만들기' }}</PrimaryButton>
    </div>
    <ProcessingOverlay
      v-if="submitting"
      title="새 비율로 재구성하고 있어요"
      detail="기존 결과를 기준으로 문구와 음식 이미지를 유지하면서 화면 비율에 맞춰 다시 배치하고 있어요."
    />
  </StepShell>
</template>
