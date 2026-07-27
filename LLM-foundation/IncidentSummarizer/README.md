# Incident Summarizer

A tiny applied-AI project: take a raw IT/operations incident report and return a
single faithful summary sentence, using the Gemini API.

It's the first project in an "applied AI, learn by building" track covering LLM API
fundamentals. The goal isn't the summarizer itself — it's learning the concepts
underneath: how a model call is structured, what tokens and context are, how
temperature affects output, how to control model "thinking," how to *measure*
whether the output is any good, and how to survive real network failures.

---

## What it does

**Input:**

```
Payroll execution failed for 342 employees after a salary revision.
Retries created duplicate payroll records for 17 employees.
```

**Output:**

```
A salary revision caused payroll execution to fail for 342 employees, and
subsequent retries resulted in duplicate payroll records for 17 employees.
```

One sentence, every number preserved, cause-and-effect intact, nothing invented.

And — the part that makes it more than a demo — a **facts-check** runs automatically
on that output, confirming no numbers were dropped and none were invented.

---

## Concepts this project teaches

- **System vs user input** — stable rules (system instruction) kept separate from
  per-call data (the incident text).
- **Tokens & context windows** — the model sees tokens, not characters; input and
  output share one fixed budget.
- **Temperature & determinism** — low temperature makes summaries faithful and
  repeatable.
- **Thinking control** — Gemini 3 models "think" before answering; that thinking
  costs hidden tokens. You can dial it down for simple tasks.
- **Prompt variables** — the incident text is a variable passed in, not hardcoded.
- **Model input/output** — the response is an object (text + token counts + stop
  reason), not just a string.
- **Evals** — an automated grader that scores open-ended output on properties you
  care about, run across a dataset so quality becomes a trackable number.
- **Errors, retries, timeouts** — 4xx = your fault, fix it; 5xx/timeout = transient,
  retry with backoff; 429 = the special case (a 4xx you *do* retry).

---

## Setup

1. **Install dependencies**

   ```
   pip install google-genai python-dotenv
   ```

   Note: the package is `google-genai` (the current unified SDK), **not** the
   deprecated `google-generativeai`.

2. **Get an API key** from Google AI Studio.

3. **Create a `.env` file** in the project root (filename is exactly `.env`):

   ```
   GEMINI_API_KEY=your_real_key_here
   ```

   No spaces around `=`, no quotes. Add `.env` to `.gitignore` so the key never gets
   committed.

4. **Run it**

   ```
   python IncidentSummarizer.py
   ```

---

## Current state of the code

The model call works: a single call with a system instruction, a 30-second request
timeout, thinking dialed to minimal, and token-usage read from the response. The
facts-check (extraction + comparison) is complete and validated. Still to wrap
everything into one `summarize()` function with latency timing and a retry loop.

```python
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(http_options=types.HttpOptions(timeout=30000))  # 30s, in ms

system_instruction = (
    "summarize the incident in one sentence, maximum words 50, "
    "keep all numbers, don't add timestamps"
)

config = types.GenerateContentConfig(
    system_instruction=system_instruction,
    thinking_config=types.ThinkingConfig(
        thinking_level=types.ThinkingLevel.MINIMAL
    ),
)

content = (
    "Payroll execution failed for 342 employees after a salary revision. "
    "Retries created duplicate payroll records for 17 employees."
)

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=content,
    config=config,
)
print(response.text)
print(response.usage_metadata)  # token counts, including hidden thinking tokens
```

The **facts-check** (separate, pure-Python, no API needed) is built and working:
extract numbers from input and output, convert to sets, subtract both directions to
find dropped and invented facts.

---

## Build progress

| Step | What | Status |
|------|------|--------|
| 0 | Environment: key, `.env`, SDK install | Done |
| 1 | Hello-world call | Done |
| 2 | Write the system instruction | Done |
| 3 | Wire system instruction into `config` | Done |
| 4 | Read token usage from `response.usage_metadata` | Done |
| 5 | 30s request timeout via `HttpOptions` | Done |
| 6 | Thinking control (`thinking_level=MINIMAL`) | Done |
| 7 | Extract `response.text` cleanly | Done |
| 8 | Test against payroll spec | Passed |
| 9 | Adversarial / ambiguous input testing (7 cases) | Done |
| 10 | **Facts-check** — naive `\d+` extractor | Done |
| 11 | **Facts-check** — compare both directions (set diff) | Done |
| 12 | **Facts-check** — return dropped + invented | Done |
| 13 | **Facts-check** — observe false failures on `1,204`, `v2.7` | Done |
| 14 | **Facts-check** — smarter regex `\d+(?:[,.]\d+)*` | Done |
| 15 | Latency timing (`time.perf_counter()`) | TODO |
| 16 | Wrap everything in `summarize(incident_text)` | TODO |
| 17 | Retry loop (503 backoff + 429 special case) | TODO |
| 18 | "Not-an-incident" guard in system instruction | TODO |

