<script setup lang="ts">
defineProps<{
  src: string
  alt: string
}>()
</script>

<template>
  <div class="overflow-hidden rounded-lg border border-mandrong-line bg-[#101311] shadow-2xl shadow-black/25">
    <img :src="src" :alt="alt" class="result-reveal block h-auto w-full" />
  </div>
</template>
