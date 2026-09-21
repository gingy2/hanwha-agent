# Langfuse Prompt Migration Guide (summary)

Systematic approach to migrating hardcoded prompts into Langfuse for centralized management.

## Prerequisites
Verify credentials are configured: `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_BASE_URL` (or `LANGFUSE_HOST`). Check presence only, never print the secret key.

## Four-Step Process
1. **Inventory** — document each prompt's name, location, type (chat or text), variables, and content before writing code.
2. **Template conversion** — transform all variable syntax to Langfuse's double-brace format (`{{var}}`). Uploading `{var}` will silently fail to substitute.
3. **Implementation** — with user authorization, create prompts labeled `production` and refactor code to fetch from Langfuse using the SDK's current API methods.
4. **Verification** — confirm all prompts use the `production` label, variables compile correctly, application behavior remains unchanged, and traced generations display linked prompts in the UI.

## Design Principles
Make dynamic, user-specific, and environment-dependent content into variables while keeping output formats, safety guidelines, and persona traits hardcoded.
