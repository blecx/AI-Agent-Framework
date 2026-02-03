# Automation and Scripting with TUI

**Estimated Time:** 30 minutes  
**Difficulty:** Advanced  
**Prerequisites:** TUI Basics, ISO 21500 Lifecycle tutorial

## Overview

This tutorial teaches you how to automate common project management workflows using bash scripts and the TUI CLI. Learn to create batch operations, generate reports, and integrate the framework into CI/CD pipelines.

## Learning Objectives

By the end of this tutorial, you will be able to:

1. Write bash scripts to automate project creation
2. Batch-process RAID entries from CSV files
3. Generate automated reports for stakeholder updates
4. Handle errors gracefully in scripts
5. Integrate scripts into CI/CD workflows
6. Schedule automated tasks with cron

## Part 1: Basic Script Structure

### Step 1: Script Template

Create a reusable script template:

```bash
#!/bin/bash
# script-template.sh
# Description: Template for TUI automation scripts

set -euo pipefail  # Exit on error, undefined vars, pipe failures
IFS=$'\n\t'         # Better word splitting

# Configuration
PROJECT_KEY="${1:-}"
TUI_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/../apps/tui" && pwd)"
LOG_FILE="/tmp/tui-automation-$(date +%Y%m%d-%H%M%S).log"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log "ERROR: $1"
    exit 1
}

# Validation
validate_project_key() {
    if [[ -z "$PROJECT_KEY" ]]; then
        error_exit "Usage: $0 <PROJECT_KEY>"
    fi
    
    if [[ ! "$PROJECT_KEY" =~ ^[A-Z0-9-]+$ ]]; then
        error_exit "Invalid project key: $PROJECT_KEY (must be uppercase alphanumeric with hyphens)"
    fi
}

# Main function
main() {
    validate_project_key
    
    log "Starting automation for project: $PROJECT_KEY"
    
    # Your automation logic here
    cd "$TUI_PATH"
    python main.py projects list | grep -q "$PROJECT_KEY" || error_exit "Project not found: $PROJECT_KEY"
    
    log "Automation completed successfully"
}

# Run main
main "$@"
```

**Usage:**
```bash
chmod +x script-template.sh
./script-template.sh TODO
```

### Step 2: Project Creation Script

Automate creating multiple projects:

```bash
#!/bin/bash
# create-projects-batch.sh
# Creates multiple projects from a configuration file

set -euo pipefail

TUI_PATH="apps/tui"
CONFIG_FILE="${1:-projects.csv}"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

# Validate config file exists
[[ -f "$CONFIG_FILE" ]] || { echo "Config file not found: $CONFIG_FILE"; exit 1; }

log "Reading projects from: $CONFIG_FILE"

# CSV format: KEY,NAME,DESCRIPTION
while IFS=',' read -r key name description || [[ -n "$key" ]]; do
    # Skip header and empty lines
    [[ "$key" == "KEY" ]] && continue
    [[ -z "$key" ]] && continue
    
    log "Creating project: $key - $name"
    
    cd "$TUI_PATH"
    python main.py projects create \
        --key "$key" \
        --name "$name" \
        --description "$description" || {
        log "ERROR: Failed to create project $key"
        continue
    }
    
    log "✓ Project created: $key"
    
done < "$CONFIG_FILE"

log "Batch project creation completed"
```

**Create config file:**
```bash
cat > projects.csv << 'EOF'
KEY,NAME,DESCRIPTION
PROJ-A,Project Alpha,Customer portal redesign
PROJ-B,Project Beta,Backend API refactoring
PROJ-C,Project Charlie,Mobile app development
PROJ-D,Project Delta,Database migration to PostgreSQL
EOF
```

**Execute:**
```bash
chmod +x create-projects-batch.sh
./create-projects-batch.sh projects.csv
```

**Output:**
```
[2026-02-03 10:15:23] Reading projects from: projects.csv
[2026-02-03 10:15:23] Creating project: PROJ-A - Project Alpha
[2026-02-03 10:15:25] ✓ Project created: PROJ-A
[2026-02-03 10:15:25] Creating project: PROJ-B - Project Beta
[2026-02-03 10:15:27] ✓ Project created: PROJ-B
...
[2026-02-03 10:15:35] Batch project creation completed
```

