# GUI Artifact Browsing

**Duration:** 15 minutes | **Difficulty:** Beginner | **Interface:** Web GUI

## Overview

Master artifact browsing in the AI-Agent Framework web interface. This comprehensive guide walks you through navigating the artifact tree structure, viewing file content with various renderers, downloading individual files, searching artifacts, understanding file metadata, and exporting complete artifact collections. You'll learn to efficiently manage and review all project-generated documents.

## Learning Objectives

By the end of this tutorial, you will be able to:
- Navigate hierarchical artifact tree structure with confidence
- Expand and collapse folder structures efficiently
- View file content with appropriate renderers (Markdown, code, plain text)
- Download individual artifacts to your local system
- Search and filter artifacts by name or type
- Understand artifact metadata (size, modification date, type)
- Export entire artifact collections as ZIP archives
- Switch between tree view and list view display modes
- Use keyboard shortcuts for faster artifact navigation
- Compare artifact viewing between GUI and TUI interfaces

## Prerequisites

- **Completed Tutorials:**
  - [Tutorial 01: Web Interface](01-web-interface.md) - UI navigation fundamentals
  - [Tutorial 02: Project Creation](02-project-creation.md) - Have at least one project
  - [Tutorial 03: Commands and Proposals](03-commands-and-proposals.md) - Generated artifacts from commands
- **Active Project:** TODO-001 (or any project) with generated artifacts from charter command
- **Docker running:** `docker ps` shows both web and API containers
- **Browser:** Modern browser with JavaScript enabled
- **No external tools required** - all interaction is browser-based

### Quick Verification

Verify you have artifacts to browse:

```bash
# Check projectDocs has artifacts for your project
ls -la projectDocs/TODO-001/artifacts/

# Expected: Folders like charters/, plans/, risks/, etc.
```

**Expected Output:**
```
drwxr-xr-x charters/
drwxr-xr-x plans/
-rw-r--r-- project-charter.md
-rw-r--r-- stakeholder-register.md
```

✅ **Pre-flight Checkpoint:** Project exists with at least 2-3 artifact files

## Steps

### Step 1: Access Artifacts View

Navigate to the artifacts browser for your project.

#### 1.1: Select Project (If Not Already Selected)

**Option A: Via Project Selector (Sidebar)**
1. Look at left sidebar for project list
2. Find "TODO-001" in the list
3. Click on "TODO-001" to select
4. Main content area updates with project details

**Option B: Via Project Dropdown (If UI Uses Dropdown)**
1. Click project dropdown in header or sidebar
2. Select "TODO-001" from dropdown menu
3. Current project indicator updates

**Visual Confirmation:**
- Project name "TODO-001" highlighted in sidebar
- Main content shows project dashboard or command panel
- Breadcrumb trail shows: Home > TODO-001

✅ **Checkpoint 1.1:** Project TODO-001 is selected and active

#### 1.2: Locate Artifacts Section/Tab

The artifacts browser may appear in different locations depending on UI layout:

**Layout Pattern A: Tabbed Interface**
1. Look for horizontal tabs in main content area
2. Tabs may include: "Commands", "Artifacts", "RAID", "Workflow"
3. Click "Artifacts" tab
4. Artifacts tree appears below tab bar

**Layout Pattern B: Sidebar Navigation**
1. Look for "Artifacts" item in left sidebar under project name
2. Click "Artifacts" navigation item
3. Main content switches to artifacts view

**Layout Pattern C: Section Accordion**
1. Scroll in main content to find "Artifacts" section
2. Click section header to expand
3. Tree view expands below header

**Expected Visual Elements:**
- Artifacts section header with title "Artifacts" or "Project Artifacts"
- Tree view or list view toggle buttons
- Search/filter input field
- "Export All" or "Download ZIP" button
- Artifact count indicator (e.g., "12 files, 3 folders")
- Loading spinner (brief) while fetching artifact list

✅ **Checkpoint 1.2:** Artifacts view is visible and loaded

**Screenshot Reference:** `docs/screenshots/gui-04-artifacts-overview.png`

#### 1.3: Understand Artifacts View Layout

**Artifacts Panel Components:**

1. **Toolbar (Top of artifacts section)**
   - View mode toggle: Tree view ⟷ List view icons
   - Search/filter input: "Filter artifacts..."
   - Sort dropdown: "Sort by: Name" or "Date Modified"
   - Export all button: "Export ZIP" or download icon
   - Artifact count: "Showing 12 of 12 items"

2. **Tree View Panel (Main area)**
   - Hierarchical folder structure
   - Expandable/collapsible folders
   - File icons indicating file types
   - File size and date metadata
   - Download buttons per file
   - Folder icons (📁 closed, 📂 open)

3. **Preview Panel (Right side or modal - if present)**
   - File content viewer
   - Markdown renderer for .md files
   - Syntax highlighter for code files
   - Close button to exit preview

**Default Initial State:**
- Tree view mode active (default)
- Root folders collapsed or auto-expanded one level
- No file selected (preview panel hidden)
- Search filter empty

✅ **Checkpoint 1.3:** Understand complete artifacts view layout

### Step 2: Navigate Artifact Tree Structure

