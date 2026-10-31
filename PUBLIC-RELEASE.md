# Public release review

## Content review

A manual review on October 31, 2026 covered the 68 tracked files at revision
`afbc570`, including the curriculum, practice procedures, source code, scripts,
Terraform configuration, Kubernetes resources, and routing/DNS examples.

The review found no company application source, deployment configuration,
credentials, customer records, employee contact details, internal hostnames,
private network addresses, or local workspace paths in those files. The Python
service is a small synthetic teaching example. The procedures describe local
practice, and the technology explanations refer to public tools and vendor
documentation.

The material uses loopback addresses, Docker/Kubernetes lab service names, and
reserved testing names. Examples that mention secrets use fictional values or
commands that generate a learner's own disposable keys. No pre-generated key,
certificate, kubeconfig, Terraform state, or authenticated session is supplied.

Technology names and generic diagrams are educational context. They are not an
inventory, map, or operating procedure for company infrastructure. Learners need
no access to company domains, accounts, repositories, or data.

## History and secret scanning

An independent review covered both original commits and all 113 original Git
objects, including 77 file blobs and commit metadata. Gitleaks 8.30.1 was
verified against its upstream release checksum and run against the checkout,
history, and raw file blobs. Additional checks searched for credentials,
private keys, authenticated URLs, private infrastructure identifiers, and
accidental file copies from other source repositories.

No actual secret or proprietary implementation was found. The scanner matched
one ordinary vendor-list phrase as a generic API key because a product name
ended in "key". Manual review adjudicated that English text as a false positive;
its current wording was reordered without changing the technology list.
Historical copies of the harmless phrase remain. No credential rotation or
history removal was indicated.

## Website boundary

The website adds original CSS, a simple original favicon, an existing public
documentation theme, and public third-party notices. Broad colors and spacing
inspired the presentation; no application component, font file, screenshot,
logo, or private brand asset was copied.

The builder stages an explicit list of reviewed documentation and presentation
assets. Runtime code and lab configuration remain in the public source
repository; they are not bundled as executable website content. Generated
state, local credentials, dependency environments, and Git metadata are excluded
from the Pages artifact. Search indexes only the public pages. There is no
analytics integration, remote font request, or runtime company-service call.

A follow-up review covered the new build configuration, workflow, theme assets,
staged documentation, and generated website. Gitleaks reported zero findings in
the current source, staging directory, and rendered site. Additional private
identifier and credential checks were also clear. The workflow uses pinned
official Actions, read-only source checkout, deployment permissions scoped to
Pages, and a fixed static artifact; pull requests cannot deploy.

## Maintaining that boundary

Review additions and Git history before publishing another revision. Keep
generated lab state, personal notes, credentials, backups, and private company
material outside the tracked files. Ignore rules help prevent accidental adds;
they do not make a file safe to publish.

The repository's static verifier checks some credential patterns alongside links
and syntax. Its result is separate from manual content review and runtime lab
validation; no single check proves that all possible secrets are absent. The
[security guide](SECURITY.md) and [maintainer guide](CONTRIBUTING.md) explain
credential handling and review steps. See [validation](VALIDATION.md) for the
checks performed on the exercises.
