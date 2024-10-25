# Contributing to LLMware

We welcome contributions to `llmware` from everyone! Our goal is to make the contribution process simple, transparent, and straightforward. Your input is vital for the growth and improvement of our project.

All contributions are governed by our [Code of Conduct](https://github.com/llmware-ai/llmware/blob/main/CODE_OF_CONDUCT.md). Please take a moment to familiarize yourself with it.

## How Can You Contribute?

### Contributing Code

#### Encountering a Bug?

1. **File an Issue**: Clearly describe the bug.
2. **Reproduce the Bug**: Provide detailed steps or scripts to reproduce it.
3. **Suggest Solutions**: If possible, propose fixes or workarounds.
4. **Submit a Pull Request (PR)**: Once you have a fix ready, submit a PR.

#### Interested in Existing Issues?

- **Good First Issues**: Look for issues labeled `good first issue` to get started.
- **Engage in Discussions**: Provide answers in our [GitHub Discussions](https://github.com/llmware-ai/llmware/discussions).
- **Help with Issues**: Assist others by asking questions, reproducing issues, or suggesting solutions. Consider submitting a PR to address these issues.

#### Contributing New Features or Major Changes?

- **Start a Discussion**: Before implementing significant changes, initiate a discussion in our [GitHub Discussions](https://github.com/llmware-ai/llmware/discussions).

#### Becoming a Contributor

- **Submit Your PRs**: For those just getting started, please see the [GitHub Workflow](#github-workflow) section below.
- **Review Process**: All submissions will be reviewed promptly. After review, your PR will be merged into the main branch.

#### Reporting Security Vulnerabilities

If you believe you’ve found a security vulnerability:

- **Do Not Submit Publicly**: Please _do not_ file an issue or PR. Instead, follow the process outlined in [Reporting a Vulnerability](https://github.com/llmware-ai/llmware/blob/main/Security.md).

### GitHub Workflow

We follow the "fork-and-pull" workflow to streamline contributions:

1. **Fork the Repository**: Use [GitHub’s fork feature](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo) to create your own copy of `llmware`.
2. **Clone Your Fork**: Clone it to your local machine:
   ```bash
   git clone git@github.com:<yourname>/llmware.git
   ```
3. **Create a Branch**: Create a new branch for your topic:
   ```bash
   git checkout -b my-topic-branch
   ```
4. **Run Tests**: Navigate to the `tests/` folder and run:
   ```bash
   ./run-tests.py -s
   ```
   Ensure there are no failures.
5. **Commit Changes**: Make your changes and commit them to your branch.
6. **Push to GitHub**: Push your branch to your GitHub fork:
   ```bash
   git push origin my-topic-branch
   ```
7. **Submit a Pull Request**: Open a [pull request](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests) for review.

**Synchronize Your Fork**: Before submitting your PR, ensure your fork is up-to-date to minimize merge conflicts:
```bash
git remote add upstream git@github.com:llmware-ai/llmware.git
git fetch upstream
git checkout upstream/main -b my-topic-branch
```

### Questions or Ideas?

If you have questions or just want to brainstorm ideas, feel free to engage in our [GitHub Discussions](https://github.com/llmware-ai/llmware/discussions). We’re here to help!
