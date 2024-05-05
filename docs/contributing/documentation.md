---
layout: default
title: Documentation contributions
parent: Contributing
nav_order: 2
permalink: contributing/documentation
---
# Contributing documentation
One way to contribute to ``llmware`` is by contributing documentation.

There are **two ways** to contribute to the ``llmware`` documentation.
The first is via **docstrings in the code**, and the second is **the docs**, which is what you are *currently reading*.
In both areas, you can contribute in a lot of ways.
Here is a non exhaustive list of these ways for the docstrings which also apply to the docs.

1. Add documentation (e.g., adding a docstring to a function)
2. Update documentation (e.g., update a docstring that is not in sync with the code)
3. Simplify documentation (e.g., formulate a docstring more clearly)
4. Enhance documentation (e.g., add more examples to a docstring or fix typos)

## Docstrings
**Docstrings** document the code within the code, which allows programmers to easily have a look while they are programming.
For an exmaple, have a look at [this docstring](https://github.com/llmware-ai/llmware/blob/c9e12a7a150162986622738e127c37ac70f31cd6/llmware/agents.py#L27-L66) which documents the ``LLMfx`` class.

We follow the docstring style of **numpy**, for which you can find an example [here](https://github.com/numpy/numpydoc/blob/main/doc/example.py) and [here](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_numpy.html).
Please be sure to follow the conventions and go over your pull request before you submit it.


## Docs

{: .note}
> All commands are executed from the `docs` sub-directory.

Contributing to this documentation is extremely important as many users will refer to it.

If you plan to contribute to the docs, we recommend that you locally install `jekyll` so you can test your changes locally.
We also recommend, that you install `jekyll` into a a ruby enviroment so it does not interfere with any other installations you might have.

We recommend that you install `rbenv` and `rvm` to manage your ruby installation.
`rbenv` is a tool that mangages different ruby versions, similar to what `conda` does for `python`.
Please [install rbenv](https://github.com/rbenv/rbenv?tab=readme-ov-file#installation) following their instructions, and the same for [install rvm](https://github.com/rvm/rvm?tab=readme-ov-file#installing-rvm).
We recommend that you install a ruby version `>=3.0`.
After having installed an isolated ruby version, you have to install the dependencies to build the docs locally.
The `docs` directory has a `Gemfile` which specifies the dependencies.
You can hence simply navigate to it and use the `bundle install` command.

```bash
bundle install
```

You should now be able to build and serve the documentation locally.
To do this, simply to the following.
```bash
bundle exec jekyll server --livereload --verbose
```
In the browser of your choice, you can then go to `http://127.0.0.1:4000/` and you will be served the documentation, which is re-build and re-loaded after any change to the `docs`.
``jekyll`` will create a ``_site`` directory where it saves the created files, please **never commit any files from the \_site directory**!

## Open Issues
If you're interested in existing issues, you can

- Look for issues with the `good first issue` and `documentation` label as a good place to get started.
- Provide answers for questions in our [GitHub discussions](https://github.com/llmware-ai/llmware/discussions)
- Provide help for bug or enhancement issues. 
  - Ask questions, reproduce the issues, or provide solutions.
  - Pull a request to fix the issue.
