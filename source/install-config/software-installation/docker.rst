.. _dockerinstall::

Docker Installation
=============================

.. .. figure:: ../../_static/infographics/Visio-C-PIP Deployment - Logical - v1.0.pdf
..    :name: fig-deployment-logical

.. .. figure:: ../../_static/infographics/cpip-diagram2.png
..    :width: 600px

   .. Logical Deployment Diagram


Calgary
+++++++

* Calgary is working with RedHat. Since Docker does not have direct packages of installation for RedHat8 with x86_64 arquitecture we can use the `CentOS installation packages. <https://docs.docker.com/engine/install/centos/>`_
* Make sure to also `install docker compose <https://docs.docker.com/compose/install/linux/>`_ since it will be used to install :ref:`StoreSCP <storescp>`