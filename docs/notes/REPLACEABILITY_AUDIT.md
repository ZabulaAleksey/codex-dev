# Replaceability audit — DEV main repositories

## Scope and evidence

Audit run: 2026-09-13. Local Git roots were discovered under `PROJECTS_ROOT=~` with bounded
filesystem traversal; GitHub owner inventory was read through the connected API. The scan did not
change product repositories. Scores are evidence-based snapshots, not release claims.

Primary local repositories:

| Repo | Local checkpoint / state | Classification | Reason |
|---|---|---|---|
| `codex-dev` | `main=040c51a`; replaceability state `bc9f890` on isolated feature branch | PRIMARY ACTIVE | global framework and current DEV queue owner; integration approval pending |
| `math-morph` | `main=027cc29`; additional clean detached/feature worktrees | PRIMARY ACTIVE | active billing/identity/equation work |
| `electro-tutor` | `origin/main=2c63e28`; isolated RTC checkpoints `9a91884`/`c3481ed` | PRIMARY ACTIVE / RTC VERIFIED LOCALLY | user-approved `ET-RTC-001` and feature SPEC isolate Jitsi; merge remains approval-gated |
| `video-chronicle` | `d1d3a09`, clean `main`; two clean feature worktrees | PRIMARY ACTIVE | active media/GUI/release track |

Non-product/local artifacts excluded: plugin cache Git metadata, old DEV staging clones, package
sdist build trees and linked worktrees already attributed to their common repository.

GitHub reports 21 owned, non-archived repositories. The 17 without a current local canonical
checkout or project-stage evidence are `UNKNOWN — NEEDS EVIDENCE`, not automatic clone/retrofit
targets: `ai-mix`, `docasaurus`, `dune-rts`, `fourier-sketch`, `initial-project`, `join-media`,
`marvel`, `monte-carlo`, `off-screen-canvas`, `receipt-scanner-ua`, `server`, `solana`,
`solar-system`, `task-js-ai`, `text-recognition-core`, `vector-diagram`, `wifi-share`.

## Consolidated score

| Repo | Module | Current implementation | Before | After | Evidence / coupling | Retrofit | Remaining risk / next |
|---|---|---|---:|---:|---|---|---|
| `codex-dev` | architecture governance | dev-karkas architecture reference | 5 | 8 | previous reference required only a common backend contract; no complete global owner | `rules/replaceable-modules.md`, FR-015/AC-018, routes and structural test | product runtime evidence remains project-owned; merge and post-merge rematerialization are gated |
| `math-morph` | billing/payments | `ports/billing.py` + `adapters/stripe.py` + canonical billing services | 7 | 7 | Stripe SDK is adapter-local; normalized provider events and contract tests exist | audit only | `api/billing.py` imports the project Stripe adapter at provider ingress; move factory to composition module as P1 |
| `math-morph` | identity/entitlements | OIDC boundary + provider-neutral entitlement ports/transport | 8 | 8 | dedicated domain/services/ports and focused contract/integration suites | audit only | live-provider acceptance and cross-product consumer remain separately gated |
| `math-morph` | equation backends | Document IR, `EquationBackend`, MathML/MathType adapters | 8 | 8 | backend-neutral IR, explicit optional bridge and golden/adapter tests | audit only | WIRIS/Word/MathType live compatibility and migration evidence remain provider-specific |
| `math-morph` | artifact storage | `ArtifactStore` port with current local implementation | 7 | 7 | application consumes a project port; provider implementation remains local | audit only | S3-compatible durable migration/export is not rehearsed |
| `electro-tutor` | RTC/whiteboard | provider-neutral `MeetingProvider`/`MeetingSession` with isolated Jitsi adapter | 2 | 8 | vendor script/domain/types/options/commands are adapter-local; timeout/retry, canonical errors, capability, URL/privacy and teardown contracts have focused and built-browser evidence | P0 completed locally | checkpoints `9a91884`/`c3481ed`; final correctness/security reviews no findings; merge remains approval-gated |
| `electro-tutor` | identity/OIDC | domain `ExternalIdentity` + `adapters/oidc.py` | 7 | 7 | provider-neutral domain principal; HTTP/JWT types stay in adapter | audit only | test-only `e2e_support.py` uses Keycloak-named helpers/config and should be renamed when the local test provider becomes swappable |
| `electro-tutor` | persistence/capabilities | application services + repository/unit-of-work adapters | 7 | 7 | boundaries and real PostgreSQL integration evidence exist on active track | audit only | active stage is `ET-09.4`; its next authorized slice remains `ET-09.4c` |
| `video-chronicle` | FFmpeg/FFprobe | `PipelinePorts`, managed command runner/process control | 8 | 8 | process creation centralized; list argv, timeout/cancel and contract tests | audit only | one internal engine is intentional; generic media-provider abstraction would be YAGNI |
| `video-chronicle` | timeline interchange | adapter-neutral contract + optional OTIO adapter | 8 | 8 | proposal-only import, optional resolver, golden/contract tests | audit only | broader OTIO capability remains explicitly optional |
| `video-chronicle` | transcription | explicit local `whisper.cpp` adapter and manifest | 7 | 7 | bounded adapter, provenance/hash/license contract and focused tests | audit only | real model WER/CER benchmark unavailable; stage remains implemented-unverified |

