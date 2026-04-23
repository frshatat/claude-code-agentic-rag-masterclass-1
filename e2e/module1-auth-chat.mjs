/**
 * End-to-end validation: password sign-in + chat creation flow.
 *
 * Updates PROGRESS.md as each phase completes.
 *
 * Run:
 *   TEST_EMAIL="test@test.com" TEST_PASSWORD='$1MhDupRhDqzqGY' node e2e/module1-auth-chat.mjs
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const PROGRESS_PATH = path.join(ROOT, 'PROGRESS.md');

// Load .env files
function loadEnvFile(filePath) {
  if (!fs.existsSync(filePath)) return;
  for (const line of fs.readFileSync(filePath, 'utf8').split('\n')) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const idx = trimmed.indexOf('=');
    if (idx === -1) continue;
    const key = trimmed.slice(0, idx).trim();
    const val = trimmed.slice(idx + 1).trim().replace(/^["']|["']$/g, '');
    if (!process.env[key]) process.env[key] = val;
  }
}
loadEnvFile(path.join(ROOT, 'backend', '.env'));
loadEnvFile(path.join(ROOT, 'frontend', '.env'));

// PROGRESS.md updater — marks a line [ ] or [-] as [x]
function markDone(label) {
  if (!fs.existsSync(PROGRESS_PATH)) return;
  let content = fs.readFileSync(PROGRESS_PATH, 'utf8');
  // Match lines with [ ] or [-] containing the label text
  const re = new RegExp(`(- )\\[[ -]\\]( .*${escapeRe(label)}.*)`, 'g');
  content = content.replace(re, '$1[x]$2');
  fs.writeFileSync(PROGRESS_PATH, content, 'utf8');
}
function markInProgress(label) {
  if (!fs.existsSync(PROGRESS_PATH)) return;
  let content = fs.readFileSync(PROGRESS_PATH, 'utf8');
  const re = new RegExp(`(- )\\[ \\]( .*${escapeRe(label)}.*)`, 'g');
  content = content.replace(re, '$1[-]$2');
  fs.writeFileSync(PROGRESS_PATH, content, 'utf8');
}
function escapeRe(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

import pkg from '/Users/farisshatat/.nvm/versions/node/v24.14.0/lib/node_modules/@playwright/mcp/node_modules/playwright-core/index.js';
const { chromium } = pkg;

const BASE = process.env.BASE_URL ?? 'http://localhost:5173';
const BACKEND_BASE_URL = process.env.BACKEND_BASE_URL ?? 'http://127.0.0.1:8000';
const TEST_EMAIL = process.env.TEST_EMAIL ?? '';
const TEST_PASSWORD = process.env.TEST_PASSWORD ?? '';
const SUPABASE_URL = process.env.SUPABASE_URL ?? process.env.VITE_SUPABASE_URL ?? '';
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY ?? process.env.VITE_SUPABASE_ANON_KEY ?? '';
const LLM_API_ENDPOINT = process.env.LLM_API_ENDPOINT ?? '';
const LLM_API_KEY = process.env.LLM_API_KEY ?? '';
const LLM_MODEL_NAME = process.env.LLM_MODEL_NAME ?? 'openai/gpt-3.5-turbo';
const EMBEDDING_API_ENDPOINT = process.env.EMBEDDING_API_ENDPOINT ?? LLM_API_ENDPOINT;
const EMBEDDING_API_KEY = process.env.EMBEDDING_API_KEY ?? LLM_API_KEY;
const EMBEDDING_MODEL_NAME = process.env.EMBEDDING_MODEL_NAME ?? 'text-embedding-3-small';
const EMBEDDING_DIMENSIONS = Number.parseInt(process.env.EMBEDDING_DIMENSIONS ?? '1536', 10);

let passed = 0;
let failed = 0;

function assert(condition, label, details) {
  if (condition) {
    console.log(`  \u2705  ${label}`);
    passed += 1;
  } else {
    failed += 1;
    console.error(`  \u274c  ${label}`);
    if (details) console.error(`      ${details}`);
  }
  return condition;
}

// ---------------------------------------------------------------------------
// Pre-flight
// ---------------------------------------------------------------------------
console.log('\n\u2500\u2500 Pre-flight \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500');
assert(Boolean(TEST_EMAIL), 'TEST_EMAIL is set', 'export TEST_EMAIL=test@test.com');
assert(Boolean(TEST_PASSWORD), 'TEST_PASSWORD is set', "export TEST_PASSWORD='...'");
assert(Boolean(SUPABASE_URL), 'SUPABASE_URL resolved');
assert(Boolean(SUPABASE_ANON_KEY), 'SUPABASE_ANON_KEY resolved');
assert(Boolean(LLM_API_ENDPOINT), 'LLM_API_ENDPOINT resolved from env');
assert(Boolean(LLM_API_KEY), 'LLM_API_KEY resolved from env');

if (!TEST_EMAIL || !TEST_PASSWORD || !SUPABASE_URL || !SUPABASE_ANON_KEY || !LLM_API_ENDPOINT || !LLM_API_KEY) {
  console.error('\nFatal: missing required env vars. Aborting.');
  process.exit(1);
}

// ---------------------------------------------------------------------------
// Phase 1: Verify password grant works via REST (smoke-test credentials)
// ---------------------------------------------------------------------------
console.log('\n\u2500\u2500 Phase 1: Password sign-in (REST) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500');

const tokenResp = await fetch(`${SUPABASE_URL}/auth/v1/token?grant_type=password`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'apikey': SUPABASE_ANON_KEY },
  body: JSON.stringify({ email: TEST_EMAIL, password: TEST_PASSWORD }),
});
const tokenBody = await tokenResp.json();
const restOk = assert(tokenResp.ok, `REST password grant accepted (${tokenResp.status})`,
  JSON.stringify(tokenBody).slice(0, 300));
assert(Boolean(tokenBody.access_token), 'access_token in REST response');

if (!restOk) {
  console.error('\nFatal: invalid credentials. Aborting.');
  process.exit(1);
}

// ---------------------------------------------------------------------------
// Phase 1b: Ensure model settings exist for this user (required for chat stream)
// ---------------------------------------------------------------------------
console.log('\n── Phase 1b: Seed model settings for test account ─────────────────────');

const settingsResp = await fetch(`${BACKEND_BASE_URL}/api/settings/model-config`, {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${tokenBody.access_token}`,
  },
  body: JSON.stringify({
    llm_model_name: LLM_MODEL_NAME,
    llm_base_url: LLM_API_ENDPOINT,
    llm_api_key: LLM_API_KEY,
    embedding_model_name: EMBEDDING_MODEL_NAME,
    embedding_base_url: EMBEDDING_API_ENDPOINT,
    embedding_api_key: EMBEDDING_API_KEY,
    embedding_dimensions: EMBEDDING_DIMENSIONS,
  }),
});

const settingsBody = await settingsResp.json().catch(() => null);
assert(
  settingsResp.ok,
  `Model settings seed succeeded (${settingsResp.status})`,
  settingsBody ? JSON.stringify(settingsBody).slice(0, 300) : undefined,
);

// ---------------------------------------------------------------------------
// Phase 2: Browser — sign in via password UI
// ---------------------------------------------------------------------------
console.log('\n\u2500\u2500 Phase 2: UI password sign-in \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500');

markInProgress('End-to-end chat flow tested');

const browser = await chromium.launch({ headless: true });
const ctx = await browser.newContext();
const page = await ctx.newPage();

await page.goto(`${BASE}/login`, { waitUntil: 'domcontentloaded' });

// Select Password tab
const passwordTab = page.locator('button:has-text("Password")');
await passwordTab.waitFor({ timeout: 8000 });
await passwordTab.click();

// Fill credentials and sign in
const emailInput = page.locator('input[type="email"]');
const pwdInput = page.locator('input[type="password"]');
const signInBtn = page.locator('button[type="submit"]');

await emailInput.fill(TEST_EMAIL);
await pwdInput.fill(TEST_PASSWORD);

// Wait for navigation away from /login after submit
const navPromise = page.waitForURL((url) => !url.href.includes('/login'), { timeout: 15000 });
await signInBtn.click();
const navOk = await navPromise.then(() => true).catch(() => false);

assert(navOk, 'Sign-in redirects away from /login', `Still on: ${page.url()}`);
await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});

// ---------------------------------------------------------------------------
// Phase 3: App shell visible
// ---------------------------------------------------------------------------
console.log('\n\u2500\u2500 Phase 3: Authenticated app shell \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500');

assert(!page.url().includes('/login'), 'Authenticated root is not /login', `URL: ${page.url()}`);

const newChatBtn = page.locator('button:has-text("New chat")');
await newChatBtn.waitFor({ timeout: 10000 }).catch(() => {});
assert(await newChatBtn.isVisible().catch(() => false), '"New chat" button visible in sidebar');

// ---------------------------------------------------------------------------
// Phase 4: Thread creation
// ---------------------------------------------------------------------------
console.log('\n\u2500\u2500 Phase 4: Thread creation \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500');

let createThreadStatus = 0;
const msgInput = page.locator('textarea[placeholder="Message\u2026"], textarea[placeholder="Message..."]');

if (await newChatBtn.isVisible().catch(() => false)) {
  for (let attempt = 1; attempt <= 2; attempt += 1) {
    const responsePromise = page.waitForResponse(
      (res) => res.url().includes('/api/threads') && res.request().method() === 'POST',
      { timeout: 10000 },
    ).catch(() => null);

    await newChatBtn.click().catch(() => {});
    const response = await responsePromise;
    createThreadStatus = response?.status() ?? 0;

    await msgInput.waitFor({ timeout: 10000 }).catch(() => {});
    if (await msgInput.isVisible().catch(() => false)) break;

    // Give auth state a moment to settle before retrying thread creation.
    await page.waitForTimeout(1000);
  }
}

const inputVisible = assert(
  await msgInput.isVisible().catch(() => false),
  'Message input rendered for new thread',
  createThreadStatus ? `Last POST /api/threads status: ${createThreadStatus}` : undefined,
);

// ---------------------------------------------------------------------------
// Phase 5: Send message and verify AI stream
// ---------------------------------------------------------------------------
console.log('\n\u2500\u2500 Phase 5: Chat send + stream \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500');

if (inputVisible) {
  const prompt = `Playwright validation ping ${Date.now()}`;
  await msgInput.fill(prompt);
  await msgInput.press('Enter');

  const userBubble = page.locator(`text="${prompt}"`);
  await userBubble.first().waitFor({ timeout: 10000 }).catch(() => {});
  assert((await userBubble.count()) > 0, 'User message visible in thread');

  await page.waitForFunction(() => {
    const muted = document.querySelectorAll('div.bg-muted');
    return muted.length > 0 &&
      (muted[muted.length - 1].textContent ?? '').replace('\u258b', '').trim().length > 0;
  }, { timeout: 60000 }).catch(() => {});

  const lastText = (await page.locator('div.bg-muted').last().textContent().catch(() => ''))
    ?.replace('\u258b', '').trim() ?? '';
  assert(lastText.length > 0, 'Assistant response stream produced output');

  if (lastText.length > 0) {
    markDone('End-to-end chat flow tested');
  }
}

// ---------------------------------------------------------------------------
// Phase 6: Login UI — both tabs present
// ---------------------------------------------------------------------------
console.log('\n\u2500\u2500 Phase 6: Login UI tabs \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500');

const signOutBtn = page.locator('button[aria-label="Sign out"]');
if (await signOutBtn.isVisible().catch(() => false)) {
  await signOutBtn.click().catch(() => {});
  await page.waitForURL((url) => url.href.includes('/login'), { timeout: 10000 }).catch(() => {});
}

await page.goto(`${BASE}/login`, { waitUntil: 'domcontentloaded' });
await page.waitForURL((url) => url.href.includes('/login'), { timeout: 10000 }).catch(() => {});
await page.locator('button:has-text("Password")').first().waitFor({ timeout: 5000 }).catch(() => {});

assert(await page.locator('button:has-text("Password")').isVisible().catch(() => false),
  'Password tab visible on login page');
assert(await page.locator('button:has-text("Magic link")').isVisible().catch(() => false),
  'Magic link tab visible on login page');

await page.locator('button:has-text("Password")').first().click().catch(() => {});
assert(await page.locator('input[type="password"]').isVisible().catch(() => false),
  'Password input shown in Password mode');
assert(await page.locator('button:has-text("Sign in")').isVisible().catch(() => false),
  '"Sign in" button visible in Password mode');

await browser.close();

// ---------------------------------------------------------------------------
// Summary + PROGRESS.md
// ---------------------------------------------------------------------------
console.log('\n\u2500\u2500 Results \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500');
console.log(`   Passed: ${passed}   Failed: ${failed}`);
console.log(`   PROGRESS.md updated at: ${PROGRESS_PATH}`);
if (failed > 0) process.exit(1);
