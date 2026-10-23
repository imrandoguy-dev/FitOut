# Fit Out

Fit-out project management for ERPNext v16, by Hipersign Technologies.

It packages the **Fit Out** module built on `construction.hipersignerp.cloud`
(`/desk/fit-out`), so any ERPNext site gets the same setup with one `install-app`.

```
Enquiry & Requirements → Estimation & BOQ → Contract Award → Design & Approvals
  → Procurement → Site Execution → Commercial Review → Handover & Closure
```

## Install

On Press (install.hipersign.com): add the app to the bench (repo
`https://github.com/imrandoguy-dev/FitOut`, branch `main`), then **Fetch Latest
Updates → Deploy**, then install it on the site. On a plain bench:

```bash
bench get-app https://github.com/imrandoguy-dev/FitOut
bench --site <site> install-app fitout
```

Requires `erpnext`.

`after_install` turns on `server_script_enabled` in `site_config.json`, because all of
the module's logic runs as Server Scripts and Frappe skips them without it. If that
fails (permissions), set it by hand:

```json
"server_script_enabled": 1
```

## What you get

### Workspace and desktop
- **Fit Out** workspace (`/desk/fit-out`) showing the **Fitout Command Centre**
  (Custom HTML Block): dashboard KPIs, project portfolio, priority actions, project
  pages, Estimation & BOQ, procurement, site execution, variations, financial control,
  invoicing, document control, workflow designer, reports, inventory and subcontractors.
- **Fit Out** Workspace Sidebar (Dashboard, Projects, Estimation & BOQ, Procurement,
  Inventory, Subcontractors, Site Execution, Variations, Invoicing, Accounting, Document
  Control, Handover, Workflow Configuration, Reports, Settings).
- **Fit Out** desktop tile with its own icon (`public/icons/desktop_icons`).

### Doctypes (module Fitout)
| Area | Doctypes |
|---|---|
| Estimation | Fit Out BOQ, Fit Out BOQ Item |
| Site execution | Fit Out Work Package, Fit Out Inspection, Fit Out Site Issue |
| Commercial | Fit Out Variation, Fit Out Cost Forecast |
| Documents & handover | Fit Out Document, Fit Out Document Revision, Fit Out Snag, Fit Out Handover, Fit Out Handover Item |
| Setup | Fit Out Workflow Stage, Fit Out Stage Log, Fit Out Settings |

### Fields added to ERPNext doctypes
- **Project**: Fit Out section (`fo_is_fitout`, `fo_stage`, `fo_location`, `fo_health`,
  `fo_health_note`, `fo_image`), Fit Out Lifecycle table (`fo_stages`), Fit Out Details
  (category, subcontractor package, inspection requirement, client approval ref, drawing
  revision, material readiness) and Cost-to-Complete forecast (`fo_ctc`).
- **Task**: `fo_stage`, `fo_work_package`.
- **Quotation**: `fo_boq`.
- Created **only if missing** (so existing fields with these names are left alone):
  Project `custom_project_manager`, Project `custom_contract_value`, Task `custom_assign_to`.

Only projects ticked **Fit Out Project** (`fo_is_fitout`) are treated as fit-out
projects; the Command Centre can also show all projects.

### Server Scripts
- APIs used by the Command Centre: `hipersign_fitout_dashboard`, `_portfolio`, `_project`,
  `_boq`, `_procurement`, `_execution`, `_commercial`, `_closeout`.
- Document events: lifecycle stage sync on Project, BOQ totals / revision number /
  Quotation link, Work Package totals and Task progress, Inspection sign-off and package
  update, Variation approval rules, Handover readiness, Workflow Stage → Project stage
  options sync.

### Defaults on a new site
- The 8 lifecycle stages above (Fit Out Workflow Stage), created only when the site has none.
- Fit Out Settings: variation approval threshold 10,000, additional approver *Managing
  Director*, commercial reviewer *Commercial Manager*, client approval required, due-soon
  window 3 days, handover window 60 days, and the cost-category keywords. Only empty values
  are filled; a site's own settings are never overwritten.

## Updating the app

Change things on the live site, then re-export into this repo and push. After the
push: Press → Fetch Latest Updates → Deploy → update the sites.

Workflow stages and Settings are per-site data and are not overwritten by updates.
Project's **Fit Out Stage** options are rebuilt from the site's active stages on every
migrate.
