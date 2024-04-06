---
layout: default
title: Code contributions
parent: Contributing
nav_order: 1
permalink: /contributing/code
---
# Contiributing code
One way to contribute to ``llmware`` is by contributing to the code base.

We briefly describe some of the important modules of ``llmware`` next, so you can more easily navigate the code base.
For newcomers, we embed links to our [fast start series from YouTube](https://www.youtube.com/playlist?list=PL1-dn33KwsmD7SB9iSO6vx4ZLRAWea1DB).

# Core modules

## Library
<iframe width="560" height="315" src="https://www.youtube.com/embed/2xDefZ4oBOM?si=IAHkxpQkFwnWyYTL" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
In ``llmware``, a *library* is a collection of documents.
A library is responsible for parsing, text chunking, and indexing.

## Embeddings
<iframe width="560" height="315" src="https://www.youtube.com/embed/xQEk6ohvfV0?si=GAPle5gVdVPkYKWv" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
In ``llmware``, an *embedding* is a vector store and an embedding model.
An embedding is responsible for applying an embedding model to a library, storing the embeddings in a vector store, and providing access to the embeddings with natural language queries.

## Prompts
<iframe width="560" height="315" src="https://www.youtube.com/embed/swiu4oBVfbA?si=rKbgO3USADCqICqr" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
In ``llmware``, a *prompt* is an input to model.

## Model Catalog
In ``llmware``, a *model catalog* is a collection of models.


## Categories of code contributions

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

# Do you have questions or just want to bounce around an idea?
Questions and discussions are welcome in our [GitHub discussions](https://github.com/llmware-ai/llmware/discussions)!
