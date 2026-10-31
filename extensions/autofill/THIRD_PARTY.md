# Third party code and research scope

`lib/dom.js` adapts the native value setter and focus/input/change/blur event pattern
from [wangshen-autofill](https://github.com/xiaoxiaobaijiangjun/wangshen-autofill/blob/main/content/filler.js),
read on 2026-10-31. The rest of its filler, demographic aliases, automatic radio
selection, model clients and network integrations were not imported. Full MIT
notice: [licenses/wangshen-autofill.txt](licenses/wangshen-autofill.txt).

The build script vendors Tesseract.js 7.0.0, Tesseract.js-core 7.0.0 and PDF.js
6.4.299 under Apache-2.0. Simplified Chinese and English data come from
tessdata_fast commit `87416418657359cb625c412a48b6e1d6d41c29bd`, also Apache-2.0.
The prepared distribution includes the original licenses in `vendor/licenses/`
and per-asset source URLs and SHA-256 fingerprints in `vendor/assets.json`.
No dependency install scripts execute. Dependencies are downloaded at build time;
runtime worker, WASM and language files all resolve to packaged extension files.

Also inspected: [JobApplyAutofill](https://github.com/aaa-wxl/JobApplyAutofill)
(MIT, local rules and optional AI) and
[ApplyPilot AI](https://github.com/pritamrauniyar/applypilot-ai) (MIT).
Their claims about coverage, speed and quality have not been independently
verified. Their complete engines and background learning were not imported.
Unlicensed candidates were not copied. Fuse.js was evaluated but is not a
runtime dependency; fuzzy matching alone would not establish factual correctness.
