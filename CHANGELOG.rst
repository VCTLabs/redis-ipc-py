Changelog
=========


0.1.0 (2024-10-24)
------------------

New
~~~
- Add sphinx doc build, update tool configs, apply cleanup. [Stephen L
  Arnold]

  * update coverage workflow to latest version

Changes
~~~~~~~
- Adjust .gitchangelog.rc and generate CHANGELOG.rst. [Stephen Arnold]

  * also update readme and dependabot config
- Bump coverage badge action to latest upstream. [Stephen L Arnold]
- Cleanup setup-python action versions in workflows. [Stephen L Arnold]
- Dev; commit normalized python files. [Stephen L Arnold]
- Update readme dev install commands and usage. [Stephen L Arnold]
- Change wording in delta message, fix typo in test file. [Stephen L
  Arnold]
- Save md report job output, merge into one delta comment. [Stephen L
  Arnold]
- Add some emphasis to important report items, trim line 1. [Stephen L
  Arnold]
- Last try, if v2 no worky, then we ditch codecov. [Stephen L Arnold]
- Fix monospace inline markup typos. [Stephen L Arnold]
- Add quick start section for tox, clean up tox cfg. [Stephen L Arnold]
- Add python packaging, trim readme, update tox cfgs. [Stephen L Arnold]

  * add python package build and pytest steps
  * keep nose for baseline tests (faster, better coverage)
  * use or-later GPL2 license identifier
- Add readme section for overlay/ppa package installs. [Stephen L
  Arnold]

Fixes
~~~~~
- Silence custom exception warnings, add docstring. [Stephen L Arnold]

  * use updated grep pipeline to grab the right coverage digits
- Remove error number from connection error test assert. [Stephen L
  Arnold]
- Restore not-quite-superfluous import (only used in Exception) [Stephen
  L Arnold]
- Chg: revert version update for codecov-action. [Stephen L Arnold]
- Update redis-ipc-py readme, authors, add python .git* files. [Stephen
  L Arnold]

Other
~~~~~
- Merge pull request #42 from VCTLabs/pkg-sprucing. [Steve Arnold]

  Improve versioning
- Merge pull request #41 from VCTLabs/workflow-cleanup. [Steve Arnold]

  action version bumps and cleanup
- Merge pull request #40 from
  VCTLabs/dependabot/github_actions/softprops/action-gh-release-2.
  [Steve Arnold]

  build(deps): bump softprops/action-gh-release from 1 to 2
- Merge pull request #39 from
  VCTLabs/dependabot/github_actions/emibcn/badge-action-2.0.3. [Steve
  Arnold]

  build(deps): bump emibcn/badge-action from 2.0.2 to 2.0.3
- Merge pull request #38 from
  VCTLabs/dependabot/github_actions/actions/download-artifact-4. [Steve
  Arnold]

  build(deps): bump actions/download-artifact from 3 to 4
- Merge pull request #36 from
  VCTLabs/dependabot/github_actions/actions/setup-python-5. [Steve
  Arnold]

  build(deps): bump actions/setup-python from 4 to 5
- Merge pull request #37 from
  VCTLabs/dependabot/github_actions/actions/upload-artifact-4. [Steve
  Arnold]

  build(deps): bump actions/upload-artifact from 3 to 4
- Merge pull request #24 from VCTLabs/precheck. [Steve Arnold]

  Pre-check and fall cleanup special.
- Update python versions (tox) and pre-commit hook versions. [Stephen L
  Arnold]
- Merge pull request #30 from
  VCTLabs/dependabot/github_actions/marocchino/sticky-pull-request-
  comment-2.5.0. [Steve Arnold]

  build(deps): bump marocchino/sticky-pull-request-comment from 2.2.0 to 2.5.0
- Merge pull request #31 from
  VCTLabs/dependabot/github_actions/ioggstream/bandit-report-
  artifacts-1.7.4. [Steve Arnold]

  build(deps): bump ioggstream/bandit-report-artifacts from 0.0.2 to 1.7.4
- Merge pull request #15 from
  VCTLabs/dependabot/github_actions/actions/upload-artifact-3. [Steve
  Arnold]

  build(deps): bump actions/upload-artifact from 2 to 3
- Merge pull request #16 from
  VCTLabs/dependabot/github_actions/actions/download-artifact-3. [Steve
  Arnold]

  build(deps): bump actions/download-artifact from 2 to 3
- Merge pull request #18 from
  VCTLabs/dependabot/github_actions/actions/setup-python-4.0.0. [Steve
  Arnold]

  build(deps): bump actions/setup-python from 3.1.1 to 4.0.0
- Merge pull request #10 from
  VCTLabs/dependabot/github_actions/marocchino/sticky-pull-request-
  comment-2.2.0. [Steve Arnold]

  build(deps): bump marocchino/sticky-pull-request-comment from 2.1.1 to 2.2.0
- Merge pull request #14 from
  VCTLabs/dependabot/github_actions/actions/setup-python-3.1.1. [Steve
  Arnold]

  build(deps): bump actions/setup-python from 2 to 3.1.1
- Merge pull request #12 from
  VCTLabs/dependabot/github_actions/actions/checkout-3. [Steve Arnold]

  build(deps): bump actions/checkout from 2 to 3
- Merge pull request #9 from VCTLabs/pretag. [Steve Arnold]

  pre-release check and workflow update
