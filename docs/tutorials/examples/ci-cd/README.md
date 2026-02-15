# CI/CD Integration Examples

This directory contains ready-to-use CI/CD workflow examples for automating project management tasks with the AI Agent Framework.

## Overview

These examples demonstrate how to:

- **Auto-generate project artifacts** on repository events
- **Run TUI commands** in headless CI environments
- **Validate project compliance** before deployment
- **Schedule periodic reports** (nightly RAID, weekly status)
- **Commit generated artifacts** back to the repository

## Supported Platforms

- ✅ **GitHub Actions** - Full workflow example with secrets management
- ✅ **GitLab CI** - Multi-stage pipeline with caching
- ⚠️ **Jenkins** - Coming soon (optional)

## Quick Start

### 1. Choose Your Platform

- **GitHub Actions:** Copy [`github-actions-example.yml`](./github-actions-example.yml) to `.github/workflows/project-management.yml`
- **GitLab CI:** Copy [`gitlab-ci-example.yml`](./gitlab-ci-example.yml) to `.gitlab-ci.yml`

### 2. Configure Secrets

Each platform requires these secrets to be set:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `PROJECT_DOCS_PATH` | Path to project docs repo | `/workspace/projectDocs` |
| `GIT_USER_NAME` | Git commit author name | `CI Bot` |
| `GIT_USER_EMAIL` | Git commit author email | `ci-bot@example.com` |
| `LLM_API_KEY` | Optional: LLM API key for AI features | `sk-...` (OpenAI) or `gsk_...` (Groq) |
| `LLM_BASE_URL` | Optional: Custom LLM endpoint | `https://api.groq.com/v1` |

#### GitHub Actions - Setting Secrets

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add each secret from the table above

#### GitLab CI - Setting Variables

1. Go to **Settings** → **CI/CD** → **Variables**
2. Click **Add variable**
3. Mark sensitive variables as **Protected** and **Masked**

### 3. Customize Triggers

#### GitHub Actions Triggers

```yaml
on:
  push:
    branches: [main, develop]  # Run on push to these branches
  schedule:
    - cron: '0 9 * * 1-5'      # Weekdays at 9 AM UTC
  workflow_dispatch:           # Manual trigger
    inputs:
      project_key:
        description: 'Project key to process'
        required: true
```

#### GitLab CI Triggers

```yaml
workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "push"'       # On push
    - if: '$CI_PIPELINE_SOURCE == "schedule"'   # On schedule
    - if: '$CI_PIPELINE_SOURCE == "web"'        # Manual trigger
```

### 4. Test Your Workflow

**GitHub Actions:**
```bash
# Manual trigger via CLI
gh workflow run project-management.yml -f project_key=TEST-12345

# Check run status
gh run list --workflow=project-management.yml
```

**GitLab CI:**
```bash
# Trigger manual pipeline
curl -X POST "https://gitlab.com/api/v4/projects/$PROJECT_ID/pipeline" \
  --header "PRIVATE-TOKEN: $GITLAB_TOKEN"

# Check pipeline status
curl "https://gitlab.com/api/v4/projects/$PROJECT_ID/pipelines" \
  --header "PRIVATE-TOKEN: $GITLAB_TOKEN"
```

## Common Use Cases

### Use Case 1: Auto-Generate Project Charter on Repo Creation

**Trigger:** Repository creation or push to `main`  
**Actions:**
1. Create project in framework
2. Generate project charter artifact
3. Commit charter to `docs/PROJECT_CHARTER.md`

**GitHub Actions Snippet:**
```yaml
- name: Generate Project Charter
  run: |
    cd apps/tui
    python main.py projects create --key ${{ github.repository_owner }}-$(basename ${{ github.repository }})
    python main.py commands propose --project $PROJECT_KEY --command generate_artifact --artifact-name "project-charter.md" --artifact-type "project_charter"
    cp projectDocs/$PROJECT_KEY/artifacts/PROJECT_CHARTER.md $GITHUB_WORKSPACE/docs/
```

### Use Case 2: Nightly RAID Register Report

**Trigger:** Scheduled (daily at 2 AM)  
**Actions:**
1. Generate RAID register for all active projects
2. Filter high-priority items
3. Send email or Slack notification

