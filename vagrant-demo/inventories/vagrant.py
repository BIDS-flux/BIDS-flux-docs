"""pyinfra inventory for the two Vagrant libvirt VMs.

We side-step the whole "where is Vagrant's private key" question by
delegating to ``vagrant ssh-config``: ``make ssh-config`` writes
``.cache/ssh_config`` and pyinfra reads it via ``ssh_config_file``.
The hostnames here (``data``, ``proc``) match the Vagrantfile
``config.vm.define`` names so that ssh_config's ``Host data`` /
``Host proc`` blocks resolve.

Important pyinfra note: every top-level *non-underscore* name in this
module becomes a group. A bare tuple ``("host", {...})`` at module
level gets iterated by pyinfra — and since strings are iterable,
pyinfra ends up walking the hostname character by character. Keep this
file exporting only the proper group lists; underscore-prefix any
helper.
"""

from pathlib import Path

_SSH_CONFIG = str((Path(__file__).resolve().parent.parent / ".cache" / "ssh_config"))

bidsflux_data = [
    (
        "data",
        {
            "ssh_config_file": _SSH_CONFIG,
            "bidsflux_role": "data",
            "bidsflux_swarm_advertise_addr": "192.168.56.10",
            "bidsflux_swarm_manager_addr": "192.168.56.10",
        },
    ),
]

bidsflux_proc = [
    (
        "proc",
        {
            "ssh_config_file": _SSH_CONFIG,
            "bidsflux_role": "proc",
            "bidsflux_swarm_advertise_addr": "192.168.56.11",
            "bidsflux_swarm_manager_addr": "192.168.56.10",
        },
    ),
]
