# Documentation site

The learning material is published as a static GitHub Pages site at [TalkingTree Onboarding](https://talkingtree-ai.github.io/onboarding/). The [public source repository](https://github.com/talkingtree-ai/onboarding) contains the runnable toy projects; the website provides navigation, search, and readable guides. No application backend or company account is involved.

## Build locally

From the repository root, create a separate documentation environment:

```bash
python3 -m venv .venv-docs
.venv-docs/bin/python -m pip install -r requirements-docs.txt
python3 scripts/verify.py
.venv-docs/bin/python scripts/build_docs.py
```

The builder stages explicitly listed public Markdown pages and presentation assets in ignored `.site-src/`, then runs a strict MkDocs build into ignored `.site/`. It does not copy a checkout, a home directory, environment files, Terraform state, generated keys, or lab runtime data. Links to runnable source files point to GitHub. Add new pages to the explicit list and navigation only after reviewing them for public sharing.

To preview on your own machine, first check that the loopback port is free, then run:

```bash
.venv-docs/bin/python -m mkdocs serve --dev-addr 127.0.0.1:18765
```

Visit the local URL printed by MkDocs. Stop it with Ctrl+C. The preview serves documentation only; it does not start any learning lab. Changes to source Markdown require rerunning the builder's staging step (`scripts/build_docs.py --stage-only`).

## Deployment

GitHub Pages uses the GitHub Actions publishing source. The Pages workflow builds on pushes to `main`, checks pull requests without deploying them, and supports a manual run. The build receives read access to source. The deployment job receives only Pages write and OpenID token permissions needed by GitHub's official Pages action.

Only `.site/` is uploaded as the Pages artifact. Action versions are pinned to reviewed commit hashes. The site uses the default GitHub Pages hostname; it requires no company DNS record, custom domain, external hosting account, or saved deployment credential.

Before publishing a change, inspect the diff and any added files, run the verifier and strict build, and review relevant rendered pages. Use the [public-release review](PUBLIC-RELEASE.md) and [security guide](SECURITY.md) to preserve the content boundary. A successful documentation build does not validate lab runtime behavior.

## Presentation and dependencies

The site uses the Material for MkDocs theme with original CSS and an original favicon. Broad visual cues include warm paper, muted green, simple rounded surfaces, and readable system typography. No application components, company font files, screenshots, or private brand assets are distributed. Search runs in the browser over public documentation; there is no analytics integration or remote font dependency.

Third-party theme and icon notices are included with the site. Update the pinned documentation requirements and official Actions deliberately, review their support status, and rebuild before accepting an upgrade.

The pinned theme's maintainers have [announced end of life on May 5, 2027](https://squidfunk.github.io/mkdocs-material/). Critical fixes and security updates continue until then. Review the maintained successor before that date; the Markdown sources and small presentation overrides keep the site independent of application code.
