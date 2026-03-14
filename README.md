# RefundPilot — Smarter Refunds for Modern Commerce

> *"Meet Priya. Meet Rohit. One deserves her money back instantly. The other is gaming the system. Today, both wait 15 days. RefundPilot knows the difference in 4 seconds."*

---

## The Story Behind RefundPilot

It started with a ₹800 kurta.

My friend Priya ordered a cotton kurta online. It arrived with a tear on the sleeve. She raised a refund. Then she waited. 3 days for a reply. Support asked for photos via email. 5 more days. Finally approved. Then 7 more days for the money to hit her account.

**Total: 15 days. On Day 3, she left a 1-star review. She never shopped there again.**

The merchant lost a lifetime customer over ₹800 —> an amount they were always going to approve anyway.

Meanwhile, Rohit returned 8 of his last 12 orders. Always "damaged in transit." He signed for every delivery. He never provided photos when asked. He cost one merchant ₹47,000 that year. Nobody noticed because every refund looked identical in a manual queue.

**Same system. Same 15-day wait. One honest customer. One serial abuser. Both treated identically.**

That's when it hit us: **the refund decision isn't a queue problem , it's an intelligence problem.** What if an autonomous AI agent could look at the refund request, pull the customer's history, check for fraud patterns, and make a decision in 4 seconds?

That's RefundPilot.

---

## What is RefundPilot?

RefundPilot is an **autonomous AI agent** that evaluates every refund request in real-time and makes an instant **approve**, **investigate**, or **escalate** decision — without human involvement for ~80% of cases.

### The 4-Second Loop

```
Refund Request → 10 Signal Analysis → Weighted Risk Score → 3-Tier Decision → Action
```

1. **OBSERVE** — Refund request arrives
2. **COLLECT** — Agent pulls 10 signals: delivery status, customer history, product risk, amount, claim pattern, RFM, cross-merchant intelligence
3. **SCORE** — Deterministic weighted formula computes risk score (0–100)
4. **DECIDE** — 3-tier logic: math decides clear cases, AI decides gray areas
5. **ACT** — Pine Labs Refund API / Evidence request / Case brief

---

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│   Customer   │     │   Merchant   │     │  Chat / WhatsApp │
│  Refund Req  │     │  Dashboard   │     │   (Hindi/English)│
└──────┬───────┘     └──────┬───────┘     └────────┬─────────┘
       │                    │                       │
       ▼                    ▼                       ▼
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React + Vite)                  │
│  Submit Refund │ Dashboard │ Chat │ Live Demo (3-character)  │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API + WebSocket
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (Python + FastAPI)                  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              AGENT ORCHESTRATOR (F22: Locked)         │    │
│  │                                                      │    │
│  │  Signal Collector ──→ Risk Scorer ──→ Decision Engine │    │
│  │  (10 signals)         (weighted math)  (3-tier logic) │    │
│  │       │                    │                │         │    │
│  │       ▼                    ▼                ▼         │    │
│  │  RFM Analysis      Deterministic      ReAct Loop      │    │
│  │  Cross-Merchant    Score 0-100        (GLM-5 for      │    │
│  │  Fraud Ring        Same input =       gray zone)      │    │
│  │  Sentiment         Same output                        │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  Action Executor ─── Pine Labs API (real orders + links)     │
│  Vision Analyzer ─── Groq Llama-4 (stock photo detection)   │
│  Fraud Detector ──── SQL graph (ring detection F20)          │
│  NL Query Engine ─── Regex intent matching                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
   ┌──────────────┐ ┌───────────┐ ┌──────────────┐
   │   GLM-5      │ │ Pine Labs │ │   SQLite     │
   │  (ZhipuAI)   │ │ Plural    │ │  (Demo DB)   │
   │              │ │ UAT API   │ │              │
   │ Explanations │ │ Orders    │ │ 9 Customers  │
   │ ReAct Loop   │ │ Refunds   │ │ 28 Orders    │
   │              │ │ Pay Links │ │ 23 Refunds   │
   │  Groq        │ │ Settle.   │ │ Fraud Ring   │
   │  (Vision)    │ │           │ │ Cross-Merch  │
   └──────────────┘ └───────────┘ └──────────────┘
