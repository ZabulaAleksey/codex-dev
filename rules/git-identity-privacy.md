# Git identity privacy

## Policy

Personal mailbox addresses must not be written into Git commit metadata for repositories that may be pushed to a remote.

Canonical GitHub commit identity for this account:

```text
158517930+ZabulaAleksey@users.noreply.github.com
```

Before committing, the effective repository Git email must equal the canonical noreply address above. If a repository intentionally requires a different non-personal address, that exception must be explicitly documented in that repository and must not use a personal mailbox.

## Required local configuration

Set the default once per machine:

```powershell
git config --global user.email "158517930+ZabulaAleksey@users.noreply.github.com"
```

Verify:

```powershell
git config --global --get user.email
git config --show-origin --get-regexp '^user\.(name|email)$'
```

A repository-local `user.email` overrides the global value. Before publishing a repository, check:

```powershell
git config --get user.email
git log -n 5 --format='%h %an <%ae>'
```

## GitHub account setting

Enable both GitHub email privacy controls:

- Keep my email addresses private.
- Block command line pushes that expose my email.

These account settings are a second line of defense; local deterministic validation remains required.

## Historical commits

Changing `user.email` affects future commits only. Existing public commits that contain a personal email require a coordinated history rewrite if removal is desired. Treat that as a separate destructive migration: inventory affected refs, back up the repository, rewrite with `git-filter-repo`, verify all refs, force-push only after review, and coordinate cleanup of other clones/forks.

Do not rewrite shared history casually. Rewriting changes commit SHAs and can invalidate signatures and disrupt pull requests, branches, tags, forks, and existing clones.