**GitLab CI Snippet:**
```yaml
nightly-raid-report:
  stage: report
  only:
    - schedules
  script:
    - mkdir -p .tmp
    - curl -s "http://localhost:8000/api/v1/projects/$PROJECT_KEY/raid" | jq '.items[] | select(.priority=="high")' > .tmp/high-priority.txt
    - python scripts/send-email.py --to team@example.com --file .tmp/high-priority.txt
```

### Use Case 3: Post-Merge Artifact Update

**Trigger:** Merge to `main` branch  
**Actions:**
1. Update project status
2. Regenerate all artifacts
3. Commit changes back to docs repo

**GitHub Actions Snippet:**
```yaml
- name: Update Artifacts
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  run: |
    cd apps/tui
    python main.py commands propose --project $PROJECT_KEY --command generate_plan
    python main.py commands apply --project $PROJECT_KEY --proposal "$PROPOSAL_ID"
    cd projectDocs/$PROJECT_KEY
    git add -A
    git commit -m "chore: regenerate artifacts [skip ci]" || echo "No changes"
    git push
```

### Use Case 4: Weekly Compliance Validation

**Trigger:** Scheduled (every Monday at 8 AM)  
**Actions:**
1. Validate all required artifacts exist
2. Check RAID register completeness
3. Generate compliance report
4. Fail pipeline if non-compliant

**GitLab CI Snippet:**
```yaml
weekly-compliance:
  stage: validate
  only:
    - schedules
  script:
    - test -d "projectDocs/$PROJECT_KEY/artifacts"
    - test -f "projectDocs/$PROJECT_KEY/project.json"
    - curl -fsS "http://localhost:8000/api/v1/projects/$PROJECT_KEY/raid" >/dev/null
  allow_failure: false
```

## Environment Setup for CI

### Python Environment

Both workflows install dependencies automatically:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Pro Tip:** Cache dependencies to speed up builds (see examples for cache configuration).

### TUI Headless Mode

The TUI runs in non-interactive mode when `stdin` is not a TTY. No special configuration needed.

### Git Configuration

CI environments need Git credentials to commit artifacts:

```bash
git config --global user.name "$GIT_USER_NAME"
git config --global user.email "$GIT_USER_EMAIL"
```

### Project Docs Repository

**Option 1: Submodule (Recommended)**
```bash
git submodule add https://github.com/yourorg/project-docs.git projectDocs
git submodule update --init --recursive
```

**Option 2: Separate Clone**
```bash
git clone https://github.com/yourorg/project-docs.git projectDocs
```

## Secrets Management Best Practices

### 1. Never Commit Secrets

- ❌ Don't hardcode API keys in workflows
- ✅ Use platform secret stores (GitHub Secrets, GitLab Variables)
- ✅ Use environment variables in scripts

### 2. Rotate Credentials Regularly

- Review access tokens quarterly
- Use short-lived tokens when possible
- Revoke unused credentials

### 3. Limit Secret Scope

- **GitHub:** Mark secrets as environment-specific
- **GitLab:** Use protected and masked variables
- Grant minimum required permissions

### 4. Audit Secret Usage

- **GitHub:** Check Actions logs (secrets are masked)
- **GitLab:** Review CI/CD audit events
- Monitor for unauthorized access

## Troubleshooting

### Issue: "Command not found: python"

**Solution:** Specify Python version in workflow:
```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
```

### Issue: "Permission denied" on git push

**Solution:** Ensure CI has write access to repository:

**GitHub Actions:**
```yaml
permissions:
  contents: write
```

**GitLab CI:**
- Use Deploy Token or Project Access Token with `write_repository` scope

### Issue: "projectDocs directory not found"

**Solution:** Create directory or initialize as submodule:
```bash
mkdir -p projectDocs
# OR
git submodule update --init --recursive
```

### Issue: "LLM service unavailable"

**Solution:** The framework falls back to templates when LLM is unavailable. To enable LLM:
1. Set `LLM_API_KEY` secret
2. Set `LLM_BASE_URL` (if using custom endpoint)
3. Verify API connectivity from CI environment

