Usage Notes
-----------

After completing the :ref:`software deployment <hardware-requirements>` you should have at least 2 servers/VMs (it could tecnically be just 1) a **data server** and a **processing server**. This section is intended to provide a guide on how to use the infraestructure for it's intended purpose of neuroimaging data management and analysis acceleration.

Data Flow
^^^^^^^^^
This section describes an overview of the data flow from the moment a study participant is scanned to the moment the data is available for a release. 

.. _diagram::

.. mermaid::

   %%{ init:
           { "theme": "forest",
           "sequence": { "showSequenceNumbers": true } }
        }%%
   sequenceDiagram
   box Gray Dicom Acquisition
   participant MRI Scanner
   participant Mercure as Mercure<br/>Storescp
   end
   box Orange Local Gitlab
   participant DicomStudy
   participant BIDS
   participant MRIQC
   participant BIDS-derivatives
   end

   box Green Centralized Gitlab
   participant BIDS-fed
   participant BIDS-derivatives-fed
   end

   MRI Scanner ->> Mercure: send dicom
   Mercure ->> DicomStudy: init
   Mercure ->> BIDS: init

   loop Every new session
   Mercure ->> DicomStudy: add session as submodule
   DicomStudy ->> BIDS: trigger heudiconv
   BIDS ->>+BIDS: open MR
   activate BIDS
   BIDS ->> BIDS: test: bids-validator
   BIDS ->> BIDS: test: protocol compliance
   BIDS ->> BIDS: run: defacing
   BIDS ->> MRIQC: trigger: mriqc
   MRIQC ->> BIDS: include/add link to reports in MR
   create actor A as Dataset Admin
   BIDS ->>-A: Notify
   A ->> BIDS: Review + (Fix) + merge MR
   loop For each configured preproc pipelines
   BIDS ->>+BIDS-derivatives: trigger preproc newly merged session
   BIDS-derivatives ->> BIDS-derivatives: open MR (preproc reports as artifacts)
   BIDS-derivatives ->>-A: Notify
   A ->> BIDS-derivatives: Review reports + merge MR
   end
   end
   A ->> BIDS: Create release
   BIDS ->> BIDS-fed: Push git + "green" data (minio)
   A ->> BIDS-derivatives: Create release
   BIDS-derivatives ->> BIDS-derivatives-fed: Push git + "green" data (minio)

As we can see in the diagram the data flow is divided into 3 parts.

1) Data acquisition in DICOM format which will be pushed to the Mercure instance. The data is then automatically pushed to the local GitLab instance.

2) Local GitLab git flow illustrates the workflow, starting from the push of a new DICOM session to executing data conversion and processing.

3) Data integration and sharing using a centralized GitLab instance.

The dataset admin stick man corresponds the indiviudal responsable for QC reviewing, dataset merging and pipeline monitoring. These tasks can be divided into multiple individuals for more efficient and robust management.

We utilize DICOM networking protocol to transfer the images from the scanner to the data server Mercure instance where it gets archived and automatically pushed to the GitLab instance based on the following DICOM tags:

- **ReferringPhysicianName:** This determines the Principal Investigator Name and corresponds to the root GitLab group name for the hierarchical structure of the dataset. 
- **StudyDescription:** This determines the study name and it corresponds to the following sub-group name in the hierarchical structure of the dataset.
- **StudyInstanceUID:** This determines the unique dicom study ID and it is used to track the dicom data in GitLab.
- **PatientID:** This determines the BIDS unique participant ID and session IDs and it is used to create link the DICOM data to the BIDS dataset.

Tecnically speaking, mercure can receive data from any MRI vendor, however, it has been only been configured to work with either a Siemens or GE 3T MRI scanner yet. This can be addapted to any scanner vendor with a bit of work and testing.

.. note:: 

    The selected DICOM tags can be modified to adapt to the restrictions of the acquisition site. Nevertheless, it is adviced to reliably have enough information in the tags to be able to create an equivalent structure. 

Git Flow
^^^^^^^^

Using DataLad for data version control enables tracking the provenance of datasets from their creation to their sharing. This is achieved through a Git flow approach, where changes to the dataset are stored in separate branches and merged when ready.

The previous :ref:`sequence diagram<diagram>` illustrates the workflow, starting from the push of a new DICOM session to executing data processing and release mechanisms on the federated instance (details to be designed).

Each GitLab actor/repository (e.g., DicomStudy, BIDS, Derivatives) is specific to a study, as defined by the DICOM tag `StudyDescription` (e.g., C-PIP). Each study follows this structure within a GitLab group, organized under groups corresponding to the local Principal Investigator or local consortia.

All operations on GitLab are automated through GitLab pipelines, executed as CI jobs by the GitLab runners and can be divided into different phases.

Pilot Phase
~~~~~~~~~~~

During the pilot phase, an experimenter will acquire one or multiple sessions to test sequences and/or full protocol. When the sessions are labelled as ``dev`` or ``pilot`` in the ``PatientID`` these are considered pilot sessions. The pilot sessions are converted to BIDS as regular session but open a `Merge Request (MR)` to the `pilot branch`. That MR triggers the same workflow as for sessions in the production phase, including BIDS-validation, defacing, and MRIQC: all useful to examine the compliance and quality of the data.

