# Langfuse SDK Upgrade Guide (summary)

Structured approach for upgrading Langfuse SDKs while maintaining trace integrity.

## Key Resources
- Consult version-specific migration paths: Python v3→v4 and JS/TS v4→v5 upgrades
- Instrumentation and attribute propagation documentation
- Sessions and OpenTelemetry integration guides

## Core Process
1. **Inventory phase**: Catalog all SDK instances, packages, exporters, initialization points, and data-emitting components across the codebase.
2. **Attribute mapping**: Identify correlation sources like session identifiers, user IDs, tags, metadata, environment variables, and trace names. Search contextually rather than just for deprecated method names.
3. **Implementation**: Apply version-specific changes, establishing each attribute's documented propagation scope before any observation-producing call that must inherit it.

## Validation
Complete a **completion report** capturing:
- Before/after versions
- Modified instrumentation paths
- Attribute sources and their propagation methods
- Validation results and inspected traces
- Any unresolved blockers

Follow intermediate migration steps when upgrading across multiple major versions rather than jumping directly to the latest release.

## This project
`langfuse==2.60.10` is installed (decorator-based `langfuse.decorators` API). Latest on PyPI is `4.15.4` (OTel-based). Do not upgrade opportunistically — several sandbox notebooks (e.g. `sandbox/W4/Mon/00_langfuse.ipynb`) use the v2 `Langfuse().trace()/.generation()` client API and would need to be rewritten too. Treat an upgrade as its own reviewed task.
