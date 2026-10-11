# Project working rules

用户最新要求（2026-10-11）：恢复最新远端开发分支并从第123节继续；为节约资源，每小节仅保留与实际改动直接相关的必要检查，无必要时省略，不重复运行已通过且源码未变的检查。全量测试范围不缩减。每完成一节立即commit保存，并沿用已授权的普通push。保留第125节全量检查，此后每15节一次（140、155……）。继续开发，旧“125后停止/不启动126”安排已被本次续接要求替代。每节仍须有实际功能成果，未知机制先查来源；95/109已延期的原流程不无故重试。

用户补充要求（2026-10-11）：每一节都必须交付具有实际意义、能够推进项目未完成事项的功能改进。不能只修漏洞而不推进项目，更不能靠孤立断言、测试、资料归档或文档更新凑节数。漏洞修复应并入相关功能节；若本轮仅做维护，明确记录为维护提交，不增加功能完成节数。开始一节前明确对应的未完成项目、此次新增能力与验收标准；结束时据实际成果核对，不将未知机制或已完成能力重新记为推进。


## Cloud continuation

This independent project is named rougezhushou and starts from local version 0.70.0. Read CLOUD_HANDOFF.md before resuming. Linux checks use scripts/verify_cloud.py; Windows UI, game sampling and desktop chat verification require the original Windows machine. Report those unavailable checks explicitly, never simulate successful native validation. Private state and personal screenshots were not migrated. Keep them excluded. Preserve the local original project and its current run. Historical receipts describe their original machine and batch, not this cloud snapshot.

## Current work order

Current validation cadence: necessary checks only after each section; full available Linux/Wine/window validation at section125, then every15 completed sections. The scope of full validation remains unchanged. Commit and ordinarily push every completed section. Do not interpret historical five-section rules or stop125 notes as current instructions.

Continue development on `codex/p2-development`. The user requested that all subsequent changes be applied on this branch. Check the active branch before editing; preserve existing changes and do not switch to or apply new work on another branch unless the user changes this instruction. Use the existing checkout.

The user authorized continuous work without confirmation between sections. Each coherent functional section records its implemented scope, necessary validation (or why none is needed), limitations and next action in DEVELOPMENT_CHECKPOINT.json and WORK_IN_PROGRESS.md, then commits and ordinarily pushes. Reuse unchanged passing evidence; do not require exhaustive native graph comparisons, repeated independent audits, screenshots or broad regression on every section. Run an actual window only when needed to verify the changed UI behavior; full Linux/Wine/window validation keeps its complete available scope. Wine is compatibility validation, not genuine Windows/game/desktop integration.

User instruction on 2026-10-07: after P2 is complete, continue P3. If the same problem remains unresolved after three attempts, defer it with evidence, attempt count and restart conditions; continue independent work. If account usage drops below 15%, finish required validation and checkpoints for the active section, then wrap up. No enabled tool currently exposes account usage; never invent a percentage.

User instructions on 2026-10-08: increase the amount of useful work in each section. Group related, source-supported functional improvements with their complete verification into one section; source collection, an isolated assertion, or routine archival preparation is not a separate progress milestone. Keep per-issue original evidence, applicability, boundary input/output checks, failure records and restart conditions. Use only necessary change-specific validation before archiving the group; full validation follows the latest cadence above. Broader scope does not reduce detail control.

User instruction on 2026-10-06: advance P2 first. Preserve the unfinished P1 checkpoint; do not resume P1 automatically from older handoff text. Recognition optimization remains after all other work.

User instruction on 2026-10-05: recognition optimization comes after all other project work. Prioritize mechanics, calculation, state handling, map/event data, chat compatibility and delivery. Keep recognition coverage, layout adaptation, accuracy and performance improvements together at the end of PROJECT_PROGRESS.md. Existing recognition remains available; do not resume its optimization from an older handoff paragraph.

## Evidence before mechanism changes

User requirement reaffirmed globally on 2026-10-07 (originally recorded on 2026-10-03): whenever a mechanism is unknown, look up evidence directly. Apply this rule on every later operation in this project.

- Check existing research receipts first, then consult pinned original game data and relevant mechanism documentation. For a new or unresolved detail, perform a targeted source search before changing its numerical model.
- Do not spend effort inventing activation order, tick phase, stacking rules, probabilities, hidden scripts or timing from adjacent mechanics. Parameters alone do not prove a missing script.
- Record sources, the facts they establish, and the exact remaining unknown. If sufficient evidence is unavailable, retain an explicit unknown and continue independent work that has evidence. Do not convert an arbitrary assumption into the default calculation.
- Reuse prior evidence when it answers the same question; do not repeatedly redesign guesses or repeat a completed search without a new lead. An implementation check against an established rule is still required.
- Verify public behavior appropriate to the change and update PROJECT_PROGRESS.md, WORK_IN_PROGRESS.md and the batch receipt. Distinguish implemented scope, tested cases and remaining gaps.
- PROJECT_PROGRESS.md lists only remaining work. Remove completed items in the same batch and record their scope/evidence in PROJECT_COMPLETED.md. Partially completed rows describe only the remaining gaps; never append completed-batch summaries or receipts to the todo list.

## Product and state boundaries

- This is an offline calculation and advice application with background read-only sampling. Do not operate the game, analyse live placement, deploy operators or trigger skills.
- Do not send chat messages during development/verification. Preserve private settings and chat bindings. Only the user's manual reset clears actual run memory; do not restore an older run over the current one.
- Combat-only relic triggers remain reference information according to the current offline scope. Do not reintroduce removed event inputs or numerical effects.
- Use temporary state directories for verification. Do not copy private runtime contents into public artifacts or backups.
- Keep the simple test interface available. Validate the actual project window when the change needs UI verification; full window validation remains part of the full-check cadence.
- Automation 1-3 was deleted at the user's request. Do not recreate it.
- Do not start overlapping edits or spawn agents unless explicitly authorized by the user or another applicable instruction.
