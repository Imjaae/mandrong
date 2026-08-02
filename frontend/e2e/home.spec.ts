import { expect, test } from '@playwright/test'

test('shows the new project entry point', async ({ page }) => {
  await page.route('**/api/v1/projects', async (route) => {
    await route.fulfill({ json: [] })
  })
  await page.goto('/')
  await expect(page.getByRole('button', { name: /새 홍보물 만들기/ })).toBeVisible()
  await expect(page.getByText('아직 만든 홍보물이 없어요')).toBeVisible()
})

test('fits the home screen on iPhone width without horizontal overflow', async ({ page }) => {
  await page.setViewportSize({ width: 393, height: 852 })
  await page.route('**/api/v1/projects', async (route) => {
    await route.fulfill({
      json: [
        {
          id: 'project-1',
          title: '가을 신메뉴 포스터',
          status: 'ready',
          current_version_id: 'version-1',
          current_image_url: null,
          created_at: '2026-08-02T09:00:00Z',
        },
      ],
    })
  })
  await page.goto('/')
  await expect(page.getByRole('button', { name: /새 홍보물 만들기/ })).toBeVisible()

  const hasHorizontalOverflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth)
  expect(hasHorizontalOverflow).toBe(false)
})