Explore the hierarchical folder structure containing all project artifacts.

#### 2.1: View Root Artifact Structure

**Expected Root-Level Folders:**
```
📂 artifacts/
├── 📁 charters/         (Charter documents)
├── 📁 plans/            (Planning documents)
├── 📁 risks/            (RAID register exports)
├── 📁 reports/          (Status reports)
├── 📁 lessons/          (Lessons learned)
└── 📁 proposals/        (Archived proposals)
```

**Note:** Folder presence depends on commands executed. New projects may only have `charters/` folder.

**Folder Icon Indicators:**
- 📁 **Closed folder** - Click to expand and see contents
- 📂 **Open folder** - Click to collapse and hide contents
- 📄 **File** - Click to view/download
- 🔒 **Locked/Read-only** - System-generated, no editing

**Folder Badges (May appear on folders):**
- Number badge: Shows file count inside (e.g., "3")
- New badge: Recently created artifacts

✅ **Checkpoint 2.1:** See root artifact folder structure

**Screenshot Reference:** `docs/screenshots/gui-04-tree-root.png`

#### 2.2: Expand Charters Folder

1. Locate the `charters/` folder in the tree
2. Click on the folder row or the expand arrow icon (►)
3. Folder expands to show contents
4. Folder icon changes from 📁 to 📂
5. Child items appear indented below

**Expected Charters Folder Contents:**
```
📂 charters/                          (expanded)
├── 📄 project-charter.md             2.4 KB  2026-02-06
├── 📄 stakeholder-register.md        1.8 KB  2026-02-06
├── 📄 assumptions-log.md             1.2 KB  2026-02-06
└── 📄 constraints-log.md             1.0 KB  2026-02-06
```

**File Row Information:**
- File name (clickable)
- File size in KB or MB
- Last modified date
- Download icon button
- File type icon (📄 for Markdown, 📝 for text, etc.)

**Tree Indentation:**
- Root folders: No indentation
- Level 1 files: One indent level (└── or ├──)
- Nested folders: Additional indentation per level

✅ **Checkpoint 2.2:** Charters folder expanded, see 3-4 markdown files

#### 2.3: Collapse and Expand Multiple Folders

Practice navigation by expanding and collapsing folders:

**Exercise 1: Expand All Root Folders**
1. Click on `plans/` folder to expand
2. Click on `risks/` folder to expand
3. Click on `reports/` folder to expand (if present)
4. Observe each folder's contents

**Exercise 2: Collapse All**
1. Click on `charters/` folder (📂 icon) to collapse
2. Click on `plans/` folder to collapse
3. Click on `risks/` folder to collapse
4. All folders return to closed state

**Keyboard Shortcuts (If Supported):**
| Shortcut | Action |
|----------|--------|
| `→` (Right arrow) | Expand selected folder |
| `←` (Left arrow) | Collapse selected folder |
| `↓` (Down arrow) | Move to next item |
| `↑` (Up arrow) | Move to previous item |
| `Enter` | Open/view selected file |

**Multi-Folder Expansion:**
- Some UIs have "Expand All" button - expands entire tree
- "Collapse All" button - closes all folders
- Hold Ctrl/Cmd + Click - Expand folder and all subfolders (some UIs)

✅ **Checkpoint 2.3:** Successfully expanded and collapsed multiple folders

**Screenshot Reference:** `docs/screenshots/gui-04-tree-expanded.png`

#### 2.4: Understand Nested Folder Structure

Some artifacts may be in nested subdirectories:

**Example Nested Structure:**
```
📂 plans/
├── 📂 scope/                      (nested subfolder)
│   ├── 📄 scope-statement.md
│   └── 📄 wbs.md
├── 📂 schedule/
│   ├── 📄 schedule-baseline.md
│   └── 📄 milestones.md
└── 📄 project-management-plan.md  (root level file)
```

**Navigation:**
1. Expand `plans/` folder (level 1)
2. See subfolders `scope/` and `schedule/`
3. Click `scope/` to expand (level 2)
4. See nested files indented further

**Visual Hierarchy:**
- Each level adds indentation (typically 20-30px)
- Tree lines connect parent to children
- Deepest nesting typically 3-4 levels

✅ **Checkpoint 2.4:** Understand nested folder navigation

### Step 3: View File Content

Open and read artifact files directly in the browser.

#### 3.1: Select and Open File

1. Locate `project-charter.md` in `charters/` folder
2. Ensure `charters/` folder is expanded
3. Click on the file name text or file row
4. File viewer opens (modal, drawer, or in-place)

**What Happens Behind the Scenes:**
1. UI sends GET request to `/artifacts/{project_key}/{file_path}`
2. API reads file from `projectDocs/TODO-001/artifacts/charters/project-charter.md`
3. File content returned in response body
4. Browser renders content based on file type

**Expected File Viewer Appearance:**
- **Modal overlay** - Popup window over main UI, dimmed background
- **Drawer** - Slides in from right side of screen
- **In-place expansion** - Content shown below file row in tree

**File Viewer Header:**
- File name: `project-charter.md`
- File path: `artifacts/charters/project-charter.md`
- File size: `2.4 KB`
- Last modified: `2026-02-06 14:30`
- Close button (X icon)
- Download button
- Copy to clipboard button (for code/text)

