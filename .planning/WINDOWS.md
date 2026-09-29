---
schema_version: 1
open_count: 1
waived_count: 0
fixed_count: 0
total_count: 1
last_updated: 2026-09-29T12:06:44.014Z
---

# Broken Windows Ledger

> Cross-phase defect register. With `workflow.windows_enforce` enabled, `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 01 | unrun-verify | .planning/phases/01-fundaciones-de-dos-tiers-y-cat-logo/01-06-PLAN.md |  | Cierre por re-ejecucion de tests 1 y 4 del UAT en el taller (D:/Repos/maura-uat): ls backend/ sin .gitignore tras uv init --vcs none y /docs documentando 200/404/422 — asignado por diseno a /gsd-verify-work (verificacion item 2 del plan 01-06) | open |  | 2026-09-29T12:06:44.014Z |  |

````json
[
  {
    "id": 1,
    "kind": "unrun-verify",
    "phase": "01",
    "file": ".planning/phases/01-fundaciones-de-dos-tiers-y-cat-logo/01-06-PLAN.md",
    "line": null,
    "description": "Cierre por re-ejecucion de tests 1 y 4 del UAT en el taller (D:/Repos/maura-uat): ls backend/ sin .gitignore tras uv init --vcs none y /docs documentando 200/404/422 — asignado por diseno a /gsd-verify-work (verificacion item 2 del plan 01-06)",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-29T12:06:44.014Z",
    "resolved_at": null,
    "milestone": null
  }
]
````
