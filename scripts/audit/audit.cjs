// Usage: node audit.cjs <baseUrl> <label>
const req = require('module').createRequire(process.env.PLAYWRIGHT_HOME ? process.env.PLAYWRIGHT_HOME + '/package.json' : __filename);
const { chromium } = req('playwright');
const axePath = req.resolve('axe-core/axe.min.js');
const fs = require('fs');
const base = process.argv[2]; const label = process.argv[3];
const pages = ['/', '/terms', '/terms/loan-estimate', '/es/terms/loan-estimate', '/terms/zero-tolerance', '/categories/compliance', '/paths', '/regulations', '/es'];
const queries = [
  ['loan estimate','loan-estimate'],['LE','loan-estimate'],['TRID','trid'],['tila respa integrated','trid'],['know before you owe','trid'],
  ['APR','annual-percentage-rate'],['DTI','debt-to-income-ratio'],['HPML','higher-priced-mortgage-loan'],['QM','qualified-mortgage'],
  ['ATR','ability-to-repay'],['estimacion del prestamo','loan-estimate'],['divulgacion de cierre','closing-disclosure'],
  ['CD','closing-disclosure'],['COC','changed-circumstance'],['change of circumstance','changed-circumstance'],['10% tolerance','ten-percent-tolerance'],
  ['zero tolerance','zero-tolerance'],['PMI','private-mortgage-insurance'],['MIP','fha-mip'],['HMDA','hmda'],['LAR','hmda-lar'],
  ['RESPA section 8','respa-section-8'],['kickback','kickback'],['UDAAP','udaap'],['ECOA','ecoa'],['Reg B','regulation-b'],
  ['VOE','verification-of-employment'],['LTV','loan-to-value-ratio'],['CLTV','combined-loan-to-value'],['AUS','automated-underwriting-system'],
  ['DU','desktop-underwriter'],['LPA','loan-product-advisor'],['escrow','escrow-account'],['QWR','qualified-written-request'],
  ['loss mit','loss-mitigation'],['HELOC','heloc'],['reverse mortgage','reverse-mortgage'],['IRRRL','va-irrrl'],['rescission','right-of-rescission'],['wire fraud','closing-wire-fraud'],
];
(async () => {
  const browser = await chromium.launch({ channel: 'chrome' });
  const out = { label, pages: {}, search: [] };
  for (const [vw, name] of [[{ width: 1280, height: 900 }, 'desktop'], [{ width: 390, height: 844 }, 'mobile']]) {
    const ctx = await browser.newContext({ viewport: vw, deviceScaleFactor: 1 });
    const page = await ctx.newPage();
    for (const p of pages) {
      let bytes = 0;
      page.removeAllListeners('response');
      page.on('response', async (r) => { try { const b = await r.body(); bytes += b.length; } catch {} });
      const t0 = Date.now();
      await page.goto(base + p, { waitUntil: 'load' });
      const ms = Date.now() - t0;
      const res = { ms, bytes };
      if (name === 'desktop') {
        await page.addScriptTag({ path: axePath });
        const ax = await page.evaluate(async () => { const r = await axe.run(document, { runOnly: ['wcag2a', 'wcag2aa', 'best-practice'] }); return r.violations.map(v => ({ id: v.id, impact: v.impact, n: v.nodes.length })); });
        res.axe = ax;
      }
      res.hscroll = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
      out.pages[`${name} ${p}`] = res;
      if (['/terms/loan-estimate', '/es/terms/loan-estimate', '/'].includes(p)) await page.screenshot({ path: `${process.env.SHOTS || 'shots'}/${label}-${name}${p.replace(/\//g, '_')}.png`, fullPage: false });
    }
    await ctx.close();
  }
  // search quality
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await ctx.newPage();
  await page.goto(base + '/terms', { waitUntil: 'load' });
  for (const [q, want] of queries) {
    const lp = q.match(/estimacion|divulgacion/) ? '/es/terms' : '/terms';
    await page.goto(base + lp, { waitUntil: 'load' });
    await page.click('#search-open');
    await page.fill('#search-input', q);
    await page.waitForTimeout(150);
    const hrefs = await page.$$eval('#search-results a', as => as.map(a => a.getAttribute('href')));
    const rank = hrefs.findIndex(h => h.replace(/\/$/, '').endsWith('/' + want));
    out.search.push({ q, want, rank, top: hrefs.slice(0, 3) });
  }
  await page.goto(base + '/terms'); await page.click('#search-open'); await page.fill('#search-input', 'loan estimate'); await page.waitForTimeout(150);
  await page.screenshot({ path: `${process.env.SHOTS || 'shots'}/${label}-search.png` });
  await browser.close();
  const hits = out.search.filter(s => s.rank >= 0 && s.rank < 3).length;
  out.searchTop3 = `${hits}/${out.search.length}`;
  fs.writeFileSync(`audit-${label}.json`, JSON.stringify(out, null, 1));
  console.log('search top3', out.searchTop3);
  for (const [k, v] of Object.entries(out.pages)) console.log(k, v.ms + 'ms', Math.round(v.bytes / 1024) + 'KB', v.hscroll ? 'HSCROLL' : '', v.axe ? v.axe.map(a => `${a.id}(${a.impact},${a.n})`).join(' ') : '');
  console.log('misses', out.search.filter(s => s.rank < 0 || s.rank >= 3).map(s => `${s.q}->${s.want} got ${s.top.join(',')}`).join('\n'));
})();
