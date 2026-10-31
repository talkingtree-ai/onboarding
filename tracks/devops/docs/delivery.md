# Containers, infrastructure as code, and GitOps

The hands-on path is [containers](../labs/01-containers/), [Terraform](../labs/02-terraform/), [K3s](../labs/03-k3s/), then [Flux](../labs/04-flux/). This reading connects the tools and introduces extensions that the core labs do not install.

## Keep three kinds of state separate

| Kind | Example | Owner and recovery question |
| --- | --- | --- |
| Desired configuration | Image digest, replicas, environment name | Which version should run, and who can change it? |
| Infrastructure bookkeeping | Terraform state and dependency bindings | Which real resource belongs to which address in configuration? |
| Application data | User record, object bytes, queue item | What is the acceptable loss window, and how is it restored? |

Git can recover a Deployment manifest. It cannot recover lost database records. Terraform state is not an application backup. Protect state and saved plans as potentially sensitive artifacts even when terminal output is redacted; see [Terraform sensitive data](https://developer.hashicorp.com/terraform/language/manage-sensitive-data).

## Build once, identify precisely

A build reads source, locked dependencies, and a base image to produce an image. CI normally tests and scans it, records the source revision and image digest, and publishes it to a registry. An image tag can move; a digest identifies content. A tag policy and retained rollback digests make release recovery predictable.

In this track, local builds replace hosted CI and public registry pushes. A registry is conceptually separate from the runtime's local image store. K3s commonly runs containerd; an image built by host Docker does not automatically exist in that runtime. Follow the K3s lab's image path rather than assuming both share an image cache. See the [K3s packaged components](https://docs.k3s.io/).

Practice describing a release without an external service: source revision → build command → test result → image identifier → rendered manifest → observed healthy response. Record failures honestly; an unavailable scanner is not a passed scan.

## Terraform chooses changes; a reviewed plan narrows surprise

Read configuration before initializing providers, then inspect format/validation and the plan. Learn to recognize creation, in-place modification, replacement, and deletion. Apply the plan you inspected when using a saved plan workflow; changes made afterward require a new plan. Repeated apply should normally converge without changes. Resource drift and provider behavior can change that result.

Give Terraform an explicit scope. The local lab does not need an AWS account, HCP account, billing details, or a credential export. Avoid importing unrelated resources into its state. The official [Terraform workflow introduction](https://developer.hashicorp.com/terraform/intro) explains the write/plan/apply model.

## Kustomize renders; Flux continuously reconciles

Kustomize combines a base and overlays into Kubernetes objects. Its `kustomization.yaml` is a build instruction file. A Flux `Kustomization` is a custom Kubernetes resource that tells a controller what source/path to reconcile and how to report health. Their similar names do not make them interchangeable. Read [Kustomize object management](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/) and [Flux concepts](https://fluxcd.io/flux/concepts/).

The essential loop is: fetch source → render → apply → assess → repeat. When someone edits a managed live object, reconciliation may restore the declared value. Permanent recovery normally changes desired state. Suspending a controller can create a temporary diagnostic window, but it also stops convergence; document the suspension and verify resumption afterward.

The Flux lab uses a local source; it does not require bootstrapping a company or personal GitHub repository. A local source is a teaching substitute for a protected remote repository. Remote GitOps adds review rules, scoped deploy credentials, trusted source verification, and availability concerns.

## Extensions worth recognizing

| Extension | Responsibility | Question to ask during a failure | Official reading |
| --- | --- | --- | --- |
| Helm / Flux HelmRelease | Package templating and release lifecycle | Which chart version and values produced the resources, and did hooks or upgrades fail? | [Flux Helm releases](https://fluxcd.io/flux/components/helm/helmreleases/) |
| Flux image automation | Observe image versions, choose a policy, update desired state | Did the image exist, meet policy, and reach the desired-state source? | [Image automation](https://fluxcd.io/flux/guides/image-update/) |
| cert-manager | Issue and renew certificates through configured issuers | Is issuance blocked, is the issuer ready, and does the certificate cover the requested name? | [Certificate resource](https://cert-manager.io/docs/usage/certificate/) |
| Traefik | Match incoming requests and apply routing middleware | Did the host/path match, and is the selected backend reachable? | [Kubernetes routing](https://doc.traefik.io/traefik/reference/routing-configuration/kubernetes/crd/http/ingressroute/) |
| External Secrets Operator | Synchronize selected values from an external secret store | Can its identity read the selected key, and when did the last refresh succeed? | [Operator overview](https://external-secrets.io/latest/introduction/overview/) |
| SOPS with age | Encrypt selected configuration values for storage in Git | Which identity can decrypt, and can that identity be recovered safely? | [Flux SOPS guide](https://fluxcd.io/flux/guides/mozilla-sops/) |
| NetworkPolicy / ResourceQuota | Restrict network paths / bound namespace resource use | Is enforcement supported, and is a needed request denied? | [Kubernetes concepts](https://kubernetes.io/docs/concepts/) |

SOP means standard operating procedure. **SOPS** is a separate encryption tool. Base64 in a Kubernetes Secret is encoding, not encryption. Encrypting a file does not decide who may decrypt it; key custody and permissions still matter. SOPS/age and External Secrets are different approaches, and using both requires a clear owner for each generated Secret. See [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/).

Optional paper drill: design a toy release that changes an image, a secret, and a database schema. Identify which steps can be reversed, which need a data migration plan, and what observation would trigger recovery. Use the [change and rollback SOP](../sops/change-and-rollback.md).
