<script setup lang="ts">
defineProps<{
  disabled?: boolean
  type?: 'button' | 'submit'
}>()
</script>

<template>
  <button
    :type="type ?? 'button'"
    :disabled="disabled"
    class="inline-flex h-12 items-center justify-center rounded-lg bg-mandrong-primary px-6 text-[15px] font-semibold text-[#0E100F] shadow-[0_12px_24px_rgba(116,212,179,0.18)] transition hover:-translate-y-0.5 hover:bg-mandrong-primaryHover disabled:translate-y-0 disabled:bg-[#3B453F] disabled:text-mandrong-muted disabled:shadow-none"
  >
    <slot />
  </button>
</template>
