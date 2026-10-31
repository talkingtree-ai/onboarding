output "service_contract" {
  description = "The model persisted by Terraform; this does not deploy anything."
  value       = terraform_data.service_contract.output
}

output "resource_id" {
  description = "A local lifecycle identifier; replacement creates a new value."
  value       = terraform_data.service_contract.id
}
