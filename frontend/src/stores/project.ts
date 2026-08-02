import { defineStore } from 'pinia'
import { api } from '../api/client'
import type { Version } from '../types/api'

export const useProjectStore = defineStore('project', {
  state: () => ({
    currentVersion: null as Version | null,
    versions: [] as Version[],
    loading: false,
    error: '',
  }),
  actions: {
    async loadVersion(versionId: string) {
      this.loading = true
      this.error = ''
      try {
        this.currentVersion = await api.getVersion(versionId)
      } catch (error) {
        this.error = error instanceof Error ? error.message : '이미지를 불러오지 못했어요.'
      } finally {
        this.loading = false
      }
    },
    async loadVersions(projectId: string) {
      this.loading = true
      this.error = ''
      try {
        this.versions = await api.listVersions(projectId)
      } catch (error) {
        this.error = error instanceof Error ? error.message : '히스토리를 불러오지 못했어요.'
      } finally {
        this.loading = false
      }
    },
  },
})
