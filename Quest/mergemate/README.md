
# MergeMate: AI PR Review and Command Handling
[![MIT License](https://img.shields.io/github/license/Hardeepsingh980/mergemate)](https://github.com/Hardeepsingh980/mergemate/blob/master/LICENSE)
![coverage](https://img.shields.io/badge/coverage-80%25-yellowgreen)
![version](https://img.shields.io/badge/version-0.1.5-blue)
[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
![commits](https://img.shields.io/github/commit-activity/m/Hardeepsingh980/mergemate)

MergeMate is a sophisticated AI tool crafted to automate pull request reviews and manage command-based interactions within GitHub issues. It harnesses LLMWare, a comprehensive development framework featuring tools and finely-tuned, to deliver insightful, context-aware responses directly within your git workflow.

## Features

- **Advanced Integration with LLMWare**: Leverages LLMWare to analyze code and manage interactions, utilizing the latest AI technologies for natural language understanding and decision-making.
- **Automated PR Reviews**: Generates thorough reviews for pull requests automatically, including specific code suggestions and adherence to best practices.
- **Command Handling**: Interprets and responds to commands in PR comments such as `/help`, `/explain`, `/status`, and `/ask`, enriching the interaction within PR discussions.
- **Markdown Support**: Improves readability and interaction by utilizing Markdown for formatting responses, complete with custom headers and footers.
- **Easy Integration**: Seamlessly integrates as a GitHub action, facilitating straightforward incorporation into any project's CI/CD pipeline.
- **Future Expansion Plans**: Aimed at extending support to other repository management platforms like GitLab and Bitbucket, broadening the accessibility and utility of MergeMate across different development environments.

## Installation

Install MergeMate quickly and easily via pip at [mergemate](https://pypi.org/project/mergemate/):

```bash
pip install mergemate
```

Deploying MergeMate prepares your environment to leverage advanced AI capabilities, streamlining project interactions and reviews.

## GitHub Action Setup

Incorporate MergeMate into your GitHub workflows using this configuration:

### Workflow Definition

Create the workflow file at `.github/workflows/mergemate.yml`.
```yaml
name: Automated PR Review and Command Handling

on:
  pull_request:
    types: [opened, synchronize]
  issue_comment:
    types: [created]

permissions:
  issues: write
  pull-requests: write

jobs:
  review_pull_request:
    if: ${{ github.event_name == 'pull_request' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install mergemate
      - name: Review PR
        run: python -m mergemate.scripts.github.pr_review
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

  handle_comment:
    if: ${{ github.event_name == 'issue_comment' && github.event.issue.pull_request && startsWith(github.event.comment.body, '/') }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install mergemate
      - name: Handle Comment
        run: python -m mergemate.scripts.github.comment_handler
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```
`NOTE`: Do not forget to add `OPENAI_API_KEY` in Github Secrets.

## Documentation

Extensive documentation is included within the package, providing detailed setup instructions, configuration options, and command usage. This ensures that users ranging from beginners to experienced developers can effectively utilize and customize MergeMate.

## Contributing

We warmly welcome contributions to MergeMate. If you are interested in enhancing its functionality or adapting it for additional use cases, please fork the repository and submit your pull requests. As an open-source project, MergeMate thrives on community involvement and contributions, which are crucial for its continuous evolution and enhancement.

## Licensing

MergeMate is proudly released under the MIT license. This permissive licensing fosters widespread adoption and significant contributions from the community, supporting both personal and commercial use.

---

MergeMate epitomizes the next step in automating interactions within GitHub's ecosystem, propelled by the ongoing advancement of AI-driven development tools. Your feedback and contributions are invaluable to us as we aim to continually expand and enhance MergeMate's capabilities, catering to a growing range of development environments and communities.
