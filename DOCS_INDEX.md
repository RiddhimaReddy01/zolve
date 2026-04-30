# Zolve MVP — Documentation Index

**Quick Links by Use Case:**

## 🚀 I want to... **run the project**
1. **START HERE:** [QUICKSTART.md](QUICKSTART.md) — 1-minute setup
2. Then: [README.md](README.md) — Full overview

## 🎬 I want to... **do a demo**
1. **START HERE:** [DEMO_SCRIPT.md](DEMO_SCRIPT.md) — 5-minute walkthrough
2. Reference: [QUICKSTART.md](QUICKSTART.md) — Commands to run

## 🏗️ I want to... **understand the architecture**
1. **START HERE:** [system_design.md](system_design.md) — Complete technical design
2. Visual: [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) — Diagrams
3. Detail: [BEHAVIOR_TRACKING.md](BEHAVIOR_TRACKING.md) — Verified earning system

## ✅ I want to... **verify alignment with spec**
1. **START HERE:** [ALIGNMENT.md](ALIGNMENT.md) — Feature mapping
2. Deep dive: [VERIFICATION_SUMMARY.md](VERIFICATION_SUMMARY.md) — 3-agent verification

## 📊 I want to... **understand what was built**
1. **START HERE:** [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) — Phase-by-phase breakdown
2. Summary: [COMPLETION_SUMMARY.txt](COMPLETION_SUMMARY.txt) — Quick facts

## 🔍 I want to... **judge code quality**
1. Read: [README.md](README.md) — Code structure section
2. Review: `backend/` and `frontend/` source files
3. Reference: [../CLAUDE.md](../CLAUDE.md) — Coding standards used

## 💡 I want to... **understand the problem we solved**
1. **START HERE:** [BEHAVIOR_TRACKING.md](BEHAVIOR_TRACKING.md) — Core differentiator
2. Context: [VERIFICATION_SUMMARY.md](VERIFICATION_SUMMARY.md) — Problem fit section

---

## 📚 All Documents

| Document | Purpose | Read Time | Audience |
|----------|---------|-----------|----------|
| [QUICKSTART.md](QUICKSTART.md) | Setup & run locally | 2 min | Developers |
| [README.md](README.md) | Project overview & API docs | 10 min | Everyone |
| [DEMO_SCRIPT.md](DEMO_SCRIPT.md) | 5-minute demo walkthrough | 5 min | Judges/Investors |
| [system_design.md](system_design.md) | Technical architecture | 20 min | Tech teams |
| [BEHAVIOR_TRACKING.md](BEHAVIOR_TRACKING.md) | Verified earning system | 10 min | Product/Strategy |
| [ALIGNMENT.md](ALIGNMENT.md) | Feature-to-spec mapping | 5 min | Judges |
| [VERIFICATION_SUMMARY.md](VERIFICATION_SUMMARY.md) | 3-agent verification report | 15 min | Judges/Investors |
| [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) | What was built, phase by phase | 15 min | Project review |
| [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) | Visual system diagrams | 10 min | Visual learners |
| [COMPLETION_SUMMARY.txt](COMPLETION_SUMMARY.txt) | Quick facts & metrics | 5 min | Quick reference |

---

## 🎯 For Different Audiences

### **For Judges/Hackathon Committee**
→ Read in order:
1. [QUICKSTART.md](QUICKSTART.md) (how to run)
2. [DEMO_SCRIPT.md](DEMO_SCRIPT.md) (what to demo)
3. [ALIGNMENT.md](ALIGNMENT.md) (spec coverage)
4. [VERIFICATION_SUMMARY.md](VERIFICATION_SUMMARY.md) (verdict)

Expected time: 25 minutes

### **For Engineers/Tech Review**
→ Read in order:
1. [README.md](README.md) (overview)
2. [system_design.md](system_design.md) (architecture)
3. [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) (execution)
4. Source code in `backend/` and `frontend/`

Expected time: 45 minutes

### **For Product/Business**
→ Read in order:
1. [BEHAVIOR_TRACKING.md](BEHAVIOR_TRACKING.md) (core concept)
2. [DEMO_SCRIPT.md](DEMO_SCRIPT.md) (user experience)
3. [README.md](README.md) (business model section)
4. [VERIFICATION_SUMMARY.md](VERIFICATION_SUMMARY.md) (market fit)

Expected time: 30 minutes

### **For Investors**
→ Read in order:
1. [README.md](README.md) (product + business model)
2. [BEHAVIOR_TRACKING.md](BEHAVIOR_TRACKING.md) (differentiation)
3. [VERIFICATION_SUMMARY.md](VERIFICATION_SUMMARY.md) (verdict)
4. [README.md](README.md) (roadmap)

Expected time: 20 minutes

### **For Quick Summary**
→ Read only:
1. [COMPLETION_SUMMARY.txt](COMPLETION_SUMMARY.txt)
2. [DEMO_SCRIPT.md](DEMO_SCRIPT.md) (first 5 minutes)

Expected time: 10 minutes

---

## 🔗 File Organization