## Part 2: RAID Management Automation

### Step 3: Bulk RAID Entry Import

Import RAID entries from CSV:

```bash
#!/bin/bash
# import-raid-entries.sh
# Imports RAID entries from CSV file

set -euo pipefail

PROJECT_KEY="${1:-}"
RAID_FILE="${2:-}"

[[ -z "$PROJECT_KEY" ]] && { echo "Usage: $0 <PROJECT_KEY> <RAID_CSV_FILE>"; exit 1; }
[[ -z "$RAID_FILE" ]] && { echo "Usage: $0 <PROJECT_KEY> <RAID_CSV_FILE>"; exit 1; }
[[ -f "$RAID_FILE" ]] || { echo "RAID file not found: $RAID_FILE"; exit 1; }

TUI_PATH="apps/tui"
TOTAL=0
SUCCESS=0
FAILED=0

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

log "Importing RAID entries for project: $PROJECT_KEY"
log "Source file: $RAID_FILE"

# CSV format: TYPE,SEVERITY,DESCRIPTION,MITIGATION
while IFS=',' read -r type severity description mitigation || [[ -n "$type" ]]; do
    # Skip header
    [[ "$type" == "TYPE" ]] && continue
    [[ -z "$type" ]] && continue
    
    TOTAL=$((TOTAL + 1))
    
    log "Adding RAID entry: $type | $severity | ${description:0:50}..."
    
    cd "$TUI_PATH"
    if python main.py raid add \
        --project "$PROJECT_KEY" \
        --type "$type" \
        --severity "$severity" \
        --description "$description" \
        --mitigation "$mitigation" 2>&1 | tee -a /tmp/raid-import.log; then
        SUCCESS=$((SUCCESS + 1))
        log "✓ Added successfully"
    else
        FAILED=$((FAILED + 1))
        log "✗ Failed to add entry"
    fi
    
done < "$RAID_FILE"

log "Import completed: $SUCCESS success, $FAILED failed out of $TOTAL total"

[[ $FAILED -gt 0 ]] && exit 1
exit 0
```

**Create RAID CSV:**
```bash
cat > raid-entries.csv << 'EOF'
TYPE,SEVERITY,DESCRIPTION,MITIGATION
risk,High,Database downtime during migration,Schedule maintenance window during low-traffic period
risk,Medium,Third-party API rate limits exceeded,Implement caching and request throttling
risk,Low,Team member taking leave during critical phase,Cross-train team members on all components
issue,High,Requirements document missing acceptance criteria,Schedule meeting with Product Owner this week
issue,Medium,Test environment not matching production config,Update test env with production-like settings
assumption,Low,All stakeholders available for weekly sync meetings,Confirmed availability with all stakeholders
dependency,High,Payment gateway approval pending,Escalated to vendor account manager
EOF
```

**Execute:**
```bash
chmod +x import-raid-entries.sh
./import-raid-entries.sh TODO raid-entries.csv
```

### Step 4: RAID Export and Reporting

Generate RAID summary reports:

```bash
#!/bin/bash
# raid-report.sh
# Generates RAID summary report in Markdown

set -euo pipefail

PROJECT_KEY="${1:-}"
OUTPUT_FILE="${2:-raid-report-$(date +%Y%m%d).md}"

[[ -z "$PROJECT_KEY" ]] && { echo "Usage: $0 <PROJECT_KEY> [OUTPUT_FILE]"; exit 1; }

TUI_PATH="apps/tui"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

log "Generating RAID report for project: $PROJECT_KEY"

cd "$TUI_PATH"

# Get RAID data
RAID_JSON=$(python main.py raid export --project "$PROJECT_KEY" --format json 2>/dev/null) || {
    log "ERROR: Failed to export RAID data"
    exit 1
}

# Count by type and severity
RISK_HIGH=$(echo "$RAID_JSON" | jq '[.entries[] | select(.type=="risk" and .severity=="High")] | length')
RISK_MED=$(echo "$RAID_JSON" | jq '[.entries[] | select(.type=="risk" and .severity=="Medium")] | length')
RISK_LOW=$(echo "$RAID_JSON" | jq '[.entries[] | select(.type=="risk" and .severity=="Low")] | length')

ISSUE_HIGH=$(echo "$RAID_JSON" | jq '[.entries[] | select(.type=="issue" and .severity=="High")] | length')
ISSUE_MED=$(echo "$RAID_JSON" | jq '[.entries[] | select(.type=="issue" and .severity=="Medium")] | length')
ISSUE_LOW=$(echo "$RAID_JSON" | jq '[.entries[] | select(.type=="issue" and .severity=="Low")] | length')

TOTAL_ENTRIES=$(echo "$RAID_JSON" | jq '.entries | length')

# Generate Markdown report
cat > "$OUTPUT_FILE" << EOF
# RAID Register Report: $PROJECT_KEY

**Generated:** $(date +'%Y-%m-%d %H:%M:%S')  
**Total Entries:** $TOTAL_ENTRIES

## Summary

| Category | High | Medium | Low | Total |
|----------|------|--------|-----|-------|
| **Risks** | $RISK_HIGH | $RISK_MED | $RISK_LOW | $((RISK_HIGH + RISK_MED + RISK_LOW)) |
| **Issues** | $ISSUE_HIGH | $ISSUE_MED | $ISSUE_LOW | $((ISSUE_HIGH + ISSUE_MED + ISSUE_LOW)) |

## High-Priority Risks

EOF

# Add high-priority risks
echo "$RAID_JSON" | jq -r '.entries[] | select(.type=="risk" and .severity=="High") | "- **\(.id):** \(.description)\n  - Mitigation: \(.mitigation)\n  - Status: \(.status)\n"' >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

## High-Priority Issues

EOF

# Add high-priority issues
echo "$RAID_JSON" | jq -r '.entries[] | select(.type=="issue" and .severity=="High") | "- **\(.id):** \(.description)\n  - Mitigation: \(.mitigation)\n  - Status: \(.status)\n"' >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

## Recommendations

EOF

# Add recommendations based on counts
if [[ $RISK_HIGH -gt 3 ]]; then
    echo "- ⚠️ **High risk count elevated:** Consider risk mitigation workshop" >> "$OUTPUT_FILE"
fi

if [[ $ISSUE_HIGH -gt 5 ]]; then
    echo "- ⚠️ **High issue count elevated:** Allocate additional resources for issue resolution" >> "$OUTPUT_FILE"
fi

if [[ $((RISK_HIGH + ISSUE_HIGH)) -eq 0 ]]; then
    echo "- ✓ **No high-priority items:** Project risk profile is healthy" >> "$OUTPUT_FILE"
fi

log "Report generated: $OUTPUT_FILE"
cat "$OUTPUT_FILE"
```

**Execute:**
```bash
chmod +x raid-report.sh
./raid-report.sh TODO raid-report.md
```

**Output (raid-report.md):**
```markdown
# RAID Register Report: TODO

**Generated:** 2026-02-03 10:30:15  
**Total Entries:** 24

## Summary

| Category | High | Medium | Low | Total |
|----------|------|--------|-----|-------|
| **Risks** | 2 | 4 | 2 | 8 |
| **Issues** | 1 | 3 | 8 | 12 |

## High-Priority Risks

- **RAID-001:** Scope creep due to stakeholder feature requests
  - Mitigation: Establish change control process
  - Status: Mitigated

...
```

## Part 3: Artifact Generation Automation

### Step 5: Batch Artifact Creation

Generate multiple artifacts in sequence:

```bash
#!/bin/bash
# generate-artifacts.sh
# Generates standard project artifacts

set -euo pipefail

PROJECT_KEY="${1:-}"
[[ -z "$PROJECT_KEY" ]] && { echo "Usage: $0 <PROJECT_KEY>"; exit 1; }

TUI_PATH="apps/tui"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

generate_artifact() {
    local type="$1"
    local title="$2"
    local prompt="$3"
    
    log "Generating artifact: $type - $title"
    
    cd "$TUI_PATH"
    python main.py artifacts create \
        --project "$PROJECT_KEY" \
        --type "$type" \
        --title "$title" \
        --prompt "$prompt" || {
        log "ERROR: Failed to generate $type"
        return 1
    }
    
    log "✓ Artifact generated: $type"
    return 0
}

log "Starting artifact generation for project: $PROJECT_KEY"

# Charter
generate_artifact "charter" \
    "Project Charter" \
    "Create a project charter for $PROJECT_KEY. Include: executive summary, objectives, stakeholders, high-level requirements, assumptions, constraints, and success criteria."

# Stakeholder Register
generate_artifact "stakeholders" \
    "Stakeholder Register" \
    "Create a stakeholder register for $PROJECT_KEY. Include key stakeholders with their roles, interest levels, influence, communication preferences, and concerns."

# Requirements
generate_artifact "requirements" \
    "Software Requirements Specification" \
    "Create detailed requirements for $PROJECT_KEY. Include functional requirements, non-functional requirements, user interface requirements, data requirements, and security requirements with IDs and acceptance criteria."

# Test Plan
generate_artifact "test-plan" \
    "Test Plan and Strategy" \
    "Create a comprehensive test plan for $PROJECT_KEY. Include test strategy, test cases, coverage targets, test environment, defect management, and UAT plan."

# WBS
generate_artifact "wbs" \
    "Work Breakdown Structure" \
    "Create a detailed WBS for $PROJECT_KEY. Structure by major phases: Project Management, Requirements, Design, Development, Testing, Deployment. Include work package IDs and estimated hours."

log "Artifact generation completed for project: $PROJECT_KEY"
```

**Execute:**
```bash
chmod +x generate-artifacts.sh
./generate-artifacts.sh PROJ-A
```

### Step 6: Progress Tracking Script

Track project progress and generate status report:

```bash
#!/bin/bash
# project-status.sh
# Generates project status summary

set -euo pipefail

PROJECT_KEY="${1:-}"
[[ -z "$PROJECT_KEY" ]] && { echo "Usage: $0 <PROJECT_KEY>"; exit 1; }

TUI_PATH="apps/tui"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

cd "$TUI_PATH"

log "Fetching status for project: $PROJECT_KEY"

# Get workflow state
STATE=$(python main.py projects show --project "$PROJECT_KEY" 2>/dev/null | grep "Workflow State:" | awk '{print $3}')

# Count artifacts
ARTIFACT_COUNT=$(find "../../projectDocs/$PROJECT_KEY/artifacts/" -type f 2>/dev/null | wc -l)

# Count RAID entries
RAID_TOTAL=$(python main.py raid list --project "$PROJECT_KEY" 2>/dev/null | grep -c "RAID-" || echo "0")

# Get git commit count
cd "../../projectDocs/$PROJECT_KEY"
COMMIT_COUNT=$(git log --oneline | wc -l)

# Recent commits
RECENT_COMMITS=$(git log --oneline -5 | sed 's/^/  /')

cd - > /dev/null

# Generate status report
cat << EOF

╔════════════════════════════════════════════════════════════════╗
║               PROJECT STATUS REPORT: $PROJECT_KEY                    ║
╚════════════════════════════════════════════════════════════════╝

Generated: $(date +'%Y-%m-%d %H:%M:%S')

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Workflow State:       $STATE
  Artifacts:            $ARTIFACT_COUNT
  RAID Entries:         $RAID_TOTAL
  Git Commits:          $COMMIT_COUNT

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RECENT ACTIVITY (Last 5 Commits)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

$RECENT_COMMITS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  → Run gap assessment: python apps/tui/main.py assess-gaps --project $PROJECT_KEY
  → Review RAID register: python apps/tui/main.py raid list --project $PROJECT_KEY
  → View in GUI: http://localhost:5173/?project=$PROJECT_KEY

EOF
```

**Execute:**
```bash
chmod +x project-status.sh
./project-status.sh TODO
```

## Part 4: CI/CD Integration

### Step 7: GitHub Actions Workflow

Integrate TUI into CI/CD pipeline:

```yaml
# .github/workflows/project-validation.yml
name: Project Validation

on:
  push:
    paths:
      - 'projectDocs/**'
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM

jobs:
  validate-projects:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run gap assessment for all projects
        run: |
          cd apps/tui
          for PROJECT in $(python main.py projects list --format json | jq -r '.[].key'); do
            echo "Assessing project: $PROJECT"
            python main.py assess-gaps --project "$PROJECT" || echo "Gap assessment failed for $PROJECT"
          done
      
      - name: Generate RAID reports
        run: |
          mkdir -p reports
          cd apps/tui
          for PROJECT in $(python main.py projects list --format json | jq -r '.[].key'); do
            echo "Generating RAID report for: $PROJECT"
            python main.py raid export --project "$PROJECT" --format markdown > "../../reports/raid-$PROJECT.md"
          done
      
      - name: Upload reports as artifacts
        uses: actions/upload-artifact@v3
        with:
          name: project-reports
          path: reports/
          retention-days: 30
      
      - name: Notify on failure
        if: failure()
        uses: actions/slack@v3
        with:
          status: ${{ job.status }}
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
```