✅ **Checkpoint 3.1:** File viewer opened, header information visible

**Screenshot Reference:** `docs/screenshots/gui-04-file-viewer-modal.png`

#### 3.2: View Markdown Rendering

**Expected Rendered Content (project-charter.md):**
```
# Project Charter: TODO-001

## Project Title
TODO Management System Implementation

## Business Case
...

## Project Objectives
1. Deliver functional TODO system
2. Meet user requirements
3. Stay within budget and timeline

## Success Criteria
- All features implemented
- 95% test coverage
- User acceptance achieved
```

**Markdown Rendering Features:**
- Headings rendered with proper hierarchy (H1, H2, H3)
- Bold and italic formatting preserved
- Lists (ordered and unordered) properly indented
- Code blocks with syntax highlighting
- Links clickable (if external references present)
- Tables rendered with borders

**View Mode Toggle (May be present):**
- "Rendered" mode: Markdown formatted (default)
- "Source" mode: Raw markdown with `#`, `**`, etc.
- Toggle button in viewer toolbar

**Zoom Controls (Some UIs):**
- Zoom in: Ctrl + `+` or button
- Zoom out: Ctrl + `-` or button
- Reset zoom: Ctrl + `0` or button

✅ **Checkpoint 3.2:** Markdown content rendered properly, headings and formatting visible

#### 3.3: Scroll Through Long Files

**For longer files (> 1 screen height):**

1. Use mouse wheel or trackpad to scroll down
2. Observe scrollbar on right side of viewer
3. Scroll to bottom to see complete content
4. Scroll back to top

**Scroll Indicators:**
- Scrollbar position shows location in document
- "Back to top" button may appear when scrolled down
- Current line/position indicator (some viewers)

**Large File Warning:**
- Files > 1 MB may show "Large file" warning
- Option to view summary or download instead of rendering
- Prevents browser performance issues

✅ **Checkpoint 3.3:** Successfully scrolled through file content

#### 3.4: View Different File Types

Close the charter file and open different file types to see rendering differences:

**Markdown Files (.md):**
- Example: `stakeholder-register.md`
- Rendered with HTML formatting
- Tables, lists, headings styled

**JSON Files (.json) - If present:**
- Example: `config.json` in some artifacts
- Syntax highlighted (keys in blue, strings in green)
- Collapsible object/array structures
- Pretty-printed with indentation

**Text Files (.txt):**
- Example: `notes.txt` if present
- Plain text, monospace font
- No special rendering
- Line numbers may appear

**Code Files (.py, .js, .sh):**
- Example: Generated scripts if present
- Syntax highlighting by language
- Line numbers
- Copy to clipboard button

**Binary Files (.zip, .png):**
- Preview not available message
- Download button only
- File size and type shown

✅ **Checkpoint 3.4:** Viewed multiple file types, understand different renderers

**Screenshot Reference:** `docs/screenshots/gui-04-markdown-rendered.png`

#### 3.5: Close File Viewer

**How to Close:**
- Click "X" button in viewer header/corner
- Click outside modal (on dimmed background)
- Press `Esc` key on keyboard
- Click "Back" or "Close" button

**Expected Behavior:**
- Viewer closes/hides
- Return to artifact tree view
- Previously selected file may remain highlighted
- No data lost

✅ **Checkpoint 3.5:** Closed file viewer, returned to tree

### Step 4: Download Individual Artifacts

Save artifact files to your local computer.

#### 4.1: Download from Tree View

1. Locate `stakeholder-register.md` in `charters/` folder
2. Find download icon button next to file name (usually ⬇️ or 💾)
3. Click the download button
4. Browser download begins

**Alternative Download Methods:**
- Right-click file name → "Download"
- Select file → Click "Download" in toolbar
- Open file viewer → Click download button in header

**What Happens:**
1. Browser requests file from `/artifacts/{project}/{path}/download`
2. API streams file content with `Content-Disposition: attachment` header
3. Browser shows download dialog or auto-downloads
4. File saved to default download location (e.g., `~/Downloads/`)

**Expected Download Behavior:**
- Download progress indicator in browser (bottom bar)
- File appears in downloads folder within 1-2 seconds (for small files)
- Original filename preserved: `stakeholder-register.md`

✅ **Checkpoint 4.1:** File downloaded to local system

**Screenshot Reference:** `docs/screenshots/gui-04-download-action.png`

#### 4.2: Verify Downloaded File

**Open file locally to verify:**

**Linux/Mac:**
```bash
# Navigate to downloads
cd ~/Downloads/

# Verify file exists
ls -lh stakeholder-register.md

# View file content
cat stakeholder-register.md
# or
less stakeholder-register.md
```

**Windows (PowerShell):**
```powershell
# Navigate to downloads
cd $HOME\Downloads\

# Verify file exists
dir stakeholder-register.md

# View file content
Get-Content stakeholder-register.md
```

**Or use GUI file explorer:**
1. Open file manager (Finder, Explorer, Nautilus)
2. Navigate to Downloads folder
3. Double-click file to open in default text editor
4. Verify content matches what was shown in web viewer

