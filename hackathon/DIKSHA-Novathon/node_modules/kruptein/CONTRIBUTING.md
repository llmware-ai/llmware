Contributing to kruptein
========================

Code Contributions
------------------
This document will guide you through the contribution process.

Step 1: Fork
------------
Fork the project [on GitHub](https://github.com/jas-/kruptein) and check out your
copy locally.

```text
$ git clone git@github.com:username/kruptein.git
$ cd node
$ git remote add upstream git://github.com/jas-/kruptein.git
```

Keep your local fork update to date using the `upstream` branch indicated in 
the above commands.

Choose branch
-------------
For developing new features and bug fixes, the `master` branch should be pulled
and built upon.

Step 2: Branch
--------------
Create a feature branch and start hacking:

```text
$ git checkout -b my-feature-branch -t origin/master
```

The branch name should be descriptive about the fixes/features it will
address.

Step 3: Commit
--------------
Make sure git knows your name and email address:

```text
$ git config --global user.name "J. Random User"
$ git config --global user.email "j.random.user@example.com"
```

Writing good commit logs is important.  A commit log should describe what
changed and why.  Follow these guidelines when writing one:

1.  The first line should be 50 characters or less and contain a short description of the change prefixed with the name of the changed subsystem (e.g. "net: add localAddress and localPort to Socket").
2.  Keep the second line blank.
3.  Wrap all other lines at 72 columns.

A good commit log can look something like this:

```text
subsystem: explaining the commit in one line

Body of commit message is a few lines of text, explaining things
in more detail, possibly giving some background about the issue
being fixed, etc. etc.

The body of the commit message can be several paragraphs, and
please do proper word-wrap and keep columns shorter than about
72 characters or so. That way `git log` will show things
nicely even when it is indented.
```

The header line should be meaningful; it is what other people see when they
run `git shortlog` or `git log --oneline`.

Check the output of `git log --oneline files_that_you_changed` to find out
what subsystem (or subsystems) your changes touch.

Step 4: Rebase
--------------
Use `git rebase` (not `git merge`) to sync your work from time to time (as
mentioned in 'Step 1').

```text
$ git fetch upstream
$ git rebase upstream/master
```

Step 5: Test
------------
Bug fixes and features **should come with tests**.  Add your tests in the
test directory.  Look at other tests to see how they should be
structured.

```text
$ npm test
```

Step 6: Push
------------
```text
$ git push origin my-feature-branch
```

Go to [https://github.com/yourusername/kruptein](https://github.com/yourusername/kruptein) and select your feature
branch. Click the 'Pull Request' button and fill out the form.

Pull requests are usually reviewed within a few days.  If there are comments
to address, apply your changes in a separate commit and push that to your
feature branch.  Post a comment in the pull request afterwards; GitHub does
not send out notifications when you add commits.
