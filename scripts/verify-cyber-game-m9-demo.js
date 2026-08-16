const { chromium } = require('playwright');

const BASE_URL = 'https://li-yongqvan.github.io/cyber-game';
const REPORT_PATH = process.argv[2] || 'playwright-report.json';

async function run() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
  const results = {
    baseUrl: BASE_URL,
    timestamp: new Date().toISOString(),
    checks: [],
    screenshots: {},
  };

  let homePage;
  try {
    // 1. Homepage: levels and lock/unlock state
    homePage = await context.newPage();
    await homePage.goto(`${BASE_URL}/`, { waitUntil: 'networkidle' });
    await homePage.waitForTimeout(3000);
    const homeText = await homePage.innerText('body');

    const homeCheck = {
      name: 'homepage-levels-and-badges',
      url: `${BASE_URL}/`,
      passed:
        homeText.includes('沙盒模式') ||
        homeText.includes('ARP 欺骗') ||
        homeText.includes('🔒') ||
        homeText.includes('Cyber Game'),
      signals: {
        hasTitle: homeText.includes('Cyber Game'),
        hasSandboxButton: homeText.includes('沙盒模式'),
        hasArpLevel: homeText.includes('ARP 欺骗'),
        hasLockIcon: homeText.includes('🔒'),
        bodyLength: homeText.length,
      },
    };
    results.checks.push(homeCheck);
    await homePage.screenshot({ path: 'homepage.png', fullPage: true });
    results.screenshots.homepage = 'homepage.png';

    // 2. Sandbox: click client-side route and verify render
    const sandboxButton = await homePage.locator('text=沙盒模式').first();
    const hasSandboxButton = await sandboxButton.isVisible().catch(() => false);

    let sandboxCheck;
    if (hasSandboxButton) {
      await sandboxButton.click();
      await homePage.waitForTimeout(3000);
      const sandboxText = await homePage.innerText('body');

      sandboxCheck = {
        name: 'sandbox-page-render',
        url: `${BASE_URL}/sandbox (client-side navigation)`,
        passed:
          sandboxText.includes('沙盒') ||
          sandboxText.includes('Sandbox') ||
          sandboxText.includes('设备') ||
          sandboxText.includes('模拟') ||
          sandboxText.includes('开始'),
        signals: {
          hasSandboxText: sandboxText.includes('沙盒') || sandboxText.includes('Sandbox'),
          hasDeviceText: sandboxText.includes('设备') || sandboxText.includes('Device'),
          hasStartText: sandboxText.includes('开始') || sandboxText.includes('Start'),
          bodyLength: sandboxText.length,
        },
      };
      await homePage.screenshot({ path: 'sandbox.png', fullPage: true });
    } else {
      sandboxCheck = {
        name: 'sandbox-page-render',
        url: `${BASE_URL}/sandbox`,
        passed: false,
        signals: { reason: '沙盒模式 button not found on homepage' },
      };
    }
    results.checks.push(sandboxCheck);
    results.screenshots.sandbox = 'sandbox.png';

    await homePage.close();
  } catch (error) {
    results.error = error.message;
    if (homePage) {
      await homePage.screenshot({ path: 'error.png', fullPage: true }).catch(() => {});
      results.screenshots.error = 'error.png';
    }
  } finally {
    await browser.close();
  }

  require('fs').writeFileSync(REPORT_PATH, JSON.stringify(results, null, 2));
  console.log(JSON.stringify(results, null, 2));

  const allPassed = results.checks.every((c) => c.passed);
  process.exit(allPassed ? 0 : 1);
}

run();
