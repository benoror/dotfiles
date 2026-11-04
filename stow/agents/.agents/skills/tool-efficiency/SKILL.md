---
name: tool-efficiency
description: >-
  Use when choosing tools, calling connectors, or learning a service. Keep
  short cheat sheets, prefer the lightest route, look before writes, log
  failures, and never guess field names, so the agent uses fewer tokens.
---
# Tool efficiency

Adapted from Michael Fenech (https://x.com/Michael_Fenech_/status/2104189815381983657).

**Expected result:** the agent does the job on the lightest route that works. Where a cheat sheet exists, it works on the first try. The agent logs each failure, so the next run does not repeat it.

## Where notes go

Keep notes in a folder that the agent can read and write in each session. Examples: a `references/` folder in the project, or agent memory. Use these two kinds of note:

- **Cheat sheet:** one short file for each service (`service-cheat-sheets/<service>.md`). It holds the route that works, the IDs and field names, and known limits.
- **Failure log:** one file (`tool-failure-log.md`). Each entry holds what you tried, why it failed, and what worked.

Do not put secrets in these notes. Write the name of the environment variable, not the value.

## When you use a service

1. Read the cheat sheet for the service. If there is no cheat sheet, write one after you learn the service.
2. Use the lightest route that works. Use this order: a known or saved route, then a connector or MCP tool, then an authenticated CLI or API client, then the public web, then a browser, then the user. Name each step by its result (for example: search mail, read a row, list files). Then find a tool in the harness that gives that result. Before you use a browser, say why the connector cannot do the job. If a connector is broken or needs a sign-in, tell the user. Do not work around it silently.
3. Before you write, send, or delete: do a read-only check. Make sure that the record exists, and check the field names and the expected values. After the write, read it back to confirm.
4. When a step fails, add an entry to the failure log. Read the log before you try the same kind of job again.
5. Do not guess field names, IDs, pages, databases, or labels. Look them up.
6. If you read the same web page on a schedule, write the extraction one time as a tested script. Save it beside the cheat sheet and use it next time. Do not read the screen again. In one test, a screen read cost about 4 times more than a script read (https://x.com/Michael_Fenech_/status/2115421573524148479). Test the script again when the page changes.

## Weekly review (optional)

Once a week, write a short scorecard: jobs done on the first try against jobs with retries, the worst service, the most common cause of waste, and one fix for next week. Use real counts from the failure log. Do not invent counts.
