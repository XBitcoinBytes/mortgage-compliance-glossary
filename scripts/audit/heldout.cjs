const req = require('module').createRequire(process.env.PLAYWRIGHT_HOME ? process.env.PLAYWRIGHT_HOME + '/package.json' : __filename);
const { chromium } = req('playwright');
const base = process.argv[2];
const Q = [
 ['good faith estimate','loan-estimate'],['seller paid closing costs','seller-concessions'],['appraisal came in low','faq-appraisal-lower-than-price'],
 ['loan officer license','mortgage-loan-originator'],['mortgage insurance removal','pmi-borrower-cancellation'],['late fee servicer','delinquency'],
 ['denied loan letter','adverse-action-notice'],['gift letter','gift-letter'],['self employed income','self-employment-income'],
 ['VA funding fee','va-funding-fee'],['FHA streamline','fha-streamline-refinance'],['203k','fha-203k'],['buydown','temporary-buydown'],
 ['balloon','balloon-payment'],['negative amortization','negative-amortization'],['title insurance','title-insurance'],['wire','closing-wire-fraud'],
 ['lock extension','rate-lock-extension'],['float down','float-down'],['tasa de interés fija','fixed-rate-mortgage'],['seguro hipotecario','private-mortgage-insurance'],
 ['tasacion','appraisal'],['ejecucion hipotecaria','foreclosure'],['cierre','closing-disclosure'],['steering','steering'],['redlining','redlining'],
 ['fair lending','fair-lending'],['flood insurance','flood-insurance'],['SAR filing','suspicious-activity-report'],['payoff','payoff-statement'],
];
(async () => {
  const fs=require('fs'); const slugs=new Set(fs.readdirSync('' + require('path').join(__dirname, '../../src/content/terms') + '').map(f=>f.replace('.json','')));
  const b = await chromium.launch({ channel: 'chrome' }); const page = await (await b.newContext()).newPage();
  let hit=0, n=0; const miss=[];
  for (const [q,want] of Q) {
    if(!slugs.has(want)){ console.log('SKIP (no such slug)',want); continue; }
    n++;
    const es=/[áéíóúñ]|tasacion|ejecucion|cierre|seguro/.test(q);
    await page.goto(base+(es?'/es/terms':'/terms')); await page.click('#search-open'); await page.fill('#search-input',q); await page.waitForTimeout(150);
    const h=await page.$$eval('#search-results a',as=>as.map(a=>a.getAttribute('href')));
    const r=h.findIndex(x=>x.endsWith('/'+want)); if(r>=0&&r<3) hit++; else miss.push(`${q}->${want} got ${h.slice(0,3).join(',')}`);
  }
  console.log(`heldout top3 ${hit}/${n}`); console.log(miss.join('\n')); await b.close();
})();
