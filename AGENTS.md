# AGENTS.md

## Project Overview

`django-rest-framework-gis` adds GIS fields, serializers, filters, pagination, and schema helpers to Django REST Framework.

Core code lives in `rest_framework_gis/`:

- `fields.py`, `serializers.py`, `filters.py`, `filterset.py`, `pagination.py`, `schema.py`, and `tilenames.py` implement GIS API helpers.
- Tests live in `tests/`.

## Source of Truth

- Use `README.rst`, `CHANGES.rst`, and `performance_tests.rst` for setup, package usage, and performance context.
- Use `.github/workflows/ci.yml` and `tox.ini` for CI-tested dependencies, QA/test commands, env vars, and supported Python/Django/DRF versions.
- Use GitHub issue/PR templates when asked to open issues or PRs.

If instructions conflict, repository config and CI workflows win first, docs next, and this file is supplemental.

## Contributing Guidelines

- Before editing, inspect the relevant implementation, tests, documentation, and configuration. Follow existing repository patterns and do not invent behavior or requirements.
- Keep each contribution focused and change only the lines necessary for its goal. Do not include unrelated refactors, formatting churn, or generated and dependency-file changes unless explicitly required.
- Add or update focused tests for every behavior change. Use test-driven development when the scope is very clear, such as bug fixes or narrowly scoped changes. For new features, tests may be added after implementation, but confirm they fail when key feature code is removed. When a test failure does not clearly state the expected outcome that was not met, add an explicit assertion message.
- Run `openwisp-qa-format` after each change when available.
- Run the relevant targeted tests, builds, and documented QA checks, including `./run-qa-checks` when provided. Do not claim a change is complete when verification fails; report the failure or blocker.
- When requirements, intended behavior, or an unexpected failure are unclear, stop and seek clarification instead of making speculative changes.
- When starting work on a new issue, create a new branch from `master`. Use `issues/<issue-number>-<short-title>` for issue work; otherwise, use a short, descriptive branch name.
- Commit messages must be descriptive and use past tense. Past tense is a writing guideline that agents and contributors must follow; it is not checked automatically. For issue work, use an allowed prefix and a capitalized, past-tense subject ending with `#<issue-number>`, for example `[fix] Fixed perennial "modified" state #213`. Repeat the issue reference in the body with `Fixes`, `Closes`, `Resolves`, or `Related to` as appropriate. After creating a commit, use `openwisp-commit --check` to validate the current `HEAD`; it cannot validate a proposed message. Use `openwisp-commit --check --rev-range <range>` for an existing commit range, and `cz -n cz_openwisp info` to view allowed prefixes and message structure.
- Add an explanatory commit body only for substantial changes, new features, or non-obvious bug fixes. The releaser automatically publishes the subject of `[feature]`, `[change]`, `[change!]`, `[deps]`, and `[fix]` commits, including scoped variants, in the changelog. Write those subjects in clear, user-friendly language suitable for release notes.
- Send new commits in response to review feedback instead of amending existing commits.

## Development Rules

