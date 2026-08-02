<script setup lang="ts">
import { computed, ref } from 'vue'
import { ImagePlus, UploadCloud } from 'lucide-vue-next'

const props = defineProps<{
  title: string
  description: string
  multiple?: boolean
  maxFiles?: number
  files: File[]
}>()

const emit = defineEmits<{
  change: [files: File[]]
}>()

const input = ref<HTMLInputElement | null>(null)
const fileLabel = computed(() => {
  if (props.files.length === 0) return props.description
  if (props.files.length === 1) return props.files[0].name
  return `${props.files.length}개 선택됨`
})

function openPicker() {
  input.value?.click()
}

function onChange(event: Event) {
  const files = Array.from((event.target as HTMLInputElement).files ?? [])
  emit('change', props.maxFiles ? files.slice(0, props.maxFiles) : files)
}
</script>

<template>
  <div class="rounded-lg border border-mandrong-line bg-[#111412] p-3">
    <button
      type="button"
      class="group w-full rounded-lg border border-dashed border-[#3A423C] bg-[#0F1210] px-5 py-6 text-left transition hover:border-mandrong-primary hover:bg-[#151A16]"
      @click="openPicker"
    >
      <input ref="input" type="file" accept="image/jpeg,image/png,image/webp" :multiple="multiple" class="hidden" @change="onChange" />
      <span class="flex items-start gap-4">
        <span class="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-[#1D2A24] text-mandrong-primary transition group-hover:scale-105">
          <ImagePlus v-if="files.length" class="h-5 w-5" />
          <UploadCloud v-else class="h-5 w-5" />
        </span>
        <span class="min-w-0">
          <strong class="block text-[15px]">{{ title }}</strong>
          <span class="mt-1 block truncate text-sm text-mandrong-muted">{{ fileLabel }}</span>
          <span class="mt-3 inline-flex rounded-full bg-[#171B18] px-3 py-1 text-xs font-medium text-mandrong-primary ring-1 ring-mandrong-line">
            파일 선택
          </span>
        </span>
      </span>
    </button>
    <div v-if="files.length" class="mt-3 flex flex-wrap gap-2">
      <span v-for="file in files" :key="file.name" class="max-w-full truncate rounded-full bg-[#1D2A24] px-3 py-1 text-xs text-mandrong-primary">
        {{ file.name }}
      </span>
    </div>
  </div>
</template>
