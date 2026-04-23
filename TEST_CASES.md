# Batch Qualification Test Cases

## Instructions
Copy the test cases below and paste into the Dashboard batch textarea.
Format: `Company, Email, Lead Name`

---

## Test Set 1: HOT Leads (Expected: 80-100 score, auto-email)
```
Packworks, partnerships@packworks.ph, Mark Santiago
TaskUs Philippines, careers@taskus.com, Ana Rodriguez
Concentrix Manila, hr.manila@concentrix.com, Maria Garcia
Teleperformance PH, recruitment@teleperformance.ph, Juan Cruz
Foundever Philippines, hiring@foundever.ph, Rosa Alvarez
```

**Why HOT:**
- Large BPO/tech firms with 500+ employees
- Active hiring signals (careers pages, job boards)
- Known for outsourcing/staffing needs
- Stable, established companies

---

## Test Set 2: WARM Leads (Expected: 60-79 score)
```
Sprout Solutions, hr@sproutsolutions.com.ph, Lisa Tan
GrowSari, partnerships@growsari.com, Carlos Mendoza
Voyager Innovations, info@voyagerinnovation.com, Patricia Lee
Taxumo, hello@taxumo.com, Miguel Santos
HealthNow, contact@healthnow.ph, Elena Reyes
```

**Why WARM:**
- Mid-sized tech/SaaS companies (50-200 employees)
- Growing but not massive hiring volume
- Some outsourcing potential
- May need contractors but not at BPO scale

---

## Test Set 3: COLD Leads (Expected: 40-59 score)
```
Sari-Sari Store Network, contact@sarisari.ph, Jun Rodriguez
Local Bakery Co, info@localbakery.ph, Anna Cruz
Tindahan Express, hello@tindahan.ph, Pedro Garcia
Small Logistics Inc, admin@smalllogistics.ph, Maria Santos
Corner Store PH, info@cornerstore.ph, Jose Alvarez
```

**Why COLD:**
- Very small businesses (<20 employees)
- Minimal web presence
- Low hiring volume
- Limited budget for staffing services

---

## Test Set 4: DISQUALIFY Leads (Expected: 0-39 score)
```
Freelance Design Studio, solo@freelancedesign.ph, Single Person
Home-Based Consulting, me@homebased.ph, Solo Consultant
Personal Blog Services, personal@blog.ph, Individual Blogger
One-Person Shop, owner@oneperson.ph, Self Employed
Micro Business, micro@business.ph, Solopreneur
```

**Why DISQUALIFY:**
- Sole proprietors / freelancers
- No hiring needs
- Zero outsourcing potential
- Not a target customer for RSS

---

## Test Set 5: Edge Cases (Mixed)
```
Unknown Company XYZ, contact@unknownxyz.ph, Mystery Person
Brand New Startup, hello@brandnewstartup.ph, Founder Name
Non-Existent Corp, fake@nonexistent.ph, Test Lead
Stealth Mode Inc, stealth@stealth.ph, Anonymous
Unverifiable Business, info@unverifiable.ph, Unknown Contact
```

**Why Edge:**
- Minimal or no web presence
- May not return search results
- Tests fallback behavior
- Verifies error handling

---

## Quick Smoke Test (2 leads, fast validation)
```
Packworks, partnerships@packworks.ph, Mark Santiago
Sprout Solutions, hr@sproutsolutions.com.ph, Lisa Tan
```

**Expected:**
- Packworks → HOT (85-95 range) + auto-email sent
- Sprout → WARM (70-80 range) + email drafted

---

## Usage Instructions

1. **Start backend server:**
   ```bash
   cd backend
   python -m uvicorn main:app --reload --port 8000
   ```

2. **Start frontend dev server:**
   ```bash
   npm run dev
   ```

3. **Navigate to dashboard:**
   - Open `http://localhost:3000/dashboard`
   - Password: `dajackal23`

4. **Run test:**
   - Copy any test set above
   - Paste into the "Companies" textarea
   - Ensure Region is set to "Philippines"
   - Click "Run Batch"
   - Watch live step feed (researching → scoring → drafting_email → logging → done)
   - Check Run History table below for results

5. **Verify results:**
   - Scores match expected tiers (HOT/WARM/COLD/DISQUALIFY)
   - HOT leads show email drafts in expanded view
   - Telegram alert sent for HOT leads (check your Telegram)
   - Email auto-sent for HOT leads (check Gmail sent folder: beerusgaming24@gmail.com)

---

## What to Look For

### ✅ Success Criteria
- [ ] All leads complete without errors
- [ ] Scores align with expected tiers
- [ ] HOT leads (≥80) have email drafts
- [ ] WARM leads (60-79) have email drafts or skip message
- [ ] COLD/DISQUALIFY leads show no email draft
- [ ] Live status updates in real-time during batch
- [ ] Run history populates after batch completes
- [ ] Pagination works (if >10 results in history)
- [ ] Telegram alert fires for HOT leads
- [ ] Auto-email sends for HOT leads

### ⚠️ Watch For
- Step gets stuck (doesn't progress after 30s)
- Score reasoning doesn't match RSS/staffing criteria
- Email draft is generic (not mentioning staffing/outsourcing)
- Region field not being used in search
- SSE stream drops mid-batch

### 🐛 Known Issues
- If Groq rate limit hit: falls back to Gemini (check logs)
- If Serper quota exhausted: search returns empty (leads will score low)
- Very obscure companies: may return "insufficient data" reasoning

---

## Expected Execution Time

- **1 lead:** ~15-20 seconds (research 5s, scoring 8s, email 5s, logging 2s)
- **5 leads:** ~2 minutes (with 2s delay between leads)
- **10 leads:** ~4 minutes (max batch size)

---

## Troubleshooting

**If batch fails:**
1. Check backend logs for errors
2. Verify API keys in `backend/.env`:
   - GROQ_API_KEY
   - SERPER_API_KEY
   - GEMINI_API_KEY
   - SUPABASE_URL + SUPABASE_KEY
3. Test single lead via curl:
   ```bash
   curl -X POST http://localhost:8000/qualify-lead \
     -H "Content-Type: application/json" \
     -H "X-API-Key: e1c9b566629d69d4f8141500aae64a186b16266639b59335f9ef75276e35586a" \
     -d '{
       "lead_name": "Test Person",
       "company": "Packworks",
       "email": "test@packworks.ph",
       "source": "manual_test",
       "region": "Philippines"
     }'
   ```

**If history table empty:**
- Click Refresh button in header
- Check browser console for errors
- Verify `GET /leads` returns data:
  ```bash
  curl -s "http://localhost:8000/leads?limit=5" \
    -H "X-API-Key: e1c9b566629d69d4f8141500aae64a186b16266639b59335f9ef75276e35586a"
  ```

**If Typebot bubble appears on dashboard:**
- Verify `components/typebot-widget.tsx` exists
- Check `app/layout.tsx` imports TypebotWidget component
- Refresh browser (hard refresh: Ctrl+Shift+R)
