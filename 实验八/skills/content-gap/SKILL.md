---
name: content-gap-analyzer
description: Run professional content gap analysis using DataForSEO MCP. Multi-language — works in any market DataForSEO supports (200+), with Polish, English, and mixed-language analyses as first-class use cases. Two modes auto-detected: Domain Mode compares your domain vs competitors (5-dimensional gap analysis, funnel mapping, info-gain angles); Topic Mode builds a content plan from top pages ranking for a seed keyword (filters article-worthy topics into 3 tiers, clusters into roadmap). Optional GSC cross-check splits findings into new/refresh/already-ranking. Produces prioritized roadmap with real volumes, KD, funnel mapping, info-gain angles, and 12-week calendar. Use this skill whenever the user mentions content gap, keyword gap, competitor content analysis, topic landscape, content roadmap, what to write about, jakie tematy pokryć, luki contentowe, plan contentu — even if they don't explicitly say "content gap analysis".
license: MIT
metadata:
  author: Marcin Żmuda
  author-url: "https://marcinzmuda.com"
  brand: "Darn"
  version: "3.3.0"
  repository: "https://github.com/MarcinZmuda/darn-content-gap-analyzer"
  requires:
    claude: ">=4.0"
    optional-mcp:
      - "DataForSEO (strongly recommended for both modes)"
      - "Google Search Console (optional, enables Phase D2.5/T2.5 cross-check)"
  geo-relevance: "global"
  languages:
    - en
    - pl
    - any-dataforseo-supported
  tags:
    - seo
    - content-gap
    - topic-analysis
    - keyword-research
    - competitor-analysis
    - dataforseo
    - multi-language
    - geo
    - ai-overview
    - topic-landscape
    - content-planning
  triggers:
    # NOTE: this list documents intended trigger phrases for contributors and evals.
    # Actual skill matching is driven ONLY by the `description` field above —
    # editing this list has no runtime effect; edit `description` instead.
    # Brand name (language-agnostic)
    - "Darn"
    - "run Darn"
    - "use Darn"
    - "odpal Darn"
    - "uruchom Darn"
    # Domain Mode — English (primary)
    - "content gap analysis"
    - "find content gaps"
    - "what topics should I cover"
    - "what am I missing"
    - "competitor content analysis"
    - "keyword gap"
    - "what are competitors ranking for"
    - "content opportunities"
    - "topic gaps"
    - "content roadmap"
    - "topical authority audit"
    - "AI visibility gap"
    - "content strategy gaps"
    - "untapped topics"
    # Domain Mode — Polish (supported)
    - "analiza luk treściowych"
    - "analiza luk contentowych"
    - "content gap"
    - "jakie tematy pokryć"
    - "co napisać na bloga"
    - "co mam napisać"
    - "analiza konkurencji SEO"
    - "luki w treści"
    - "znajdź luki contentowe"
    - "audyt topical authority"
    - "strategia treści"
    - "mapa contentowa"
    # Topic Mode — English (primary)
    - "content plan for keyword"
    - "what to write about"
    - "topic landscape"
    - "build content plan from keyword"
    - "articles to write about"
    - "topic cluster for"
    - "analyze topic"
    # Topic Mode — Polish (supported)
    - "plan contentu dla hasła"
    - "plan artykułów"
    - "tematy do napisania o"
    - "co pisać o temacie"
    - "mapa tematu"
    - "analiza tematu"
    - "rozkład tematu"
    - "pokaż tematy dla hasła"
---

# Darn — Content Gap Analyzer (DataForSEO edition)

**Darn** is a production-grade content gap analysis skill using the DataForSEO MCP server. It replaces weeks of manual SERP inspection with targeted API calls that return exact search volumes, keyword difficulty, SERP features including AI Overview detection, and content gap detection.