```

---

## The 3 Cases — Sequence Diagrams

### Case 1: Priya (Loyal Customer → AUTO_APPROVE)

```
Priya                    RefundPilot Agent              Pine Labs
  │                           │                           │
  │── "Kurta arrived torn" ──→│                           │
  │                           │── Collect 10 signals      │
  │                           │   S1: 2% refund rate ✅    │
  │                           │   S2: No contradiction ✅  │
  │                           │   S3: ₹800 low risk ✅     │
  │                           │   S4: First claim ✅       │
  │                           │   S7-S9: RFM clean ✅      │
  │                           │   S10: 0 cross-merchant ✅ │
  │                           │                           │
  │                           │── Score: 28/100           │
  │                           │── Decision: AUTO_APPROVE   │
  │                           │                           │
  │                           │── Create Order ──────────→│
  │                           │←── order_id: v1-XXXXX ───│
  │                           │── Initiate Refund ───────→│
  │                           │                           │
  │←── "Approved in 3.9s" ───│                           │
  │    Return pickup scheduled │                           │
  │    ₹800 refund confirmed  │                           │
```

**Result:** Priya gets her money back in seconds. She stays a customer.

### Case 2: Vikram (Suspect → INVESTIGATE via ReAct Loop)

```
Vikram                   RefundPilot Agent              GLM-5 / Groq
  │                           │                           │
  │── "Shoes don't match" ───→│                           │
  │                           │── Collect 10 signals      │
  │                           │   S1: 50% refund rate 🚩  │
  │                           │   S4: 4th same claim 🚩   │
  │                           │   S10: 1 cross-merchant ⚠ │
  │                           │                           │
  │                           │── Score: 55/100           │
  │                           │── Decision: INVESTIGATE    │
  │                           │                           │
  │                           │── ReAct Loop begins ─────→│
  │                           │   THOUGHT: "High refund    │
  │                           │   rate, check evidence"    │
  │                           │   ACTION: request_evidence │
  │                           │                           │
  │←── "Upload damage photo   │                           │
  │     with barcode" ────────│                           │
  │                           │                           │
  │── [uploads photo] ───────→│── Vision Analysis ───────→│
  │                           │←── "Stock photo detected!" │
  │                           │                           │
  │                           │   THOUGHT: "Evidence is    │
  │                           │   suspicious, escalate"    │
  │                           │   ACTION: escalate         │
  │                           │                           │
  │←── "Escalated for review" │                           │
```

**Result:** Agent autonomously investigated, caught the stock photo, escalated.

### Case 3: Rohit (Serial Abuser → ESCALATE + Fraud Ring)

```
Rohit                    RefundPilot Agent              Pine Labs
  │                           │                           │
  │── "Shoes damaged" ───────→│                           │
  │                           │── Collect 10 signals      │
  │                           │   S1: 67% refund rate 🚩🚩│
  │                           │   S2: Signed delivery! 🚩 │
  │                           │   S4: 9th "damaged" 🚩🚩  │
  │                           │   S8: 8 refunds/90d 🚩🚩  │
  │                           │   S10: 2 cross-merchant 🚩│
  │                           │                           │
  │                           │── Score: 81/100           │
  │                           │── CIRCUIT BREAKER FIRES    │
  │                           │── Decision: ESCALATE       │
  │                           │                           │
  │                           │── Fraud Ring Check:        │
  │                           │   "2 other accounts at     │
  │                           │    same address! (Deepak,  │
  │                           │    Sunita)"                │
  │                           │                           │
  │                           │── Create Order (tracking)→│
  │                           │── Build Case Brief:        │
  │                           │   Top 5 signals            │
  │                           │   Counterfactual           │
  │                           │   Recommended actions      │
  │                           │                           │
  │←── "Escalated. Fraud ring │                           │
  │     detected." ───────────│                           │
