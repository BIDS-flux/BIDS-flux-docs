"""Phase 3: join the worker to the existing swarm.

Run with ``--limit itappcpippp01.uc.ucalgary.ca``. Requires
``vagrant-demo/.cache/swarm-token`` to be populated first
(``make swarm-fetch-join`` does this).
"""

from tasks import swarm

swarm.join_worker()
