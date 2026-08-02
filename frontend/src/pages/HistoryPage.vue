<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProjectStore } from '../stores/project'

const route = useRoute()
const router = useRouter()
const store = useProjectStore()

onMounted(() => store.loadVersions(String(route.params.id)))
</script>

<template>
  <main class="mx-auto flex h-[calc(100dvh-73px)] max-w-6xl flex-col overflow-hidden px-3 py-3 sm:px-6 sm:py-6">
    <div class="flex items-center justify-between">
      <h1 class="text-[24px] font-semibold sm:text-[28px]">히스토리</h1>
      <button class="h-10 rounded-lg border border-mandrong-line px-4 text-sm text-mandrong-muted transition hover:border-mandrong-primary hover:text-mandrong-text" @click="router.back()">이전</button>
    </div>
    <p v-if="store.error" class="mt-4 text-mandrong-danger">{{ store.error }}</p>
    <div class="mt-4 grid min-h-0 flex-1 auto-rows-[minmax(0,1fr)] gap-3 overflow-y-auto sm:mt-6 sm:grid-cols-2 sm:gap-4 lg:grid-cols-3">
      <button
        v-for="version in store.versions"
        :key="version.id"
        class="grid min-h-0 grid-cols-[92px_minmax(0,1fr)] gap-3 rounded-lg border border-mandrong-line bg-mandrong-surface/72 p-3 text-left transition hover:border-mandrong-primary hover:bg-[#1D211E] sm:block"
        @click="router.push(`/projects/${route.params.id}/result/${version.id}`)"
      >
        <div class="flex h-24 min-h-0 items-center justify-center overflow-hidden rounded-lg bg-[#101311] sm:h-[calc(100%-52px)]">
          <img :src="version.image_url" :alt="`버전 ${version.version_number}`" class="max-h-full max-w-full object-contain" />
        </div>
        <span class="min-w-0">
          <strong class="mt-1 block sm:mt-3">버전 {{ version.version_number }}</strong>
          <span class="text-sm text-mandrong-muted">{{ version.summary }}</span>
        </span>
      </button>
    </div>
  </main>
</template>