```

**Result:** Caught in 1.5 seconds. Fraud ring exposed. Case brief ready for human reviewer.

---

## The Core: 10-Signal Weighted Risk Scoring

### Why Weighted Rules, Not Pure LLM?

We asked ourselves: *"Should an LLM decide whether to give ₹50,000 back to a customer?"*

**No.** Here's why:

- **LLMs hallucinate.** A refund decision worth lakhs can't be based on vibes.
- **LLMs aren't deterministic.** Same input, different output = compliance nightmare.
- **LLMs are slow + expensive.** 3-8 seconds per call at scale = unsustainable.

Instead, we use a **hybrid approach inspired by industry leaders** (Appriss Retail / The Retail Equation, Signifyd, Riskified):

```
RiskScore = Σ (weight_i × signal_score_i)    where Σ weights = 1.0
```

The score is **pure math**  same input always gives the same output. The LLM only generates the **explanation text**, never the score.

### The 10 Signals

| # | Signal | Weight | What It Catches |
|---|--------|--------|-----------------|
| S1 | Customer Refund Rate | 0.18 | Chronic returners |
| S2 | Delivery Contradiction | 0.14 | "Damaged" but signed for delivery |
| S3 | Amount Risk | 0.07 | High-value claim scrutiny |
| S4 | Claim Pattern Repetition | 0.11 | Same excuse every time |
| S5 | Product Category Deviation | 0.07 | Returns above category norm |
| S6 | Sentiment Analysis | 0.06 | Formulaic messages = suspicious |
| S7 | RFM: Recency | 0.08 | Recent refund = suspicious |
| S8 | RFM: Frequency | 0.08 | Burst of refunds |
| S9 | RFM: Monetary Ratio | 0.08 | Refunded > purchased |
| S10 | Cross-Merchant Fraud | 0.13 | Claims at OTHER Pine Labs merchants |

### "But aren't the weights biased?"

**Yes — intentionally.** The current weights are based on:

1. **Industry research** — Appriss Retail, which processes 370M+ returns/year for retailers like Home Depot, Best Buy, and Victoria's Secret, uses weighted behavioral scoring as their core methodology.
2. **RFM analysis** — Recency-Frequency-Monetary is a foundational retail analytics technique (Bult & Wansbeek 1995, Fader et al. 2005).
3. **Domain expertise** — S1 (customer refund rate) gets the highest weight because longitudinal behavior is the single most predictive signal for refund abuse.

**But we acknowledge these are starting weights.** In production, they evolve:

- **Per-merchant calibration**: A fashion merchant weighs S2 (delivery contradiction) higher for wardrobing detection. An electronics merchant weighs S3 (amount risk) higher.
- **Merchant presets**: We ship 3 presets (Default, Fashion, Electronics) with pre-tuned weights.
- **Future: Adaptive Weight Tuning** (see roadmap) — ML models auto-calibrate weights per merchant using their historical refund outcomes.

The math is transparent. Every signal's contribution is visible on screen. The merchant sees exactly WHY the agent decided what it did.

### References

1. **Appriss Retail / The Retail Equation** — Processes 370M+ returns/year for Home Depot, Best Buy, Victoria's Secret using weighted behavioral return scoring. [apprissretail.com](https://apprissretail.com/)
2. **Signifyd** — Commerce protection platform using merchant network intelligence for fraud scoring across 10,000+ merchants. [$1.7B valuation](https://www.signifyd.com/). Same cross-merchant concept as our S10.
3. **Riskified** — ML-based e-commerce fraud prevention, publicly traded (RSKD). Uses behavioral signals + network effects. [riskified.com](https://www.riskified.com/)
4. **RFM Analysis** — Bult, J.R. & Wansbeek, T. (1995). "Optimal Selection for Direct Mail." Marketing Science, 14(4). [doi:10.1287/mksc.14.4.378](https://doi.org/10.1287/mksc.14.4.378)
5. **RFM in Customer Segmentation** — Fader, P.S., Hardie, B.G.S., & Lee, K.L. (2005). "Counting Your Customers the Easy Way." Marketing Science, 24(2). [doi:10.1287/mksc.1040.0098](https://doi.org/10.1287/mksc.1040.0098)
6. **Pine Labs Plural API** — Payment gateway APIs for orders, refunds, payment links, settlements. [developer.pinelabs.com](https://developer.pluralbypinetree.com/)
7. **ZhipuAI GLM-5** — Large language model for reasoning and explanation generation. [open.bigmodel.cn](https://open.bigmodel.cn/)
8. **Groq Llama 4 Scout** — Fast inference for vision analysis (stock photo detection, damage assessment). [groq.com](https://groq.com/)

### 3-Tier Decision Logic

```
Score 0-30:   MATH DECIDES → Auto-approve. No LLM needed. Fast, cheap, deterministic.
Score 31-70:  AI DECIDES   → ReAct tool-use loop. Agent picks: evidence? credit? escalate?
Score 71-100: MATH DECIDES → Auto-escalate. No debate. Human gets pre-built case brief.
```

Clear cases don't need expensive AI reasoning. The LLM only runs for genuinely ambiguous cases — the gray zone where human-like judgment adds real value.

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend | Python + FastAPI | Async, WebSocket, clean agent orchestration |
| Scoring | Weighted Rule Engine + RFM | Deterministic, auditable, industry-standard |
| Text AI | ZhipuAI GLM-5 | Explanations, ReAct reasoning |
| Vision AI | Groq Llama-4 Scout | Stock photo detection, damage analysis |
| Payments | Pine Labs Plural UAT API | Real orders, payment links, refund API |
| Database | SQLite (WAL mode) | Zero-setup, concurrent access |
| Frontend | React 18 + Vite + Tailwind | Dark UI, responsive, real-time |

---

## Pine Labs Integration

RefundPilot uses Pine Labs as **load-bearing infrastructure in both directions**:

### Data IN (feeds scoring)
- **S10 Cross-Merchant**: Pine Labs network reveals claims at other merchants
- **S9 Monetary Ratio**: Transaction history provides purchase totals
- **Fraud Ring**: Shared payment methods across Pine Labs merchants

### Data OUT (executes actions)
- **Refund API**: `POST /refunds/{order_id}` — processes refund to original payment method
- **Payment Links**: `POST /paymentlink` — real clickable links for store credit
- **Orders**: `POST /orders` — creates tracking orders for every decision
- **Settlements**: `GET /settlements/v1/list` — reconciliation tracking

**This system literally cannot work without Pine Labs.** It's not a payment gateway bolted on — it's the data backbone.

---

## Features

| # | Feature | Description |
|---|---------|-------------|
| F1 | 10-Signal Scoring | Deterministic weighted formula, merchant-configurable |
| F2 | Transparent Reasoning | Every signal's contribution visible + LLM explanation |
| F3 | Dynamic Risk Meter | Animated 0-100 score with signal-by-signal buildup |
| F4 | RFM Abuse Profiling | Recency-Frequency-Monetary behavioral analysis |
| F5 | Evidence Collection | Autonomous photo request with barcode verification |
| F6 | Store Credit Negotiation | Smart credit offers with bonus (Pine Labs Payment Link) |
| F8 | Vision Analysis | EXIF extraction + Groq vision (stock photo detection) |
| F19 | Product Defect Dampener | Halves S1 weight when SKU has abnormal refund rate |
| F20 | Fraud Ring Detection | Shared shipping address SQL graph analysis |
| F21 | Circuit Breakers | Hard fraud signals override LLM decisions |
| F22 | Concurrent Locking | Per-customer asyncio.Lock prevents race conditions |
| F23 | Seasonal Baselines | Diwali/BBD/New Year threshold adjustments |
| F24 | Smart Reconciliation | Settlement tracking (settled/pending/failed) |
| F25 | Conversational Commerce | Free-text refund via chat (Hindi/English) |
| F26 | Fraud Similarity | Cosine distance to known fraudster profile |
| F27 | Graph Analytics | Customer↔Address network visualization |

---

## API Endpoints (22 total)

```
POST   /api/refund                    — Submit refund (full agent pipeline)
GET    /api/refund/{id}               — Get refund details
GET    /api/refund                    — List refunds
POST   /api/demo/run/{scenario}       — Run demo scenario (priya/vikram/rohit)
GET    /api/demo/scenarios            — List demo scenarios
POST   /api/query                     — Natural language merchant query
POST   /api/chat/refund               — Conversational refund (F25)
GET    /api/dashboard/stats           — KPI aggregates
GET    /api/dashboard/refunds         — Recent refunds with customer info
GET    /api/dashboard/customers       — All customer profiles
GET    /api/dashboard/customers/{id}  — Customer detail + history
GET    /api/dashboard/alerts          — Fraud spike alerts
GET    /api/dashboard/audit-log       — Audit trail
GET    /api/dashboard/reconciliation  — Settlement status (F24)
GET    /api/dashboard/fraud-graph     — Network graph data (F27)
GET    /api/dashboard/fraud-similarity/{id} — Fraud similarity % (F26)
GET    /api/dashboard/cohorts/products — Product refund cohorts
GET    /api/dashboard/cohorts/cities   — City refund cohorts
GET    /api/dashboard/cohorts/reasons  — Reason refund cohorts
POST   /api/webhook/evidence/{id}     — Upload evidence (EXIF + Vision)
POST   /api/webhook/fraud-ring/{id}   — Check fraud ring (F20)
GET    /health                        — Health check
```

---

## Running Locally

### Prerequisites
- Python 3.11+
- Node.js 18+
- API keys in `backend/.env`:
  ```
  ZHIPU_API_KEY=your_key
  GROQ_API_KEY=your_key
  PINELABS_MERCHANT_ID=your_mid
  PINELABS_CLIENT_ID=your_client_id
  PINELABS_CLIENT_SECRET=your_secret
  LLM_ENABLED=false
  ```

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --port 8001
```

