# AutoSystems Lead Scoring Guide

## How Scoring Works

Every lead is scored **0–100 points** across 4 criteria. The total determines the tier.

---

## The 4 Criteria

### 1. Firmographic Fit — up to 30 points
_"Is this company the right size for us?"_

| Company Size | Points |
|---|---|
| 10–150 employees | **30** ← sweet spot |
| 150–350 employees | 24 |
| 350–500 employees | 16 |
| Fewer than 10 employees | 8 |
| 500–1000 employees | 5 |
| More than 1000 employees | **0** ← auto-disqualify |
| Unknown | 13 |

> AutoSystems is built for SMBs. A solo freelancer has no budget. A Fortune 500 has a 6-month procurement cycle. The 10–150 range is the sweet spot.

---

### 2. Sales Automation Need — up to 25 points
_"Does this company have a sales problem we can actually solve?"_

| Signal | Points |
|---|---|
| Active B2B sales team, high lead volume, outbound campaigns | **25** |
| Some outbound effort, growing sales team, client-acquisition focus | 20 |
| Owner-led sales, mostly inbound, early stage | 14 |
| No clear sales function (NGO, government, content-only) | 5 |
| Cannot determine from research | 11 |

> A logistics company processing hundreds of leads/week = perfect fit. A lifestyle blog = not a fit.

---

### 3. Growth Momentum — up to 25 points
_"Are they growing? Growing companies have budget and urgency."_

| Signal | Points |
|---|---|
| Raised funding **AND** actively hiring | **25** |
| Raised funding **OR** actively hiring sales/marketing | 22 |
| New product, major partnership, expansion announced | 18 |
| Some online activity, moderate news | 12 |
| Minimal presence, no growth signals | 6 |
| Declining (layoffs, pivot away, funding dried up) | 2 |
| No data available | 9 |

> A company that just raised a Series A and is hiring 5 sales reps needs sales automation **now**.

---

### 4. Risk & Credibility — up to 20 points
_"Is this a legitimate business we want to work with?"_

| Signal | Points |
|---|---|
| Established, verifiable, no red flags | **20** |
| Legitimate but limited public info or old minor press | 16 |
| Active concerns (bad press, unclear leadership) | 8 |
| Major red flags (fraud, lawsuits, imminent shutdown) | 0 |
| Cannot assess | 14 |

---

## Tier Thresholds

```
80 – 100  →  HOT          Immediate personal outreach. Auto-email sent.
60 –  79  →  WARM         Personalized email campaign. Follow up in 3 days.
40 –  59  →  COLD         Add to nurture sequence.
 0 –  39  →  DISQUALIFY   Not a fit. Stop here.
```

---

## Real Examples

### Packworks (PH B2B SaaS, ~80 employees, funded, mobile ERP for SMEs)
| Criterion | Reasoning | Points |
|---|---|---|
| Firmographic Fit | ~80 employees = sweet spot | **30** |
| Sales Need | B2B SaaS with active sales team | **25** |
| Growth Momentum | Funded + likely hiring | **22** |
| Risk & Credibility | Established, no red flags | **18** |
| **TOTAL** | | **95 → HOT** |

---

### Unknown company (no verifiable data at all)
| Criterion | Reasoning | Points |
|---|---|---|
| Firmographic Fit | Unknown size | **13** |
| Sales Need | Cannot determine | **11** |
| Growth Momentum | No data | **9** |
| Risk & Credibility | Cannot assess | **14** |
| **TOTAL** | | **47 → COLD** |

> ✓ Unknown = COLD, not WARM. This is intentional. If we can't verify a company exists, we don't chase it.

---

### Apple Inc (>1000 employees)
| Criterion | Reasoning | Points |
|---|---|---|
| Firmographic Fit | 166,000 employees = hard disqualify | **0** |
| Sales Need | Has dedicated sales org | 5 |
| Growth Momentum | Active company | 22 |
| Risk & Credibility | Established | 20 |
| **TOTAL** | Capped at low → | **DISQUALIFY** |

---

## Key Design Decisions

| Decision | Why |
|---|---|
| Unknown data leans COLD, not neutral | Encourages inbound leads to provide real info. Prevents garbage leads scoring WARM. |
| No "job title" criterion | We often don't know who submitted. AutoSystems sells to owners/ops leads anyway. |
| Firmographic Fit worth 30 pts | The most important signal — no amount of growth compensates for enterprise procurement. |
| Growth Momentum worth 25 pts | Budget availability and urgency are directly correlated with recent funding/hiring. |
| Hard enterprise disqualifier | >1000 employees → Criterion 1 = 0, total cannot reach HOT or WARM. |

---

_Scoring is performed by Groq (llama-3.3-70b-versatile) with Gemini 1.5 Flash as fallback._
