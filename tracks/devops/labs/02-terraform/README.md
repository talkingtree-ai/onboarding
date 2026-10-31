# Lab 02 — Terraform without a cloud account

**Time:** about 45 minutes. **Cost:** no cloud resources or accounts. You need
Terraform CLI 1.6 or newer within the 1.x series, a terminal, and a writable local
directory. [Install Terraform](https://developer.hashicorp.com/terraform/install)
on your own machine if needed. Once installed, this exercise requires no remote
provider download.

This lab uses the built-in `terraform_data` resource to learn configuration,
validation, plans, state, in-place updates, replacement, and destruction. It
stores a synthetic service contract in local Terraform state. It **does not
create a VM, cluster, container, file-based config, or cloud infrastructure**.
No provisioners run commands and no cloud credentials are required.

## 1. Review and plan

Read the `.tf` files before running anything. Work from this directory on your
own machine; do not copy real infrastructure variables or state into the lab.

```bash
terraform version
terraform fmt -check
terraform init
terraform validate
cp terraform.tfvars.example terraform.tfvars
terraform plan -out=practice.tfplan
terraform show practice.tfplan
```

Expected: initialization succeeds using `terraform.io/builtin/terraform`,
validation succeeds, and the first plan proposes **1 to add, 0 to change,
0 to destroy**. The contract includes `sandbox-status-service`, one replica,
and the health paths used by the container lab. IDs and computed output values
may be unknown until apply. A saved plan is a snapshot: inspect it before apply,
and regenerate it after any input or configuration change.

If `fmt -check` fails after your own edits, run `terraform fmt` and review the
diff. A successful `validate` checks configuration consistency; it does not prove
that an intended change is safe or that an external system is healthy.

## 2. Apply and compare desired state

```bash
terraform apply practice.tfplan
terraform output
terraform state list
terraform plan
```

Expected: apply creates one local state object; state lists
`terraform_data.service_contract`; the next plan reports **No changes**.
Applying a saved plan does not ask for another interactive approval: reviewing
the plan is the decision point. No `-auto-approve` is needed for this lab.

The local `terraform.tfstate` file maps a resource address to its current data
and generated identifier. It is not the source configuration and should not be
edited by hand. Backups and binary plan files can contain sensitive values even
if terminal output is redacted; keep all of them out of Git. This lab has only
synthetic values, but the habit should carry over to real work.

## 3. Update versus replace

Edit `terraform.tfvars` so `replicas = 2`; keep `release = "v1"`.

```bash
terraform plan -out=practice.tfplan
terraform show practice.tfplan
terraform apply practice.tfplan
terraform output
```

Expected: **0 to add, 1 to change, 0 to destroy**. The contract changes while
the resource ID remains the same. This is a model update, not an actual scale-out.

Now change `release` to `"v2"` in the same file and repeat those commands.
Expected: the resource is replaced because `triggers_replace` changed:
**1 to add, 0 to change, 1 to destroy**. The ID changes. In a real provider,
replacement can interrupt a service; determine the impact before approval.

## 4. Validation and diagnosis

```bash
terraform plan -var='replicas=0'
terraform plan -var='environment=production'
```

Both should fail with the custom variable validation message and leave state
unchanged. CLI `-var` overrides the matching value in `terraform.tfvars` for
that command; it does not rewrite the file. Try a fractional replica count and
an invalid service name too.

Explain these scenarios in your own notes:

- A colleague deletes a local state file and assumes all infrastructure was
  destroyed. What can remain when using a real provider?
- Two people run apply against separate copies of state. Why is shared,
  access-controlled state and locking needed for a real team?
- A secret is marked `sensitive`. Why is that not encryption of state?
- A reviewed plan is old and configuration has changed. Why should a fresh plan
  be reviewed instead of blindly applying the old artifact?

Do not experiment with `state rm`, manual state edits, or locking bypass flags
on real infrastructure. This exercise intentionally uses a local backend so it
cannot teach remote locking, provider permissions, live drift detection, or
cloud failure modes. Those need a separately approved environment later.

## Cleanup

Review destruction before applying it, just as you reviewed creation:

```bash
terraform plan -destroy -out=destroy.tfplan
terraform show destroy.tfplan
terraform apply destroy.tfplan
terraform state list
```

Expected: **0 to add, 0 to change, 1 to destroy**, then an empty state list.
This removes only the lab's state object. Keep or delete the ignored local
`.terraform/`, `*.tfstate*`, `*.tfplan`, and `terraform.tfvars` files deliberately.
Never delete state to simulate destroying real resources.

## Read more

- [Built-in terraform_data lifecycle](https://developer.hashicorp.com/terraform/language/resources/terraform-data)
- [Input variables](https://developer.hashicorp.com/terraform/language/values/variables)
- [Plan behavior and saved plans](https://developer.hashicorp.com/terraform/cli/commands/plan)
- [Terraform state](https://developer.hashicorp.com/terraform/language/state)
- [Sensitive data and state](https://developer.hashicorp.com/terraform/language/manage-sensitive-data)
