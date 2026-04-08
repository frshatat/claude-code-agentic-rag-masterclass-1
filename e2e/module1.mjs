/**
 * End-to-end validation tests for Module 1: App Shell
 *
 * Run:  node e2e/module1.mjs
 *
 * Tests covered (from plan Phase 3 & 4 validation checklists):
 *  1. Navigate to app root → redirected to /login
 *  2. Login page renders email input + send magic link button
 *  3. /auth/callback route mounts without crashing (pre-auth)
 *  4. Attempting to navigate directly to / without auth → back to /login
 */

import pkg from '/Users/farisshatat/.nvm/versions/node/v24.14.0/lib/node_modules/@playwright/mcp/node_modules/playwright-core/index.js';
const { chromium } = pkg;

const BASE = 'http://localhost:5173';
let passed = 0;
let failed = 0;

function assert(condition, label) {
  if (condition) {
    console.log(`  ✅  ${label}`);
    passed++;
  } else {
    console.error(`  ❌  ${label}`);
    failed++;
  }
}

const browser = await chromium.launch({ headless: true });
const ctx = await browser.newContext();
const page = await ctx.newPage();

// -------------------------------------------------------------------
// Test 1: Root redirects to /login when unauthenticated
// -------------------------------------------------------------------
console.log('\n── Phase 3: Auth flow ─────────────────────────────────────');
await page.goto(BASE + '/');
await page.waitForURL(/\/login/, { timeout: 5000 });
assert(page.url().includes('/login'), 'Root / redirects to /login when unauthenticated');

// -------------------------------------------------------------------
// Test 2: Login page renders the email input
// -------------------------------------------------------------------
const emailInput = page.locator('input[type="email"]');
await emailInput.waitFor({ timeout: 5000 });
assert(await emailInput.isVisible(), 'Login page renders email input');

// -------------------------------------------------------------------
// Test 3: Login page has a submit / send magic link button
// -------------------------------------------------------------------
const submitBtn = page.locator('button[type="submit"], button:has-text("magic"), button:has-text("Sign"), button:has-text("Login"), button:has-text("Send")').first();
await submitBtn.waitFor({ timeout: 5000 });
assert(await submitBtn.isVisible(), 'Login page renders submit button');

// -------------------------------------------------------------------
// Test 4: Direct navigation to / still redirects (protected route)
// -------------------------------------------------------------------
await page.goto(BASE + '/');
await page.waitForURL(/\/login/, { timeout: 5000 });
assert(page.url().includes('/login'), 'Direct navigation to / redirects to /login (protected route guard works)');

// -------------------------------------------------------------------
// Test 5: /auth/callback mounts without a crash
// -------------------------------------------------------------------
let cbError = false;
page.on('pageerror', () => { cbError = true; });
await page.goto(BASE + '/auth/callback');
await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
assert(!cbError, '/auth/callback mounts without a JS crash');

// -------------------------------------------------------------------
// Test 6: Backend /health responds from the browser context
// -------------------------------------------------------------------
console.log('\n── Phase 1: Backend health ─────────────────────────────────');
const resp = await page.request.get('http://127.0.0.1:8000/health');
assert(resp.status() === 200, 'GET /health returns 200');
const body = await resp.json();
assert(body.status === 'ok', 'GET /health body is {"status":"ok"}');

// -------------------------------------------------------------------
// Test 7: Unauthenticated /api/threads returns 403
// -------------------------------------------------------------------
const threadsResp = await page.request.get('http://127.0.0.1:8000/api/threads');
assert(threadsResp.status() === 403, 'GET /api/threads without auth returns 403');

await browser.close();

// -------------------------------------------------------------------
// Summary
// -------------------------------------------------------------------
console.log(`\n── Results ─────────────────────────────────────────────────`);
console.log(`   Passed: ${passed}   Failed: ${failed}`);
if (failed > 0) process.exit(1);
