---
layout: default
title: Contributing
nav_order: 3
has_children: true
description: llmware contributions.
permalink: /contributing
---
# Contributing to llmware

{: .note}
> The contributions to `llmware` are governed by our [Code of Conduct](https://github.com/llmware-ai/llmware/blob/main/CODE_OF_CONDUCT.md).

{: .warning}
> Have you found a security issue? Then please jump to [Security Vulnerabilities](#security-vulnerabilities).

Contributions to `llmware` are welcome from everyone.
Our goal is to make the process simple, transparent, and straightforward.

On this page, we provide information for people interested in contributing to ``llmware``.
This includes information on contribution areas and the contribution process.


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
12. Post projects in which you use ``llmware`` in our Discord forum [made with llmware](https://discord.com/channels/1179245642770559067/1218567269471486012), ideially with a link to a public GitHub repository

We briefly describe some of the important modules of ``llmware`` next, so you can more easily navigate the code base.
For newcomers, we embed links to our [fast start series from YouTube](https://www.youtube.com/playlist?list=PL1-dn33KwsmD7SB9iSO6vx4ZLRAWea1DB).

### Core modules

#### Library
<iframe width="560" height="315" src="https://www.youtube.com/embed/2xDefZ4oBOM?si=IAHkxpQkFwnWyYTL" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
In ``llmware``, a *library* is a collection of documents.
A library is responsible for parsing, text chunking, and indexing.

#### Embeddings
<iframe width="560" height="315" src="https://www.youtube.com/embed/xQEk6ohvfV0?si=GAPle5gVdVPkYKWv" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
In ``llmware``, an *embedding* is a vector store and an embedding model.
An embedding is responsible for applying an embedding model to a library, storing the embeddings in a vector store, and providing access to the embeddings with natural language queries.

#### Prompts
<iframe width="560" height="315" src="https://www.youtube.com/embed/swiu4oBVfbA?si=rKbgO3USADCqICqr" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
In ``llmware``, a *prompt* is an input to model.

#### Model Catalog
In ``llmware``, a *model catalog* is a collection of models.


## Code contributions

### New or Enhancement to existing Features
You want to submit a code contribution that adds a new feature or enhances an existing one?
Then the best way to start is by opening a discussion in our [GitHub discussions](https://github.com/llmware-ai/llmware/discussions).
Please do this before you work on it, so you do not put effort into it just to realise after submission that
it will not be merged.

### Bugs
If you encounter a bug, you can

- File an issue about the bug.
- Provide a self-contained minimal example that reproduces the bug, which is extremely important.
- Provide possible solutions for the bug.
- Submit a pull a request to fix the bug.

We encourage you to read [How to create a Minimal, Reproducible Example](https://stackoverflow.com/help/minimal-reproducible-example) from the Stackoverflow helpcenter, and the tag description of [self-container](https://stackoverflow.com/tags/self-contained/info), also from Stackoverflow.

## Documentation contributions
There are two ways to contribute to the ``llmware`` documentation.
The first is via docstrings in the code, and the second is what you are currently reading.
In both areas, you can contribute in a lot of ways.
Here is a non exhaustive list of these ways.

1. Add documentation (e.g., adding a docstring to a function)
2. Update documentation (e.g., update a docstring that is not in sync with the code)
3. Simplify documentation (e.g., formulate a docstring more clearly)
4. Enhance documentation (e.g., add more examples to a docstring or fix typos)

## Open Issues
If you're interested in existing issues, you can

- Look for issues with the `good first issue` label as a good place to get started.
- Provide answers for questions in our [GitHub discussions](https://github.com/llmware-ai/llmware/discussions)
- Provide help for bug or enhancement issues. 
  - Ask questions, reproduce the issues, or provide solutions.
  - Pull a request to fix the issue.

 

## Security Vulnerabilities
**If you believe you've found a security vulnerability, then please _do not_ submit an issue ticket or pull request or otherwise publicly disclose the issue.**
Please follow the process at [Reporting a Vulnerability](https://github.com/llmware-ai/llmware/blob/main/Security.md)



## GitHub workflow

Generally, we follow the [``fork-and-pull``](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork) Git workflow.

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

## Do you have questions or just want to bounce around an idea?
Questions and discussions are welcome in our [GitHub discussions](https://github.com/llmware-ai/llmware/discussions)!