### Step 8: Automated Daily Reports

Use cron to schedule daily reports:

```bash
#!/bin/bash
# daily-report-cron.sh
# Scheduled daily project status report

set -euo pipefail

REPORT_DIR="/var/reports/project-framework"
DATE=$(date +%Y-%m-%d)
TUI_PATH="/home/user/project-framework/apps/tui"

mkdir -p "$REPORT_DIR"

cd "$TUI_PATH"

# Get all projects
PROJECTS=$(python main.py projects list --format json | jq -r '.[].key')

# Generate report for each project
for PROJECT in $PROJECTS; do
    echo "Generating daily report for: $PROJECT"
    
    # Status summary
    python main.py projects show --project "$PROJECT" > "$REPORT_DIR/${PROJECT}-status-${DATE}.txt"
    
    # RAID summary
    python main.py raid list --project "$PROJECT" > "$REPORT_DIR/${PROJECT}-raid-${DATE}.txt"
    
    # Gap assessment
    python main.py assess-gaps --project "$PROJECT" > "$REPORT_DIR/${PROJECT}-gaps-${DATE}.txt"
done

# Combine into daily digest
cat > "$REPORT_DIR/daily-digest-${DATE}.md" << EOF
# Daily Project Digest - $DATE

## Projects Summary

EOF

for PROJECT in $PROJECTS; do
    STATE=$(grep "Workflow State:" "$REPORT_DIR/${PROJECT}-status-${DATE}.txt" | awk '{print $3}')
    RAID_COUNT=$(grep -c "RAID-" "$REPORT_DIR/${PROJECT}-raid-${DATE}.txt" || echo "0")
    
    cat >> "$REPORT_DIR/daily-digest-${DATE}.md" << EOF

### $PROJECT
- **State:** $STATE
- **RAID Entries:** $RAID_COUNT
- [Full Status](./${PROJECT}-status-${DATE}.txt)
- [RAID Register](./${PROJECT}-raid-${DATE}.txt)
- [Gap Assessment](./${PROJECT}-gaps-${DATE}.txt)

EOF
done

# Email report (requires mailutils)
if command -v mail &> /dev/null; then
    mail -s "Daily Project Digest - $DATE" team@example.com < "$REPORT_DIR/daily-digest-${DATE}.md"
fi

# Cleanup old reports (keep 30 days)
find "$REPORT_DIR" -type f -mtime +30 -delete

echo "Daily report generated: $REPORT_DIR/daily-digest-${DATE}.md"
```

**Install as cron job:**
```bash
# Add to crontab
crontab -e

# Run daily at 9 AM
0 9 * * * /path/to/daily-report-cron.sh >> /var/log/project-reports.log 2>&1
```

## Part 5: Advanced Patterns

### Step 9: Parallel Project Processing

Process multiple projects in parallel:

```bash
#!/bin/bash
# parallel-gap-assessment.sh
# Runs gap assessment for all projects in parallel

set -euo pipefail

TUI_PATH="apps/tui"
MAX_PARALLEL=4  # Number of parallel jobs

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

assess_project() {
    local project="$1"
    log "Starting gap assessment for: $project"
    
    cd "$TUI_PATH"
    python main.py assess-gaps --project "$project" > "/tmp/gap-$project.txt" 2>&1
    
    if [ $? -eq 0 ]; then
        log "✓ Gap assessment completed: $project"
    else
        log "✗ Gap assessment failed: $project"
    fi
}

export -f assess_project log
export TUI_PATH

cd "$TUI_PATH"
PROJECTS=$(python main.py projects list --format json | jq -r '.[].key')

log "Running gap assessments for all projects (max $MAX_PARALLEL parallel)"

# Use GNU parallel if available, otherwise fallback to xargs
if command -v parallel &> /dev/null; then
    echo "$PROJECTS" | parallel -j "$MAX_PARALLEL" assess_project {}
else
    echo "$PROJECTS" | xargs -n 1 -P "$MAX_PARALLEL" -I {} bash -c 'assess_project "$@"' _ {}
fi

log "All gap assessments completed"

# Combine results
cat /tmp/gap-*.txt > /tmp/all-gaps-$(date +%Y%m%d).txt
log "Combined report: /tmp/all-gaps-$(date +%Y%m%d).txt"
```