**Four metrics per call:** output ✓ · token usage ✓ · facts preserved ✓ · latency (TODO)

---

## The facts-check, explained

The summary is open-ended text, so you can't check it with `==`. Instead you check a
*property*: were all the numbers kept, and were any invented? This is a small
**eval** — an automated grader for a fuzzy output.

**How it works (extract → compare → report):**

1. **Extract** numbers from the input and from the output with `re.findall`.
2. **Compare both directions** using set difference:
   - `set(input) - set(output)` → **dropped facts** (were in the source, missing from summary)
   - `set(output) - set(input)` → **invented facts** (in summary, never in the source)
3. **Report** the two sets back in the result object.

Both directions matter: dropped facts test "keep all numbers," invented facts test
"add nothing." A summary that quietly introduces a number is arguably worse than one
that drops one.

**The regex evolution (the real lesson):**

- Started naive: `\d+` = "one or more digits."
- Ran it on a real messy input and *watched it break*: `1,204` shattered into
  `1` and `204`; `v2.7` split into `2` and `7`. These cause **false** "dropped fact"
  alarms.
- Wrote the rule in plain English first: *a number begins with a digit, ends with a
  digit, and may contain commas or dots only in between.*
- Built the pattern from that rule: `\d+(?:[,.]\d+)*` — a digit-run, then zero or
  more of (separator + more digits).
- Hit the classic `findall` + capturing-group trap (it returned only group contents:
  `,204`, `.7`, empty strings). Fixed it with a **non-capturing group** `(?:...)`,
  which makes `findall` return the whole match again.

**Known limitations (deliberately punted):**

- Presence ≠ correctness — it checks a number *appears*, not that it's used right.
- Blind to word-numbers ("seventeen").
- Can't tell a version number (`v2.7`) from a decimal measurement.

---

## FAQ — questions from the build

**Which model is free? Should I run a Hugging Face model locally instead?**
For learning API fundamentals, use a hosted free tier — running locally swaps API
concepts for hardware problems and slows you down. Google Gemini (via AI Studio) has
the most generous free tier; Groq is a fast, OpenAI-compatible alternative. Save
local Hugging Face (or Ollama, which is easier than raw `transformers`) for later
when you want privacy, no rate limits, or to learn model internals.

**Is `GEMINI_API_KEY=` the correct variable name? Where does the `.env` file go?**
The name is correct — the SDK looks for exactly `GEMINI_API_KEY`. The file must be
named exactly `.env` (not `environment.env`), and the value goes right after the `=`
with no spaces or quotes. Put it in the project root; `load_dotenv()` searches from
the current directory upward.

**Why do I get "No API key was provided" even though I have a `.env` file?**
A `.env` file does not load itself. The SDK reads from the *process environment*
(`os.environ`), and a file on disk isn't that. `python-dotenv`'s `load_dotenv()` is
the bridge — it reads the file and injects the key into the environment. You must
call `load_dotenv()` *before* creating the client. Two separate places a secret can
live (file vs environment); the SDK only reads the second.

**Why did `gemini-2.5-flash` give a 404 NOT_FOUND?**
The model name was stale — the 2.5 line is being retired for new users. Model IDs
churn fast. The current Flash workhorse is `gemini-3.6-flash`. When a model 404s,
check Google's live model list / release notes rather than guessing. A 404 is a
*client* error (your input is wrong), so retrying it is pointless — fix the input.

**How do I pass a `system_instruction`?**
It's not a direct argument to `generate_content`. It lives inside a config object:
`config=types.GenerateContentConfig(system_instruction=...)`, and the config is
passed as the `config=` argument. Needs `from google.genai import types`. The config
is the container for all generation knobs — `temperature`, `max_output_tokens`, and
`thinking_config` go in the same place.

**What's the code for a timeout?**
Set it on the client via `http_options`:
`genai.Client(http_options=types.HttpOptions(timeout=30000))`. The value is in
**milliseconds** (30000 = 30s), which trips people up. A timeout turns "hang
forever" into a clean failure your retry loop can handle.

