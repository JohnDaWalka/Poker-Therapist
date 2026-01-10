# CodeQL Variables Configuration

This document describes the repository variables that can be configured for CodeQL workflows.

## Available Variables

Configure these variables in **Settings > Secrets and variables > Actions > Variables** in your GitHub repository.

### CODEQL_QUERIES
- **Type:** String
- **Default:** Empty (uses CodeQL default queries)
- **Description:** Comma-separated list of query suites to run
- **Example values:**
  - `security-extended`
  - `security-and-quality`
  - `security-extended,security-and-quality`
  - `+security-extended` (prefix with + to add to config file queries)
- **Usage:** Allows customization of which CodeQL query suites are executed during analysis

### CODEQL_CONFIG_FILE
- **Type:** String
- **Default:** Empty (no config file)
- **Description:** Path to a CodeQL configuration file in the repository
- **Example values:**
  - `.github/codeql/codeql-config.yml`
  - `config/codeql-config.yml`
- **Usage:** Allows using a custom CodeQL configuration file for advanced settings

### CODEQL_RUNNER
- **Type:** String
- **Default:** `ubuntu-latest` (or `macos-latest` for Swift)
- **Description:** GitHub Actions runner type to use for CodeQL analysis
- **Example values:**
  - `ubuntu-latest`
  - `ubuntu-22.04`
  - `windows-latest`
  - `macos-latest`
- **Usage:** Allows using different runner types (e.g., larger runners for better performance)

### CODEQL_TIMEOUT_MINUTES
- **Type:** Number
- **Default:** `360` (6 hours, or 120 for Swift)
- **Description:** Maximum time in minutes for the analysis job
- **Example values:**
  - `120` (2 hours)
  - `360` (6 hours)
  - `720` (12 hours)
- **Usage:** Adjusts timeout for repositories with different analysis times

## Workflows Using These Variables

- `.github/workflows/codeql.yml` - CodeQL Advanced workflow (triggers on main branch)
- `.github/workflows/ADVcodeql.yml` - Advanced CodeQL workflow (triggers on master branch)

## How to Configure

1. Go to your repository on GitHub
2. Navigate to **Settings**
3. Click on **Secrets and variables** in the left sidebar
4. Click on **Actions**
5. Click on the **Variables** tab
6. Click **New repository variable**
7. Add the variable name and value
8. Click **Add variable**

## Examples

### Example 1: Enable Security Extended Queries
Set `CODEQL_QUERIES` to:
```
security-extended
```

### Example 2: Use Custom Configuration File
Set `CODEQL_CONFIG_FILE` to:
```
.github/codeql/codeql-config.yml
```

Then create the config file at that path with your custom configuration.

### Example 3: Increase Timeout for Large Repository
Set `CODEQL_TIMEOUT_MINUTES` to:
```
720
```

### Example 4: Use Larger Runner
Set `CODEQL_RUNNER` to:
```
ubuntu-latest-8-cores
```
(Note: Larger runners may require GitHub Enterprise or additional configuration)

## Notes

- All variables have sensible defaults and are optional
- Empty string values will use the default behavior
- Variables are evaluated at workflow runtime
- Changes to variables take effect on the next workflow run
- No workflow file changes are needed to adjust these settings
