<script setup lang="ts">
defineProps<{
  title: string
  detail: string
}>()
</script>

<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/78 px-5 backdrop-blur">
      <div class="w-full max-w-sm rounded-xl border border-mandrong-line bg-[#111412] p-5 text-center shadow-2xl shadow-black/40">
        <div class="waiting-frame mx-auto aspect-[4/5] w-36 rounded-lg border border-mandrong-line p-4">
          <div class="flex h-full flex-col justify-between rounded-md bg-[#0F1210]/88 p-3">
            <div class="space-y-2">
              <div class="h-2.5 w-12 rounded-full bg-mandrong-primary/70" />
              <div class="h-5 w-20 rounded bg-[#30382F]" />
              <div class="h-5 w-16 rounded bg-[#242B25]" />
            </div>
            <div class="h-14 rounded-md bg-[#1D2A24]" />
          </div>
        </div>
        <h2 class="mt-5 text-xl font-semibold">{{ title }}</h2>
        <p class="mt-2 text-sm leading-6 text-mandrong-muted">{{ detail }}</p>
      </div>
    </div>
  </Teleport>
</template>