### Frontend
```bash
cd frontend
npm install
node patch-rollup.cjs   # Required for ARM64 Windows
npx vite --port 5173
```

Open **http://localhost:5173** → Go to **Live Demo** → Click **Run All 3 Scenarios**.

---

## Future Roadmap

1. **Isolation Forest Anomaly Detection** — ML-based unsupervised anomaly detector trained on merchant's historical data. Catches novel fraud patterns no predefined rule can express.

2. **Adaptive Weight Tuning** — Auto-calibrate signal weights per merchant using their refund outcomes (approved vs. confirmed-fraud). The 9-signal weights evolve from generic to merchant-specific.

3. **Cross-Merchant Fraud Network** — Federated learning across Pine Labs merchants. Abuser flagged on Store A → warning on Store B. Without sharing PII.

4. **Predictive Refund Prevention** — Predict which orders will result in refunds before they ship. Intervene with better packaging or proactive communication.

5. **Auto-Chargeback Defense** — When a customer files a chargeback, agent compiles delivery proof + communication history and submits defense package autonomously.

6. **Voice Agent** — Merchant calls and asks "How many refunds this week?" — voice agent answers with live data.

7. **Shopify/WooCommerce Plugin** — One-click install widget. Connect Pine Labs → RefundPilot is live. Zero-code for merchants.

---

## Team

Built for the **Pine Labs AI Hackathon (Playground)** — Agentic / Autonomous Commerce & Intelligent Payments.

---

*"Decision in 4 seconds. Not 15 days. Math decides clear cases. AI decides gray areas. Every fraud caught is a chargeback Pine Labs doesn't process."*
