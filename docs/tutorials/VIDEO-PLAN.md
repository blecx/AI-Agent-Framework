# Video Content Plan

This document outlines the planned video content for the ISO 21500 AI-Agent Framework tutorials. Videos are planned but not yet created.

---

## 🎯 Video Strategy

**Goals:**
- Visual demonstrations of key workflows
- Reduce learning curve for new users
- Show real-time interaction and feedback
- Complement written tutorials with visual learning

**Format:**
- 5-20 minute focused videos
- Screen recordings with voiceover
- Timestamped sections for easy navigation
- Subtitles/transcripts for accessibility

**Hosting:**
- YouTube (primary) or similar platform
- Embedded in documentation when possible
- Links in tutorials
- Playlist organization by learning path

---

## 📹 Priority 1: Core Concepts (5-10 min each)

Essential videos covering fundamental concepts. Target: New users in first 30 minutes.

### 1. System Overview and Architecture (7 min)
**Covers:**
- Three-client architecture (Web UI, TUI, CLI)
- API-first design benefits
- Docker container communication
- Git-based document storage
- ISO 21500 project management concepts

**Value:** Helps users understand "the big picture" before diving into details.

---

### 2. Docker Setup Walkthrough (5 min)
**Covers:**
- Prerequisites check
- `docker compose up` execution
- Verifying services (health checks)
- Accessing Web UI and API docs
- Common first-run issues

**Value:** Reduces setup friction, most common barrier for new users.

---

### 3. TUI vs GUI Decision Guide (6 min)
**Covers:**
- When to use Web UI (visual, interactive)
- When to use TUI (automation, scripting)
- Hybrid workflows (using both)
- Remote access considerations
- Performance comparison

**Value:** Helps users choose the right interface for their workflow.

---

### 4. Propose/Apply Workflow Explanation (8 min)
**Covers:**
- Why two-step workflow matters
- Reviewing proposals before applying
- Using diff viewer effectively
- Handling rejected proposals
- Best practices for safe changes

**Value:** Core workflow understanding prevents mistakes.

---

## 📹 Priority 2: Tutorial Companions (follow tutorial structure)

Video walkthroughs matching existing written tutorials. Target: Users working through tutorials.

### 1. Beginner Path (10 min)
**Follows tutorials:**
- TUI Quick Start (01-quick-start.md)
- First Project (02-first-project.md)
- RAID Management (04-raid-management.md)

**Covers:**
- Live demonstration of all commands
- Expected output at each step
- Common mistakes and fixes
- Tips for efficiency

**Value:** Side-by-side learning with written tutorials.

---

### 2. Intermediate Path (15 min)
**Follows tutorials:**
- Artifact Workflow (03-artifact-workflow.md)
- Full Lifecycle (05-full-lifecycle.md)

**Covers:**
- Complete project lifecycle
- Multiple artifact types
- Template usage
- Quality gates

**Value:** Shows how pieces fit together in real projects.

---

### 3. Advanced Path (20 min)
**Follows tutorials:**
- TUI-GUI Hybrid (advanced/01-tui-gui-hybrid.md)
- Complete ISO 21500 (advanced/02-complete-iso21500.md)
- Automation/Scripting (advanced/03-automation-scripting.md)

**Covers:**
- Advanced workflows
- Automation examples
- CI/CD integration
- Custom templates

**Value:** Demonstrates production-ready usage patterns.

---

## 📹 Priority 3: Deep Dives (15-20 min each)

In-depth exploration of specific topics. Target: Users wanting deep understanding.

### 1. ISO 21500 Phases Explained (18 min)
**Covers:**
- Initiation artifacts (charter, stakeholders)
- Planning artifacts (WBS, schedule, budget)
- Execution tracking (status reports, changes)
- Control processes (RAID, quality)
- Closure documentation (lessons learned)

**Value:** Connects technical tool to project management theory.

---

### 2. Template Customization (15 min)
**Covers:**
- Template structure (Jinja2)
- Prompt engineering for LLMs
- Output format customization
- Adding new artifact types
- Testing templates

**Value:** Enables users to adapt framework to their needs.

---

### 3. CI/CD Integration Patterns (20 min)
**Covers:**
- GitHub Actions integration
- Automated project updates
- Scheduled artifact generation
- Quality gate enforcement
- Deployment workflows

**Value:** Shows production automation examples.

---

## 🎬 Recording Setup Guide

### Tools Required

