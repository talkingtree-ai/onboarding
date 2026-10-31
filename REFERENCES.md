# Public documentation

These are upstream learning resources, not links to company systems. The guides were checked while preparing the material in October 2026; vendors can change commands, support matrices, releases, and account terms. Follow the lab's named versions and recheck upstream guidance when updating them.

## Containers and Linux

- [Docker Engine installation](https://docs.docker.com/engine/install/)
- [Docker Compose plugin installation](https://docs.docker.com/compose/install/linux/)
- [Docker Compose specification](https://docs.docker.com/reference/compose-file/)
- [Docker build guidance](https://docs.docker.com/build/building/best-practices/)
- [Docker storage volumes](https://docs.docker.com/engine/storage/volumes/)
- [Docker Desktop licensing](https://docs.docker.com/subscription/desktop-license/)
- [Python HTTP server reference](https://docs.python.org/3/library/http.server.html)
- [Ubuntu Server documentation](https://documentation.ubuntu.com/server/)
- [systemd resource controls](https://www.freedesktop.org/software/systemd/man/latest/systemd.resource-control.html)

## Infrastructure as code

- [Terraform installation](https://developer.hashicorp.com/terraform/install)
- [Terraform language](https://developer.hashicorp.com/terraform/language)
- [Built-in terraform_data resource](https://developer.hashicorp.com/terraform/language/resources/terraform-data)
- [Terraform plan](https://developer.hashicorp.com/terraform/cli/commands/plan)
- [Terraform state](https://developer.hashicorp.com/terraform/language/state)
- [Terraform sensitive data](https://developer.hashicorp.com/terraform/language/manage-sensitive-data)

## Kubernetes and K3s

- [K3s quick start](https://docs.k3s.io/quick-start), [requirements](https://docs.k3s.io/installation/requirements), and [architecture](https://docs.k3s.io/architecture)
- [k3d overview and installation](https://k3d.io/v5.9.0/), [registries](https://k3d.io/v5.9.0/usage/registries/), and [kubeconfig handling](https://k3d.io/v5.9.0/usage/kubeconfig/)
- [k3d v5.9.0 release](https://github.com/k3d-io/k3d/releases/tag/v5.9.0)
- [K3s 1.35 releases](https://docs.k3s.io/release-notes/v1.35.X)
- [Install kubectl](https://kubernetes.io/docs/tasks/tools/), [version skew](https://kubernetes.io/releases/version-skew-policy/)
- [Kubernetes concepts](https://kubernetes.io/docs/concepts/)
- [Kustomize](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/)
- [Probes](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/), [resources](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/), [Pod security](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Helm](https://helm.sh/docs/), [Traefik Kubernetes routing](https://doc.traefik.io/traefik/reference/install-configuration/providers/kubernetes/kubernetes-ingress/), [cert-manager](https://cert-manager.io/docs/)

## Reverse proxy and local DNS

- [Traefik file provider](https://doc.traefik.io/traefik/reference/install-configuration/providers/others/file/), [HTTP router rules](https://doc.traefik.io/traefik/reference/routing-configuration/http/routing/rules-and-priority/), [TLS certificates](https://doc.traefik.io/traefik/reference/routing-configuration/http/tls/tls-certificates/)
- [CoreDNS file-backed zones](https://coredns.io/plugins/file/)
- [DNS concepts: RFC 1034](https://www.rfc-editor.org/rfc/rfc1034), [zone-file format: RFC 1035](https://www.rfc-editor.org/rfc/rfc1035)
- [IANA special-use names](https://www.iana.org/assignments/special-use-domain-names), [reserved testing domains: RFC 2606](https://www.rfc-editor.org/rfc/rfc2606)
- [curl hostname overrides and certificate verification](https://curl.se/docs/manpage.html)

## GitOps and secrets

- [Flux concepts](https://fluxcd.io/flux/concepts/), [installation](https://fluxcd.io/flux/installation/), and [v2.9.4 release](https://github.com/fluxcd/flux2/releases/tag/v2.9.4)
- [Flux OCI artifacts](https://fluxcd.io/flux/cheatsheets/oci-artifacts/)
- [OCIRepository](https://fluxcd.io/flux/components/source/ocirepositories/), [Flux Kustomization](https://fluxcd.io/flux/components/kustomize/kustomizations/)
- [Flux Helm releases](https://fluxcd.io/flux/guides/helmreleases/), [image automation](https://fluxcd.io/flux/guides/image-update/), [SOPS integration](https://fluxcd.io/flux/guides/mozilla-sops/)
- [SOPS documentation](https://getsops.io/docs/), [age](https://github.com/FiloSottile/age)
- [External Secrets Operator](https://external-secrets.io/latest/)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)

## Identity, applications, and data

- [Auth0 documentation](https://auth0.com/docs), [pricing and free-plan terms](https://auth0.com/pricing)
- [OAuth authorization code with PKCE](https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow-with-pkce)
- [Next.js documentation](https://nextjs.org/docs), [FastAPI](https://fastapi.tiangolo.com/), [Flask](https://flask.palletsprojects.com/)
- [MongoDB documentation](https://www.mongodb.com/docs/), [Qdrant](https://qdrant.tech/documentation/), [Valkey](https://valkey.io/docs/), [SeaweedFS](https://github.com/seaweedfs/seaweedfs/wiki)

## Cloud concepts — reading only

The core labs never provision these services. Use the architecture guide to connect their roles to local substitutes; no AWS or Cloudflare account is needed.

- [AWS VPC](https://docs.aws.amazon.com/vpc/), [EC2](https://docs.aws.amazon.com/ec2/), [IAM](https://docs.aws.amazon.com/iam/), [ECR](https://docs.aws.amazon.com/ecr/)
- [S3](https://docs.aws.amazon.com/s3/), [DocumentDB](https://docs.aws.amazon.com/documentdb/), [ElastiCache](https://docs.aws.amazon.com/elasticache/)
- [CloudFront](https://docs.aws.amazon.com/cloudfront/), [Route 53](https://docs.aws.amazon.com/route53/), [ACM](https://docs.aws.amazon.com/acm/), [WAF](https://docs.aws.amazon.com/waf/)
- [KMS](https://docs.aws.amazon.com/kms/), [Secrets Manager](https://docs.aws.amazon.com/secretsmanager/), [AWS Backup](https://docs.aws.amazon.com/aws-backup/), [CloudWatch](https://docs.aws.amazon.com/cloudwatch/)
- [Cloudflare documentation](https://developers.cloudflare.com/)