**Expected File Properties:**
- File size: Same as shown in web UI (e.g., 1.8 KB)
- Content: Identical to web viewer
- Format: Plain text Markdown file
- Editable: Can open and edit locally

✅ **Checkpoint 4.2:** Downloaded file verified and readable locally

#### 4.3: Download Multiple Files

**To download several files:**

**Method A: Individual Downloads**
1. Click download button for `project-charter.md`
2. Wait for download to complete
3. Click download button for `assumptions-log.md`
4. Repeat for each desired file
5. All files appear in Downloads folder

**Method B: Export All (Next section)**
- More efficient for bulk downloads
- Gets all artifacts in single ZIP file

**Browser Download Management:**
- Downloads appear in browser's download panel (Ctrl+J or Cmd+Shift+J)
- Can pause/resume downloads
- View download history

✅ **Checkpoint 4.3:** Multiple files downloaded successfully

### Step 5: Search and Filter Artifacts

Find specific artifacts quickly using search functionality.

#### 5.1: Use Search/Filter Input

1. Locate search input field at top of artifacts panel
2. Placeholder text: "Filter artifacts..." or "Search files..."
3. Click in input field to focus
4. Type search query: `charter`

**Expected Behavior:**
- Tree updates in real-time as you type
- Only matching files and their parent folders shown
- Non-matching items hidden
- Match count updates: "Showing 2 of 12 items"

**Matching Logic:**
- Case-insensitive search
- Matches file names and folder names
- Partial matches included (e.g., "char" matches "charter")
- Highlights matched text in file names (some UIs)

✅ **Checkpoint 5.1:** Search filters artifact list, see only matching items

**Screenshot Reference:** `docs/screenshots/gui-04-search-filter.png`

#### 5.2: Test Different Search Queries

**Exercise: Try various search terms:**

**Search 1: "stakeholder"**
- Expected: Shows `stakeholder-register.md` and any other stakeholder files
- Parent folder `charters/` remains visible

**Search 2: ".md"**
- Expected: Shows all Markdown files across all folders
- Filters out non-Markdown files

**Search 3: "risk"**
- Expected: Shows files in `risks/` folder
- May also match files with "risk" in name

**Search 4: "2026-02-06"** (date search, if supported)
- Expected: Shows files modified on that date
- May not work in all UI implementations

**Search 5: "" (empty string)**
- Expected: Clear filter, show all artifacts again
- Returns to full tree view

✅ **Checkpoint 5.2:** Search works for multiple query types

#### 5.3: Clear Search Filter

1. Clear the search input (delete all text or click X button)
2. OR press `Esc` key while input is focused
3. Full artifact tree returns
4. Count updates: "Showing 12 of 12 items"

**Quick Clear Options:**
- Backspace to delete characters
- Click "X" or "Clear" button in search input (if present)
- `Esc` key to clear and unfocus
- Reload page (less efficient)

✅ **Checkpoint 5.3:** Search cleared, full artifact list visible again

### Step 6: Export All Artifacts as ZIP

Download entire artifact collection in one archive file.

#### 6.1: Locate Export Button

**Button location options:**
- Toolbar at top of artifacts panel: "Export All" or "Download ZIP" button
- Context menu: Right-click in artifacts panel
- File menu: "File" → "Export Artifacts"
- Download icon with "All" label

**Button Visual:**
- Icon: 📦 package icon or ⬇️ download with folder icon
- Text: "Export All", "Download ZIP", or "Export Artifacts"
- May show artifact count: "Export All (12 files)"

✅ **Checkpoint 6.1:** Export button located

#### 6.2: Initiate ZIP Export

1. Click the "Export All" or "Download ZIP" button
2. Loading indicator appears briefly
3. Browser download starts after 1-3 seconds (depends on artifact size)

**What Happens Behind the Scenes:**
1. UI sends POST request to `/artifacts/{project}/export`
2. API creates temporary ZIP archive
3. API includes all files in `projectDocs/{project}/artifacts/` directory
4. API streams ZIP file to browser
5. Browser saves ZIP to downloads

**Expected ZIP File:**
- Filename: `TODO-001-artifacts.zip` or `TODO-001-2026-02-06.zip`
- Size: Sum of all artifact files + ZIP compression overhead (usually smaller)
- Location: Default downloads folder

**Large Project Warning:**
- Projects with many/large artifacts may take 10-30 seconds
- Progress indicator shows "Preparing export..."
- Don't navigate away until download starts

✅ **Checkpoint 6.2:** ZIP export initiated, download in progress

**Screenshot Reference:** `docs/screenshots/gui-04-export-zip.png`

#### 6.3: Extract and Verify ZIP Contents

**Verify downloaded ZIP file:**

**Linux/Mac:**
```bash
# Navigate to downloads
cd ~/Downloads/

# Check ZIP file
ls -lh TODO-001-artifacts.zip

# Extract ZIP
unzip -l TODO-001-artifacts.zip  # List contents
unzip TODO-001-artifacts.zip -d TODO-001-extracted/  # Extract all

# Verify structure
tree TODO-001-extracted/
# or
ls -R TODO-001-extracted/
```

