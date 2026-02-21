# Compact Gantt — Swimlanes & Tasks UI Redesign Spec
**Version 1.0 | February 2026**

---

## 1. Overview

This spec defines changes to the Swimlanes and Tasks tabs in Compact Gantt. The goal is to eliminate the cross-referencing problem caused by treating swimlanes and tasks as flat siblings in separate tabs, while keeping implementation complexity low and preserving the existing data model and Excel schema.

The approach: swimlane header rows act as visual dividers within the Tasks tab, lane assignment becomes implicit through position, and the Swimlanes tab is retained but slimmed down. All changes are additive to the existing Excel schema — no breaking changes to import/export.

---

## 2. Swimlanes Tab

### 2.1 Column Changes

- ID column moved to left of Name field (standard convention)
- Lane Order field hidden in UI; retained in Excel as Lane Order (always ascending, no value in displaying it)
- Row Count renamed **Minimum Row Count** and moved to right of Name field

### 2.2 Minimum Row Count Behaviour

Minimum Row Count defines the height floor of a swimlane in chart rows. If child tasks occupy more chart rows than the minimum, the swimlane expands to fit:

- Minimum Row Count = minimum height, not a fixed height
- Setting Minimum Row Count to 3 when tasks occupy 4 chart rows still displays all 4 rows
- Setting Minimum Row Count higher than task rows adds deliberate white space / padding
- Minimum Row Count defaults to 1 on new swimlane creation

### 2.3 Deleting a Swimlane

Deleting a swimlane deletes all child tasks. Before proceeding, a confirmation popup must display:

- The swimlane name
- The number of tasks that will be deleted
- Cancel and Confirm buttons

There is no undo. The action is irreversible once confirmed.

### 2.4 New Swimlane Creation

A new swimlane is always created with one default task (see Section 4: Default Task). This ensures the Add Task workflow — which requires a selected table row — is immediately available after creating a swimlane.

### 2.5 Retained Functionality

- Move Up / Move Down reorders swimlanes
- Title field and Label Position field unchanged

---

## 3. Tasks Tab

### 3.1 Swimlane Header Rows

Swimlane groups are divided by non-editable header rows inserted between them. Header row properties:

- Greyed-out background
- Bold swimlane name as label
- Non-editable and non-selectable
- Rendered dynamically based on Lane ID grouping

### 3.2 Chart Row

- The Row column is renamed **Chart Row** throughout the UI
- Chart Row is relative to the swimlane, not the absolute chart position
- Two tasks with the same Chart Row number within the same swimlane are valid — they occupy the same horizontal band and are differentiated by their date ranges
- Chart Row is a free-entry integer for now; range limiting is a future feature

### 3.3 Lane ID

- Lane ID column is hidden in the UI
- Lane ID is retained in the Excel schema unchanged
- Swimlane membership is visually communicated by the header row grouping

### 3.4 Add Task

- Add Task button is disabled when no table row is selected
- When a table row is selected, the new task is inserted immediately below it in the table
- The new task inherits Chart Row, Start Date, Finish Date, and Lane ID from the selected task
- See Section 4 for full default task field values

### 3.5 Move Up / Move Down

- Constrained within the current swimlane — a task cannot be moved past a swimlane header boundary
- Action is disabled when the task is already at the top or bottom of its swimlane

### 3.6 Duplicate

- Duplicated task is inserted on the table row immediately below the original
- All fields are inherited including Chart Row number and Lane ID
- ID is auto-incremented as normal

### 3.7 Moving Tasks Between Swimlanes

There is no direct move-between-swimlane action in this version. The intended workflow is delete and re-add. Cut and paste is a future feature.

---

## 4. Default Task on Creation

The following defines the state of a newly created task, whether created via Add Task or as the default task on new swimlane creation.

### 4.1 System-Populated and Defaulted Fields

| Field | Default Value | Notes |
|---|---|---|
| ID | Auto-incremented | System-populated |
| Lane ID | Inherited from parent swimlane | System-populated; hidden in UI |
| Chart Row | Inherited from selected task; else 1 | System-populated |
| Name | "New Task" | User should update |
| Start Date | Inherited from selected task; else Timeframe start + 1 day | User should update |
| Finish Date | Inherited from selected task; else Start Date + 10 days | User should update |

> **Note:** if a task is selected when Add Task is clicked, Chart Row, Start Date, and Finish Date are all inherited from the selected task.