**Screen Recording:**
- OBS Studio (recommended, open-source)
- Camtasia (alternative, paid)
- macOS: QuickTime Player + ScreenFlow
- Linux: SimpleScreenRecorder or Kazam

**Audio:**
- USB microphone (Blue Yeti, Audio-Technica AT2020)
- Noise cancellation (Krisp, RTX Voice)
- Audio editing: Audacity (free)

**Editing:**
- DaVinci Resolve (free, professional)
- OpenShot (free, simple)
- Adobe Premiere (paid)

### Recording Best Practices

**Preparation:**
1. Clean environment (docker compose down -v)
2. Fresh terminal with clear history
3. Prepared examples and data
4. Script or outline (not word-for-word)
5. Test audio levels

**During Recording:**
1. Start with title card (tutorial name, duration)
2. Speak clearly and at moderate pace
3. Pause between sections (easier editing)
4. Show errors and fixes (learning opportunity)
5. Use cursor highlighting for focus

**Post-Production:**
1. Cut dead air and mistakes
2. Add chapter markers (YouTube)
3. Speed up long waits (docker build, etc.)
4. Add text overlays for key commands
5. Generate subtitles (YouTube auto or manual)

### Format Specifications

**Video:**
- Resolution: 1920x1080 (1080p minimum)
- Frame rate: 30fps
- Format: MP4 (H.264)
- Bitrate: 5-8 Mbps

**Audio:**
- Sample rate: 48kHz
- Bitrate: 192 kbps
- Format: AAC
- Mono or stereo

**Length:**
- Core concepts: 5-10 minutes
- Tutorial companions: 10-20 minutes
- Deep dives: 15-25 minutes
- Maximum: 30 minutes (attention span)

---

## 🤝 Contribution Guide for Video Creators

### How to Contribute Videos

1. **Check VIDEO-PLAN.md** for planned topics
2. **Claim a topic** by commenting on Issue #186
3. **Record following guidelines** above
4. **Submit for review** via PR (link to hosted video)
5. **Iterate based on feedback**
6. **Publish** and update tutorials with links

### Video Hosting

**Approved Platforms:**
- YouTube (primary, best for embedding)
- Vimeo (alternative)
- GitHub Releases (short clips only)
- Self-hosted (with CDN, not recommended)

**Requirements:**
- Public or unlisted (not private)
- Downloadable preferred (resilience)
- Subtitles/captions included
- Creative Commons license preferred

### Quality Standards

**Must Have:**
- Clear audio (no background noise)
- Readable text (large fonts)
- Follows tutorial structure
- Shows successful completion
- Under 30 minutes

**Nice to Have:**
- Chapter markers
- Manual subtitles
- Multiple takes (A/B comparison)
- Error demonstrations
- Links to related content

### Review Process

1. **Submit PR** with video link and tutorial updates
2. **Maintainer review** (content accuracy, quality)
3. **Community feedback** (optional, for major videos)
4. **Revisions** if needed
5. **Merge** when approved
6. **Announce** in releases/discussions

---

## 📊 Success Metrics

When videos are published, track:

- View count and watch time
- Tutorial completion rates (before/after videos)
- User feedback (comments, surveys)
- Support question reduction
- Contributor participation

**Target Metrics:**
- 70% video watch-through rate
- 20% increase in tutorial completion
- 30% reduction in setup-related questions

---

## 🔮 Future Enhancements

**Phase 2 (if successful):**
- Animated explainer videos (Whiteboard style)
- Interactive video tutorials (branch points)
- Live coding sessions (Twitch/YouTube Live)
- Community-contributed tips (short clips)

**Accessibility:**
- Full transcripts for all videos
- Sign language interpretation (priority videos)
- Audio descriptions for visual elements
- Multi-language subtitles

**Platform Integration:**
- Video player in documentation
- Progress tracking across tutorials
- Video-specific feedback forms
- Certificate of completion (with video views)

---

## 📝 Notes for Maintainers

- Keep VIDEO-PLAN.md updated as videos are created
- Mark completed videos with ✅ and links
- Track feedback and iterate on format
- Budget for hosting costs (YouTube is free but has ads)
- Consider sponsorship for professional production
- Archive source files (unedited recordings)

---

**Last Updated:** 2026-02-06  
**Status:** Planning phase (no videos created yet)  
**Next Steps:** Add placeholders to tutorials, recruit contributors

**Questions?** Open an issue or discussion in the repository.