**Windows (PowerShell):**
```powershell
# Navigate to downloads
cd $HOME\Downloads\

# Check ZIP file
dir TODO-001-artifacts.zip

# Extract ZIP
Expand-Archive -Path TODO-001-artifacts.zip -DestinationPath TODO-001-extracted

# Verify structure
tree TODO-001-extracted /F
# or
dir TODO-001-extracted -Recurse
```

**Or use GUI:**
1. Open file manager (Finder, Explorer, Nautilus)
2. Navigate to Downloads folder
3. Right-click ZIP file → Extract or Open with Archive Manager
4. Browse extracted folder structure

**Expected Extracted Structure:**
```
TODO-001-extracted/
└── artifacts/
    ├── charters/
    │   ├── project-charter.md
    │   ├── stakeholder-register.md
    │   ├── assumptions-log.md
    │   └── constraints-log.md
    ├── plans/
    │   └── project-management-plan.md
    └── risks/
        └── risk-register.md
```

**Verification Checks:**
- All files present (compare count with UI)
- Folder structure preserved
- File sizes match originals
- Files readable and contain correct content

✅ **Checkpoint 6.3:** ZIP extracted successfully, all artifacts present

#### 6.4: Compare ZIP with UI Tree

**Exercise: Verify completeness**

1. Return to web UI artifacts view
2. Note folder structure and file count
3. Compare with extracted ZIP structure
4. Verify all folders and files match

**Quick Comparison Commands:**

**Count files in UI:**
- Look for artifact count display: "12 files, 3 folders"

**Count files in ZIP extraction:**
```bash
# Linux/Mac
find TODO-001-extracted/ -type f | wc -l  # Count files
find TODO-001-extracted/ -type d | wc -l  # Count folders

# Windows PowerShell
(Get-ChildItem TODO-001-extracted -Recurse -File).Count  # Files
(Get-ChildItem TODO-001-extracted -Recurse -Directory).Count  # Folders
```

**Expected:** Counts match between UI and extracted ZIP

✅ **Checkpoint 6.4:** ZIP export contains complete artifact collection

### Step 7: Switch View Modes (Optional Feature)

Some UIs offer alternative view modes for artifacts.

#### 7.1: Toggle to List View (If Available)

**Locate view mode toggle:**
- Icons in artifacts toolbar: Tree icon 🌲 and List icon 📋
- View menu: "View" → "List" or "Tree"
- Button labels: "Tree View" / "List View"

**Switch to List View:**
1. Click list icon or "List View" button
2. Tree collapses to flat list

**Expected List View Layout:**
```
| File Name                  | Path                     | Size    | Date       | Actions |
|----------------------------|--------------------------|---------|------------|---------|
| project-charter.md         | artifacts/charters/      | 2.4 KB  | 2026-02-06 | ⬇️ 👁️  |
| stakeholder-register.md    | artifacts/charters/      | 1.8 KB  | 2026-02-06 | ⬇️ 👁️  |
| assumptions-log.md         | artifacts/charters/      | 1.2 KB  | 2026-02-06 | ⬇️ 👁️  |
| project-management-plan.md | artifacts/plans/         | 3.2 KB  | 2026-02-06 | ⬇️ 👁️  |
| risk-register.md           | artifacts/risks/         | 1.5 KB  | 2026-02-06 | ⬇️ 👁️  |
```

**List View Features:**
- All files shown in flat table
- Sortable columns (click column header)
- Path column shows folder location
- Actions column: download, view buttons
- No expand/collapse needed

**Sorting Options:**
- Sort by name (A-Z or Z-A)
- Sort by size (largest first or smallest first)
- Sort by date (newest first or oldest first)
- Sort by type (group by extension)

✅ **Checkpoint 7.1:** List view displayed (if feature available)

**Screenshot Reference:** `docs/screenshots/gui-04-list-view.png`

#### 7.2: Return to Tree View

1. Click tree icon or "Tree View" button
2. Hierarchical folder structure returns
3. Last folder expansion state may be preserved

✅ **Checkpoint 7.2:** Tree view restored

**Note:** If your UI doesn't have list view, skip this step - tree view only is common.

### Step 8: Understand Artifact Metadata

Learn to interpret file information displayed in the UI.

#### 8.1: File Metadata Fields

**For each file in the tree, metadata typically shown:**

| Field | Example | Meaning |
|-------|---------|---------|
| **Name** | `project-charter.md` | File name including extension |
| **Size** | `2.4 KB` | File size in bytes, KB, or MB |
| **Modified** | `2026-02-06` or `2 hours ago` | Last modification timestamp |
| **Type** | `Markdown` or `.md` | File type or extension |
| **Icon** | 📄 | Visual indicator of file type |
| **Path** | `artifacts/charters/` | Full directory path (list view) |

**Size Units:**
- B: Bytes (< 1024 bytes)
- KB: Kilobytes (1024 bytes to 1 MB)
- MB: Megabytes (> 1024 KB)
- Typical artifact sizes: 1-10 KB for text files

**Date Formats:**
- Absolute: `2026-02-06` or `Feb 6, 2026`
- Relative: `2 hours ago` or `Yesterday`
- Hover for full timestamp: `2026-02-06 14:30:22 UTC`