```
zolve/
├── README.md                    ← Start here for overview
├── QUICKSTART.md                ← Setup & running
├── DEMO_SCRIPT.md               ← Demo walkthrough
├── system_design.md             ← Technical architecture
├── BEHAVIOR_TRACKING.md         ← Core differentiator
├── ALIGNMENT.md                 ← Feature mapping
├── VERIFICATION_SUMMARY.md      ← Verification report
├── IMPLEMENTATION_STATUS.md     ← What was built
├── SYSTEM_OVERVIEW.md           ← Visual diagrams
├── COMPLETION_SUMMARY.txt       ← Quick facts
├── DOCS_INDEX.md                ← You are here
│
├── backend/
│   ├── main.py                  ← FastAPI app
│   ├── routes/                  ← API endpoints (4 modules)
│   ├── game_engine.py           ← Business logic
│   ├── database.py              ← Database class
│   ├── models.py                ← Pydantic models
│   ├── constants.py             ← Constants
│   ├── exceptions.py            ← Exception hierarchy
│   ├── zolve.db                 ← SQLite database
│   └── requirements.txt          ← Python dependencies
│
├── frontend/
│   └── app.py                   ← Streamlit app (9 pages)
│
└── (project root files)
    ├── .gitignore
    └── CLAUDE.md                ← Coding standards
```

---

## 🎓 Learning Path

**For someone new to the project:**

1. **5 minutes** — Read [QUICKSTART.md](QUICKSTART.md)
   - Understand: How to run
   - Action: Start the servers

2. **10 minutes** — Read [BEHAVIOR_TRACKING.md](BEHAVIOR_TRACKING.md)
   - Understand: Core differentiator (verified earning)
   - Action: Check the database

3. **5 minutes** — Read [README.md](README.md) "Architecture" section
   - Understand: System layers (API, database, frontend)
   - Action: Open browser to http://localhost:8501

4. **5 minutes** — Read [DEMO_SCRIPT.md](DEMO_SCRIPT.md)
   - Understand: User journey
   - Action: Walk through demo yourself

5. **10 minutes** — Explore code:
   - `backend/main.py` — API routes
   - `backend/game_engine.py` — Business logic
   - `frontend/app.py` — UI pages

**Total time: 35 minutes for complete understanding**

---

## 📖 Topic-Based Guide

**Want to understand...**

### How Earning Works
→ [BEHAVIOR_TRACKING.md](BEHAVIOR_TRACKING.md) (earning section)
+ [system_design.md](system_design.md) (9 earning events)
+ `backend/game_engine.py` (source code)

### How Tiers Work
→ [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) (tier system section)
+ [README.md](README.md) (tier thresholds)
+ `backend/game_engine.py` (calculate_user_tier function)

### How Data Flows
→ [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) (data flow diagram)
+ [system_design.md](system_design.md) (database schema)
+ [README.md](README.md) (API endpoints)

### How the Frontend Works
→ [README.md](README.md) (frontend section)
+ [DEMO_SCRIPT.md](DEMO_SCRIPT.md) (page-by-page)
+ `frontend/app.py` (source code)

### How Verified Behaviors Work
→ [BEHAVIOR_TRACKING.md](BEHAVIOR_TRACKING.md) (complete doc)
+ [DEMO_SCRIPT.md](DEMO_SCRIPT.md) (Link Bank section)
+ `backend/routes/bank.py` (source code)

### Why This Differentiates
→ [BEHAVIOR_TRACKING.md](BEHAVIOR_TRACKING.md) (before/after comparison)
+ [DEMO_SCRIPT.md](DEMO_SCRIPT.md) (key messages)
+ [VERIFICATION_SUMMARY.md](VERIFICATION_SUMMARY.md) (problem fit section)

---

## 🎯 Executive Summary (30-Second Version)

**What:** Behavioral finance gamification platform with verified earning system

**Why:** Traditional apps reward free engagement; Zolve rewards real financial discipline

**How:** Users link bank accounts → system auto-detects on-time payments, credit improvements → awards coins → tier progression

**Result:** 95% spec alignment, production-ready code, 5-hour build, ready to demo

---

## ❓ FAQ About Documentation

**Q: Which doc should I read first?**
A: [QUICKSTART.md](QUICKSTART.md) to run it, then [DEMO_SCRIPT.md](DEMO_SCRIPT.md) to understand it.

**Q: Is the code documented?**
A: Yes, all functions have type hints and docstrings. See `backend/` source files.

**Q: Can I just read one document?**
A: Yes: [BEHAVIOR_TRACKING.md](BEHAVIOR_TRACKING.md) covers the core concept.

**Q: Where's the business plan?**
A: [README.md](README.md) has business model. [VERIFICATION_SUMMARY.md](VERIFICATION_SUMMARY.md) has market fit analysis.

**Q: Where's the roadmap?**
A: [README.md](README.md) has 4-phase roadmap. [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) has Phase 2 details.

**Q: How long does it take to read everything?**
A: ~2 hours to read all docs thoroughly. ~30 min for essentials.

---

## 🚀 Next Steps

1. **Run it** — [QUICKSTART.md](QUICKSTART.md)
2. **Demo it** — [DEMO_SCRIPT.md](DEMO_SCRIPT.md)
3. **Review it** — [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)
4. **Deep dive** — [system_design.md](system_design.md)

---

**Questions? Start with [QUICKSTART.md](QUICKSTART.md), then reach out!**
