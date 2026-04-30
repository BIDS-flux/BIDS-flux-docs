"""pyinfra inventory for the two Vagrant libvirt VMs.

Important pyinfra note: every top-level *non-underscore* name in this
module becomes a group. A bare tuple like ``("host", {...})`` at module
level is iterated by pyinfra — and since a string is iterable, pyinfra
ends up walking the hostname character by character. Keep this file
exporting only the proper group lists (``bidsflux_data`` and
``bidsflux_proc``); use ``_`` prefixes for any helper.

VM hostnames match the swarm placement constraints baked into the
upstream calgary docker-compose.stack.yml:

    data: itappcpipdp01.uc.ucalgary.ca
    proc: itappcpippp01.uc.ucalgary.ca
"""

import os

# Vagrant's insecure_private_key — used because Vagrantfile sets
# `config.ssh.insert_key = false`. Override via env var if your install
# has the global key elsewhere (older vagrant.d locations etc.).
_DEFAULT_KEY = os.path.expanduser(
    os.environ.get("BIDSFLUX_VAGRANT_KEY", "~/.vagrant.d/insecure_private_key")
)

bidsflux_data = [
    (
        "itappcpipdp01.uc.ucalgary.ca",
        {
            "ssh_hostname": "192.168.56.10",
            "ssh_user": "vagrant",
            "ssh_key": _DEFAULT_KEY,
            "bidsflux_role": "data",
            "bidsflux_swarm_advertise_addr": "192.168.56.10",
            "bidsflux_swarm_manager_addr": "192.168.56.10",
        },
    ),
]

bidsflux_proc = [
    (
        "itappcpippp01.uc.ucalgary.ca",
        {
            "ssh_hostname": "192.168.56.11",
            "ssh_user": "vagrant",
            "ssh_key": _DEFAULT_KEY,
            "bidsflux_role": "proc",
            "bidsflux_swarm_advertise_addr": "192.168.56.11",
            "bidsflux_swarm_manager_addr": "192.168.56.10",
        },
    ),
]
