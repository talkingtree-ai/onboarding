locals {
  service_contract = {
    name        = "${var.environment}-${var.service_name}"
    environment = var.environment
    replicas    = var.replicas
    health_path = "/healthz"
    ready_path  = "/readyz"
    port        = 8080
  }
}

# Built into Terraform. No external provider, API call, shell, or cloud resource.
resource "terraform_data" "service_contract" {
  input            = local.service_contract
  triggers_replace = var.release
}
