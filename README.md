# Applied AI Engineering — Learning Repository

This repository documents my journey of learning applied AI engineering through small, focused implementations.

My background is primarily in backend and distributed systems using Java, Spring Boot, Python, REST APIs, Redis Streams, RabbitMQ, SQL databases, and cloud infrastructure.

Instead of starting with a large AI agent or copying a complete framework-based project, I am following a bottom-up approach:

> Learn one concept, build a small working module, understand its limitations, and then combine it with other modules.

This repository is at an early stage and will evolve as I continue learning.

---

## Current Progress

### Log Parser

The first module in this repository is a simple log parser.

It reads application logs, extracts useful information, and generates a structured summary.

The purpose of this module is to strengthen the Python foundations required for later applied AI work, including:

* File handling
* String processing
* Lists and dictionaries
* Functions
* Type hints
* JSON serialization
* Error handling
* Basic testing

Example input:

```text
2026-07-26 ERROR PaymentService Connection timeout
2026-07-26 INFO UserService User created
2026-07-26 ERROR PayrollService Duplicate payroll run
```

Example output:

```json
{
  "total_logs": 3,
  "total_errors": 2,
  "errors_by_service": {
    "PaymentService": 1,
    "PayrollService": 1
  }
}
```

The implementation is intentionally small. The focus is on understanding each part rather than building a large system immediately.

---

### Incident Validator

The second module checks whether a summary of an incident stayed faithful to the original — specifically, whether every number in the source text survived into the summary, and whether any numbers were invented that were never there.

It takes the numbers from the original text and the numbers from the summary, compares them both directions, and reports what was dropped and what was invented.

The purpose of this module is to strengthen the Python foundations required for later applied AI work, including:

* Regular expressions (the `re` module)
* Character classes, quantifiers, and non-capturing groups
* Sets and set operations (difference in both directions)
* Converting between lists and sets
* Functions and structured return values
* Debugging by inspecting inputs before logic

Example input:

```text
Original: During a 90-minute outage, a migration dropped 3 tables affecting 1,204 accounts.
Summary:  A migration dropped 3 tables and affected 1204 accounts over 90 minutes.
```

Example output:

```json
{
  "dropped_facts": ["1,204"],
  "invented_facts": ["1204"]
}
```

The core lesson lives in the regex: a naive `\d+` shatters `1,204` into `1` and `204`, producing false alarms. Growing the pattern into `\d+(?:[,.]\d+)*` — and understanding *why* the group must be non-capturing — is the real exercise. As with the log parser, the implementation stays deliberately small so each part is understood rather than copied.

---

### Incident Summarizer

The third module is the first applied-AI project: it takes a raw IT/operations incident report and returns a single faithful summary sentence using the Gemini API.

The summarizer itself is the vehicle; the goal is learning LLM API fundamentals — how a model call is structured, system vs user input, tokens and context windows, temperature and determinism, controlling model "thinking," and surviving real network failures with retries and timeouts.

The Incident Validator above plugs into this module as its faithfulness check: after the model produces a summary, the validator confirms no numbers were dropped or invented. This is a small **eval** — an automated grader that turns "is this summary any good?" into a measurable result.

The purpose of this module is to learn applied-AI foundations, including:

* Structuring a model API call (system instruction vs per-call input)
* Tokens, context windows, and reading token usage
* Temperature and determinism
* Thinking control (`thinking_level`) and its hidden token cost
* Timeouts and retry loops (4xx vs 5xx, and the 429 special case)
* Evaluating open-ended output automatically

Example input:

```text
Payroll execution failed for 342 employees after a salary revision.
Retries created duplicate payroll records for 17 employees.
```

Example output:

```text
A salary revision caused payroll execution to fail for 342 employees, and
subsequent retries resulted in duplicate payroll records for 17 employees.
```

One sentence, every number preserved, cause-and-effect intact, nothing invented — with the validator confirming that automatically.

---

## Why I Am Using a Bottom-Up Approach

Applied AI applications often combine several concepts at the same time:

* Python application development
* LLM APIs
* Prompt design
* Structured outputs
* Embeddings
* Retrieval
* Tool calling
* Evaluations
* Reliability and observability

Starting with all of these together can make debugging difficult because it becomes unclear whether a problem comes from the application code, the model, the prompt, the retrieved context, or the workflow.

This repository separates those concepts into smaller modules so that each one can be understood independently before integration.

---

## Learning Roadmap

The planned learning sequence is:

```text
Log Parsing
    ↓
Structured Data Validation
    ↓
LLM API Integration
    ↓
Structured LLM Outputs
    ↓
Embeddings and Similarity Search
    ↓
Retrieval-Augmented Generation
    ↓
Tool Calling
    ↓
LLM Evaluations
    ↓
Controlled AI Workflows
```

Each stage will result in a small working implementation.

The roadmap may change as I learn more and identify which concepts need deeper exploration.

---

## Planned Modules

The following modules are planned but are not yet complete.

### Incident Validator

Validate structured incident data using typed Python models.

Learning goals:

* Pydantic
* Input validation
* Optional and required fields
* Validation errors
* Typed application boundaries

### Incident Summarizer

Use an LLM API to convert verbose incident information into a concise technical summary.

Learning goals:

* LLM API calls
* Prompt construction
* Tokens
* Latency tracking
* API error handling

### Structured Incident Extractor

Convert an unstructured incident description into a validated JSON response.

Learning goals:

* Structured outputs
* Schema validation
* Handling missing information
* Preventing invalid model responses from entering application logic

### Similar Incident Search

Compare a new incident with a small collection of historical incidents.

Learning goals:

* Embeddings
* Vector similarity
* Top-k retrieval
* Similarity thresholds
* Semantic search

### Runbook Retrieval

Retrieve relevant operational documentation for an incident.

Learning goals:

* Document chunking
* Retrieval-Augmented Generation
* Context construction
* Source attribution
* Grounded responses

### Investigation Tool Calling

Allow an LLM to select from a controlled set of investigation tools.

Possible tools may include:

* Search application logs
* Check service health
* Check recent deployments

Learning goals:

* Tool schemas
* Argument validation
* Controlled execution
* Tool failure handling
* Limiting the number of tool calls

### Evaluation Runner

Create a small dataset to measure whether changes improve or degrade the system.

Learning goals:

* Structured output validity
* Classification accuracy
* Retrieval hit rate
* Tool-selection accuracy
* Prompt regression testing

---

## Future Integration

After understanding the individual modules, I plan to combine them into a small incident-triage workflow.

The possible workflow will be:

```text
Incident description
    ↓
Structured extraction
    ↓
Similar incident retrieval
    ↓
Relevant runbook retrieval
    ↓
Controlled investigation tools
    ↓
Evidence-backed diagnosis
```

This is a future direction for the repository and not a claim about the current implementation.

---

## Learning Principles

### Understand before abstracting

I am avoiding large frameworks during the early stages wherever possible.

The objective is to first understand what the framework would otherwise handle automatically.

### Build small modules

Each module should solve one focused problem and remain small enough to understand completely.

### Test failure cases

A module is not considered complete only because it works on one successful example.

I also want to understand:

* What happens with malformed input?
* What happens when a field is missing?
* What happens when an API call fails?
* What happens when retrieval returns irrelevant results?
* What happens when an LLM produces invalid output?

### Keep AI decisions controlled

Important validation, limits, and execution rules should remain in application code.

The model should not be treated as a fully reliable component.

### Measure progress

As the repository grows, I plan to add small evaluation datasets instead of relying only on manually checking a few outputs.

---

## Repository Structure

The current repository structure may be small and will expand gradually.

```text
.
├── log_parser/
│   ├── main.py
│   ├── parser.py
│   ├── sample.log
│   └── tests/
├── README.md
└── requirements.txt
```

Future modules may be organized separately as they are added.

---

## Technology

Currently used or planned:

* Python
* Pytest
* Pydantic
* FastAPI
* LLM APIs
* Embedding models
* Docker

Technologies listed as planned may not yet be present in the repository.

---

## Background

I am a software engineer with approximately three years of product engineering experience.

My previous work includes:

* Java and Spring Boot backend services
* Python-based asynchronous processing
* REST API development
* Redis Streams and RabbitMQ
* Multi-tenant HR and payroll systems
* SQL query optimization
* AWS and GCP deployments
* React and TypeScript frontend development

I am using this repository to extend those backend engineering foundations into applied AI systems.

---

## Repository Status

This repository is currently in the early learning stage.

Completed:

* Basic log parser

In progress:

* Improving the log parser
* Adding validation and tests
* Documenting learnings and failure cases

Planned:

* Structured data validation
* LLM API integration
* Structured outputs
* Embeddings
* Retrieval
* Tool calling
* Evaluations

---

## Note for Reviewers

This repository is not intended to present an already completed AI platform.

It is a record of how I am learning applied AI engineering from the fundamentals, one working module at a time.

The goal is to make the learning process transparent and to demonstrate steady progress through code, tests, documentation, and small practical implementations.
