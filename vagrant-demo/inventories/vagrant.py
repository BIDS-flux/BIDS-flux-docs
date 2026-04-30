"""pyinfra inventory for the two Vagrant libvirt VMs.

VM hostnames match the swarm placement constraints baked into the
upstream calgary docker-compose.stack.yml:

    data: itappcpipdp01.uc.ucalgary.ca
    proc: itappcpippp01.uc.ucalgary.ca

Run pyinfra from ``vagrant-demo/`` so the relative ``.vagrant/`` paths resolve.
Switch to a different host (typhon, washoe-replacement, …) by copying this
file and replacing the ``ssh_*`` keys.
"""

from pathlib import Path

VAGRANT_DIR = Path(__file__).resolve().parent.parent

DATA_KEY = VAGRANT_DIR / ".vagrant" / "machines" / "data" / "libvirt" / "private_key"
PROC_KEY = VAGRANT_DIR / ".vagrant" / "machines" / "proc" / "libvirt" / "private_key"

data_server = (
    "itappcpipdp01.uc.ucalgary.ca",
    {
        "ssh_hostname": "192.168.56.10",
        "ssh_user": "vagrant",
        "ssh_key": str(DATA_KEY),
        "bidsflux_role": "data",
        "bidsflux_swarm_advertise_addr": "192.168.56.10",
        "bidsflux_swarm_manager_addr": "192.168.56.10",
    },
)

proc_server = (
    "itappcpippp01.uc.ucalgary.ca",
    {
        "ssh_hostname": "192.168.56.11",
        "ssh_user": "vagrant",
        "ssh_key": str(PROC_KEY),
        "bidsflux_role": "proc",
        "bidsflux_swarm_advertise_addr": "192.168.56.11",
        "bidsflux_swarm_manager_addr": "192.168.56.10",
    },
)

bidsflux_data = [data_server]
bidsflux_proc = [proc_server]
