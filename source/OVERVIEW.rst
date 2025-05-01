BIDS-flux: A Scalable FAIR Data Management Platform Tailored for Multi-site Neuroimaging Research
=====
.. image:: img/Overview.png

Welcome to the documentation for the BIDS-flux neuroinformatics platform. This documentation provides an in-depth guide to the deployment, configuration, functionality, and usage of the BIDS-flux infraestructure.

About
-----

In the age of data-driven research, managing large-scale, high-quality datasets is essential but remains complex and resource-intensive. Scientific data collection, curation, and sharing often follow sequential phases, limiting real-time observability and operational improvements. Adhering to FAIR principles (Findability, Accessibility, Interoperability, and Reusability) is crucial, alongside ethical and security considerations, especially for human research data.

To address these challenges, we have developed a scalable FAIR data management platform tailored for neuroimaging research. Built on BIDS standards and Datalad, this platform integrates GitLab for workflow orchestration and MinIO for object storage. It enables continuous data ingestion from multiple sources (MRI, RedCap, Biopac), standardization (heudiconv, phys2bids), anonymization, quality control (MRIQC), and reproducible processing with BIDSApps.

Leveraging Git decentralization and federated dataset management, our platform allows multiple sites to contribute data independently while ensuring robust version control and long-term archival (e.g., DataVerse). Given the vulnerabilities of centralized digital infrastructures, this distributed approach enhances research resilience.

Beyond automation, our goal is to make data access and analysis intuitive for researchers. We plan to integrate BinderHub-powered environments to support interactive exploration and executable, reproducible preprints (e.g., NeuroLibre), ensuring full provenance tracking from data collection to publication.

While initially designed for neuroimaging, this modular infrastructure can be adapted to other scientific domains, provided compatible data standards and reproducible tools.

Principles
----------

The **BIDS-flux** infrastructure is built around **FAIR principles** to ensure that research data is well-organized, shareable, and reproducible.

Findable
^^^^^^^^

- All datasets are structured using the **BIDS standard**, ensuring consistent metadata and organization.
- Persistent identifiers (e.g., DOIs, dataset UUIDs) allow datasets to be easily referenced and discovered.
- Comprehensive metadata indexing enables efficient search and retrieval within repositories.

Accessible
^^^^^^^^^^

- Data is stored in a **GitLab-hosted Datalad repository**, enabling controlled access via standard authentication mechanisms.
- Object storage (**MinIO**) ensures scalable and secure access to raw and processed datasets.
- Researchers can retrieve datasets through command-line tools, APIs, or web interfaces while maintaining security and ethical compliance.

Interoperable
^^^^^^^^^^^^^

- Data follows the **BIDS standard**, ensuring compatibility with a wide range of neuroimaging and scientific tools.
- Standardized formats (e.g., **NIfTI for MRI, JSON for metadata**) enable seamless integration with automated workflows.
- The use of **Datalad and Git-annex** allows interoperability across different storage systems and computing environments.

Reusable
^^^^^^^^

- **Datalad provenance tracking** ensures every dataset version and modification is documented, enabling reproducibility and re-usability.
- Containerized processing workflows (**BIDSApps**) ensure consistency across different computational environments.

.. note::

   This documentation is a work in progress, and we are continuously updating and expanding it to provide you with the most comprehensive and helpful information. Thank you for your patience.

.. _hardware-requirements:

Hardware Requirements
---------------------

The **BIDS-flux** infrastructure is designed to scale and adapt flexibly to various hardware setups, typically including:

- **Two servers or virtual machines (VMs) per site**:
  
  - A dedicated **Data Server** for data ingestion, management, and storage.
  - A dedicated **Processing Server** optimized for data processing and analysis.
  - Accessible only to the local site, with no external access.

- **One centralized data repository** to aggregate data from multiple sites, enabling efficient collaboration, centralized data management, backups, and sharing of BIDS-compatible derivatives.
- Widely accessible to the scientific community, with controlled access to sensitive data.

