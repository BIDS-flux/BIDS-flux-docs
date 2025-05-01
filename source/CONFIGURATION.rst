MRI Configuration
-----------------

MRI scanner configuration of a DICOM node to push the data to the Mercure server / StoreSCP. You will need the hostname, IP, port, and AEtitle of the dicom listenner to configure the node in the scanner. Speak to your scanner vendor / field engineer to get the correct configuration instructions.

Network security
----------------
The **BIDS-flux** infrastructure is designed to be deployed in a secure network environment. The following security measures are recommended:
- **Firewall**: Ensure that the firewall is configured to allow only necessary ports and protocols for communication between servers and external access.

GitLab Authentication and Authorization
---------------------------------------

Gitlab can be configured to use a number of different authentication and authorization methods, see the official `GitLab documentation <https://docs.gitlab.com/administration/auth/>`_. OpenID Connect has been used in the past for some of the C-PIP sites, but this is not the default configuration. The default configuration uses GitLab's built-in authentication system. This means that admin will need to create a GitLab account in order to access the system.