- Merge pull request #8 from VCTLabs/precommit-ci. [Steve Arnold]

  enable pre-commit.ci functionality
- Merge pull request #7 from
  VCTLabs/dependabot/github_actions/marocchino/sticky-pull-request-
  comment-2.1.1. [Steve Arnold]

  build(deps): bump marocchino/sticky-pull-request-comment from 2.1.0 to 2.1.1
- Merge pull request #6 from VCTLabs/branch-cov. [Steve Arnold]

  Branch coverage and not-so-simple tests
- Merge pull request #5 from VCTLabs/exc-tests. [S. Lockwood-Childs]

  improve tests
- Revert "chg: usr: save md report job output, merge into one delta
  comment" [Stephen L Arnold]

  This reverts commit d89b001b1ae3878e267e6c5f7693d5106637f7a0.
- Merge pull request #4 from VCTLabs/ci-test. [Steve Arnold]

  test codecov gh-action fix for missing reports
- Merge pull request #3 from VCTLabs/pytest. [Steve Arnold]

  Pytest and CI with redis-server
- Merge pull request #2 from VCTLabs/coverage. [Steve Arnold]

  document tox usage
- Merge pull request #10 from VCTLabs/process. [S. Lockwood-Childs]

  new: usr: add issue/PR templates and base .gitignore file
- Cpplint cleanup and workflow (#8) [Steve Arnold]

  * add doctest to pylint workflow, with minimal nose cfg
  * cpplint cleanup commit, mainly whitespace, if/else, and curly braces
  * cleanup indenting, revert if/else brace changes, add cfg file
  * fix constructor warnings in inc/json.hh, add cpplint worklow
- Merge pull request #5 from VCTLabs/flake8. [Steve Arnold]

  more CI quality checks using flake8/pep8, pylint, bandit, and codeql
- Silence "/tmp" path socket warning with a usage comment. [Stephen L
  Arnold]
- Add pylint workflow (check only, fail under 9.25) [Stephen L Arnold]
- More fun with badges. [Stephen L Arnold]
- Add bandit workflow (with github annotaions), disable flake8 ignores.
  [Stephen L Arnold]
- Update readme status, use status table. [Stephen L Arnold]
- Add python examples to readme (doctest-able even) [Stephen L Arnold]
- Pylint cleanup commit, update pep8speaks config. [Stephen L Arnold]
- Flake8 cleanup commit, add modified gitchangelog.rc and flake8 cfg.
  [Stephen L Arnold]
- Switch build status badge to (internal) github actions. [Stephen L
  Arnold]
- Test alternate github license provider 2. [Stephen L Arnold]
- Update license (filename) to GPL-2.0 generated by github. [Stephen L
  Arnold]
- Add status badges to readme file (#4) [Steve Arnold]

  * add status badges to readme file
  * fix license file parsing (on github) and add SPDX id to primary sources
- Merge branch 'py_client' [S. Lockwood-Childs]
- Some redis-py fixes in python module. [S. Lockwood-Childs]

  * redis.Connection is for tcp connections, not unix sockets,
    use redis.StrictRedis instead

  * blpop() returns None on timeout or (queue, value) if successful in
    popping value from queue
- Debug fix properly access globals. [nll]
- Deleted bogus comma. [nll]
- This is a version ready to be tested it is not checked out. [nll]
- Add server-side class to python module. [S. Lockwood-Childs]

  client-side class has one public method
    redis_ipc_send_and_receive()

  but server-side class has two
    redis_ipc_receive_command()
    redis_ipc_send_reply()

  because server has to do some processing between getting a command
  and sending back a reply
- C library encodes tid as integer, so match in python module. [S.
  Lockwood-Childs]
- Python module is really close to client-side functionality. [S.
  Lockwood-Childs]

  "client-side" means the code that generates commands and receives
  replies, as opposed to "server-side" code that waits for commands
  and services them.

  python now follows C-library conventions so it should (soon) interoperate
  with a server app written in C:

  * same mandatory fields for commands

    cmd["timestamp"]
    cmd["component"]
    cmd["thread"]
    cmd["tid"]
    cmd["results_queue"]
    cmd["command_id"]

  * same naming of queues for commands and their replies

    * command queue in format "queues.commands.$SERVER_COMPONENT"

    * reply queue in format "queues.results.$CLIENT_COMPONENT.$CLIENT_THREAD"

  TODO:

  Still need to fill in the actual redis connection bits,
  plus generate real timestamps for commands
- This version can do a few things it thinks it can send and receive
  messages, but it can not those functions are stubs the file can be
  imported into Python the code is written to raise exceptions, but none
  are handled yet no logging is performed. [nll]
- New version of skeleton and a tiny bit of meat. [nll]
- A little more client code for redis. [nll]
- A little more client code. [nll]
- Skeleton of redis client. [nll]
- Merge branch 'autotools' [S. Lockwood-Childs]
- Make new autotools baseline, move to subdirs, add Makefile.am and
  configure.ac, populate initial GPL files. [Steve Arnold]
- Still filling holes in README doc. [Stephanie Lockwood-Childs]
- Another README formatting tweakage. [Stephanie Lockwood-Childs]
- README formatting fixes. [Stephanie Lockwood-Childs]
- Putting documentation README. [Stephanie Lockwood-Childs]

  Still a work in progress, some sections missing...
