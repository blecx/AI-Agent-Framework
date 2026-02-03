# GUI Artifact Browsing

**Duration:** 15 minutes | **Difficulty:** Beginner | **Interface:** Web GUI

## Overview

Browse and view project artifacts using the ArtifactsList component. Learn navigation, file viewing, and download capabilities.

## Learning Objectives

- Navigate artifact tree
- View file content
- Download artifacts
- Filter artifacts
- Export project artifacts

## Prerequisites

- Completed: [Tutorial 03: Commands and Proposals](03-commands-and-proposals.md)
- Project TODO-001 with artifacts

## Steps

### Step 1: Access ArtifactsList

1. Select TODO-001 project
2. Find "Artifacts" tab/section
3. Artifact tree appears

✅ **Checkpoint:** See artifacts/ directory structure

### Step 2: Navigate Artifact Tree

Expand folders:
- artifacts/
  - charters/
    - project-charter.md
    - stakeholder-register.md
    - assumptions-log.md

Click folder icons to expand/collapse

✅ **Checkpoint:** Tree navigation works

### Step 3: View File Content

1. Click "project-charter.md"
2. File content viewer opens
3. Markdown rendered or source shown

✅ **Checkpoint:** File content displayed

### Step 4: Download Artifact

1. Click download icon next to file
2. File downloads to browser
3. Verify downloaded file

✅ **Checkpoint:** File downloaded successfully

### Step 5: Export All Artifacts

1. Click "Export All" button
2. ZIP file downloads
3. Contains all project artifacts

✅ **Checkpoint:** ZIP export works

## ArtifactsList Features

- Tree view navigation
- File preview
- Markdown rendering
- Download individual files
- Export all as ZIP
- File metadata (size, date)

## What You've Learned

✅ Navigate artifact tree  
✅ View file content in browser  
✅ Download individual files  
✅ Export all artifacts as ZIP  
✅ Understand ArtifactsList component

## Next Steps

1. **[Tutorial 05: Workflow States](05-workflow-states.md)** - ISO 21500 phases (20 min)
2. **[TUI Artifact Workflow](../tui-basics/03-artifact-workflow.md)** - CLI browsing (15 min)

## TUI Equivalent

```bash
python apps/tui/main.py artifacts list --project TODO-001
python apps/tui/main.py artifacts export --project TODO-001 --output todo.zip
```

## Success Checklist

- [ ] Navigate artifact tree
- [ ] View file content
- [ ] Download single file
- [ ] Export all artifacts
- [ ] Compare with TUI

---

**Tutorial Series:** [GUI Basics](../README.md#gui-basics) | **Previous:** [03 - Commands and Proposals](03-commands-and-proposals.md) | **Next:** [05 - Workflow States](05-workflow-states.md)
