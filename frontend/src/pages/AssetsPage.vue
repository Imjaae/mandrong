<script setup lang="ts">
import { useRouter } from 'vue-router'
import StepShell from '../components/StepShell.vue'
import PrimaryButton from '../components/PrimaryButton.vue'
import FileUploadBox from '../components/FileUploadBox.vue'
import { useDraftStore } from '../stores/draft'

const router = useRouter()
const draft = useDraftStore()

function setMenuFiles(files: File[]) {
  draft.menuFiles = files.slice(0, 8)
}

function setLogoFile(files: File[]) {
  draft.logoFile = files[0] ?? null
  if (draft.logoFile) {
    draft.useLogo = true
  }
}
</script>

<template>
  <StepShell title="사진과 매장 정보를 선택해주세요" subtitle="음식 사진이 없어도 진행할 수 있지만, 사진이 있으면 더 정확합니다.">
    <div class="space-y-6">
      <FileUploadBox
        title="메뉴 사진"
        description="JPG, PNG, WEBP 파일을 최대 8개까지 선택"
        multiple
        :max-files="8"
        :files="draft.menuFiles"
        @change="setMenuFiles"
      />
      <section class="rounded-lg border border-mandrong-line bg-[#111412] p-5">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 class="font-semibold">매장 로고</h2>
            <p class="mt-1 text-sm text-mandrong-muted">로고는 미리 등록해두고, 이번 작업에 사용할지만 선택합니다.</p>
          </div>
          <label class="flex items-center gap-3 text-sm font-medium">
            <input v-model="draft.useLogo" type="checkbox" class="h-5 w-5 accent-mandrong-primary" :disabled="!draft.logoFile" />
            이번 작업에 로고 사용
          </label>
        </div>
        <FileUploadBox
          class="mt-4"
          title="로고 파일"
          description="로고 이미지를 한 개 선택"
          :max-files="1"
          :files="draft.logoFile ? [draft.logoFile] : []"
          @change="setLogoFile"
        />
      </section>
      <div class="grid gap-4 sm:grid-cols-2">
        <label class="block">
          <span class="field-label">매장명</span>
          <input v-model="draft.store_name" class="field-input" />
        </label>
        <label class="block">
          <span class="field-label">메뉴명</span>
          <input v-model="draft.menu_name" class="field-input" />
        </label>
        <label class="block">
          <span class="field-label">가격</span>
          <input v-model="draft.price" class="field-input" />
        </label>
        <label class="block">
          <span class="field-label">지역 또는 주소</span>
          <input v-model="draft.store_location" class="field-input" />
        </label>
      </div>
      <label class="block">
        <span class="field-label">전화번호 또는 주문 방법</span>
        <input v-model="draft.contact" class="field-input" />
      </label>
    </div>
    <div class="mt-10 flex justify-between">
      <button class="h-12 rounded-lg border border-mandrong-line bg-[#111412] px-5 text-mandrong-muted transition hover:border-mandrong-primary hover:text-mandrong-text" @click="router.back()">이전</button>
      <PrimaryButton @click="router.push('/projects/new/style')">다음</PrimaryButton>
    </div>
  </StepShell>
</template>
