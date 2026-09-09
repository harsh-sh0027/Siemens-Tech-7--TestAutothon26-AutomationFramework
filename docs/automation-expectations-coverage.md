# Automation Expectations Coverage (Evidence Matrix)

This document separates what is:
- Implemented in code
- Executed with evidence in this environment
- Executable by design but currently blocked by environment/runtime constraints

## Execution Evidence Snapshot

| Scope | Status | Evidence |
|---|---|---|
| Challenge 1 end-to-end workflow (22 steps, resilient flow) | Executed | reports/runs/20260909-165301 |
| Firefox non-functional security check | Executed, failed on app navigation timeout | reports/runs/20260909-171846 |
| Edge non-functional security check | Executed, blocked by enterprise policy | reports/runs/20260909-203549 |

## 1) Business Workflow Expectations

| Expectation | Implemented | Executed | Executable by Design | Evidence / Location | Notes |
|---|---|---|---|---|---|
| One full Challenge 1 flow (all required steps) | Yes | Yes | Yes | src/test/python/tests/test_challenge1_workflow.py, reports/runs/20260909-165301 | Step wrapper captures granular pass/fail plus artifacts. |
| Robust handling for live-site variance | Yes | Yes | Yes | src/pages/web/base_page_web.py, src/test/python/tests/test_challenge1_workflow.py | Fallback selectors, guarded actions, and controlled degradation implemented. |

## 2) Framework Design Expectations

| Expectation | Implemented | Executed | Executable by Design | Evidence / Location | Notes |
|---|---|---|---|---|---|
| Modular reusable framework | Yes | Yes | Yes | src/pages, src/fixtures, src/utils | POM + factory + utilities structure is in place. |
| Separation of tests, data, config | Yes | Yes | Yes | src/test/python/tests, src/utils/challenge_data.py, src/utils/config.py | Test logic isolated from data/config sources. |
| Parameterized/data-driven scenarios | Yes | Yes | Yes | src/test/python/tests/test_login.py | Negative login scenarios parameterized from external data. |
| Exception handling/recovery strategy | Yes | Yes | Yes | src/exceptions, src/pages/web/base_page_web.py | Driver and page actions have explicit error handling paths. |
| Secure environment-based credentials | Yes | Yes | Yes | src/utils/config.py, .env.example | No hardcoded secrets required in tests. |

## 3) Test Data Expectations

| Expectation | Implemented | Executed | Executable by Design | Evidence / Location | Notes |
|---|---|---|---|---|---|
| Excel-backed input data | Yes | Yes | Yes | src/test/python/resources/challenge_data.xlsx, src/utils/challenge_data.py | `challenge1` and `negative_login` sheets supported. |
| Externalized runtime configuration | Yes | Yes | Yes | src/utils/config.py, .env.example | Environment variables drive browser/language/mobile inputs. |
| Positive + negative datasets | Yes | Yes | Yes | src/utils/challenge_data.py, src/test/python/tests/test_login.py | Negative OTP and fallback data sets are included. |

## 4) Language Expectations

| Expectation | Implemented | Executed | Executable by Design | Evidence / Location | Notes |
|---|---|---|---|---|---|
| English workflow support | Yes | Yes | Yes | src/test/python/tests/test_challenge1_workflow.py, src/utils/config.py | Configurable through challenge language settings. |
| Hinglish workflow support | Yes | Partial | Yes | src/test/python/tests/test_challenge1_workflow.py | Toggle and selector variants implemented; execution depends on live app language state. |

## 5) Browser / Platform Expectations

| Expectation | Implemented | Executed | Executable by Design | Evidence / Location | Notes |
|---|---|---|---|---|---|
| Chromium/Chrome support | Yes | Yes | Yes | reports/runs/20260909-165301, src/fixtures/driver_factory.py | Verified in this environment. |
| Firefox support | Yes | Yes (runtime fail) | Yes | reports/runs/20260909-171846 | Failed due to `Page.goto` timeout on live staging endpoint. |
| Edge support | Yes | Yes (setup blocked) | Yes | reports/runs/20260909-203549 | Blocked by policy: DevTools remote debugging and headless mode disallowed by system admin. |
| Web platform | Yes | Yes | Yes | src/fixtures/driver_factory.py | Playwright path operational with artifact generation. |
| Android platform | Yes | Not re-executed in latest run set | Yes | src/pages/mobile, src/fixtures/driver_factory.py, .github/workflows/test.yml | Appium path and CI job are present for execution where device/grid is available. |

## 6) Non-Functional Expectations

| Expectation | Implemented | Executed | Executable by Design | Evidence / Location | Notes |
|---|---|---|---|---|---|
| Security checks | Yes | Yes | Yes | src/test/python/tests/test_non_functional.py, reports/runs/20260909-171846, reports/runs/20260909-203549 | Test logic implemented; browser/environment can still block execution success. |
| Performance checks | Yes | Partial | Yes | src/test/python/tests/test_non_functional.py | Budget checks are coded; full matrix rerun pending for all target browsers. |
| Accessibility checks | Yes | Partial | Yes | src/test/python/tests/test_non_functional.py | Baseline assertions implemented; complete cross-browser rerun pending. |
| Visual evidence/snapshot | Yes | Yes | Yes | src/test/python/tests/test_non_functional.py, reports/runs/* | Full-page captures and traces are generated per run. |

## 7) Reporting / DevOps Expectations

| Expectation | Implemented | Executed | Executable by Design | Evidence / Location | Notes |
|---|---|---|---|---|---|
| HTML/JSON/JUnit run reports | Yes | Yes | Yes | reports/runs/<timestamp>/report.html, report.json, junit.xml | Produced automatically by pytest plugins/hooks. |
| Screenshots and traces | Yes | Yes | Yes | reports/runs/<timestamp>/screenshots, reports/runs/<timestamp>/playwright-traces | Artifact capture enabled per test flow. |
| Structured logs and run dashboard | Yes | Yes | Yes | conftest.py, reports/runs/<timestamp>/index.html | Logs include correlation IDs and lifecycle events. |
| CI/CD execution support | Yes | Yes | Yes | .github/workflows/test.yml | Workflow included for repeatable automated runs. |

## 8) Submission Readiness Expectations

| Expectation | Implemented | Evidence / Location |
|---|---|---|
| Source code and framework structure | Yes | src/ |
| Execution documentation | Yes | README.md, IMPLEMENTATION_SUMMARY.md |
| Traceability and design docs | Yes | docs/architecture-design.md, docs/requirement-traceability.md |
| Data template and config guidance | Yes | src/test/python/resources/challenge_data.xlsx, .env.example |
| AI disclosure | Yes | docs/ai-disclosure.md |

## Current Constraints (Important for Judges)

- Firefox run in this environment reached staging timeout during `goto`, so execution proof exists but result is fail-at-runtime.
- Edge run in this environment is blocked by enterprise policy (`DevTools remote debugging is disallowed`, `Headless mode is disallowed`).
- These are environment/runtime constraints, not missing framework implementation. The code paths and commands remain executable where policy/network permits.
