How-to guides: Virtual machine setup and configuration
==============================================

The following section contains guides on how to setup and configure your virtual machine(s).

We require two virtual machines to fulfill distinct roles: a data storage server and a data processing server. These VMs must be interconnected with high-bandwidth connectivity. The data storage server should establish a connection to the Digital Alliance compute server for backup purposes. \\

The data processing server, will host a Gitlab self-hosted instance. This entails an internet connection, setting up SSH protocols and access, as well as connecting and managing Gitlab runners for effective software development and continuous integration. \\

([Installation requirements for Gitlab](https://docs.gitlab.com/ee/install/requirements.html))

([Resources for the Gitlab runners](https://docs.gitlab.com/ee/install/requirements.html#gitlab-runner))

The system requirements will depend on how many processes you plan to run. For reference, the SaaS runners on Linux are configured so that a single job runs in a single instance with:

    * 1 vCPU
    * 3.75 GB of RAM

Therefore a minimal setup processing 3-5 subjects at a time would require 5 vCPU and about 20 GB of RAM. This is just to run the gitlab runners. Storage space should accomodate the neuroimaging dataset. For example, the raw data for one of our studies takes up XGB space and we need additional space for the processed derivative images. 


⏩️ :doc:`Hardware requirements </guides/virtual-machine/configuration>`
    Description of the hardware and software requirements for running the virtual machine(s).


.. toctree::
   :maxdepth: 1
   :hidden:

   Virtual machine configuration </guides/virtual-machine/configuration>
