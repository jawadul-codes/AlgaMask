# Release Step 1 — browser workflow audit

Date: 2026-10-25. Status: completed for the scenarios listed below.

## Environment

- Current compiled Flutter app in the in-app browser, real offline development RAG.
- API 127.0.0.1:8125, web 127.0.0.1:3002; user's 8124/3001 services untouched.
- Dataset 0.1.0-rc.4, index 0.1.0-dev.3.
- Isolated database: /tmp/algamask-browser-audit.A7gUpB/runs.sqlite3.
- Build/log folder: var/dev/session-bhm1jmw5.
- Repaired build/log folder: var/dev/session-k1cjlzo4.
- Browser controls were used for selections and submissions. Backend tests are
  listed separately from browser observations.

## Observed scenarios

| Scenario | Browser observation |
| --- | --- |
| Default spirulina/5%/45 g/cocoa-spice | Ready, run succeeds; three candidates plus B0/A0; protein about 5.7 g and energy 157 kcal on selected candidate. |
| History | Default run listed; reopening returns its report. |
| Print report | Opens separate HTML report for the same ID, with exact masses, source records and unknown sugar. |
| Chlorella/3%/45 g/vanilla/12 g protein/426 kcal/0 g sugar | Run disabled; 5.0187 g protein maximum and 5.01 g suggested boundary; energy/sugar unknown. |
| Corrected chlorella targets | Protein 5.01 g and optional energy/sugar blank restore eligibility. |
| Invalid protein NaN | Field validation plus disabled Run. |
| Spirulina/5%/50 g/vanilla/5 g protein/175 kcal/tree nut preference | Ready and run succeeds; saved request confirms all inputs and ingredient_preference. |
| Same selection, verified-free-from | Run disabled; supplier coverage explanation; no spurious missing-nutrition messages. |
| Oats preference | Run disabled; no oat-free recipe; nutrition explicitly not evaluated. Removing oats restores eligibility. |
| Copy run JSON | Success feedback and parseable clipboard JSON confirmed for the preference run. Initial immediate clipboard read raced completion; not counted as an app failure. |
| Fixed proof with retained protein 5 g | Correctly blocks: A1 protein 4.8887 g; suggested 4.88 g boundary. |
| Fixed proof with protein 4.88 g | Succeeds: A1 plus B0/A0, input mass 45 g and fixed species/flavour. |
| History after all blocked scenarios | Exactly three submitted runs; no blocked/invalid preview created a job. |
| History backend outage | Refresh displays actionable connection failure; existing rows remain visible. |
| Input backend outage | Target edit disables Run, displays connection error and Check again. |
| Input recovery | After restarting the same backend/database, Check again restores eligibility with the existing inputs. |
| Updated history navigation | With the rebuilt app, New experiment from history directly opens the form, including when a report was previously open. |
| Persistence after restart | Three existing audit runs remain; a fourth run from the rebuilt UI also succeeds. |
| History filter | Chlorella shows No experiments match these filters; All algae restores four rows. |

## Audit run IDs

- Default: 0af9f425-31d3-4582-9667-ce4fe4ceee99.
- Screenshot preference: 9da84d38-293a-4d72-8d60-f0aaeea5be19.
- Fixed proof: cd684637-86f2-4e86-9d22-67042e1eead7.
- Rebuilt UI default run: d6ec2631-862d-4ea9-9b28-dfeff5483d58.

## Findings and repairs

1. Reproduced: New experiment from history popped back to the previous report.
   History now returns an explicit new-experiment signal; the parent clears its
   report and rechecks the inputs. Ordinary Back still restores the previous view.
2. Source inspection: Clipboard writes had no exception handler. Added recovery
   feedback for denied/unsupported clipboard writes and a regression test. This
   failure was simulated in a widget test; successful browser copy was observed.
3. Reproduced during the outage: returning from a report to its input form reused
   the previous eligibility result until an input changed. All New experiment
   actions now request a fresh check immediately.
4. Reproduced during restart: explicit port 8125 temporarily could not be rebound
   despite no listener. The launcher now sets SO_REUSEADDR before binding, allowing
   restart after TIME_WAIT while still rejecting active listeners. It does not use
   SO_REUSEPORT. A connection-close/rebind regression and existing collision tests pass.

## Verification and limits

- Flutter analysis clean; 29 Flutter tests passed (including new history-navigation
  and denied-clipboard tests). Repaired web build succeeded and was browser-retested.
- 207 backend tests passed; 10 opt-in ML tests skipped for this client/launcher
  increment. No RAG retrieval or scientific dataset changes were made.
- Browser screenshots and DOM confirmed layout at 689 x 849. A requested 390 x 844
  viewport override did not take effect in the in-app browser (actual width was
  checked), so this is not claimed as a phone-browser pass. Existing automated
  390 px form/report layout tests passed. The viewport override was reset.
- Chrome/Safari/mobile hardware, multi-user deployment, large history pagination,
  mid-generation process crashes and physical printing are outside this audit.
- No forced generation failure or saved failed-job retry was created in the browser;
  existing automated recovery tests cover those contracts. These remain release
  Step 5 fault/recovery checks if required for the chosen deployment.
- Evidence: /tmp/algamask-browser-audit.A7gUpB/offline-warning.png and
  /tmp/algamask-browser-audit.A7gUpB/verified-report.png. Temporary files may be
  removed by macOS; this Markdown records their substantive findings.
- Owned audit services were stopped; temporary database/logs retained. User's
  8124/3001 services were not stopped. No commit or push made.

## Follow-up for Steps 2–4

- Candidate ingredients are shown as internal IDs; amounts rounded to one decimal
  in the Flutter cards can appear not to sum exactly. HTML/JSON preserve precision.
- Controls can exceed candidate nutrition limits. The comparison basis explains
  this, but it should be more visible near the controls in Step 2.
- Background evidence remains broader than species/flavour requests; Step 2 must
  make applicability clear. Nutrition and recipe expansion belong to Steps 3/4.