- Follow the DRY principle: do not duplicate information or code across files.
- Respect module boundaries and encapsulation. The module that owns a model, stored state, lifecycle, or domain invariant must expose the cohesive public operation that reads or changes it. Integrations must use that operation, not write its fields, coordinate multi-step changes to its internal state, or depend on its storage representation. Prefer behavior-oriented public APIs over setters for internal flags. When an integration needs a missing capability, add it to the owning module with invariant tests, then call it from the integration.
- Preserve public APIs, serializer output formats, GeoJSON compatibility, filter semantics, and pagination behavior unless explicitly required.
- Mark user-facing strings for translation with Django i18n helpers in Django code.
- Place imports at the top of the file. Only defer imports when necessary (e.g., Django model imports inside functions or methods where the app registry is not yet ready).
- Avoid unnecessary blank lines inside function and method bodies.
- Prefer short, precise names that rely on their nearest meaningful scope. Do not repeat a feature, domain object, or namespace already named by the containing module, class, or function. For example, prefer `EstimatedLocation.refresh()` over `EstimatedLocation.refresh_estimated_location()`. Repeat that context only when the name is used outside that scope or is needed to distinguish genuinely different concepts. When a concise name cannot express a necessary distinction, use a concise docstring to describe it rather than encoding it in an excessively long name.
- Before adding a comment or docstring, ask whether it conveys information a reader cannot reasonably infer from clear code, names, and surrounding scope. Add a concise comment when it explains a non-obvious reason, constraint, compatibility or security requirement, side effect, or unavoidable complexity. In opaque syntax or domain-specific code, especially shell scripts, a comment may also explain what the code does. Do not add comments that merely restate adjacent code one-to-one.
- Update docs when behavior, settings, public APIs, setup steps, or supported versions change, including when a documented feature's behavior changes or a new user-facing feature is added.

## Testing and QA

- When separate tests cover different cases of the same feature, share almost identical setup, and primarily vary in input or expected outcome, group them in one test method with `subTest`. Keep each subtest's setup explicit and independent, and retain separate test methods when cases exercise genuinely distinct behavior. Leave one blank line before each with `self.subTest(...)` statement only when a test method contains multiple such statements. Do not add a blank line for a single `subTest` statement inside a loop.
- Use targeted tests while iterating, then run the documented full test command before considering the change complete.
- For focused tests, call `./tests/manage.py test <pythonpath>` directly. Use `./runtests` only for the full suite because it runs multiple coverage and integration configurations and is not a focused-test runner.
- Prefer in-process tests so coverage tools can measure changed code.
- Keep helpers and classes used by only one test method inside that method. Promote them to class or module scope only when genuinely reused.
- When changing GIS fields or serializers, add tests for GeoJSON input and output, validation failures, and affected geometry edge cases, including coordinate or SRID transformations. When changing filters, pagination, schema helpers, or tile names, test the changed public behavior and invalid or boundary input.
- Keep tests quiet on success. When code under test writes to stdout or stderr, use `capture_stdout`, `capture_stderr`, or `capture_any_output` from `openwisp_utils.tests` and assert the expected output. Do not leave unasserted output, logs, or warnings in test runs.

## Django Rules

- Build internal URLs with named URL patterns and `reverse()` or `reverse_lazy()`, including in tests. Use the appropriate namespace and URL arguments.
- In the main behavior test for non-trivial, frequently called views, include `assertNumQueries()` with representative data to enforce an intentional query budget and catch N+1 queries. Use `AssertNumQueriesSubTestMixin` from `openwisp_utils.tests` where available: it records the query-count check as a subtest, so subsequent assertions in the method still run. Change the expected count only when the extra queries are necessary and understood.
- Before defining a new class, view, URL, REST endpoint, or test layout, inspect analogous implementations in related OpenWISP modules. Match their established names, URL names, API shape, and test organization unless the behavior requires a difference.
- Treat email addresses as case-insensitive when identifying, deduplicating, importing, migrating, or searching users by email. Use `email__iexact` for direct and `Q()` ORM lookups. Keep username matching case-sensitive unless explicitly required. Normalize email records this module owns to lowercase, and cover casing-only inputs, including legacy mixed-case records when relevant.

## Security and API Rules

- Watch for invalid geometry handling, excessive query costs, unsafe user-controlled filters, and compatibility regressions across Django, DRF, GEOS, and GDAL.
- Preserve validation around GeoJSON, bounding boxes, distance filters, tile names, pagination links, and schema output.

## Troubleshooting

- If documentation and CI commands differ, use CI for verification and report the exact documentation path, CI workflow path, and differing commands. Do not change the documentation until the user explicitly chooses one of these actions: update the named documentation file in the current change because the divergence was caused by that change, or leave it unchanged for a separate follow-up. Never decide that scope distinction independently.
