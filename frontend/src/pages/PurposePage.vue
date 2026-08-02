<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import StepShell from '../components/StepShell.vue'
import PrimaryButton from '../components/PrimaryButton.vue'
import { displaySizes, purposeLabels, useDraftStore } from '../stores/draft'
import type { Purpose } from '../types/api'

const router = useRouter()
const draft = useDraftStore()
const purposes = Object.entries(purposeLabels) as [Purpose, string][]
const canNext = computed(() => draft.size.width >= 256 && draft.size.height >= 256 && draft.size.width <= 4096 && draft.size.height <= 4096)

function goNext() {
  if (draft.sizeMode === 'custom') {
    draft.normalizeCustomSize()
  }
  router.push('/projects/new/copy')
}
</script>

<template>
  <StepShell title="어디에 쓸 홍보물인가요?" subtitle="기본 크기로 시작하거나 직접 가로와 세로를 지정할 수 있어요.">
    <div class="grid gap-3 sm:grid-cols-2">
      <button
        v-for="[value, label] in purposes"
        :key="value"
        class="rounded-lg border bg-[#111412] px-5 py-5 text-left transition hover:-translate-y-0.5 hover:border-mandrong-primary hover:bg-[#151A16] hover:shadow-sm"
        :class="draft.purpose === value ? 'border-mandrong-primary ring-4 ring-mandrong-primary/10' : 'border-mandrong-line'"
        @click="draft.setPurpose(value)"
      >
        <span class="flex items-center justify-between gap-3">
          <strong class="block">{{ label }}</strong>
          <span v-if="draft.purpose === value" class="h-2.5 w-2.5 rounded-full bg-mandrong-primary" />
        </span>
        <span class="mt-2 block text-sm text-mandrong-muted">{{ displaySizes[value] }}</span>
        <span v-if="value === 'x_banner'" class="mt-1 block text-xs text-mandrong-muted">생성 크기 608x1808</span>
      </button>
    </div>

    <section class="mt-8 rounded-lg border border-mandrong-line bg-[#111412] p-4">
      <div class="flex rounded-lg border border-mandrong-line bg-[#0F1210] p-1">
        <button
          class="h-10 flex-1 rounded-md text-sm font-medium"
          :class="draft.sizeMode === 'preset' ? 'bg-mandrong-primary text-[#0E100F]' : 'text-mandrong-muted'"
          @click="draft.usePresetSize()"
        >
          기본 크기
        </button>
        <button
          class="h-10 flex-1 rounded-md text-sm font-medium"
          :class="draft.sizeMode === 'custom' ? 'bg-mandrong-primary text-[#0E100F]' : 'text-mandrong-muted'"
          @click="draft.useCustomSize()"
        >
          직접 지정
        </button>
      </div>

      <div v-if="draft.sizeMode === 'custom'" class="mt-5 grid gap-4 sm:grid-cols-2">
        <label class="block">
          <span class="field-label">가로 크기</span>
          <div class="flex h-12 items-center rounded-lg border border-mandrong-line bg-[#101311] px-4">
            <input v-model.number="draft.customWidth" type="number" min="256" max="4096" step="16" class="w-full bg-transparent outline-none" @blur="draft.normalizeCustomSize()" />
            <span class="text-sm text-mandrong-muted">px</span>
          </div>
        </label>
        <label class="block">
          <span class="field-label">세로 크기</span>
          <div class="flex h-12 items-center rounded-lg border border-mandrong-line bg-[#101311] px-4">
            <input v-model.number="draft.customHeight" type="number" min="256" max="4096" step="16" class="w-full bg-transparent outline-none" @blur="draft.normalizeCustomSize()" />
            <span class="text-sm text-mandrong-muted">px</span>
          </div>
        </label>
        <p class="text-sm text-mandrong-muted sm:col-span-2">이미지 생성 규칙에 맞게 16px 단위로 자동 조정됩니다. 현재 생성 크기: {{ draft.size.width }}x{{ draft.size.height }}</p>
      </div>
    </section>

    <div class="mt-10 flex justify-end">
      <PrimaryButton :disabled="!canNext" @click="goNext">다음</PrimaryButton>
    </div>
  </StepShell>
</template>
