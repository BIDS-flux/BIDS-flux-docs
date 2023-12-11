.. _storescp:

StoreSCP Using Docker Setup
=============================

Calgary
+++++++

StoreSCP stands for ``"Store Service Class Provider"``. In the DICOM network communication model, a Service Class Provider (SCP) is an entity that provides services to a Service Class User (SCU). In this case, ``storescp acts as a receiver (server)`` in a network exchange where it accepts DICOM images or data sent over the network from a sender (client), which is typically a SCU like a PACS system, MRI or CT scanner, or another workstation.

The C-PIP pipeline will have a StoreSCP container listening for DICOMS sessions being pushed from the MRI. StoreSCP deployment is simple since it relies on docker and all the configuration/code is already in a GitHub repository.

#. First, make sure you have :ref:`docker and docker compose <dockerinstall>` installed.

#. Then clone the GitHub repository `https://gitlab.com/cal_cpip/calgary-servers.git <https://gitlab.com/cal_cpip/calgary-servers.git>`_ which will contain the requied configurations, dockerfiles, and docker compose files.

   .. note:: 

      Some modifications have been made to this repository in order to function using ``self-signed certificates``.

#. In the sequoia folder of the repository you will find the docker compose file ``docker-compose_storescp_dev.yml``.

#. Check the following configuration files inside the ``calgary-servers/sequoia/storescp/`` folder:

   * storescp/exect_on_study_received.py
   * storescp/start.sh
   * storescp/unf_**.py
   * storescp/_vars.env

#. Finally, all you need to do is run the following command to spin up this container.

.. code-block:: bash

   sudo docker compose -f calgary-servers/sequoia/docker-compose_storescp_dev.yml up

