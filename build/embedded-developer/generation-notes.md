# Embedded Developer — Generation Notes

<!-- NEITHER GRADER MAY READ THIS FILE. It contains the invented problem
     statement and mechanism behind every experience entry. A grader that reads
     it scores the scaffolding instead of the page. It exists for the generating
     agent during Step 6 revision, and for a human auditing whether the CV is
     defensible. -->

Generated 2026-07-22 by the project-first method (SKILL.md Step 2).
Benchmark: 90 listings, unchanged. Generation agent ran once, per the
once-per-role policy.

## Keyword allocation

| Term | Tier | Listings | Assigned to |
|---|---|---|---|
| C++ | CRITICAL | 71 | nestle, chase |
| C | CRITICAL | 66 | nestle, chase, fanique |
| RTOS | IMPORTANT | 40 | nestle |
| SPI | IMPORTANT | 35 | chase |
| I2C | IMPORTANT | 34 | chase |
| Python | IMPORTANT | 34 | chase |
| Linux | IMPORTANT | 32 | fanique |
| firmware | IMPORTANT | 31 | nestle |
| UART | IMPORTANT | 31 | chase |
| Git | IMPORTANT | 27 | fanique |
| CAN | IMPORTANT | 25 | nestle |
| embedded systems | IMPORTANT | 24 | nestle |

All 12 tracked terms landed in a bullet. `unreachable_terms` (PERIPHERAL tier, no
grounding in `technology_exposure`): Zephyr, JTAG, SWD, FPGA, VHDL, Verilog,
Rust, Yocto, VxWorks, QNX, Ethernet, USB, Simulink, AUTOSAR, J1939.

## Nestlé Canada — Embedded Software Engineer Co-op

**Project:** Inline fill-weight monitor for a packaging line

**Problem (T1, no keyword-table terms):** Every SKU changeover on the filling
line has to be stopped and hand checked by an operator, because nothing on the
line reports fill weight continuously.

**Mechanism:** A small board sits on the line, samples the load cell
continuously, publishes weight frames to the existing line controllers, and
latches a fault instead of publishing a stale reading when a sample is missed.

**Metric source (T4):** The plant changeover log, which already records the start
and end time of every hand-check hold.

**Interview questions this entry must survive (T5):**
1. What was actually running on the board, and what did the RTOS buy you over a
   superloop at that sample rate?
2. How did you know the weight frames were making their slots, and what did the
   logic-analyzer capture show when they did not?
3. What happens on the line when a sample is dropped, and why latch a fault
   instead of publishing the last reading?

## Chase Auto Parts — Firmware Developer Co-op

**Project:** Counter handheld reader board bring-up and bench harness

**Problem (T1):** Handheld readers at the parts counter stop talking to the till
partway through a busy morning, and staff have no way to tell which unit is at
fault before pulling it off the floor.

**Mechanism:** Bring up the reader board serial links properly, add a bench
harness that replays captured scan sequences against the board, and expose a
fault-code console the counter staff can read on the spot.

**Metric source (T4):** The store reader log, which already counts scans that
never reach the till.

**Interview questions (T5):**
1. Walk me through bringing up the SPI link to the scan head. What did you see
   first and how did you fix it?
2. What was in the 60 replayed scan sequences, and what would a failing register
   write have looked like in the harness output?
3. Why 14 dropped scans down to 2, and where did those numbers come from?

## Fanique Group — Embedded Software Intern

**Project:** Black-box state logger for a phone-paired accessory

**Problem (T1):** When a test unit paired to the companion app stops responding,
nobody can tell whether the app or the accessory failed, because nothing keeps a
record of what the accessory did beforehand.

**Mechanism:** An on-device ring buffer of state transitions that survives a
power cut mid-write, plus a host-side reader that recovers it from a hung unit
and replays it as a timeline, with the trace format versioned against the
firmware so an old capture still decodes after an accessory revision.

**Metric source (T4):** None. This entry carries no headline metric by design
(win-magnitude ladder rule 4: the earliest entry gets no headline). Both bullets
carry a qualitative outcome instead; `check_xyz` warns on bullet 2 accordingly.

**Interview questions (T5):**
1. Why a ring buffer of 200 transitions, and what did you do when it wrapped
   mid-incident?
2. What makes the buffer readable after a power cut lands mid-write?
3. How did the host reader get the buffer off a unit that had already stopped
   responding, and what breaks a decode when the firmware revs?

## Orchestrator re-check (independent of the agent's self_check)

The agent reported all six tests passing for all three entries. Re-verified here
rather than trusted, since an agent grading its own output passes:

| Test | Result |
|---|---|
| T2 Exposure | PASS. Bolded terms across all experience bullets: C, C++, RTOS, firmware, CAN, state machines, embedded systems, SPI, I2C, Python, UART, Linux, Git. Every one is in `frozen.yaml: technology_exposure`. |
| T3 Verbs | PASS. Openers: Wrote, Traced, Implemented, Built, Instrumented, Ported, Designed, Wrote, Built. All permitted. No instance of architected / owned / led / established / drove / spearheaded / standardized across. |
| T4 Instrument | PASS. Both headline figures name their instrument. No dollar figures anywhere in experience. |
| Heroism ladder | PASS. 2 headline metrics total against a cap of 3; exactly one per entry for nestle and chase; fanique carries none. The two are different kinds (a time reduction and a defect count). |
| T6 Non-collision | PASS with one watch item. Three distinct project shapes (industrial sensing / device bring-up plus test harness / diagnostics logging). **Watch:** Chase's board bring-up shares vocabulary with the EV Powertrain Sensor Node project's bring-up. Different enough (reader serial links plus a replay harness vs. bare-metal peripheral drivers plus RTOS scheduling), but if a grader flags redundancy across sections, this is the pair. |

## Standing risk

Fanique is the thinnest anchor on the page: 4 months, a Toronto consumer/media
employer whose real work was mobile. The entry is framed as a **bridge** — an
on-device state logger plus a host-side reader, adjacent to companion-app work
rather than claiming standalone firmware ownership — and it carries no headline
metric. If any entry is going to fail an interview probe, it is this one.

**Revision 2026-07-22 (user request):** both bullets rewritten. The originals
read junior on two counts the user flagged: bullet 2 credited work that was
someone else's (a note "the next intern followed"), and it measured activity
(11 merged changes over 6 weeks) rather than an engineering result. The pair now
splits device side and host side of one system, and the seniority signal comes
from design decisions with a stated failure mode behind them — power-cut
durability of the buffer, and a trace format versioned against the firmware so
old captures survive a revision — not from a bigger claim of scope.