Example Deployment: Canadian Paediatric Imaging Platform (`C-PIP <cpip.org>`_)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The **Canadian Paediatric Imaging Platform** (`C-PIP <cpip.org>`_) is a three-year longitudinal study involving approximately 750 participants. Each participant undergoes MRI scans (`MRI protocol <TODO.org>`_) annually, along with neuropsychological assessments. The resulting data and derivatives are managed according to the Brain Imaging Data Structure (BIDS) standard, with the dataset continuously expanding as additional BIDS-compatible derivatives become available.

Hardware specifications for C-PIP include:

**Compute resources per local server**:
 - CPUs: Intel® Xeon® Gold processors, totaling 32 cores per server (approximately 128 vCPUs available for virtualization).
 - RAM: 12 × 16 GB RAM modules, totaling 192 GB per server (384 GB across both servers).

**Storage resources per local server**:
 - 12 × 16TB NL-SAS HDDs (primary data storage).
 - 2 × 480 GB M.2 SSDs in RAID 1 (OS and VM boot).

**Centralized data repository**:
 - Provides centralized data pooling from all sites, BIDS-standard data storage, derivative management, comprehensive backup, and archival capabilities. The following resources were estimated for the duration of the project.
 .. image:: img/green-server-resources.png
  :width: 600px

This modular approach allows flexibility and scalability to efficiently handle large-scale imaging and associated data management tasks.

Software Stack
--------------

**BIDS-flux** is built to work on a **Linux** operating system with the following software stack:

Local Infrastructure
^^^^^^^^^^^^^^^^^^^^

The local infrastructure is designed to be deployed locally at each site =======

- **Docker** - Containerization and reproducibility https://docs.docker.com/
- **Git** - Version control for code and data https://git-scm.com/doc
- **Mercure** - Data ingestion and curation https://mercure-imaging.org/docs/
- **Datalad** - Version control for large-scale data https://docs.datalad.org/en/stable/index.html
- **GitLab** - Workflow orchestration and version control https://docs.gitlab.com/
- **MinIO** - Object storage for raw and processed data https://min.io/docs/minio/linux/index.html
- **Heudiconv** - DICOM to BIDS conversion https://heudiconv.readthedocs.io/en/latest/
- **NiPreps** - Neuroimaging PREProcessing toolS https://www.nipreps.org/ 
- **BIDSApps** - Containerized reproducible processing workflows
- **NeuroLibre** (comming soon) - Executable, reproducible preprints
- **DataVerse** (comming soon) - Long-term archival and publication
- **BinderHub** (comming soon) - Interactive exploration and analysis

Centralized Infrastructure
^^^^^^^^^^^^^^^^^^^^^^^^^^
- **Docker** - Containerization and reproducibility https://docs.docker.com/
- **Git** - Version control for code and data https://git-scm.com/doc
- **Gitea** - Workflow orchestration and version control https://docs.gitea.com/
- **MinIO** - Object storage for raw and processed data https://min.io/docs/minio/linux/index.html
- **DataCat** - Data pooling, sharing and quering platform https://datacat.readthedocs.io/en/latest/
- **DataVerse** - Long-term archival and publication
- **BinderHub** - Interactive exploration and analysis https://binderhub.readthedocs.io/en/latest/
- **JupyterHub** - Multi-user Jupyter notebook server https://jupyterhub.readthedocs.io/en/stable/
- **Keycloak** - Authentication and authorization https://www.keycloak.org/docs/latest/server_admin/index.html
- **Traefik** - Reverse proxy and load balancer https://doc.traefik.io/traefik/

If you have any questions or need assistance, feel free to [link to contact information or support].

.. image:: img/logo_chusj.jpeg
  :width: 200px
.. image:: img/logo_uoc.jpeg
  :width: 200px
.. image:: img/logo_sickkids.jpeg
  :width: 200px