Once merged to the pilot branch they also trigger:

  - A configuration of the `forbids <https://github.com/UNFmontreal/forbids>`_ tool that will enforce the protocol in future sessions.

  - A configuration of standard pre-processing pipelines based on the acquired data.

  - Standard pre-processing pipelines are then triggered to check if the pilot data are compatible and produce sensible results.

The merge of new sessions iterating on the protocol reconfigure the protocol and pipelines, and also opens a `Merge Request` from the `cherry-picked` configs on `config` to the `base` branch. When the protocol is finalized and all checks pass, that MR with the latest config is to be reviewed, manually edited if necessary, and merged, effectively setting-up the repo for tests and derivatives generation during the production phase.

.. mermaid::

    %%{ init: { "theme": "forest" } }%%
    gitGraph:
        commit "start"
        branch config
        branch base
        checkout base
        commit id:"zzzzzzzzzzz"

        branch pilot
        checkout base                    

        branch convert/pilot1
        checkout convert/pilot1
        commit id:"heudiconv"
        commit id:"post-heudiconv-fixes"
        commit id:"fill-intendedfor/b0field"
        commit id:"deface"

        checkout pilot
        merge convert/pilot1
        commit id:"configs"

        checkout config
        cherry-pick id:"configs"

        checkout base
        commit id:"to better align"

        branch convert/pilot2
        checkout convert/pilot2
        commit id:"heudiconv-2"
        commit id:"post-heudiconv-fixes-2"
        commit id:"fill-intendedfor/b0field-2"
        commit id:"deface-2"

        checkout pilot
        merge convert/pilot2
        commit id:"reconfigs"

        checkout config
        cherry-pick id:"reconfigs"

        checkout base
        merge config

        checkout main
        merge base

Production Phase
~~~~~~~~~~~~~~~~

During the production phase, new sessions are `converted` into separated ``convert/{session_name}`` branches and open new Merge Requests with tests / QC reports to be reviewed and edited if necessary, before merging into the `dev` branch.

.. mermaid::

    %%{ init: { "theme": "forest" } }%%
    gitGraph:
        commit "start"

        branch base
        checkout base
        commit id:"zzzzzzzzzzz"

        branch dev
        checkout base

        branch convert/session_name1
        checkout convert/session_name1
        commit id:"heudiconv"
        commit id:"post-heudiconv-fixes"
        commit id:"fill-intendedfor/b0field"
        commit id:"deface"

        checkout dev
        merge convert/session_name1

        checkout base
        branch convert/session_name2
        checkout convert/session_name2
        commit id:"heudiconv-2"
        commit id:"post-heudiconv-fixes-2"
        commit id:"fill-intendedfor/b0field-2"
        commit id:"deface-2"

        checkout dev
        merge convert/session_name2

Relsease Phase
~~~~~~~~~~~~~~~~

When working on a data-release, a new release branch can be created from ``dev``, iterated upon (eg. edit README, docs, ) through branches and MRs, and finally merge to the ``main`` branch and tagged with a release version.
New sessions continues to be added to the ``dev`` branch in the back.


.. mermaid::

    %%{ init: { "theme": "forest" } }%%
    gitGraph:
        branch dev
        checkout main
        commit
        commit id:"previous_release" tag:"rel/www"

        checkout dev
        commit id:"long history"
        commit id:"bunch_of_sessions_now"

        branch rel/xxx
        checkout rel/xxx

        branch fix/xyz
        checkout dev
        commit
        commit

        checkout fix/xyz
        commit id:"random-fix"
        checkout rel/xxx
        merge fix/xyz

        checkout dev
        commit
        commit

        checkout rel/xxx
        branch fix/zyx
        checkout fix/zyx
        commit id:"edit README"
        checkout rel/xxx
        merge fix/zyx

        checkout main
        merge rel/xxx tag:"rel/xxx"

        checkout dev
        commit


Management
^^^^^^^^^^

Automated
~~~~~~~~~~

After proper configurations have been made, the data ingestion process is fully automated. The data is pushed to the Mercure instance and automatically pushed to the local GitLab instance. The data is then converted to BIDS format and processed using the configured pipelines.


Manual Input
~~~~~~~~~~~~

The dataset administrator is responsible for reviewing the BIDS-converted data and associated pre-processing reports. They may also manually edit the BIDS dataset when necessary. Additionally, the administrator oversees the approval process for merge requests, ensuring that any required modifications are made prior to granting approval.

Access Management
~~~~~~~~~~~~~~~~~

Access to the data is managed through GitLab groups and S3 bucket policies. This access can be as granular as the project requires. The dataset administrator is responsible for managing access to the data, including granting and revoking permissions as needed. Access to the data is typically restricted to authorized personnel only, ensuring that sensitive information is protected. When data is ready to be shared openly or with specific collaboration groups or individuals, the dataset administrator can create a release branch and tag it with a version number.

Different tiers of access using gitlab can be reviewed in the `official GitLab documentation <https://docs.gitlab.com/user/permissions/>`_.


Data Access
^^^^^^^^^^^

Required steps to access the data: