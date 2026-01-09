# Project Schedule

**Project:** {{ project_name }}  
**Project Key:** {{ project_key }}  
**Generated:** {{ timestamp }}  
**Standard:** ISO 21500

---

## Schedule Overview

{{ llm_schedule }}

---

## Gantt Chart

```mermaid
gantt
    title {{ project_name }} Project Schedule
    dateFormat YYYY-MM-DD
    section Initiation
    Project Charter           :a1, 2024-01-01, 5d
    Stakeholder Identification :a2, after a1, 3d
    section Planning
    Scope Definition          :b1, after a2, 7d
    WBS Creation             :b2, after b1, 5d
    Schedule Development     :b3, after b2, 7d
    Resource Planning        :b4, after b3, 5d
    section Execution
    Deliverable Production   :c1, after b4, 30d
    Quality Assurance        :c2, after c1, 10d
    section Closure
    Final Documentation      :d1, after c2, 5d
    Lessons Learned         :d2, after d1, 3d
```

---

## Key Milestones

| Milestone | Target Date | Description |
|-----------|------------|-------------|
| Project Kickoff | Week 1 | Project initiation complete |
| Planning Complete | Week 4 | All plans approved |
| Execution Start | Week 5 | Begin deliverable production |
| Quality Review | Week 10 | QA checkpoint |
| Project Closure | Week 12 | Final deliverables and documentation |

---

*This schedule follows ISO 21500 project management standards and should be updated regularly.*
