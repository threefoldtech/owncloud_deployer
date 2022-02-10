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
  type = string
  default = "test"
}


resource "random_string" "random" {
  length           = 3
  special          = false
  upper            = false
}

resource "random_password" "password" {
  length           = 8
  special          = true
}

locals {
  password = "${random_password.password.result}"
  user     = "${var.user}"
  admin_name = "${var.user}"
  server_req = "oc_server_req"
  name_req = "oc_name_req"
  network_name = "oc_network_${var.user}_${random_string.random.result}"
  disk_name = "oc_disk"
  vm_name = "oc_vm"
  disk_size = 70 #GB
  rootfs_size = 2 #GB
  disk_mount_point = "/var/lib/docker"
  vm_cpu = 2
  vm_memory = 8096
  domain_name = "owncloud${var.user}${random_string.random.result}"
}
resource "grid_scheduler" "sched" {
  requests {
    name = local.server_req
    cru = local.vm_cpu
    sru = local.disk_size + local.rootfs_size
    mru = local.vm_memory
  }

  requests {
    name = local.name_req
    domain = true
  }
}

resource "grid_network" "ownnet" {
  nodes = [grid_scheduler.sched.nodes[local.server_req]]
  ip_range      = "10.1.0.0/16"
  name          = local.network_name
  description   = "server network"
  add_wg_access = true
}

resource "grid_deployment" "nodes" {
  node = grid_scheduler.sched.nodes[local.server_req]
  network_name = grid_network.ownnet.name
  ip_range     = lookup(grid_network.ownnet.nodes_ip_range, grid_scheduler.sched.nodes[local.server_req], "")
  disks {
    name        = local.disk_name
    # will hold images, volumes etc. modify the size according to your needs
    size        = local.disk_size
    description = "volume holding docker data"
  }
  vms {
    name        = "owncloud_${var.user}"
    flist       = "https://hub.grid.tf/samehabouelsaad.3bot/abouelsaad-owncloud-10.9.1.flist"
    entrypoint  = "/sbin/zinit init"
    cpu         = local.vm_cpu
    memory      = local.vm_memory
    rootfs_size  = local.rootfs_size * 1024
    mounts {
      disk_name   = local.disk_name
      mount_point = local.disk_mount_point
    }
    env_vars = {
      SSH_KEY     = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSkhNAIP22RH/sQx7alFS6vcqw1OAQUkC5MLv6t3L78YVTRv+/owSqIqCQHr2+zfb3aJijsxj9nqg54rVkEiCXOkT6IE/MGWSP6O/x/cCG8J7AT+OCCjo9IB/+V3CA8yREHi7ggqPv6hEfNoa1AMbnxqxT7a+5sJUVd14/Ib9OQKWBCXzosa0SjTY/RO1SrL93E80N+SJQRBCMemzlepn4wLDWvqs7DiruY+g9E2CskhDijt4iJCuNFZzAcTS3UeqxOG2QfLK2zc8M9/AycMcEyHn94Lml6V75Lk09iLB9QGTGsa4oAD3GFLce4VoKKZx0e6lwwnMNoAHKhBEMFmO5 root@waleed-ng",
      OWNCLOUD_DOMAIN = data.grid_gateway_domain.domain.fqdn,
      OWNCLOUD_ADMIN_USERNAME = local.admin_name,
      OWNCLOUD_ADMIN_PASSWORD = local.password,
      # configure smtp settings bellow only If you have an working smtp service and you know what you’re doing.
      # otherwise leave these settings empty. gives wrong smtp settings will cause issues/server errors in taiga.
      OWNCLOUD_MAIL_SMTP_SECURE = "none", # tls, ssl, or none
      OWNCLOUD_MAIL_SMTP_HOST = "",
      OWNCLOUD_MAIL_SMTP_NAME = "",
      OWNCLOUD_MAIL_SMTP_PASSWORD = "",
      OWNCLOUD_MAIL_SMTP_PORT = "",
      OWNCLOUD_MAIL_DOMAIN =  data.grid_gateway_domain.domain.fqdn,
      OWNCLOUD_MAIL_FROM_ADDRESS = "owncloud",
    }
    planetary = true
  }
}

data "grid_gateway_domain" "domain" {
  node = grid_scheduler.sched.nodes[local.name_req]
  name = local.domain_name
}
resource "grid_name_proxy" "p1" {
  node            = grid_scheduler.sched.nodes[local.name_req]
  name            = local.domain_name # this is not the domain name, it is resource name, no?
  backends = [format("http://%s:80", grid_deployment.nodes.vms[0].ygg_ip)]
  tls_passthrough = false
}


output "node_ip" {
  value = grid_deployment.nodes.vms[0].ip
}


output "node_ygg_ip" {
  value = grid_deployment.nodes.vms[0].ygg_ip
}

output "admin_name" {
  value = local.admin_name
}

output "admin_password" {
  sensitive = true
  value = local.password
}

output "fqdn" {
  value = data.grid_gateway_domain.domain.fqdn
}
