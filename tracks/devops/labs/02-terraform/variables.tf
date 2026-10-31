variable "environment" {
  description = "Synthetic local environment name; this lab never targets a cloud."
  type        = string
  default     = "sandbox"

  validation {
    condition     = contains(["sandbox", "practice"], var.environment)
    error_message = "Choose sandbox or practice. This lab has no production environment."
  }
}

variable "service_name" {
  description = "A short lowercase DNS-style name for the modelled service."
  type        = string
  default     = "status-service"

  validation {
    condition     = length(var.service_name) <= 40 && can(regex("^[a-z][a-z0-9-]*[a-z0-9]$", var.service_name))
    error_message = "Use 2–40 lowercase letters, numbers, or hyphens; start with a letter and end with a letter or number."
  }
}

variable "replicas" {
  description = "A conceptual desired replica count. No containers are created."
  type        = number
  default     = 1

  validation {
    condition     = var.replicas >= 1 && var.replicas <= 3 && floor(var.replicas) == var.replicas
    error_message = "Choose a whole number from 1 to 3."
  }
}

variable "release" {
  description = "Changing this synthetic release models resource replacement."
  type        = string
  default     = "v1"

  validation {
    condition     = can(regex("^v[1-9][0-9]*$", var.release))
    error_message = "Use a synthetic release such as v1 or v2."
  }
}
