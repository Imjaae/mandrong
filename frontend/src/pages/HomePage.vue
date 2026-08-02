<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight, BookOpen, Check, FileText, Image, Instagram, MoreVertical, Pencil, Plus, Trash2, X } from 'lucide-vue-next'
import { api } from '../api/client'
import PrimaryButton from '../components/PrimaryButton.vue'
import { useDraftStore } from '../stores/draft'
import type { Project, Purpose } from '../types/api'
import adImageUrl from '../../assets/designImages/adImage.png'

const router = useRouter()
const draft = useDraftStore()
const projects = ref<Project[]>([])
const error = ref('')
const activeMenuId = ref('')
const renamingId = ref('')
const renameTitle = ref('')
const quickStarts: { label: string; description: string; purpose: Purpose; icon: typeof FileText }[] = [
  { label: '포스터', description: '이벤트, 신메뉴, 행사 포스터를 손쉽게 제작해보세요.', purpose: 'poster', icon: FileText },
  { label: '배너', description: '웹페이지, 행사 안내, 광고 배너를 빠르게 만들어보세요.', purpose: 'banner', icon: Image },
  { label: 'SNS', description: '인스타그램, 피드와 스토리 홍보 이미지를 제작해보세요.', purpose: 'sns_square', icon: Instagram },
  { label: '메뉴판', description: '깔끔하고 보기 좋은 매장용 메뉴판을 만들어보세요.', purpose: 'menu_board', icon: BookOpen },
]

onMounted(loadProjects)

async function loadProjects() {
  try {
    projects.value = await api.listProjects()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '최근 작업을 불러오지 못했어요.'
  }
}

function startQuick(purpose: Purpose) {
  draft.reset()
  draft.setPurpose(purpose)
  router.push('/projects/new/copy')
}

function statusLabel(status: string) {
  if (status === 'ready') return 'ready'
  if (status === 'generating' || status === 'editing') return 'processing'
  if (status === 'failed') return 'failed'
  return status
}

function openProject(project: Project) {
  router.push(project.current_version_id ? `/projects/${project.id}/result/${project.current_version_id}` : '/projects/new/purpose')
}

function startRename(project: Project) {
  activeMenuId.value = ''
  renamingId.value = project.id
  renameTitle.value = project.title
}

async function saveRename(project: Project) {
  const title = renameTitle.value.trim()
  if (!title) return
  try {
    await api.renameProject(project.id, title)
    renamingId.value = ''
    await loadProjects()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '이름을 변경하지 못했어요.'
  }
}

async function deleteProject(project: Project) {
  activeMenuId.value = ''
  if (!window.confirm(`'${project.title}' 작업을 삭제할까요?`)) return
  try {
    await api.deleteProject(project.id)
    projects.value = projects.value.filter((item) => item.id !== project.id)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '작업을 삭제하지 못했어요.'
  }
}
</script>

<template>
  <main class="mx-auto max-w-7xl px-4 py-6 sm:px-6 sm:py-10 lg:py-14">
    <section class="grid items-center gap-8 sm:gap-10 lg:min-h-[520px] lg:grid-cols-[minmax(0,1fr)_560px] lg:gap-12">
      <div class="mx-auto max-w-2xl text-center lg:mx-0 lg:text-left">
        <span class="inline-flex rounded-full border border-mandrong-primary/30 bg-mandrong-primary/10 px-3 py-2 text-xs font-medium text-mandrong-primary sm:px-4 sm:text-sm">
          메뉴 사진과 문구만 준비하세요
        </span>
        <h1 class="mt-5 text-[32px] font-semibold leading-tight tracking-normal sm:mt-6 sm:text-[52px]">
          오늘 필요한 홍보물을<br class="hidden sm:block" />
          쉽고 빠르게 만들어보세요
        </h1>
        <p class="mx-auto mt-4 max-w-xl text-base leading-7 text-mandrong-muted sm:mt-6 sm:text-lg sm:leading-8 lg:mx-0">
          포스터, 배너, 메뉴판, SNS 이미지까지 복잡한 편집 없이 AI가 한 번에 완성합니다.
        </p>
        <PrimaryButton class="mt-9 gap-2 px-8" @click="router.push('/projects/new/purpose')">
          <Plus class="h-4 w-4" />
          새 홍보물 만들기
        </PrimaryButton>
        <div class="mt-6 flex flex-wrap justify-center gap-3 text-xs font-medium text-mandrong-primary sm:mt-8 sm:gap-5 sm:text-sm lg:justify-start">
          <span>AI 자동 디자인</span>
          <span>간편한 수정</span>
          <span>고퀄리티 다운로드</span>
        </div>
      </div>

      <div class="page-enter">
        <div class="rounded-xl border border-mandrong-line bg-[#121513] p-3 shadow-2xl shadow-black/35">
          <img :src="adImageUrl" alt="만드롱 홍보물 예시" class="block w-full rounded-lg" />
        </div>
      </div>
    </section>

    <section class="mt-8 lg:mt-2">
      <h2 class="mb-4 text-xl font-semibold">빠른 시작</h2>
      <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <button
          v-for="item in quickStarts"
          :key="item.purpose"
          class="group flex min-h-24 items-center gap-3 rounded-lg border border-mandrong-line bg-mandrong-surface/72 p-4 text-left transition hover:-translate-y-0.5 hover:border-mandrong-primary hover:bg-[#1B211D] sm:min-h-28 sm:gap-4 sm:p-5"
          @click="startQuick(item.purpose)"
        >
          <span class="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-mandrong-primary/10 text-mandrong-primary ring-1 ring-mandrong-primary/25 sm:h-14 sm:w-14">
            <component :is="item.icon" class="h-6 w-6 sm:h-7 sm:w-7" />
          </span>
          <span class="min-w-0">
            <span class="flex items-center justify-between gap-3">
              <strong class="text-base sm:text-lg">{{ item.label }}</strong>
              <ArrowRight class="h-4 w-4 text-mandrong-muted transition group-hover:translate-x-1 group-hover:text-mandrong-primary" />
            </span>
            <span class="mt-1 block text-sm leading-6 text-mandrong-muted">{{ item.description }}</span>
          </span>
        </button>
      </div>
    </section>

    <section class="mt-6">
      <div class="mb-4 flex items-end justify-between">
        <h2 class="text-xl font-semibold">최근 작업</h2>
        <span class="text-sm text-mandrong-muted">모두 보기</span>
      </div>
      <p v-if="error" class="mt-4 text-mandrong-danger">{{ error }}</p>
      <div v-else-if="projects.length === 0" class="rounded-lg border border-mandrong-line bg-mandrong-surface px-5 py-8 text-mandrong-muted">
        아직 만든 홍보물이 없어요
      </div>
      <div v-else class="rounded-lg border border-mandrong-line bg-mandrong-surface/72">
        <div
          v-for="project in projects"
          :key="project.id"
          class="relative grid w-full grid-cols-[64px_minmax(0,1fr)_36px] items-center gap-3 border-b border-mandrong-line px-3 py-3 text-left transition last:border-b-0 hover:bg-[#1D211E] sm:grid-cols-[72px_minmax(0,1fr)_86px_88px_36px] sm:px-4 md:grid-cols-[96px_minmax(0,1fr)_120px_92px_72px_32px] md:gap-4 md:px-5"
          @click="openProject(project)"
        >
          <span class="h-12 overflow-hidden rounded-md border border-mandrong-line bg-[#101311] sm:h-14 md:h-12">
            <img v-if="project.current_image_url" :src="project.current_image_url" alt="" class="h-full w-full object-cover" />
          </span>
          <span class="min-w-0">
            <strong v-if="renamingId !== project.id" class="block truncate">{{ project.title }}</strong>
            <span v-else class="flex items-center gap-2">
              <input v-model="renameTitle" class="h-9 min-w-0 flex-1 rounded-lg border border-mandrong-line bg-[#101311] px-3 text-sm" @click.stop @keydown.enter.stop="saveRename(project)" @keydown.esc.stop="renamingId = ''" />
              <button class="flex h-9 w-9 items-center justify-center rounded-lg border border-mandrong-line text-mandrong-primary" @click.stop="saveRename(project)">
                <Check class="h-4 w-4" />
              </button>
              <button class="flex h-9 w-9 items-center justify-center rounded-lg border border-mandrong-line text-mandrong-muted" @click.stop="renamingId = ''">
                <X class="h-4 w-4" />
              </button>
            </span>
            <span class="text-xs text-mandrong-muted sm:text-sm">{{ project.status }}</span>
          </span>
          <span class="hidden text-sm text-mandrong-muted md:block">{{ new Date(project.created_at).toLocaleDateString('ko-KR') }}</span>
          <span
            class="hidden rounded-full px-3 py-1 text-center text-xs font-semibold sm:block"
            :class="{
              'bg-mandrong-primary/10 text-mandrong-primary ring-1 ring-mandrong-primary/25': statusLabel(project.status) === 'ready',
              'bg-mandrong-warning/10 text-mandrong-warning ring-1 ring-mandrong-warning/25': statusLabel(project.status) === 'processing',
              'bg-mandrong-danger/10 text-mandrong-danger ring-1 ring-mandrong-danger/25': statusLabel(project.status) === 'failed',
            }"
          >
            {{ statusLabel(project.status) }}
          </span>
          <button class="hidden h-9 rounded-lg border border-mandrong-line text-sm text-mandrong-text transition hover:border-mandrong-primary md:block" @click.stop="openProject(project)">열기</button>
          <button class="flex h-9 w-9 items-center justify-center rounded-lg text-mandrong-muted transition hover:bg-[#252B27] hover:text-mandrong-text" @click.stop="activeMenuId = activeMenuId === project.id ? '' : project.id">
            <MoreVertical class="h-4 w-4" />
          </button>
          <div v-if="activeMenuId === project.id" class="absolute right-4 top-12 z-10 w-36 rounded-lg border border-mandrong-line bg-[#111412] p-1 shadow-2xl shadow-black/35" @click.stop>
            <button class="flex h-10 w-full items-center gap-2 rounded-md px-3 text-sm text-mandrong-text hover:bg-[#1D211E]" @click="startRename(project)">
              <Pencil class="h-4 w-4" />
              이름 변경
            </button>
            <button class="flex h-10 w-full items-center gap-2 rounded-md px-3 text-sm text-mandrong-danger hover:bg-mandrong-danger/10" @click="deleteProject(project)">
              <Trash2 class="h-4 w-4" />
              삭제
            </button>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>
