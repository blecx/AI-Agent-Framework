# Tasks: blecs Agent Migration

- [x] Add blecs authority agent definitions
- [x] Add UX modular prompt skills
- [x] Add Spec Kit-compatible command prompts
- [x] Wire runtime UX gate in autonomous workflow
- [x] Extend CI PR gate for UX evidence
- [x] Update existing agents to enforce UX delegation
- [x] Validate prompt quality and CI behavior

## Namespace Alignment TODO (Required Before Phase 2)

- [x] Rename legacy authority agent files and IDs to blecs equivalents
- [x] Rename old extension command files to blecs extension files (`blecs.*`)
- [x] Update all prompt/CI/workflow references to blecs authority names
- [x] Re-run prompt and syntax validation after namespace migration

## Phase 2 TODOs (Integration)

- [ ] Integrate `speckit.*` command flow into operational scripts
- [x] Integrate `blecs.*` workflow packet generation into issue execution flow
- [x] Persist UX consultation outcomes in issue/PR evidence artifacts
- [ ] Add CI/prompt validators for Spec Kit-compatible command prompt contracts
- [ ] Add docs for full transition from legacy prompt flow to blecs Spec Kit flow
- [ ] Add automated checks to prevent UX-authority bypass on UI-affecting issues
