# Autonomous advent of code

- Each day during advent of code this repo solves the latest puzzle and submits the solution - all without human intervention
- All code in this repo was written by `sourcery-ai[bot]`
- Everything was set up by manually writing [five issues](https://github.com/JohnDaWalka/test-aoc/labels/inception) and asking `sourcery-ai[bot]` to implement them
- Since then everything runs fully autonomously

There are two main processes that work together to solve the puzzles:

- Four GitHub actions workflows download the puzzles, create issues for `sourcery-ai[bot]` to solve the puzzles, merge PRs, and submit solutions. All actions they perform are carried out by @SourceryAI which is a GitHub account not associated with a real person
- `sourcery-ai[bot]` solves the puzzles and opens pull requests with the solutions and answers

## How does it work?

Here are the steps:

1. Twelve hours after each puzzle is published a GitHub actions workflow [^1]:
   - Download the puzzle and input
   - ROT13 encode the puzzle [^2]
   - Commit both to the puzzle directory and push to `main`
   - This triggers step 2
2. A GitHub action workflow is triggered when puzzles are pushed to main:
   - Create a GitHub issue to solve the part
   - Post an issue comment with content `@sourcery-ai develop`
   - This triggers step 3
3. `sourcery-ai[bot]` listens to the comment:
   - Runs a script to ROT13 decode the puzzle
   - Posts a plan to the issue to solve the puzzle
   - Opens a pull request to implement the solution and write the solution
   - This triggers step 4
4. A GitHub action workflow is triggered when pull requests are opened
   - It merges pull requests only if the author is `sourcery-ai[bot]`
   - This triggers step 5
5. A GitHub action workflow is triggered when answers are pushed to `main`
   - It submits the answer to advent of code
   - It updates the results below
   - If the answer is correct and it was for part 1, it downloads the second part of the puzzle and commits it
   - This triggers step 2

How `sourcery-ai[bot]` works:

- When a member of a repo comments on an issue with `@sourcery-ai develop` it will post a plan to the issue, open a pull request with the solution, and request a review from the commenter
- If any review comments are left on its pull request it will address them and push new commits

## Results

Here are the puzzles attempted and whether they were successfully solved or not.

<!-- begin-results: 2024 -->
<!-- end-results: 2024 -->

## Try out Sourcery

`sourcery-ai[bot]` is an GitHub app with two main functions:

- Issue agent
  - Comment an issue with `@sourcery-ai plan` to post a comment with a planned implementation
  - Comment and issue with `@sourcery-ai develop` to open a pull request to resolve the issue 👈 the functionality on display in this repo
- Pull request agent
  - Automatically reviews pull requests
  - Generates pull request titles / bodies
  - Generates review guides with diagrams explaining the changes

The functionality in this repo (`@sourcery-ai develop`) is currently in alpha testing and will be generally available in the new year. As well as the functionality shown here it will:

- Run in GitHub / GitLab - cloud and self-hosted
- Integrate with issue trackers - Linear, Jira
- Resolve errors in production - Sentry, etc.

It will be most useful for handling routine maintenance and clearing your backlog by:

- Fixing bugs
- Implementing smaller features
- Automatically fixing production issues
- Writing documentation

If you like the sound of this, [join our waitlist](https://getsourcery.netlify.app/) and tell us anything else you want it to do.

## Triggering the `merge-repos` Workflow

To trigger the `merge-repos` workflow, you need to dispatch a repository event with the event type `merge-repos`. You can do this using the GitHub API or the `gh` CLI tool.

### Example using `gh` CLI

```sh
gh api repos/:owner/:repo/dispatches --field event_type=merge-repos --field client_payload='{"source_repo": "source-repo-name", "target_repo": "target-repo-name"}'
```

Replace `:owner` with the repository owner, `:repo` with the repository name, `source-repo-name` with the name of the source repository, and `target-repo-name` with the name of the target repository.

### Example using GitHub API

```sh
curl -X POST -H "Accept: application/vnd.github.v3+json" -H "Authorization: token YOUR_GITHUB_TOKEN" https://api.github.com/repos/:owner/:repo/dispatches -d '{"event_type":"merge-repos","client_payload":{"source_repo":"source-repo-name","target_repo":"target-repo-name"}}'
```

Replace `YOUR_GITHUB_TOKEN` with your GitHub token, `:owner` with the repository owner, `:repo` with the repository name, `source-repo-name` with the name of the source repository, and `target-repo-name` with the name of the target repository.

## Rotating `GH_TOKEN` Regularly

To rotate the `GH_TOKEN` regularly, follow these steps:

1. Generate a new GitHub token with the required permissions.
2. Update the GitHub Secrets in your repository settings with the new token.
3. Update any local environment variables or configuration files that use the `GH_TOKEN`.
4. Monitor the usage of the new token to ensure it is working correctly.
5. Revoke the old token to minimize the risk of unauthorized access.

## Monitoring the Usage of `GH_TOKEN`

To monitor the usage of the `GH_TOKEN`, follow these best practices:

1. Enable GitHub's security features, such as security alerts and vulnerability scanning, to detect any suspicious activity.
2. Regularly review the audit logs in your GitHub repository to track the usage of the `GH_TOKEN`.
3. Set up notifications for any unusual activity or changes in the repository.
4. Use third-party tools or services to monitor the usage of the `GH_TOKEN` and detect any potential security issues.
5. Periodically review and update the permissions assigned to the `GH_TOKEN` to ensure they are still necessary and appropriate.
curl -X POST -H "Accept: application/vnd.github.v3+json" -H "Authorization: token YOUR_GITHUB_TOKEN" https://api.github.com/repos/:owner/:repo/dispatches -d '{"event_type":"merge-repos","client_payload":{"source_repo":"source-repo-name","target_repo":"target-repo-name"}}'
