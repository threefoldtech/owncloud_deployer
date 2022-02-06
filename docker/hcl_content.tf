terraform {
  required_providers {
    grid = {
      source = "threefoldtech/grid"
    }
  }
}

provider "grid" {
}

variable "user" {
  type    = string
  default = "test"
}


resource "random_string" "random" {
  length  = 6
  special = false
  upper   = false
}

resource "random_password" "password" {
  length  = 8
  special = true
}
resource "grid_scheduler" "sched" {
  # a machine for the first server instance
  requests {
    name = "server_${var.user}"
    cru  = 2
    sru  = 151200
    mru  = 8096
  }

  requests {
    name   = "name_${var.user}"
    domain = true
  }
}

resource "grid_network" "ownnet" {
  nodes         = [grid_scheduler.sched.nodes["server_${var.user}"]]
  ip_range      = "10.1.0.0/16"
  name          = "network_${var.user}"
  description   = "server network"
  add_wg_access = true
}

resource "grid_deployment" "nodes" {
  node         = grid_scheduler.sched.nodes["server_${var.user}"]
  network_name = grid_network.ownnet.name
  ip_range     = lookup(grid_network.ownnet.nodes_ip_range, grid_scheduler.sched.nodes["server_${var.user}"], "")
  disks {
    name = "data_${var.user}"
    # will hold images, volumes etc. modify the size according to your needs
    size        = 70
    description = "volume holding docker data"
  }
  vms {
    name       = "owncloud_${var.user}"
    flist      = "https://hub.grid.tf/samehabouelsaad.3bot/abouelsaad-owncloud-10.9.1.flist"
    entrypoint = "/sbin/zinit init"
    cpu        = 4
    memory     = 4096
    mounts {
      disk_name   = "data_${var.user}"
      mount_point = "/var/lib/docker"
    }
    env_vars = {
      SSH_KEY                 = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC9MI7fh4xEOOEKL7PvLvXmSeRWesToj6E26bbDASvlZnyzlSKFLuYRpnVjkr8JcuWKZP6RQn8+2aRs6Owyx7Tx+9kmEh7WI5fol0JNDn1D0gjp4XtGnqnON7d0d5oFI+EjQQwgCZwvg0PnV/2DYoH4GJ6KPCclPz4a6eXrblCLA2CHTzghDgyj2x5B4vB3rtoI/GAYYNqxB7REngOG6hct8vdtSndeY1sxuRoBnophf7MPHklRQ6EG2GxQVzAOsBgGHWSJPsXQkxbs8am0C9uEDL+BJuSyFbc/fSRKptU1UmS18kdEjRgGNoQD7D+Maxh1EbmudYqKW92TVgdxXWTQv1b1+3dG5+9g+hIWkbKZCBcfMe4nA5H7qerLvoFWLl6dKhayt1xx5mv8XhXCpEC22/XHxhRBHBaWwSSI+QPOCvs4cdrn4sQU+EXsy7+T7FIXPeWiC2jhFd6j8WIHAv6/rRPsiwV1dobzZOrCxTOnrqPB+756t7ANxuktsVlAZaM= sameh@sameh-inspiron-3576",
      OWNCLOUD_DOMAIN         = data.grid_gateway_domain.domain.fqdn,
      OWNCLOUD_ADMIN_USERNAME = "admin",
      OWNCLOUD_ADMIN_PASSWORD = random_password.password.result,
      # configure smtp settings bellow only If you have an working smtp service and you know what you’re doing.
      # otherwise leave these settings empty. gives wrong smtp settings will cause issues/server errors in taiga.
      OWNCLOUD_MAIL_SMTP_SECURE   = "none", # tls, ssl, or none
      OWNCLOUD_MAIL_SMTP_HOST     = "",
      OWNCLOUD_MAIL_SMTP_NAME     = "",
      OWNCLOUD_MAIL_SMTP_PASSWORD = "",
      OWNCLOUD_MAIL_SMTP_PORT     = "",
      OWNCLOUD_MAIL_DOMAIN        = data.grid_gateway_domain.domain.fqdn,
      OWNCLOUD_MAIL_FROM_ADDRESS  = "owncloud",
    }
    planetary = true
  }
}

data "grid_gateway_domain" "domain" {
  node = grid_scheduler.sched.nodes["name_${var.user}"]
  name = "owncloud${var.user}"
}
resource "grid_name_proxy" "p1" {
  node            = grid_scheduler.sched.nodes["name_${var.user}"]
  name            = "owncloud${var.user}"
  backends        = [format("http://%s:80", grid_deployment.nodes.vms[0].ygg_ip)]
  tls_passthrough = false
}


output "nodes_ip" {
  value = grid_deployment.nodes.vms[0].ip
}


output "nodes_ygg_ip" {
  value = grid_deployment.nodes.vms[0].ygg_ip
}

output "admin_passwords" {
  sensitive = true
  value     = grid_deployment.nodes.vms[0].env_vars.OWNCLOUD_ADMIN_PASSWORD
}

output "fqdn" {
  value = data.grid_gateway_domain.domain.fqdn
}
