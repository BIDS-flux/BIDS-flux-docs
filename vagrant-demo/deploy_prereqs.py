"""Phase 1: install pre-requisites on every targeted host.

Run unlimited (both VMs in parallel) — operations are independent.
"""

from tasks import prereqs

prereqs.run()
