---
name: langfuse
description: Integrate with Langfuse for AI observability, prompt management, experimentation, and evaluation workflows — tracing setup, trace/dataset/prompt/score queries via CLI or API, CI/CD experiment gates, instrumentation audits, prompt migration to Langfuse. Installed from github.com/langfuse/skills.
---

# Langfuse Skill Documentation

Source: https://github.com/langfuse/skills (skills/langfuse)

## Overview
This skill enables interaction with Langfuse for AI observability, prompt management, experimentation, and evaluation workflows. It provides access to documentation, CLI tools, and API capabilities.

## Key Capabilities

**Allowed Tools:**
- Web fetching from langfuse.com
- Bash commands for langfuse-cli operations (schema discovery, API calls, data queries)

**Primary Functions:**
- Query and modify Langfuse data via CLI
- Access comprehensive documentation
- Support AI engineering tasks including tracing, monitoring, datasets, experiments, and evaluations

## Core Principles

1. **Documentation Priority**: Always fetch current docs before implementation—Langfuse updates frequently
2. **CLI for Data Access**: Use langfuse-cli for querying/modifying data
3. **Use-Case Guidance**: Reference specific guides (in `references/`) before implementation details
4. **Latest Versions**: Employ current SDK/API versions unless otherwise justified
5. **UI Verification**: Inspect screenshots when uncertain about interface labels

## Documentation Access Methods

**Method 1—Index**: Fetch `https://langfuse.com/llms.txt` for structured page listing

**Method 2—Direct Pages**: Append `.md` to documentation paths or use `Accept: text/markdown` headers

**Method 3—Search**: Query `https://langfuse.com/api/search-docs?query=<encoded-query>` across all documentation and GitHub resources

## CLI Usage

Discover schema and available operations:
```bash
npx langfuse-cli api __schema
npx langfuse-cli api <resource> --help
```

Set credentials via environment variables (`LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_BASE_URL`) before making calls.

## Use-Case References Available
See `references/`:
- `instrumentation.md` — Application instrumentation (tracing setup, self-audit loop)
- `create-dataset.md` — Dataset creation and management
- `prompt-migration.md` / `prompt-engineering.md` — Prompt migration and engineering
- `setting-up-evals.md` / `judge-calibration.md` — Evaluation setup and calibration
- `user-feedback.md` — User feedback capture
- `sdk-upgrade.md` — SDK upgrades
- `ci-cd.md` — CI/CD integration
- `error-analysis.md` — Error analysis
- `cli.md` — CLI reference

## Note on this project (hanwha-agent)
This repo has `langfuse==2.60.10` installed (legacy decorator-based SDK, not the OTel-based v3/v4 API that current langfuse.com docs describe). Instrumentation here uses `langfuse.decorators.observe` / `langfuse_context`, not the `from langfuse import observe` v3+ syntax. See `backend/app/core/tracing.py`. Upgrading to v4 is a separate, deliberate task (see `references/sdk-upgrade.md`) — do not silently mix APIs.
