<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import StepShell from '../components/StepShell.vue'
import PrimaryButton from '../components/PrimaryButton.vue'
import { useDraftStore } from '../stores/draft'

const router = useRouter()
const draft = useDraftStore()
const canNext = computed(() => {
  const length = draft.promotionText.trim().length
  return length > 0 && length <= 1000
})
</script>

<template>
  <StepShell title="홍보 문구를 적어주세요" subtitle="가격, 혜택, 안내 문구까지 한 번에 적으면 됩니다.">
    <label class="block">
      <span class="field-label">넣고 싶은 문구</span>
      <textarea
        v-model="draft.promotionText"
        class="min-h-64 w-full rounded-lg border border-mandrong-line bg-[#101311] px-4 py-4 leading-7"
        maxlength="1000"
        placeholder="예: 오늘 점심은 따뜻한 갈비탕&#10;진한 국물과 푸짐한 고기&#10;평일 점심 한정 9,900원"
      />
      <span class="mt-2 block text-sm" :class="draft.promotionText.length > 1000 ? 'text-mandrong-danger' : 'text-mandrong-muted'">
        {{ draft.promotionText.length }}/1000자
      </span>
    </label>
    <div class="mt-10 flex justify-between">
      <button class="h-12 rounded-lg border border-mandrong-line px-5 text-mandrong-muted transition hover:border-mandrong-primary hover:text-mandrong-text" @click="router.push('/projects/new/purpose')">이전</button>
      <PrimaryButton :disabled="!canNext" @click="router.push('/projects/new/assets')">다음</PrimaryButton>
    </div>
  </StepShell>
</template>