✅ **Checkpoint 8.1:** Understand all metadata fields shown

#### 8.2: Compare Metadata with Backend

**Verify metadata accuracy:**

**Check actual file on backend:**
```bash
# View file details in projectDocs
ls -lh projectDocs/TODO-001/artifacts/charters/project-charter.md

# Expected output:
# -rw-r--r-- 1 user user 2.4K Feb  6 14:30 project-charter.md

# Or get detailed info
stat projectDocs/TODO-001/artifacts/charters/project-charter.md
```

**Expected:**
- File size in UI matches `ls -lh` output
- Modified date in UI matches file timestamp
- File exists at expected path

✅ **Checkpoint 8.2:** UI metadata matches actual file properties

### Step 9: Advanced Artifact Features (Optional)

Explore advanced features if available in your UI.

#### 9.1: File History/Versions (If Supported)

Some implementations track artifact versions:

**Look for:**
- "History" button next to files
- "Versions" dropdown in file viewer
- Git commit integration showing artifact changes

**If available:**
1. Click "History" on `project-charter.md`
2. See list of versions with timestamps
3. View or restore previous versions
4. Compare differences between versions

**Typical Version History:**
```
v3: 2026-02-06 14:30 - Updated success criteria (current)
v2: 2026-02-06 12:15 - Added stakeholder section
v1: 2026-02-06 10:00 - Initial charter creation
```

✅ **Checkpoint 9.1:** Version history explored (if present)

#### 9.2: Artifact Links/References (If Supported)

Some files reference other artifacts:

**Example in project-charter.md:**
```markdown
See also:
- [Stakeholder Register](./stakeholder-register.md)
- [Risk Register](../risks/risk-register.md)
```

**If links are clickable in viewer:**
1. Open `project-charter.md`
2. Click on linked file name
3. Viewer navigates to linked artifact
4. Breadcrumb trail shows navigation path

**Expected Behavior:**
- Links styled differently (blue, underlined)
- Click link to jump to referenced file
- Back button to return to previous file

✅ **Checkpoint 9.2:** Tested artifact cross-references (if supported)

#### 9.3: Bulk Operations (If Supported)

**Advanced UIs may allow:**
- Select multiple files with checkboxes
- Bulk download (downloads as ZIP)
- Bulk delete (caution: may not be available for safety)
- Bulk move to folder

**To test (if available):**
1. Look for checkboxes next to file names
2. Check 2-3 files in charters folder
3. Look for bulk action buttons: "Download Selected" or "Export Selected"
4. Click bulk download
5. ZIP file with only selected files downloads

✅ **Checkpoint 9.3:** Bulk operations tested (if available)

## Artifact Types Reference

Complete guide to artifact types you'll encounter:

| Artifact Type | Folder | ISO 21500 Phase | Typical Size | Purpose |
|---------------|--------|-----------------|--------------|---------|
| **Project Charter** | `charters/` | Initiating | 2-5 KB | Project authorization and high-level info |
| **Stakeholder Register** | `charters/` | Initiating | 1-3 KB | List of stakeholders and their interests |
| **Assumptions Log** | `charters/` | Initiating | 1-2 KB | Project assumptions and constraints |
| **Project Management Plan** | `plans/` | Planning | 3-10 KB | Complete project plan |
| **Scope Statement** | `plans/scope/` | Planning | 2-5 KB | Detailed scope definition |
| **WBS** | `plans/scope/` | Planning | 2-8 KB | Work breakdown structure |
| **Schedule Baseline** | `plans/schedule/` | Planning | 2-5 KB | Approved project schedule |
| **Risk Register** | `risks/` | Planning | 2-10 KB | All identified risks and mitigation plans |
| **Status Reports** | `reports/` | Monitoring | 1-3 KB | Weekly/monthly progress reports |
| **Change Log** | `reports/` | Monitoring | 1-5 KB | Approved project changes |
| **Lessons Learned** | `lessons/` | Closing | 2-8 KB | Project retrospective and learnings |
| **Proposal Archives** | `proposals/` | Any | 1-5 KB | Applied command proposals (historical) |

**File Naming Conventions:**
- Lowercase with hyphens: `project-charter.md`, `risk-register.md`
- No spaces: Use hyphens instead of spaces
- Descriptive: Name indicates content
- Extensions: Always `.md` (Markdown) for text artifacts, `.json` for data exports

## What You've Learned

By completing this tutorial, you can now:

✅ Navigate hierarchical artifact tree structure with confidence  
✅ Expand and collapse folders efficiently  
✅ View Markdown files with proper rendering in browser  
✅ Download individual artifacts to local system  
✅ Search and filter artifacts by name quickly  
✅ Export entire artifact collection as ZIP archive  
✅ Understand artifact metadata (size, date, type)  
✅ Switch between tree and list view modes (if available)  
✅ Verify downloaded artifacts match originals  
✅ Compare artifact structure between UI and filesystem  
✅ Interpret file types and their purposes in ISO 21500 workflow  

**Key Concepts Mastered:**
- Artifact tree navigation patterns
- File viewer modal/drawer UI patterns
- Markdown rendering in browser
- Browser download mechanisms
- ZIP export functionality
- Artifact metadata interpretation
- Search/filter real-time updates
- View mode alternatives (tree vs. list)