### Issue: Build timeout

**Solution:** Optimize workflow:
- Cache dependencies (pip, npm)
- Run only necessary steps
- Increase timeout limits

## Advanced Patterns

### Parallel Execution

Process multiple projects simultaneously:

**GitHub Actions:**
```yaml
strategy:
  matrix:
    project: [PROJ-A, PROJ-B, PROJ-C]
steps:
  - name: Process ${{ matrix.project }}
    run: cd apps/tui && python main.py commands propose --project ${{ matrix.project }} --command generate_plan
```

**GitLab CI:**
```yaml
process-projects:
  parallel:
    matrix:
      - PROJECT: [PROJ-A, PROJ-B, PROJ-C]
  script:
    - cd apps/tui && python main.py commands propose --project $PROJECT --command generate_plan
```

### Conditional Execution

Run different steps based on conditions:

**GitHub Actions:**
```yaml
- name: Generate Charter (new projects only)
  if: github.event.action == 'created'
  run: cd apps/tui && python main.py commands propose --project $PROJECT_KEY --command generate_artifact --artifact-name "project-charter.md" --artifact-type "project_charter"
  
- name: Update RAID (existing projects)
  if: github.event.action != 'created'
  run: curl -s "http://localhost:8000/api/v1/projects/$PROJECT_KEY/raid" | jq .
```

**GitLab CI:**
```yaml
generate-charter:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "push" && $CI_COMMIT_BRANCH == "main"'
  script:
    - cd apps/tui && python main.py commands propose --project $PROJECT_KEY --command generate_artifact --artifact-name "project-charter.md" --artifact-type "project_charter"
```

### Artifact Retention

Save generated artifacts for review:

**GitHub Actions:**
```yaml
- uses: actions/upload-artifact@v4
  with:
    name: project-artifacts
    path: projectDocs/${{ env.PROJECT_KEY }}/artifacts/
    retention-days: 90
```

**GitLab CI:**
```yaml
artifacts:
  paths:
    - projectDocs/$PROJECT_KEY/artifacts/
  expire_in: 90 days
```

## Performance Optimization

### 1. Dependency Caching

**GitHub Actions:**
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

**GitLab CI:**
```yaml
cache:
  key: $CI_COMMIT_REF_SLUG
  paths:
    - .cache/pip
```

### 2. Docker Layer Caching

Build Docker images faster:

**GitHub Actions:**
```yaml
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

**GitLab CI:**
```yaml
image: docker:latest
services:
  - docker:dind
variables:
  DOCKER_DRIVER: overlay2
  DOCKER_BUILDKIT: 1
```

### 3. Skip Unnecessary Steps

Use `[skip ci]` in commit messages:
```bash
git commit -m "docs: update README [skip ci]"
```

## Integration with Existing Workflows

### Add to Existing GitHub Actions

Merge into existing workflows:
```yaml
jobs:
  test:
    # ... existing test job ...
  
  project-management:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # ... add project management steps ...
```

### Add to Existing GitLab CI

Extend existing stages:
```yaml
stages:
  - test
  - build
  - project-management  # New stage
  - deploy

# ... existing jobs ...

generate-artifacts:
  stage: project-management
  # ... project management steps ...
```

## Security Considerations

1. **Least Privilege:** Grant minimum required permissions to CI tokens
2. **Audit Logs:** Review CI execution logs regularly
3. **Branch Protection:** Require reviews before merging workflow changes
4. **Secrets Rotation:** Rotate API keys and tokens quarterly
5. **Network Isolation:** Restrict CI runners to private networks when handling sensitive data
6. **Dependency Scanning:** Use Dependabot (GitHub) or Renovate to update dependencies

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [Tutorial: Automation & Scripting](../../advanced/03-automation-scripting.md)
- [TUI Command Reference](../../tui-basics/03-tui-command-cheatsheet.md)
- [API Documentation](/docs/api/)

## Contributing

Found an issue or have an improvement? Please open an issue or submit a PR with your CI/CD example for other platforms (Jenkins, CircleCI, Travis CI, etc.).

## License

Examples are provided under the same license as the AI Agent Framework project.

---

**Last Updated:** 2026-02-16