### Step 10: Error Handling and Retry Logic

Robust error handling for production scripts:

```bash
#!/bin/bash
# robust-raid-add.sh
# Adds RAID entry with retry logic

set -euo pipefail

MAX_RETRIES=3
RETRY_DELAY=5

retry_command() {
    local cmd="$1"
    local attempt=1
    
    while [ $attempt -le $MAX_RETRIES ]; do
        echo "[Attempt $attempt/$MAX_RETRIES] Executing: $cmd"
        
        if eval "$cmd"; then
            echo "✓ Command succeeded"
            return 0
        else
            echo "✗ Command failed (attempt $attempt/$MAX_RETRIES)"
            
            if [ $attempt -lt $MAX_RETRIES ]; then
                echo "Retrying in $RETRY_DELAY seconds..."
                sleep $RETRY_DELAY
            fi
        fi
        
        attempt=$((attempt + 1))
    done
    
    echo "ERROR: Command failed after $MAX_RETRIES attempts"
    return 1
}

# Example usage
PROJECT_KEY="TODO"
TUI_PATH="apps/tui"

cd "$TUI_PATH"

retry_command "python main.py raid add \
    --project '$PROJECT_KEY' \
    --type risk \
    --severity High \
    --description 'API rate limit exceeded' \
    --mitigation 'Implement caching and throttling'"

echo "RAID entry added successfully (with retry logic)"
```

## Part 6: Integration with External Tools

### Step 11: JIRA Integration

Sync RAID entries with JIRA:

```bash
#!/bin/bash
# sync-raid-to-jira.sh
# Syncs high-priority RAID entries to JIRA

set -euo pipefail

PROJECT_KEY="${1:-}"
JIRA_PROJECT="${2:-}"
JIRA_URL="${JIRA_URL:-https://your-company.atlassian.net}"
JIRA_TOKEN="${JIRA_TOKEN:-}"

[[ -z "$PROJECT_KEY" ]] || [[ -z "$JIRA_PROJECT" ]] && {
    echo "Usage: $0 <PROJECT_KEY> <JIRA_PROJECT>"
    echo "Set JIRA_URL and JIRA_TOKEN environment variables"
    exit 1
}

TUI_PATH="apps/tui"

cd "$TUI_PATH"

# Export high-priority RAID entries
RAID_JSON=$(python main.py raid export --project "$PROJECT_KEY" --format json)

# Filter high-severity items
HIGH_PRIORITY=$(echo "$RAID_JSON" | jq -r '.entries[] | select(.severity=="High" and .status=="Open")')

echo "$HIGH_PRIORITY" | jq -c '.' | while read -r entry; do
    ID=$(echo "$entry" | jq -r '.id')
    TYPE=$(echo "$entry" | jq -r '.type')
    DESC=$(echo "$entry" | jq -r '.description')
    MITIGATION=$(echo "$entry" | jq -r '.mitigation')
    
    # Check if already exists in JIRA
    JIRA_KEY="$PROJECT_KEY-$ID"
    
    echo "Creating JIRA issue for: $ID"
    
    # Create JIRA issue
    curl -X POST "$JIRA_URL/rest/api/3/issue" \
        -H "Authorization: Bearer $JIRA_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"fields\": {
                \"project\": {\"key\": \"$JIRA_PROJECT\"},
                \"summary\": \"[$TYPE] $DESC\",
                \"description\": {
                    \"type\": \"doc\",
                    \"version\": 1,
                    \"content\": [{
                        \"type\": \"paragraph\",
                        \"content\": [{
                            \"type\": \"text\",
                            \"text\": \"Mitigation: $MITIGATION\"
                        }]
                    }]
                },
                \"issuetype\": {\"name\": \"Task\"},
                \"labels\": [\"raid-sync\", \"$TYPE\", \"auto-created\"]
            }
        }"
    
    echo "✓ JIRA issue created for $ID"
done

echo "RAID sync to JIRA completed"
```

