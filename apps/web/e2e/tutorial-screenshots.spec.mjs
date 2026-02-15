import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { test } from '@playwright/test';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const outputDir = path.resolve(__dirname, '../../../docs/tutorials/assets/screenshots/workflow');

function ensureDir() {
  fs.mkdirSync(outputDir, { recursive: true });
}

async function save(page, name) {
  await page.screenshot({
    path: path.join(outputDir, name),
    fullPage: true,
  });
}

test.describe('Tutorial workflow screenshots', () => {
  test('capture current shipped GUI workflow views', async ({ page }) => {
    ensureDir();

    await page.goto('/', { waitUntil: 'networkidle' });
    await save(page, '01-home-overview.png');

    const projectCards = page.locator('.project-card');
    if (await projectCards.count()) {
      await projectCards.first().click();
    } else {
      const uniqueKey = `TUT-${Date.now()}`;
      await page.getByRole('button', { name: '+ Create New Project' }).click();
      await page.locator('input[placeholder="e.g., PROJ001"]').fill(uniqueKey);
      await page.locator('input[placeholder="e.g., My Project"]').fill('Tutorial Visual Walkthrough');
      await page.getByRole('button', { name: 'Create Project' }).click();
    }

    await page.waitForSelector('.project-view');
    await save(page, '02-project-commands-tab.png');

    const commandCards = page.locator('.command-card');
    if (await commandCards.count()) {
      await commandCards.first().click();
      await save(page, '03-command-selection.png');
    }

    await page.getByRole('button', { name: /Artifacts/i }).click();
    await page.waitForSelector('.artifacts-list');
    await save(page, '04-artifacts-tab.png');

    const artifactCards = page.locator('.artifact-card');
    if (await artifactCards.count()) {
      await artifactCards.first().click();
      await page.waitForSelector('.artifact-viewer-overlay');
      await save(page, '05-artifact-viewer.png');
    }
  });
});
