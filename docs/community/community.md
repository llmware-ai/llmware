---
layout: default
title: Community
nav_order: 6
has_children: true
description: community resources, getting help and sharing ideas
permalink: /community
---

# Community 

Welcome to the llmware community!   We are on a mission to pioneer the use of small language models as transformational tools 
in the enterprise to automate workflows and knowledge-based processes cost-effectively, securely and with high quality.  We believe that the 
secret is increasing out that small models can be extremely effective, but require a lot of attention to detail in building scalable data pipelines 
and fine-tuning both models and end-to-end workflows.  

We are open to both the most advanced machine learning researchers and the beginning developer just learning python.  

We publish a wide range of examples, use cases and tutorial videos, and are always looking for feedback, new ideas and contributors.  



{: .note}
> The contributions to `llmware` are governed by our [Code of Conduct](https://github.com/llmware-ai/llmware/blob/main/CODE_OF_CONDUCT.md).

{: .warning}
> Have you found a security issue? Then please jump to [Security Vulnerabilities](#security-vulnerabilities).

On this page, we provide information ``llmware`` contributions.
There are **two ways** on how you can contribute.
The first is by making **code contributions**, and the second by making contributions to the **documentation**.
Please look at our [contribution suggestions](#how-can-you-contribute) if you need inspiration, or take a look at [open issues](#open-issues).

Contributions to `llmware` are welcome from everyone.
Our goal is to make the process simple, transparent, and straightforward.
We are happy to receive suggestions on how the process can be improved.

## How can you contribute?

{: .note}
> If you have never contributed before look for issues with the tag [``good first issue``](https://github.com/llmware-ai/llmware/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22).

The most usual ways to contribute is to add new features, fix bugs, add tests, or add documentation.
You can visit the [issues](https://github.com/llmware-ai/llmware/issues) site of the project and search for tags such as
``bug``, ``enhancement``, ``documentation``, or ``test``.


Here is a non exhaustive list of contributions you can make.

1. Code refactoring
2. Add new text data bases 
3. Add new vector data bases 
4. Fix bugs
5. Add usage examples (see for example the issues [jupyter notebook - more examples and better support](https://github.com/llmware-ai/llmware/issues/508) and [google colab examples and start up scripts](https://github.com/llmware-ai/llmware/issues/507))
6. Add experimental features
7. Improve code quality
8. Improve documentation in the docs (what you are reading right now)
9. Improve documentation by adding or updating docstrings in modules, classes, methods, or functions (see for example [Add docstrings](https://github.com/llmware-ai/llmware/issues/219))
10. Improve test coverage
11. Answer questions in our [Discord channel](https://discord.gg/MhZn5Nc39h), especially in the [technical support forum](https://discord.com/channels/1179245642770559067/1218498778915672194)
12. Post projects in which you use ``llmware`` in our Discord forum [made with llmware](https://discord.com/channels/1179245642770559067/1218567269471486012), ideally with a link to a public GitHub repository

## Open Issues
If you're interested in existing issues, you can

- Look for issues, if you are a new to the project, look for issues with the `good first issue` label.
- Provide answers for questions in our [GitHub discussions](https://github.com/llmware-ai/llmware/discussions)
- Provide help for bug or enhancement issues. 
  - Ask questions, reproduce the issues, or provide solutions.
  - Pull a request to fix the issue.

 

## Security Vulnerabilities
**If you believe you've found a security vulnerability, then please _do not_ submit an issue ticket or pull request or otherwise publicly disclose the issue.**
Please follow the process at [Reporting a Vulnerability](https://github.com/llmware-ai/llmware/blob/main/Security.md)



## GitHub workflow

We follow the [``fork-and-pull``](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork) Git workflow.

1.  [Fork](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo) the repository on GitHub.
2. Clone your fork to your local machine with `git clone git@github.com:<yourname>/llmware.git`.
3. Create a branch with `git checkout -b my-topic-branch`.
4. Run the test suite by navigating to the tests/ folder and running ```./run-tests.py -s``` to ensure there are no failures
5. [Commit](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/committing-changes-to-a-pull-request-branch-created-from-a-fork) changes to your own branch, then push to GitHub with `git push origin my-topic-branch`.
6. Submit a [pull request](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests) so that we can review your changes.

Remember to [synchronize your forked repository](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo#keep-your-fork-synced) _before_ submitting proposed changes upstream. If you have an existing local repository, please update it before you start, to minimize the chance of merge conflicts.

```shell
git remote add upstream git@github.com:llmware-ai/llmware.git
git fetch upstream
git checkout upstream/main -b my-topic-branch
```

## Community
Questions and discussions are welcome in any shape or form.
Please fell free to join our community on our discord channel, on which we are active daily.
You are also welcome if you just want to post an idea!

- [Discord Channel](https://discord.gg/MhZn5Nc39h)
- [GitHub discussions](https://github.com/llmware-ai/llmware/discussions)
