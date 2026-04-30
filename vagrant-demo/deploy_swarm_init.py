"""Phase 2: initialise Docker Swarm and cpip_network on the manager.

Run with ``--limit itappcpipdp01.uc.ucalgary.ca``.
"""

from tasks import swarm

swarm.init_manager()
