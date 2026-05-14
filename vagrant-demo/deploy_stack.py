"""Phase 4: stage upstream stack, deploy compose, run post-install.

Run with ``--limit itappcpipdp01.uc.ucalgary.ca``. Set ``GITLAB_TOKEN`` in
the environment to drive the post-install GitLab API steps; otherwise that
part is skipped with an instructional message.
"""

from tasks import stack, post_install

stack.deploy_on_manager()
post_install.run_on_manager()
