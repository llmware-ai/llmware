# Contributing to llmware
Contributions to `llmware` are welcome from everyone. Our goal is to make the process as simple, transparent, and straightforward as possible.  

The following are a set of guidelines for contributing to `llmware`.  As with everything in the project, the contributions to `llmware` are governed by our [Code of Conduct](https://github.com/llmware-ai/llmware/blob/main/CODE_OF_CONDUCT.md).

## How can you contribute?

### Contributing code

**If you encounter a bug, you can**

- File an issue about the bug.
- Provide clear and concrete ways/scripts to reproduce the bug.
- Provide possible solutions for the bug.
- Submit a pull a request to fix the bug.

**If you're interested in existing issues, you can**

- Look for issues with the `good first issue` label as a good place to get started.
- Provide answers for questions in our [github discussions](https://github.com/llmware-ai/llmware/discussions)
- Provide help for bug or enhancement issues. 
  - Ask questions, reproduce the issues, or provide solutions.
  - Pull a request to fix the issue.

**If you'd like to contribute a new feature or significantly change an existing one, you can**

- Start a discussion with us in our [github discussions](https://github.com/llmware-ai/llmware/discussions). 

**If you want to become a contributor of llmware, submit your pull requests!!** 

- For those just getting started, see [GitHub workflow](https://github.com/llmware-ai/llmware/blob/main/CONTRIBUTING.md#github-workflow) below.
- All submissions will be reviewed as quickly as possible.
- Once the review is complete, your PR will be merged into the Main branch.

**If you believe you've found a security vulnerability**

Please _do not_ submit an issue ticket or pull request or otherwise publicly disclose the issue.  Follow the process at [Reporting a Vulnerability](https://github.com/llmware-ai/llmware/blob/main/Security.md)

### GitHub workflow

Generally, we follow the "fork-and-pull" Git workflow.

1.  [Fork](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo) the repository on GitHub.
2.  Clone your fork to your local machine with `git clone git@github.com:<yourname>/llmware.git`.
3.  Create a branch with `git checkout -b my-topic-branch`.
4.  Run the test suite by navigating to the tests/ folder and running ```./run-tests.py -s``` to ensure there are no failures
5.  [Commit](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/committing-changes-to-a-pull-request-branch-created-from-a-fork) changes to your own branch, then push to GitHub with `git push origin my-topic-branch`.
6.  Submit a [pull request](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests) so that we can review your changes.

Remember to [synchronize your forked repository](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo#keep-your-fork-synced) _before_ submitting proposed changes upstream. If you have an existing local repository, please update it before you start, to minimize the chance of merge conflicts.

```shell
git remote add upstream git@github.com:llmware-ai/llmware.git
git fetch upstream
git checkout upstream/main -b my-topic-branch
```

### Do you have questions or just want to bounce around an idea?
Questions and discussions are welcome in our [github discussions](https://github.com/llmware-ai/llmware/discussions)!
