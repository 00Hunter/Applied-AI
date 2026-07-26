# Log Parser

A command-line tool that reads a plain-text log file, counts ERROR-level
entries, and reports how many errors each service produced — output as JSON.

## What it does

Reads logs in the format:

    2026-07-21 ERROR PaymentService Connection timeout
    2026-07-21 INFO  UserService    User created

Filters for ERROR lines only, tallies errors per service, and prints:

    {
      "total_errors": 2,
      "services": {
        "PaymentService": 1,
        "PayrollService": 1
      }
    }

## How to run

Place your logs in `logs.txt` in the same folder, then:

    python parser.py

## How it works

The program follows a five-stage pipeline:

1. **Read**      — open the file and iterate it line by line
2. **Parse**     — split each line into fields (date, level, service, message)
3. **Filter**    — keep only lines where the level is ERROR
4. **Aggregate** — count total errors and per-service errors into a dictionary
5. **Serialize** — assemble a result dict and convert it to JSON with json.dumps

## Concepts used

- Reading files with a context manager (`with open(...)`)
- String splitting (`.split()`)
- Lists and dictionaries (including the `.get(key, 0) + 1` counting idiom)
- Nested dictionaries for structured output
- JSON serialization (`json.dumps` with indentation)