### 4.2 Optional Fields

The following fields are left blank on creation. Blank values fall back to the global default rendering behaviour.

| Field | Behaviour |
|---|---|
| Label Content | Left blank — falls back to global default |
| Label Placement | Left blank — falls back to global default |
| Label Offset | Left blank — falls back to global default |
| Fill Color | Left blank — falls back to global default |
| Date Format | Left blank — falls back to global default |

---

## 5. Excel Schema

All changes are non-breaking to the existing Excel schema. The following table summarises field visibility by context.

| Field | Shown in UI | Shown in Excel | Notes |
|---|---|---|---|
| Lane ID | No | Yes | Retained unchanged |
| Lane Order | No | Yes | Renamed from Lane field; always ascending |
| Chart Row | Yes | Yes | Renamed from Row in UI only |
| Minimum Row Count | Yes | Yes | Renamed from Row Count |

---

## 6. Suggested Sequence of Work

Implement and verify one slice at a time before proceeding to the next. Do not implement multiple slices in a single session.

**Before starting:** read the codebase and summarise the current implementation before writing any code.

| # | Task | Scope |
|---|---|---|
| 1 | Read codebase | Read `ui/tabs/swimlanes_tab.py`, `ui/tabs/tasks_tab.py`, `models/task.py`, `repositories/excel_repository.py`. Summarise current implementation before making any changes. |
| 2 | Swimlanes tab — UI changes | Move ID column left of Name. Rename Row Count to Minimum Row Count and move right of Name. Hide Lane Order field in UI (retain in Excel). |
| 3 | Swimlanes tab — delete cascade | Deleting a swimlane deletes all child tasks. Requires confirmation popup listing the swimlane name and task count before proceeding. |
| 4 | Swimlanes tab — new swimlane default | New swimlane created with one default task (see Section 4). Minimum Row Count defaults to 1. |
| 5 | Tasks tab — swimlane header rows | Insert non-editable, greyed-out, bold, non-selectable swimlane header rows as visual dividers between swimlane groups. Headers display swimlane name. |
| 6 | Tasks tab — Chart Row rename | Rename Row column to Chart Row throughout UI. Chart Row is relative to the swimlane, not the absolute chart. |
| 7 | Tasks tab — Lane ID hidden | Hide Lane ID column in UI. Retain in Excel schema unchanged. |
| 8 | Tasks tab — Add Task constraints | Disable Add Task button when no table row is selected. When a row is selected, insert new task immediately below it, inheriting Chart Row, Start Date, Finish Date, and Lane ID from the selected task. |
| 9 | Tasks tab — Move Up/Down boundary | Move Up and Move Down constrained within the current swimlane. Action is disabled when the task is already at the top or bottom of its swimlane. |
| 10 | Tasks tab — Duplicate behaviour | Duplicated task inserted on table row immediately below the original. Inherits all fields including Chart Row number and Lane ID. ID is auto-incremented. |
| 11 | Excel regression check | Verify existing files (e.g. `POAP__TTP_30_1_.xlsx`) load correctly under updated schema. Lane ID and Lane Order retained in Excel. Chart Row field updated in Excel if previously named Row. |
| 12 | Validation pass | Confirm all Valid column logic still works. Confirm blank optional task fields fall back to global defaults without rendering errors. |

---

## 7. Briefing Claude Code

Use the following approach when opening a Claude Code session with this spec.

### Step 1 — Orient

Paste this as your opening message before sharing the spec:

```
Do not write any code yet. Read the following files and summarise your
understanding of how Swimlanes and Tasks are currently implemented:

  ui/tabs/swimlanes_tab.py
  ui/tabs/tasks_tab.py
  models/task.py
  repositories/excel_repository.py

Flag any ambiguities or anything that conflicts with the spec before we start.
```

### Step 2 — Share the spec

Paste this file in full and ask the tool to flag any conflicts with the existing codebase before writing any code.

### Step 3 — Implement slice by slice

Work through the sequence table in Section 6. Ask the tool to implement one numbered item at a time. Do not proceed to the next slice until the current one has been verified.

### Step 4 — Regression check

After all slices are complete, ask the tool to load `POAP__TTP_30_1_.xlsx` and confirm it loads without errors under the updated schema.

---

*Compact Gantt UI Spec v1.0 | February 2026 | haymanjoyce/compact_gantt*
