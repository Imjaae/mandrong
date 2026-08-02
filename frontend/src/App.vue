<script setup lang="ts">
import { RouterView } from 'vue-router'
import logoUrl from '../assets/designImages/mandrong-logo-header.png'
</script>

<template>
  <div class="min-h-screen bg-mandrong-bg text-mandrong-text">
    <header class="sticky top-0 z-20 border-b border-mandrong-line bg-[#0E100F]/88 backdrop-blur">
      <div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6 sm:py-4">
        <RouterLink to="/" class="flex items-center gap-3 text-lg font-semibold">
          <img :src="logoUrl" alt="MANDRONG" class="h-11 w-auto max-w-[210px] object-contain sm:h-12 sm:max-w-[260px]" />
        </RouterLink>
      </div>
    </header>
    <RouterView />
  </div>
</template>
