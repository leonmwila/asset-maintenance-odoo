# Asset Maintenance MIS User Manual

Version: 1.0  
Date: 11 March 2026

## Introduction

Asset Maintenance MIS is an Odoo-based management system used to register, track, repair, and report on institutional assets. It supports the full lifecycle of an asset from Lot/Serial registration, assignment, and repair processing to parts approvals, spare-part request evidence, and disposal.

The system is customized for structured institutional use, including:
- Asset/Lot management with GRZ numbering support
- Repair workflow with role-based approvals
- Parts approval and technician pickup evidence flow
- Depreciation tracking on Lot/Serial records
- Multi-company/institution support

This manual explains how each user type should use the system safely and consistently.

## Table of Contents

1. [System Overview](#system-overview)
2. [General Navigation](#general-navigation)
3. [Receptionist](#receptionist)
4. [Technician](#technician)
5. [Supervisor](#supervisor)
6. [Senior Supervisor](#senior-supervisor)
7. [IT Admin](#it-admin)
8. [Store Manager](#store-manager)
9. [Asset Labelling](#asset-labelling)
10. [Key Workflows (End-to-End)](#key-workflows-end-to-end)
11. [Reports and Monitoring](#reports-and-monitoring)
12. [Troubleshooting Guide](#troubleshooting-guide)
13. [Data Quality and Governance Rules](#data-quality-and-governance-rules)

## System Overview

### Core Areas

- **Inventory / Assets (Lots/Serials):** Asset records, GRZ details, assignment fields, depreciation data.
- **Repairs:** Repair orders, parts lines, approvals, transfer/return requests.
- **Spare Part Requests:** Evidence records that confirm approved request and technician collection.
- **Administration:** User access, institutions, province/district settings, system configuration.

### Main States in Repair Process

- **Draft** → **Confirmed** → **Parts Approved** → **Under Repair** → **Done**  
Additional states may include **Transferred**, **Returned**, or **Failed** based on workflow outcome.

## General Navigation

1. Log in with your assigned role account.
2. Use the top app menu to open the module (Inventory, Repairs, etc.).
3. Use search filters for quick access by Asset, Serial Number, Institution, or date.
4. Open a record and use action buttons in the header (for example: Approve Parts, Start Repair, Mark Collected).
5. Save frequently and avoid browser back navigation during data entry.

---

## Receptionist

### Primary Responsibilities

- Receive assets/issues and create initial repair records.
- Capture accurate customer/institution and asset details.
- Ensure requests are complete before handing over to technical team.

### Daily Tasks

1. Open **Repairs** module.
2. Create a new Repair Order.
3. Enter:
   - Asset/Product
   - Asset Serial (Lot/Serial)
   - Requesting institution/contact
   - Complaint/issue details
4. Save as **Draft**.
5. Notify Technician/Supervisor for review.

### Do/Don’t

**Do:**
- Verify serial number before saving.
- Use clear issue descriptions.
- Confirm institution and station fields.

**Don’t:**
- Approve parts.
- Change depreciation values.
- Close repair orders.

---

## Technician

### Primary Responsibilities

- Diagnose and execute repairs.
- Add parts and operations to repair orders.
- Provide proof of spare collection via signature on request records.

### Technician Workflow

1. Open assigned Repair Order.
2. Diagnose the issue.
3. Add required **Parts** lines.
4. Add **Operations** (if applicable).
5. Save and submit for parts approval.
6. After approval, open **Spare Part Requests** and complete pickup proof:
   - Add on-screen signature
   - Enter technician name in signed-by field
   - Mark as collected (if this step is assigned to technician role)
7. Start repair when permitted.
8. Complete repair and update notes/outcome.

### Critical Rules

- Do not start repairs requiring parts before approval.
- Do not bypass collection proof where required.
- Always use actual quantities consumed.

---

## Supervisor

### Primary Responsibilities

- Review technical requests.
- Validate repair readiness and workflow compliance.
- Approve or escalate according to policy.

### Typical Actions

- Verify part relevance and quantities added by technician.
- Ensure repair request has complete asset and issue details.
- Approve process steps permitted by role.
- Monitor pending repairs and bottlenecks.

### Checklist Before Approving Progress

- Correct asset and serial selected
- Reasonable parts requested
- Required approvals completed
- No missing mandatory fields

---

## Senior Supervisor

### Primary Responsibilities

- Final authority for parts approval and high-impact decisions.
- Oversight on repair quality, compliance, and service-level timelines.

### Key Actions

1. Open **Confirmed** repairs awaiting approval.
2. Review parts and operations lines.
3. Click **Approve Parts** where valid.
4. Confirm that spare part request evidence record is created in approved state.
5. Track exceptions (failed, transferred, returned repairs).

### Governance Expectations

- Enforce approval discipline.
- Prevent unauthorized workflow skips.
- Escalate repeated data quality issues.

---

## IT Admin

### Primary Responsibilities

- Maintain uptime, user access, module consistency, and environment health.
- Manage upgrades and deployment hygiene.

### Core Tasks

- User and role provisioning
- Access rights auditing
- Module upgrades after pull/deploy
- Odoo and database backup/restore
- Container/service monitoring

### Recommended Post-Deployment Routine

1. Pull latest code.
2. Start services.
3. Upgrade changed modules (for this project, typically `company_extension`, `product_depreciation`, and any newly changed module).
4. Restart Odoo service if needed.
5. Ask users to hard refresh browser.

### Admin Safeguards

- Never run production with unknown module state.
- Keep backup before upgrades.
- Track release notes and changed addons.

---

## Store Manager

### Primary Responsibilities

- Handle spare issue tracking and pickup evidence.
- Confirm who collected approved parts.
- Maintain accountability trail.

### Spare Part Request Handling

1. Open **Inventory → Spare Part Requests**.
2. Filter by **Approved** status.
3. Open request and verify:
   - Repair reference
   - Requested parts and quantities
   - Technician identity
4. Confirm signature exists.
5. Mark as **Collected** when pickup occurs.
6. Record notes (if needed).

### Control Rules

- No release without approved request.
- No release without identifiable collector/signature.
- Keep records complete for audit.

---

## Asset Labelling

### Purpose

The Asset Labelling feature allows users to track which physical Lot/Serial items have been labelled in the system. This is useful for inventory management and ensuring all assets are properly marked with their identifiers.

### Features

- **Labelled Column:** Each Lot/Serial number has a "Labelled" checkbox indicating whether the physical item has been labelled.
- **Bulk Label Action:** Select multiple items and mark them as labelled in one action.
- **Bulk Remove Label Action:** Undo labelling if a mistake was made or an item was found to not be labelled.
- **Barcode Scanner Support:** Scan an item's barcode (GRZ number) to automatically mark it as labelled and search for it in the list.

### How to Label Items Manually (Without Barcode Scanner)

1. Go to **Inventory → Lots / Serial Numbers**.
2. Use the checkboxes on the left side of each row to select the items you want to label.
3. Once selected, click the **Action** dropdown button (⋮ or arrow icon).
4. Choose **Label Items** from the list.
5. A success notification will appear confirming how many items were marked as labelled.
6. The "Labelled" column will now show a checkmark for the selected items.

### How to Remove Labels (Correct Mistakes)

1. Go to **Inventory → Lots / Serial Numbers**.
2. Use the checkboxes to select the items you want to unmark.
3. Click the **Action** dropdown button.
4. Choose **Remove Label** from the list.
5. A success notification will appear confirming the labels were removed.

### How to Use Barcode Scanner (With Scanner Device)

1. Go to **Inventory → Lots / Serial Numbers** list view.
2. Ensure the **search field at the top is NOT focused** (click elsewhere on the page if needed).
3. Hold your barcode scanner and scan an item's GRZ barcode.
4. The system will automatically:
   - Search for the matching Lot/Serial number
   - Mark it as labelled
   - Display it in the list

**Important:** If your cursor is in the search field at the top, the barcode will be typed into the search field instead. Click elsewhere on the page first to enable scanner mode.

### Do/Don't

**Do:**
- Use bulk actions when labelling multiple items at once for efficiency.
- Use the barcode scanner when available for speed and accuracy.
- Verify items are correctly marked after scanning or bulk actions.

**Don't:**
- Mark items as labelled if they haven't been physically labelled yet.
- Use the barcode scanner while the search field is active.

---

## Key Workflows (End-to-End)

### A. Repair With Spare Parts

1. Receptionist creates repair order.
2. Technician adds parts.
3. Supervisor/Senior Supervisor reviews.
4. Senior Supervisor approves parts.
5. System auto-creates **Spare Part Request** in approved state.
6. Technician/Store Manager completes collection proof (signature + collected action).
7. Technician performs and closes repair.

### B. Lot/Serial Depreciation Tracking

1. Create/open Lot/Serial.
2. Fill general fields (asset, supplier, assignment, etc.).
3. In depreciation tab, maintain depreciation data.
4. Depreciation uses lot acquisition price when provided; otherwise product acquisition price.

---

## Reports and Monitoring

- Track pending repairs by state.
- Track approved versus collected spare requests.
- Monitor failed/transferred/returned repairs.
- Review asset and depreciation data completeness.

Suggested weekly checks:
- Requests approved but not collected
- Repairs in confirmed state too long
- Records missing mandatory identifiers

---

## Troubleshooting Guide

### 1) Screen errors after deployment

- Upgrade changed modules.
- Restart Odoo service.
- Hard refresh browser.

### 2) New field not showing

- Verify module upgrade was executed on correct database.
- Confirm user has access rights.

### 3) Button/action missing

- Check user group/role permissions.
- Check record state conditions for button visibility.

### 4) Strange behavior after pull

- Usually module mismatch, not container build issue.
- Rebuild containers only when Dockerfile/dependencies changed.

---

## Data Quality and Governance Rules

- One asset should map correctly to its serial/lot.
- Every repair must have a clear issue statement and responsible role.
- Parts approval must be traceable to approving user and time.
- Spare collection must be traceable to collector/signature.
- Never edit records in ways that break audit history.

---

## Appendix: Role Quick Matrix

| Activity | Receptionist | Technician | Supervisor | Senior Supervisor | Store Manager | IT Admin |
|---|---|---|---|---|---|---|
| Create repair order | Yes | Optional | Optional | Optional | No | Optional |
| Add repair parts | No | Yes | Optional | Optional | No | Optional |
| Approve parts | No | No | Optional (policy-based) | Yes | No | Optional |
| View spare part requests | Optional | Yes | Yes | Yes | Yes | Yes |
| Mark spare request collected | No | Optional | Optional | Optional | Yes | Optional |
| Sign pickup proof | No | Yes | No | No | Optional | No |
| Label items (bulk) | Optional | Optional | Optional | Optional | Yes | Optional |
| Use barcode scanner | Optional | Yes | Optional | Optional | Optional | No |
| Manage users/access | No | No | No | No | No | Yes |
| Upgrade modules/deploy | No | No | No | No | No | Yes |

---

End of Manual