> **Author:** [Marcin Żmuda](https://marcinzmuda.com) · **Repo:** https://github.com/MarcinZmuda/darn-content-gap-analyzer · **License:** MIT

## Two operating modes

Darn has two entry points — Claude picks automatically based on what the user provides:

### Domain Mode — "my site vs competitors"
User provides their domain + competitor domains. Darn runs Domain Intersection to find keywords competitors rank for but user doesn't. Full 5-dimensional gap analysis (keyword gap, topic cluster gap, format gap, information gain gap, AI visibility gap) with funnel stage mapping and 12-week calendar. Typical cost: **$1-5 per analysis** (more for enterprise-scale analyses with 10+ competitors and 10k+ keywords).

Use when: established site, clear competitors, want to find what to publish to catch up / overtake.

### Topic Mode — "build content plan from a keyword"
User provides a single seed keyword or topic (e.g., "rozwód", "email marketing automation", "plant-based protein"). Darn pulls the top 15 pages ranking for that keyword, extracts their full ranked-keywords footprint, filters article-worthy topics, clusters them, and produces a content plan. Typical cost: **$0.40-1.50 per analysis** (~$0.35-0.80 for a standard single keyword).

Use when: pre-launch site, new topic cluster, freelancer/agency scoping a niche, affiliate/content-site research, deciding whether a topic is worth entering.

Both modes share the same deliverable structure (clusters, priority scoring, funnel mapping, info-gain angles, content calendar) — just a different starting point.

## Prerequisites

1. **DataForSEO account** with API credentials
2. **DataForSEO MCP server connected** to Claude (see `references/setup.md`)
3. **API credits** — budget depends on mode:
   - Domain Mode: $1-5 per standard analysis, up to $15-30 for enterprise-scale (10+ competitors, 10k+ keywords)
   - Topic Mode: $0.40-1.50 per analysis
4. **Optional but recommended** (Domain Mode only): project context prepared (see `references/project-context.md` for template — pasted into chat, saved as artifact, or stored in memory). Topic Mode works without project context.

## Multi-language support

Darn works in **any market DataForSEO supports** (200+ locations, 40+ languages). English and Polish are first-class tested languages; German, Spanish, French, Japanese and others all work. Output language matches market language — Polish analysis produces Polish briefs, English analysis produces English briefs (no translation layer).

Repo ships with Polish market reference defaults (`location_code: 2616, language_code: "pl"`) because the author is Poland-based, but all market settings are overridable per analysis. See `references/market-specifics.md` for per-market aggregator filtering and defaults.

## Quick start prompts

After installation, trigger Darn with any of these. English examples first, Polish examples shown to demonstrate multi-language support.

### Domain Mode triggers

English (primary):
```
Run content gap analysis for [your-domain.com] vs [competitor1.com], [competitor2.com] for US market
Use Darn on [your-domain.com]
Find content gaps: my site vs top 3 competitors in SaaS invoicing niche, UK market
```

Polish (same skill, multi-language support):
```
Znajdź luki contentowe dla [domena.pl] względem [konkurent1.pl], [konkurent2.pl]
Odpal Darn na [domena.pl]
```

### Topic Mode triggers

English (primary):
```
Run Darn Topic Mode for "email marketing automation", US market
Analyze topic: "SaaS customer onboarding"
Build content plan for "plant-based protein" in Germany
```

Polish:
```
Zrób plan contentu dla hasła "rozwód"
Pokaż mi tematy do napisania o "kredyt hipoteczny"
```

### Mode auto-detection

Claude infers the mode from the input:
- **One or more domains** (containing `.pl`, `.com`, `.io` etc.) → Domain Mode
- **A short phrase without domain names** → Topic Mode
- **Mixed** (e.g., "analyze `rozwód` for my site faktura.app") → ask user which mode

If ambiguous, ask in one message: "Did you want Domain Mode (compare domains) or Topic Mode (plan content for this keyword)?"

## When this skill fits

**Domain Mode fits when:** target domain wants organic/AI-search growth, 2–5 competitor domains identified (or willing to discover), DataForSEO API access available. Works for blogs, SaaS, e-commerce, local services, agencies, publishers — any market DataForSEO supports (200+).

**Topic Mode fits when:** starting a new site/topic from scratch, scoping whether a niche is worth entering, building content strategy around a specific keyword, freelancer/agency doing topic research for a client, affiliate site planning.

**Doesn't fit when:** deep backlink gap analysis is the primary need (use Ahrefs/Semrush), or technical SEO audit is what the user actually needs.

## Workflow phases

Claude first detects which mode applies (Domain or Topic), then runs the mode-specific phase sequence. Both modes converge on a shared Phase 6-8 (cluster, score, deliver).

### Phase 0 — Mode detection (always first)

Before any API calls, determine which mode the user wants:

**Signals for Domain Mode:**
- Input contains one or more domain names (`.pl`, `.com`, `.io`, `.co.uk`, etc.)
- User explicitly says "my site vs", "competitor", "gap analysis", "compare domains"
- Project context exists with target domain filled in

**Signals for Topic Mode:**
- Input is a short phrase, keyword, or topic description (e.g., "rozwód", "email marketing automation")
- User says "plan contentu dla", "what to write about", "topic landscape", "tematy do napisania"
- No domain in the input
- User explicitly says "Topic Mode" or "topic analysis"

**Ambiguous cases:**
- "Analyze rozwód for faktura.app" → could be either. Ask user.
- "Content plan for SaaS invoicing" → Topic Mode (no specific competitor, topic-centric framing).
- "faktura.app" alone → Domain Mode but incomplete (ask for competitors).

**Confirm mode in one turn:**
> "Detected **Topic Mode** — I'll analyze the landscape around `rozwód`, pull top 15 ranking pages and their full keyword footprint, then build a content plan. Estimated cost: ~$0.40. Proceed? (yes/no)"

Or:
> "Detected **Domain Mode** — I'll compare `faktura.app` vs `ifirma.pl, wfirma.pl, infakt.pl`. Estimated cost: ~$1.50. Proceed? (yes/no)"

---

# DOMAIN MODE (compare my site vs competitors)

The original Darn workflow. Use when user has a domain and competitors.

**Phases D0 through D5** are documented in full in `references/domain-mode-workflow.md`. Read that file when entering Domain Mode.

Quick phase overview:

- **Phase D0** — Load project context (30 sec if ready, 2-4 min first-time)
- **Phase D1** — Competitor discovery and validation (5–10 min, ~$0.15)
- **Phase D2** — Keyword gap detection via Domain Intersection (10–15 min, ~$0.10-0.20)
- **Phase D2.5** — GSC cross-check, optional (30 sec, free) — see `references/gsc-integration.md`
- **Phase D3** — Cluster expansion (15–30 min, ~$0.75)
- **Phase D4** — SERP deep inspection with AI Overview detection (20–30 min, ~$0.20)
- **Phase D5** — Bulk Keyword Difficulty (5 min, ~$0.01)

**→ Domain Mode converges with Topic Mode at shared Phase 6 below.**

---

# TOPIC MODE (plan content for a keyword)

Use when user gives a single seed keyword/topic and wants a content plan built from the pages already ranking for that topic.

**Phases T0 through T5** are documented in full in `references/topic-mode-workflow.md`. Read that file when entering Topic Mode. The article-worthiness filter logic (Tier 1/2/3) is detailed in `references/topic-mode-filtering.md`.

Quick phase overview:

- **Phase T0** — Scope confirmation (30 sec, no API)
- **Phase T1** — SERP snapshot: top 15 URLs (1 min, ~$0.002)
- **Phase T2** — Extract ranked keywords per URL (5-8 min, ~$0.30)
- **Phase T2.5** — GSC exclusion, optional (30 sec, free) — see `references/gsc-integration.md`
- **Phase T3** — Article-worthiness filter with 3-tier classification (2 min, no API) — see `references/topic-mode-filtering.md`
- **Phase T4** — Bulk Keyword Difficulty (2 min, ~$0.01)
- **Phase T5** — SERP feature scan for top candidates (3-5 min, ~$0.05)

**→ Topic Mode converges with Domain Mode at shared Phase 6 below.**

---

# SHARED PHASES (both modes converge here)

### Phase 6 — Cluster, score, prioritize (30–45 min, no API cost)

1. **Cluster** keywords semantically (SERP-overlap or LLM-assisted; see `references/prioritization.md`)
2. **Score each cluster on 4 axes** — scoring adjusts per mode:

   | Axis | Domain Mode scoring | Topic Mode scoring |
   |---|---|---|
   | **Demand signal** (1-5) | Total cluster search volume | Total cluster search volume |
   | **Business value** (1-5) | Based on project-context goal (leads/brand/AI citations) | Based on user-stated angle or inferred from intent mix; if no context, weight commercial-intent clusters higher for leads-oriented topics, informational higher for brand-building topics |
   | **Winnability** (1-5) | Based on target's current position + avg KD + top 10 authority | **No user domain to compare against** — use: avg cluster KD + SERP authority mix (low if top 10 all DR 80+; high if mixed DR with smaller sites ranking) + presence of information-gain opportunity |
   | **Funnel coverage need** (1-5) | Gap vs competitors' funnel distribution (from `funnel-analysis.md`) | Gap in topic landscape itself — which funnel stages are underserved in the top 15 pages (e.g., 12 Awareness articles, 0 Decision pages → Decision = 5) |

3. **Compute priority** = Demand × Value × Winnability × (1 + FunnelNeed/10)
4. **Bonuses (cap +30)** — full table in `references/prioritization.md` (single source of truth). Summary:
   - (Domain Mode) Cluster hits 3+ gap dimensions = +10
   - (Topic Mode) Co-occurrence: keyword in 3–5 URL footprints = +5; in 6+ = +10 (validated demand)
   - Strong info-gain angle available = +10 (both modes)
   - AIO visible + distinctive angle identified = +10 (both modes)
   - Cluster includes transactional queries = +10 (both modes)
   - (Topic Mode only) Tier 1 cluster = +10; Tier 2 = +5; Tier 3 = +0

5. **Sort descending** — top 10–20 clusters = roadmap

**Topic Mode specific:** also output a **page-level landscape table** showing which top-15 URL owns which cluster (position, volume, format). This surfaces "who to study" per cluster, not just what to write.

### Phase 7 — Information-gain angle for top clusters (30–60 min, no API cost)

For each top-10 cluster, identify what target can say that top results cannot. Six angles:
- First-party data
- Expert interview
- Contrarian stance
- Framework / mental model
- Specific niche
- Temporal gain (freshness)

Use prompts in `references/information-gain.md`. **Required field — clusters without identified angle get demoted.**

### Phase 8 — Deliver report (30 min, no API cost)

Report structure adjusts per mode. Both use `references/report-template.md` as the base.

**Domain Mode report:**
1. Executive summary
2. Scorecard (target vs. competitors)
3. Gap matrix (clusters × 5 dimensions)
4. Funnel Stage Gap section (Awareness/Consideration/Decision/Retention — target vs competitors)
5. GEO/AI Visibility section (topics × AIO citations × gap)
6. Top 10–20 content roadmap with article briefs
7. Content Calendar (week-by-week for next 12 weeks)
8. Easy wins (target's existing pages 11–30)
9. Strategic cluster plans (pillar + supporting)
10. Methodology + cost breakdown

**Topic Mode report:**
1. Executive summary — topic overview, total addressable search volume, competitive density
2. **Page-level landscape** (top 15 URLs with position, DR/authority estimate, format, owned clusters)
3. Topic cluster map — clusters with tier (T1/T2/T3), volume, avg KD, funnel stage
4. Funnel Stage distribution — which stages are oversaturated vs underserved in this topic
5. GEO/AI Visibility — AIO presence per cluster, currently cited sources
6. **Top 10-20 article roadmap**, split by tier:
   - Tier 1 (high-confidence article topics) — write first
   - Tier 2 (commercial-informational hybrid) — write with CTA/monetization angle
   - Tier 3 (manual review) — validated separately
7. Content Calendar (week-by-week, 12 weeks)
8. Pillar + supporting architecture recommendation (if enough volume in cluster)
9. Methodology + cost breakdown

Save full roadmap as `.xlsx` to the client's output location: `/mnt/user-data/outputs/` on claude.ai; the current working directory (or a user-specified path) in Claude Code / Desktop.

## Validation Checkpoints

### Input validation (Domain Mode) — confirm before proceeding past Phase D1

- [ ] Target domain confirmed and reachable (not staging URL or typo)
- [ ] Minimum 2 competitors validated as actual SERP competitors (not just business competitors)
- [ ] Market locked (location_code + language_code set explicitly)
- [ ] Business goal stated in concrete terms (leads / brand / AI citations / revenue X%)
- [ ] Budget cap confirmed and shown to user
- [ ] If project context was provided (pasted/artifact/memory), has it been acknowledged and used?

### Input validation (Topic Mode) — confirm before proceeding past Phase T1

- [ ] Seed keyword is not too generic (e.g. "marketing" → will return noise) nor too specific (e.g. "how to hire a family law attorney in downtown Krakow on Tuesdays" → too narrow)
- [ ] Market locked (location_code + language_code)
- [ ] Budget cap confirmed
- [ ] SERP returned at least 5 organic results for the seed keyword
- [ ] Top 15 URLs aren't all from the same domain (if yes, flag monopoly and ask user if they want to proceed)
- [ ] User understands this mode doesn't need their domain — and they get a landscape view, not a vs-competitor view

### Output validation — every cluster in roadmap must have (both modes):

- [ ] Cited DataForSEO data (search volume, KD, position) — NOT estimated
- [ ] At least 5 member keywords or justification for being a 1-keyword cluster
- [ ] Identified information-gain angle (one of six)
- [ ] Suggested format (long guide / comparison / tool / video / etc.) with reason
- [ ] Mapped to funnel stage
- [ ] Mapped to gap dimensions (Domain Mode) OR tier + co-occurrence (Topic Mode)
- [ ] Effort tier assigned (easy win / new content / strategic cluster)
- [ ] (Domain Mode) At least 2 internal-linking sources from existing target pages identified
- [ ] (Topic Mode) Which of the top 15 URLs currently owns this cluster (for "study this page" reference)

If a cluster fails any of these checks, demote or remove from roadmap.

## Worked examples

Two end-to-end walkthroughs — one per mode — are in `references/worked-examples.md`. They show mode auto-detection, cost reporting at each phase, concrete outputs with real numbers, and `.xlsx` delivery. Read before starting your own analysis.

## Market-specific aggregator filtering

Different markets have different aggregator/news domains that show up as noise in competitor discovery. For example: Polish SERPs have Allegro/Ceneo/WP, US has Amazon/CNN/Reddit, German has Otto/Spiegel. For B2B/SaaS targets, exclude these. For e-commerce targets, include them.

Full per-market reference (PL, US, UK, DE, ES, FR) + DataForSEO location codes table in `references/market-specifics.md`.

## Cost control

### Domain Mode budgets

| Project size | Competitors | Keywords analyzed | Typical total |
|---|---|---|---|
| Small blog | 3 | ~500 | $0.80–1.50 |
| Mid SaaS | 4 | ~2 000 | $1.50–3.00 |
| Large publisher | 5 | ~10 000 | $4–10 |
| Enterprise e-commerce | 5+ | 30 000+ | $15–30+ |

### Topic Mode budgets

| Scope | Top URLs pulled | Keywords analyzed | Typical total |
|---|---|---|---|
| Narrow keyword (e.g. "rozwód kościelny") | 10 | ~400 | $0.25–0.40 |
| Standard keyword (e.g. "rozwód") | 15 | ~1,200 | $0.35–0.80 |
| Broad keyword (e.g. "email marketing") | 15-20 | ~2,500 | $0.60–1.50 |
| Very broad keyword (e.g. "marketing") | 20 | ~4,000+ | $1.50–3.00 (warn user, usually too broad to be useful) |

Topic Mode is much cheaper than Domain Mode because it skips multi-competitor Domain Intersection — it uses a single SERP + `ranked_keywords` per URL + bulk KD. A user can run 10+ Topic Mode analyses per day on trivial budget.

Always confirm cost estimate with user before first paid call. Show running total at each phase.

## Honesty rules

- **Use real DataForSEO numbers** — don't round, massage, or estimate. Show exact values returned by API.
- **Mark low-confidence findings explicitly.** Cluster with <10 keywords, or keywords with `search_volume: 0`, or domains with `total_count: 0` — flag as "insufficient data" rather than forcing an opinion.
- **Volumes are monthly averages** — flag seasonal categories (Christmas gifts, tax season, back-to-school) where a 12-month average misrepresents peak demand.
- **KD is solid but not gospel.** DataForSEO's KD correlates with ranking difficulty but individual pages can break through with strong info-gain. Note KD as directional, not deterministic.
- **Flag when competitor selection is shaky.** If competitors share <100 keywords with target, say so explicitly — the whole analysis is softer.
- **State project-context limitations.** If user skipped ICP or didn't provide competitors — note which parts of the analysis suffered and which recommendations are generic vs. tailored.
- **Flag business-model mismatches.** If two "competitors" are SMB ($50/month) and Enterprise ($50k/year), gap keywords from the enterprise competitor aren't realistic targets — note this.
- **Labs data is not live.** Domain Intersection, Ranked Keywords, and competitor data come from DataForSEO's periodically refreshed database, not live SERPs — positions can lag reality by weeks. This is the main source of false-positive "gaps" (you rank, the database doesn't know yet). The GSC cross-check (Phase D2.5/T2.5) or a live SERP spot-check catches these.
- **Don't overpromise traffic.** ETV is a ceiling based on ranking + CTR curves, not a forecast. State it as "maximum theoretical traffic if we rank top 3" not "expected traffic."

## Troubleshooting — common issues

Common issues and fixes for both modes are in `references/troubleshooting.md`. Covers:

- Empty DataForSEO results in Phase D1
- MCP tools not visible to Claude
- Cost overruns and budget guardrails
- Scoring mismatches with business intuition
- AIO citations not showing
- Project context conflicts with user prompt
- Topic Mode specific: thin SERP, single-domain monopoly, filter over-drops
- GSC cross-check returning 0 matches

Read `references/troubleshooting.md` when something unexpected happens.

## Reference files

**Workflows (read when entering each mode):**

- `references/domain-mode-workflow.md` — Phase D0-D5 full workflow
- `references/topic-mode-workflow.md` — Phase T0-T5 full workflow

**Core methodology (read as needed during analysis):**

- `references/project-context.md` — TEMPLATE for project context (copy and fill per project)
- `references/market-specifics.md` — per-market aggregator filtering (PL, US, UK, DE, ES, FR) + DataForSEO location codes
- `references/dimensions.md` — five gap dimensions explained (Domain Mode)
- `references/endpoints.md` — DataForSEO endpoints reference (both modes)
- `references/competitor-validation.md` — 4-check filter for SERP competitors (Domain Mode)
- `references/topic-mode-filtering.md` — Topic Mode article-worthiness filter (Tier 1/2/3 logic)
- `references/prioritization.md` — clustering and 4-axis scoring (both modes)
- `references/information-gain.md` — six angles + LLM prompts (both modes)
- `references/funnel-analysis.md` — Awareness/Consideration/Decision/Retention mapping (both modes)
- `references/gsc-integration.md` — optional GSC cross-check (both modes)
- `references/report-template.md` — final deliverable structure (both modes)

**Setup and fallback:**

- `references/setup.md` — DataForSEO MCP connection (+ optional GSC)
- `references/api-templates.md` — fallback for users without MCP

**Examples and troubleshooting:**

- `references/worked-examples.md` — 4 walkthroughs (2× English primary + 2× Polish multi-language demo)
- `references/troubleshooting.md` — common issues and fixes for both modes

---

## Changelog

**v3.3.0 (2026-07-07)** — Audit fixes: MCP tool names aligned with official DataForSEO server, phase costs unified, scoring bonuses consolidated (single source: prioritization.md), Tier 1 criteria unified, GSC thresholds unified, target normalization rules, PAA click depth default lowered to 2, install paths fixed, plugin manifest added.

**v3.2.3 (2026-04-20)** — Initial public release

Production-grade content gap analysis skill. Two modes (Domain + Topic), multi-language support (200+ markets via DataForSEO), optional GSC cross-check. Full details in `CHANGELOG.md`.
