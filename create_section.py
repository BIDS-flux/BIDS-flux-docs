import os

sections = [
    "setting-up-gitlab/index",
    "user-accounts-and-permissions/index",
    "ci-cd-pipelines/index",
    "gitlab-runner/index",
    "docker-and-singularity-compatibility/index",
    "using-datalad/index",
    "managing-git-repositories/index",
    "preprocessing-automation/index",
    "pipeline-configuration/index",
    "workflow-description/index",
    "version-control-best-practices/index",
    "commit-messages/index",
    "data-integration/index",
    "data-sharing/index"]

# Define the current directory
current_dir = os.getcwd()

for section in sections:
    # Split the section path into folder and file parts
    folder, file = section.split('/')
    
    # Create the folder if it doesn't exist
    folder_path = os.path.join(current_dir, folder)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Create the index.rst file
    index_rst = os.path.join(folder_path, 'index.rst')
    with open(index_rst, 'w') as f:
        f.write(f".. _{folder}-index:\n\n")
        f.write(f"{folder.title().replace('-', ' ')}\n")
        f.write("=" * len(folder) + "\n\n")
        f.write(f"This section provides information on {folder.replace('-', ' ')} for the [Your Project Name] project.\n\n")
        f.write(".. toctree::\n")
        f.write("   :maxdepth: 2\n\n")
        f.write(f"   subsection1/index\n")
        f.write(f"   subsection2/index\n")
        f.write("   # Add more subsections as needed\n\n")
        f.write("If you have any questions or need assistance, feel free to [link to contact information or support].\n\n")
        f.write(f".. note::\n\n")
        f.write(f"   Explore the subsections listed above for detailed information on {folder.replace('-', ' ')}.\n\n")
        f.write(".. note::\n\n")
        f.write(f"   For the latest project updates and release notes, please refer to the [Project Updates](../project-updates/index) section.\n\n")
        f.write(".. include:: ../../about.rst\n")
    
    print(f"Created {index_rst}")

print("Folders and index.rst files created successfully.")