**How do I control the model's "thinking"?**
Gemini 3 uses `thinking_level` (not the older `thinking_budget`), nested as
`GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.MINIMAL))`.
Default is HIGH. On a simple summary task, setting MINIMAL cut a call from 564 → 80
total tokens (~86% saving — the ~484 hidden `thoughts_token_count` went to 0) with
no quality loss. Read `response.usage_metadata` to see the thinking tokens.

**What is an "eval" and why build one?**
An eval is an automated grader that checks whether open-ended output has the
properties you care about, run across a dataset so quality becomes a trackable
score. The grader can be programmatic (like the facts-check), an LLM-as-judge, or a
human — match the grader to how fuzzy the property is. The facts-check is the small
programmatic version; a fuller eval *system* is saved for the RAG project, which has
more and fuzzier failure modes.

**Why does `re.findall` return weird fragments / empty strings?**
Because the pattern had a **capturing group** `( )`. When a pattern contains a
capturing group, `findall` returns only the *group's* contents, not the whole match
— so `1,204` came back as just `,204`, and plain numbers came back as `''`. Fix:
make the group **non-capturing** with `(?:...)`. Then `findall` returns whole
matches again.

**How do I handle a 503?**
A 503 is a *server* error (transient, "try again later"). Retry it with exponential
backoff — wait, retry, wait longer, up to a cap. This is the opposite of a 404:
retry 5xx and timeouts, never retry ordinary 4xx.

**Isn't a 429 a 4xx? Why retry it?**
Yes — and it's the exception to "never retry 4xx." A 429 RESOURCE_EXHAUSTED means
you're sending requests faster than the free tier allows; it's *transient*, and the
error even includes a `retryDelay` field telling you exactly how long to wait. So
the retry rule is really: retry 5xx/timeout with backoff, retry 429 using its own
`retryDelay`, fail immediately on *other* 4xx.

**I keep hitting the rate limit — should I set up billing?**
No. Enabling billing on a project *removes* the free tier entirely and bills every
call from the first token. Free-tier limits reset on their own (per-minute limits in
~60s; the daily cap at midnight Pacific / ~1:30 PM IST). If you're blocked and want
to keep working, switch to a *different* free model (e.g. `gemini-3.5-flash-lite`) —
each model has its own quota bucket. And note: quota is per Google Cloud *project*,
not per key, so making extra keys in the same project doesn't help.

**The rate limit kept climbing (20s → 50s) instead of counting down. Why?**
Because you kept retrying *during* the cooldown. Every early retry spends another
request and pushes the reset window further out. The fix is to stop sending
requests and let the window pass untouched. (This is exactly what an automated
retry loop reading `retryDelay` prevents.)

**Do the prompt details (role, exact constraints) really matter that much?**
The exact wording is polish you can tune later. The one real concept: the system
prompt is your only control surface, and anything you don't specify, the model
decides for you — usually longer and chattier than you want. You learn this best by
running a rough prompt and watching where it breaks, not by perfecting it up front.

---

## Key gotchas worth remembering

- **A variable is not a wire.** Defining `system_instruction = "..."` or building
  `GenerateContentConfig(...)` on its own line does nothing until it's *passed into*
  the call. Constructing an object and using it are two separate acts. This causes
  the classic "my code looks right but does nothing" bug.
- **`.env` is not the environment.** The file needs `load_dotenv()` to reach
  `os.environ`, which is what the SDK actually reads.
- **4xx vs 5xx is the error taxonomy — with one exception.** 4xx = you sent
  something wrong, fix it, don't retry. 5xx / timeout = transient, retry with
  backoff. **429 is the exception:** a 4xx you *do* retry, using its `retryDelay`.
- **Model names expire.** Don't treat any model ID (or any blog) as permanent; a 404
  is your cue to check the current live list.
- **"Don't add X" ≠ "remove X."** The instruction kept an existing timestamp because
  "don't add" only forbids inventing one. Small wording gaps produce very different
  behavior — that's prompting in a nutshell.
- **When output looks wrong, suspect the inputs before the logic.** A phantom
  `2026 / 03 / 14` in the facts-check turned out to be a date leaking into the input
  list — the comparison was correct all along. Print your data right before the
  operation that surprised you.
- **Order doesn't matter when you compare with sets.** The two number-lists came out
  in different orders, but set difference is order-blind, so it didn't matter — a
  reason to build the check on sets, not positional list comparison.
- **`findall` + capturing group = fragments.** A capturing `( )` makes `findall`
  return only the group; use non-capturing `(?:...)` to get whole matches.
- **The model has no "reject non-incident" behavior.** It forced incident-framing
  onto pure noise and a recipe. That's a system-instruction gap (the not-an-incident
  guard, still TODO), not a model defect.