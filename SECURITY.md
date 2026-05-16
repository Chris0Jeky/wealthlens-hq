# Security Policy

Last updated: 2026-05-16

## Reporting a Vulnerability

If you discover a security vulnerability in WealthLens HQ, please report it responsibly.

**Do not open a public GitHub issue for security vulnerabilities.**

Instead, email **jeky.tck@gmail.com** with:

- A description of the vulnerability
- Steps to reproduce
- Affected files or endpoints
- Severity assessment (if known)

You should receive an acknowledgement within 48 hours. We will work with you to understand the issue and coordinate a fix before any public disclosure.

## Scope

This policy covers:

- The WealthLens dashboard backend (FastAPI)
- The WealthLens dashboard frontend (Vue 3)
- Data pipelines in `automation/`
- GitHub Actions workflows
- Any secrets, API keys, or credentials

## What We Consider a Vulnerability

- Exposed secrets or API keys in code or git history
- SQL injection, XSS, or command injection
- Authentication or authorization bypass
- Insecure data handling or storage
- Dependency vulnerabilities with known exploits

## What Is Out of Scope

- Publicly available data from ONS, HMRC, WID, or BoE (this is open data)
- Issues in third-party dependencies without a proof of concept
- Social engineering attacks
- Denial of service (this is a small open-source project)

## Security Practices

- No API keys, passwords, or secrets are committed to the repository
- Environment variables are used for all sensitive configuration
- CORS origins are configurable via environment variables
- Dependencies are monitored via GitHub Dependabot