## Next Steps

Now that you can efficiently browse and manage artifacts:

1. **[Tutorial 05: Workflow States](05-workflow-states.md)** ✨ NEXT - Visualize ISO 21500 phases and transitions (20 min)
2. **[TUI Artifact Workflow](../tui-basics/03-artifact-workflow.md)** - Command-line artifact browsing for comparison (15 min)
3. **[Advanced: Multi-Project Management](../advanced/04-multi-project.md)** - Manage artifacts across multiple projects (25 min)

**Recommended Path:** Complete Tutorial 05 to understand workflow states, then explore TUI equivalent for efficiency.

## TUI Equivalent

The TUI provides similar functionality via command-line:

**List all artifacts:**
```bash
python apps/tui/main.py artifacts list --project TODO-001
```

**Expected Output:**
```
Artifacts for TODO-001:
  artifacts/charters/project-charter.md (2.4 KB)
  artifacts/charters/stakeholder-register.md (1.8 KB)
  artifacts/charters/assumptions-log.md (1.2 KB)
  artifacts/plans/project-management-plan.md (3.2 KB)
  artifacts/risks/risk-register.md (1.5 KB)

Total: 5 files, 10.1 KB
```

**View specific artifact:**
```bash
python apps/tui/main.py artifacts view --project TODO-001 --path charters/project-charter.md
```

**Export all artifacts as ZIP:**
```bash
python apps/tui/main.py artifacts export --project TODO-001 --output todo-artifacts.zip

# Verify ZIP
unzip -l todo-artifacts.zip
```

**Search artifacts:**
```bash
python apps/tui/main.py artifacts list --project TODO-001 --filter charter
```

See [TUI Artifact Workflow](../tui-basics/03-artifact-workflow.md) for complete command-line tutorial.

**GUI vs TUI Comparison:**
| Feature | GUI (Web) | TUI (CLI) |
|---------|-----------|-----------|
| **Tree Navigation** | Visual expand/collapse | Hierarchical text list |
| **File Viewing** | In-browser rendering | Terminal pager (less/more) |
| **Download** | Click download button | Specify --output path |
| **Export ZIP** | Click "Export All" | `artifacts export` command |
| **Search** | Real-time filter | `--filter` flag |
| **Markdown** | Rendered HTML | Raw or terminal markdown |
| **Bulk Operations** | Checkboxes + buttons | Script with loops |
| **Speed** | Point-and-click | Fast for automation |

**When to use GUI vs TUI:**
- **GUI:** Learning, exploration, visual browsing, one-time downloads
- **TUI:** Automation, scripting, remote SSH access, bulk operations, CI/CD pipelines

## Troubleshooting

Comprehensive troubleshooting guide for artifact browsing issues:

### Issue 1: Artifacts Panel Empty or Loading Forever

**Symptoms:**
- Artifacts section shows "Loading..." indefinitely
- Or shows "No artifacts found" but artifacts should exist
- Tree never populates

**Diagnostic Steps:**
```bash
# 1. Verify artifacts exist on backend
ls -la projectDocs/TODO-001/artifacts/

# Expected: Folders and files present

# 2. Check API endpoint directly
curl http://localhost:8000/artifacts/TODO-001

# Expected: JSON array of artifact objects

# 3. Check browser DevTools Network tab
# Look for failed /artifacts API calls
```

**Solutions:**
- **API not responding:** Restart API container: `docker compose restart api`
- **No artifacts generated:** Run charter command first (see Tutorial 03)
- **Permission errors:** Check projectDocs folder permissions: `chmod -R 755 projectDocs/`
- **CORS issue:** Check browser console for CORS errors, verify API CORS config

**Expected Resolution Time:** 3-8 minutes

### Issue 2: File Viewer Won't Open

**Symptoms:**
- Click file name but nothing happens
- Error: "Cannot load file"
- Viewer opens but shows blank content

**Diagnostic Steps:**
```bash
# 1. Verify file exists and is readable
cat projectDocs/TODO-001/artifacts/charters/project-charter.md

# 2. Test API endpoint
curl http://localhost:8000/artifacts/TODO-001/charters/project-charter.md

# Expected: File content returned

# 3. Check browser console for JavaScript errors
```

**Solutions:**
- **File path encoding:** Special characters in filename may cause issues (rare)
- **File size too large:** Files > 10 MB may not render; download instead
- **Corrupted file:** Regenerate artifact by running command again
- **Modal blocked:** Disable popup blocker for localhost in browser settings
- **React error:** Hard refresh browser (Ctrl+Shift+R)

**Expected Resolution Time:** 5-10 minutes

### Issue 3: Download Fails or Corrupted File

**Symptoms:**
- Download button does nothing
- File downloads but is 0 bytes or corrupted
- Error: "Download failed"

**Diagnostic Steps:**
```bash
# 1. Check file integrity on backend
md5sum projectDocs/TODO-001/artifacts/charters/project-charter.md

# 2. Test direct download via curl
curl -O http://localhost:8000/artifacts/TODO-001/charters/project-charter.md

# 3. Check browser downloads folder
ls -lh ~/Downloads/project-charter.md
```

