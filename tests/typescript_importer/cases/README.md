# TypeScript Case Bundles
Status: Informative

This directory is reserved for future fixed-shape TypeScript importer fixture bundles.

The fixed first-slice case directories now contain placeholder-only bundle files. None are live fixture cases.

Current placeholder bundle state:

- admitted cases now carry placeholder `source.ts`, `expected.scirh`, `module_manifest.json`, `feature_tier_report.json`, and `validation_report.json`
- rejected boundary cases now carry placeholder `source.ts`, `module_manifest.json`, `feature_tier_report.json`, and `validation_report.json`
- rejected boundary cases intentionally omit `expected.scirh`
- no case in this first slice may imply executable `D-JS`, lowering, reconstruction, or benchmark scope
- none of these files are live importer outputs