## Top coupling findings

1. Electro Tutor RTC/UI direct Jitsi coupling was the only P0; user-approved `ET-RTC-001` now
   isolates it behind a system-owned meeting port in an unmerged feature branch.
2. Electro Tutor exact fetch restored `origin/main=2c63e28`; the dedicated SPEC/stage and isolated
   checkpoints preserve the unrelated partial `ET-09.4` track.
3. MathMorph billing ingress imports the Stripe adapter factory directly in the API controller.
4. MathMorph worker composition selects the Stripe operation adapter directly; this is acceptable
   as a composition root but should remain the only non-adapter selection site.
5. MathMorph provider webhook storage retains raw payload for audit/idempotency, so retention and
   export/migration policy remains security-sensitive even though domain events are normalized.
6. MathMorph artifact storage has a port, but durable S3-compatible migration/fallback is not yet
   rehearsed.
7. Electro Tutor local/test orchestration contains Keycloak-specific helper names outside the OIDC
   adapter; production domain types remain neutral, so this is P1 naming/config debt.
8. Video Chronicle FFmpeg/FFprobe invocation is correctly centralized; bypasses were not found.
9. Video Chronicle uses optional adapters for OTIO/transcription without leaking their types into
   canonical project schema.
10. Seventeen remote-only owned repositories lack local stage/code evidence and remain UNKNOWN;
    cloning or retrofitting them automatically would exceed the active-repository contract.

## Priority and migration debt

- **P0 completed locally:** Electro Tutor `Classroom.tsx` → system-owned meeting port + isolated
  Jitsi adapter/composition root. Contract, loader recovery, URL/privacy, capability and teardown
  behavior are verified on `feature/et-rtc-provider-boundary`; integration is not yet performed.
- **P1:** MathMorph webhook factory/composition cleanup; Electro Tutor Keycloak-specific test
  helper naming; MathMorph artifact-storage migration rehearsal.
- **P2 / YAGNI:** do not wrap every FFmpeg operation in a generic media-provider hierarchy. Keep
  the current `PipelinePorts`/process boundary; FFmpeg is the selected internal engine.

Provider switches, data migrations, production secrets and deploy are outside this audit. The P0
product mutation is isolated and verified; no merge, push or branch deletion was performed.

## Deterministic guards and suites

- Global: `tools/test_replaceable_module_policy.py` ensures one canonical policy owner, all routes,
  FR-015/AC-018 and the structural-vs-runtime evidence boundary.
- MathMorph existing evidence surfaces: billing/provider/entitlement contract and integration
  tests, document/equation adapter goldens, project validator.
- Electro Tutor evidence surfaces: OIDC/auth transport and PostgreSQL repository tests plus the new
  fake/Jitsi meeting contract suite, structural UI guard, build and built-browser classroom path.
- Video Chronicle existing evidence surfaces: process control, pipeline ports, OTIO interchange and
  transcription tests.

Generic cross-language regex vendor lint was intentionally not added: it would classify provider
ingress/composition/tests as false positives. Each project should use its AST/import/dependency
tooling when the P1/P0 retrofit is executed.