**Solutions:**
- **Disk space:** Check available disk space: `df -h`
- **Browser permission:** Grant browser permission to download files
- **API streaming issue:** Restart API: `docker compose restart api`
- **Antivirus blocking:** Temporarily disable antivirus or add localhost exception
- **Try different browser:** Test in Chrome, Firefox, Safari

**Expected Resolution Time:** 5-15 minutes

### Issue 4: ZIP Export Fails or Incomplete

**Symptoms:**
- "Export All" button does nothing
- ZIP downloads but is corrupted
- ZIP missing files
- Error: "Failed to create archive"

**Diagnostic Steps:**
```bash
# 1. Check artifacts directory size
du -sh projectDocs/TODO-001/artifacts/

# 2. Manually create ZIP to test
cd projectDocs/TODO-001/
zip -r test-export.zip artifacts/

# 3. Check API logs during export
docker compose logs api --tail=100 | grep -i "export\|zip"
```

**Solutions:**
- **Large artifact set:** Export may timeout (> 100 MB); download folders individually
- **Disk space:** Ensure enough space for ZIP creation: `df -h /tmp`
- **API memory:** Increase API container memory limits in docker-compose.yml
- **Corrupted ZIP:** Try unzipping with `unzip -t file.zip` to test integrity
- **Partial export:** Check which files are missing, re-run commands to regenerate

**Expected Resolution Time:** 10-20 minutes

### Issue 5: Search/Filter Not Working

**Symptoms:**
- Type in search box but tree doesn't filter
- Search shows no results when matches should exist
- Filter clears immediately

**Diagnostic Steps:**
1. Open browser DevTools Console
2. Type in search input
3. Look for JavaScript errors
4. Verify React state updates in React DevTools (if installed)

**Solutions:**
- **JavaScript error:** Check console for errors, may need UI rebuild
- **Input not focused:** Click inside search box to ensure focus
- **Case sensitivity:** Try different case (though search should be case-insensitive)
- **Special characters:** Avoid regex special characters if not supported
- **React state issue:** Hard refresh (Ctrl+Shift+R) to reload app

**Expected Resolution Time:** 2-5 minutes

### Issue 6: Markdown Not Rendering (Shows Raw Text)

**Symptoms:**
- File viewer shows raw Markdown with `#`, `**`, etc.
- No formatting, just plain text
- Links not clickable

**Diagnostic Steps:**
1. Check if "Source" view mode is selected (should be "Rendered")
2. Open browser DevTools Console for errors
3. Test with different Markdown file

**Solutions:**
- **Source mode active:** Toggle to "Rendered" or "Preview" mode
- **Markdown library missing:** Rebuild web container: `docker compose build web`
- **Large file:** Files > 1 MB may show raw text for performance; download instead
- **Unsupported Markdown:** Some extended Markdown features may not render
- **Use external viewer:** Download file and open in dedicated Markdown viewer

**Expected Resolution Time:** 3-8 minutes

## Success Checklist

Before proceeding to Tutorial 05, verify you can:

- [ ] Navigate to Artifacts view for your project
- [ ] See artifact folder tree structure (charters, plans, risks, etc.)
- [ ] Expand and collapse folders by clicking
- [ ] View contents of at least 3 different folders
- [ ] Open `project-charter.md` file and see rendered Markdown
- [ ] Scroll through file content in viewer
- [ ] Close file viewer and return to tree
- [ ] Download `stakeholder-register.md` to local system
- [ ] Verify downloaded file exists and is readable
- [ ] Use search to filter artifacts (e.g., search "charter")
- [ ] Clear search and see full tree again
- [ ] Click "Export All" and download ZIP file
- [ ] Extract ZIP and verify all artifacts present
- [ ] Compare UI artifact count with extracted file count
- [ ] Understand file metadata (size, date, type)
- [ ] Switch between tree and list view (if available)
- [ ] Know where each artifact type is stored (charters/, plans/, etc.)

**Estimated Total Time:** 15-20 minutes (30-45 minutes with troubleshooting)

**If all checkpoints passed:** ✅ Ready for Tutorial 05: Workflow States!

---

**Tutorial Series:** [GUI Basics](../README.md#gui-basics) | **Previous:** [03 - Commands and Proposals](03-commands-and-proposals.md) | **Next:** [05 - Workflow States](05-workflow-states.md)

**Related Tutorials:**
- [TUI Artifact Workflow](../tui-basics/03-artifact-workflow.md) - Command-line artifact browsing
- [Advanced: Artifact Templates](../advanced/02-custom-templates.md) - Customize artifact generation
- [API: Artifacts Endpoints](http://localhost:8000/docs#/artifacts) - API documentation

**Additional Resources:**
- [Markdown Guide](https://www.markdownguide.org/) - Learn Markdown syntax
- [ISO 21500 Artifacts Guide](../../spec/iso21500-artifacts.md) - Complete artifact reference
- [Git Artifact Storage](../../architecture/git-storage.md) - How artifacts are stored
- [Error Catalog](../ERROR-CATALOG.md) - Comprehensive error solutions
