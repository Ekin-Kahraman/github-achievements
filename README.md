# GitHub achievements

A small, dependency-free checker for badges visible on a GitHub profile, and an
explicit repository for practicing coauthored pull requests. The initial six pull
requests build the catalog, parser, progress report, CLI, regression tests, and
documentation. Codex helped author these changes and is credited in their commits.

Requires Python 3.10 or later. It reads public profile HTML; it does not need a
GitHub token and cannot award badges or change account settings.

## Check a profile

```sh
python3 cli.py Ekin-Kahraman
python3 cli.py Ekin-Kahraman --json
```

Supply independently checked counts to calculate remaining milestones:

```sh
python3 cli.py Ekin-Kahraman --counts examples/counts.json
```

The example counts describe the account before this repository's six practice
pull requests on 29 October 2026. They are a snapshot, not live API statistics.
The `starstruck` count is the highest star count on one owned repository, not a
sum across repositories. Only merged PRs with actual coauthor attribution belong
in `pair-extraordinaire`; ordinary merged PRs belong in `pull-shark`.

## Offline checks

```sh
python3 -m unittest discover -s tests -v
python3 cli.py example --html tests/profile.html --json
```

The fixture exercises duplicated desktop/mobile badge images. Tests also cover
unknown image formats, malformed counts, missing files, and award delays.

## Interpreting results

- A visible badge is evidence of the displayed tier. A missing badge may be hidden,
  disabled, private, or not yet awarded; absence does not establish account history.
- Counts are optional inputs. The checker never infers an exact count from a badge.
- Meeting a reported threshold is not proof that GitHub has awarded it. Read the
  observed tier separately from the calculated remaining count.
- Galaxy Brain requires accepted answers to other people's questions. Self-created
  test questions are not a reliable qualifying route. Two researched answers posted
  from this account are [duplication QC](https://github.com/scverse/SnapATAC2/discussions/351#discussioncomment-19256936)
  and [pseudobulk peak counts](https://github.com/scverse/SnapATAC2/discussions/354#discussioncomment-19256937).
  Acceptance remains the question author's or maintainer's decision.
- Public Sponsor involves payment. This checker neither creates a sponsorship nor
  handles payment information.
- Historical event badges such as Arctic Code Vault Contributor and Mars 2020
  Contributor are outside this catalog of currently obtainable achievements.

Thresholds in `catalog.json` are community observations checked on 29 October 2026,
not a contractual GitHub API. The profile HTML can change. Unknown badge asset
formats are reported as unknown rather than silently assigned a tier.

Sources: [GitHub profile reference](https://docs.github.com/en/account-and-profile/reference/profile-reference#earning-achievements),
[community-maintained achievement catalog](https://github.com/Schweinepriester/github-profile-achievements),
and [GitHub's achievement visibility settings](https://docs.github.com/en/account-and-profile/how-tos/contribution-settings/manage-visibility-settings-for-private-contributions-and-achievements).