### Step 12: Slack Notifications

Send notifications to Slack:

```bash
#!/bin/bash
# notify-slack.sh
# Sends project status to Slack

set -euo pipefail

PROJECT_KEY="${1:-}"
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"

[[ -z "$PROJECT_KEY" ]] || [[ -z "$SLACK_WEBHOOK" ]] && {
    echo "Usage: $0 <PROJECT_KEY>"
    echo "Set SLACK_WEBHOOK environment variable"
    exit 1
}

TUI_PATH="apps/tui"

cd "$TUI_PATH"

# Get project status
STATE=$(python main.py projects show --project "$PROJECT_KEY" | grep "Workflow State:" | awk '{print $3}')
RAID_COUNT=$(python main.py raid list --project "$PROJECT_KEY" | grep -c "RAID-" || echo "0")

# Get high-priority items
HIGH_RISKS=$(python main.py raid list --project "$PROJECT_KEY" --filter severity=High --filter type=risk | grep -c "RAID-" || echo "0")
HIGH_ISSUES=$(python main.py raid list --project "$PROJECT_KEY" --filter severity=High --filter type=issue | grep -c "RAID-" || echo "0")

# Determine status color
if [[ $HIGH_RISKS -gt 3 ]] || [[ $HIGH_ISSUES -gt 5 ]]; then
    COLOR="#ff0000"  # Red
    STATUS="⚠️ Attention Required"
elif [[ $HIGH_RISKS -gt 0 ]] || [[ $HIGH_ISSUES -gt 0 ]]; then
    COLOR="#ffaa00"  # Orange
    STATUS="⚡ Action Needed"
else
    COLOR="#00ff00"  # Green
    STATUS="✓ On Track"
fi

# Send to Slack
curl -X POST "$SLACK_WEBHOOK" \
    -H "Content-Type: application/json" \
    -d "{
        \"attachments\": [{
            \"color\": \"$COLOR\",
            \"title\": \"Project Status: $PROJECT_KEY\",
            \"fields\": [
                {\"title\": \"Workflow State\", \"value\": \"$STATE\", \"short\": true},
                {\"title\": \"Status\", \"value\": \"$STATUS\", \"short\": true},
                {\"title\": \"Total RAID Entries\", \"value\": \"$RAID_COUNT\", \"short\": true},
                {\"title\": \"High-Priority Risks\", \"value\": \"$HIGH_RISKS\", \"short\": true},
                {\"title\": \"High-Priority Issues\", \"value\": \"$HIGH_ISSUES\", \"short\": true}
            ],
            \"footer\": \"Generated: $(date +'%Y-%m-%d %H:%M:%S')\",
            \"actions\": [{
                \"type\": \"button\",
                \"text\": \"View in GUI\",
                \"url\": \"http://localhost:5173/?project=$PROJECT_KEY\"
            }]
        }]
    }"

echo "✓ Notification sent to Slack"
```

## Summary

**Key Takeaways:**

1. **Script Structure:** Use proper error handling, logging, and validation
2. **Batch Operations:** Automate repetitive tasks (project creation, RAID import)
3. **Reporting:** Generate automated reports for stakeholders
4. **CI/CD Integration:** Include project validation in pipelines
5. **External Tools:** Integrate with JIRA, Slack, email for team collaboration
6. **Scheduled Tasks:** Use cron for daily/weekly automated reports
7. **Error Handling:** Implement retry logic and graceful degradation
8. **Parallel Processing:** Speed up batch operations with parallelization

**Best Practices:**

- Always validate inputs
- Log all actions with timestamps
- Handle errors gracefully
- Use configuration files for batch operations
- Test scripts with dry-run mode before production
- Document script usage and parameters
- Version control your automation scripts
- Monitor script execution and failures

## Additional Resources

- [TUI Command Reference](../tui-basics/03-tui-command-cheatsheet.md)
- [Bash Scripting Best Practices](https://google.github.io/styleguide/shellguide.html)
- [jq Manual](https://stedolan.github.io/jq/manual/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Cron Syntax Guide](https://crontab.guru/)
