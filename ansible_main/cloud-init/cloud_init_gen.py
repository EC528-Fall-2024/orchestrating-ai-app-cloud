import os

current_dir = os.path.dirname(os.path.abspath(__file__))
requirements_path = os.path.join(current_dir, 'requirements.txt')

# CHANGE THIS SSH KEY
ssh_key = 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFbUbFFMOV4SKX3B5Jo/1tWXa6kNhRdLoGpQtTB7/uuG suijs@bu.edu'


def generate_cloud_init_yaml(requirements_path, output_path):
    # Read the requirements.txt file
    with open(requirements_path, 'r') as req_file:
        requirements = [line.strip() for line in req_file if line.strip() and not line.startswith('#')]

    # Create the cloud-init YAML content

    # cloud-init config file
    yaml_content = f"""#cloud-config
users:
  - name: user
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh_authorized_keys:
      - {ssh_key}

ssh_pwauth: false

package_update: true
package_upgrade: true

packages:
  - python3-pip
  - openssh-server
  - nmap
  - openssh-client
  - python3
  - python3-pip
  - ansible
  - git
  - curl
  - wget
  - vim

write_files:
  - path: /run/scripts/format_and_mount.sh
    permissions: '0755'
    content: |
      #!/bin/bash

      sudo mkfs.ext4 -m 0 -E lazy_itable_init=0,lazy_journal_init=0,discard /dev/sdb
      sudo mkdir -p /mnt/disks/client
      sudo mount -o discard,defaults /dev/sdb /mnt/disks/client
      sudo chmod a+w /mnt/disks/client
      sudo cp /etc/fstab /etc/fstab.backup
      UUID=$(sudo blkid -s UUID -o value /dev/sdb)
      echo "UUID=$UUID /mnt/disks/client ext4 discard,defaults,nofail 0 2" >> /etc/fstab
      echo "Formatted and mounted disk at /mnt/disks/client" >> /run/log.txt

      sudo mkfs.ext4 -m 0 -E lazy_itable_init=0,lazy_journal_init=0,discard /dev/sdc
      sudo mkdir -p /mnt/disks/src
      sudo mount -o discard,defaults /dev/sdc /mnt/disks/src
      sudo chmod a+w /mnt/disks/src
      sudo cp /etc/fstab /etc/fstab.backup
      UUID=$(sudo blkid -s UUID -o value /dev/sdc)
      echo "UUID=$UUID /mnt/disks/src ext4 discard,defaults,nofail 0 2" >> /etc/fstab
      echo "Formatted and mounted disk at /mnt/disks/src" >> /run/log.txt

runcmd:
  - sudo pip3 install {' '.join(requirements)}
  - [ sh, "/run/scripts/format_and_mount.sh" ]

"""
    # Write the cloud-init YAML file
    with open(output_path, 'w') as config_file:
        config_file.write(yaml_content)


output_path = os.path.join(current_dir, 'cloud-init-config.yaml')
generate_cloud_init_yaml(requirements_path, output_path)