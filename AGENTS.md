# Career Intelligence Platform

## Project Purpose

Career Intelligence Platform is an AI-powered career guidance and skill intelligence
system.

The platform will build a structured representation of a student's skills,
projects, experience, and career goals, compare them with current job-role
requirements, identify skill gaps, and provide personalized recommendations
for becoming job-ready.

## Core Vision

The system should eventually support:

1. Student career profile
2. Resume analysis
3. Skill extraction
4. GitHub/project analysis
5. Job-market and job-description analysis
6. Skill-gap detection
7. Personalized learning roadmap
8. AI Career Twin
9. AI technical/HR interview preparation
10. Career-readiness analytics

## Development Principles

- Build incrementally.
- Do not implement the entire platform at once.
- Prefer small, testable vertical slices.
- Keep frontend, backend, database, and AI responsibilities separated.
- Write maintainable, production-quality code.
- Do not introduce unnecessary dependencies.
- Test features before considering them complete.
- Document important architectural decisions.
- Never expose API keys or secrets in source code.
- Use environment variables for secrets and configuration.

## AI Development Rules

AI agents are development assistants, not autonomous decision makers.

Before making major architectural changes:

1. Inspect the existing project.
2. Understand the current architecture.
3. Explain the proposed change.
4. Avoid modifying unrelated files.
5. Implement the smallest appropriate change.
6. Run relevant tests.
7. Report what was changed and verified.

Do not rewrite working parts of the project without a clear reason.

## Git Rules

- `main` must remain stable.
- Use feature branches for meaningful features.
- Make small, descriptive commits.
- Do not commit secrets, API keys, credentials, or local environment files.
- Pull/synchronize before starting work when working across machines.