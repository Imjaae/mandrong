<script setup lang="ts">
import { RouterView } from 'vue-router'
import logoUrl from '../assets/designImages/mandrong logo.png'
</script>

<template>
  <div class="min-h-screen bg-mandrong-bg text-mandrong-text">
    <header class="sticky top-0 z-20 border-b border-mandrong-line bg-[#0E100F]/88 backdrop-blur">
      <div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6 sm:py-4">
        <RouterLink to="/" class="flex items-center gap-3 text-lg font-semibold">
          <img :src="logoUrl" alt="MANDRONG" class="h-9 w-auto max-w-[152px] object-contain sm:h-10 sm:max-w-[180px]" />
        </RouterLink>
        <span class="rounded-full border border-mandrong-line bg-mandrong-surface px-3 py-1 text-xs text-mandrong-muted sm:text-sm">AI 홍보물 제작</span>
      </div>
    </header>
    <RouterView />
  </div>
</template>
