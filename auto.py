"""Clone remote repository and update files with tenant data."""
import os
import git
import yaml
from github import Github
from logs import setup_logger


BASE_PATH = "/Users/sanskar/Desktop/Skills/Saiyam/GitHubAutomate"
USERNAME = "Saiyam74"
GITHUB_TOKEN = "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"
REPO_NAME = "Scrawling_amazon"

logger = setup_logger('GitAutomation')


def clone_repo(repo_path):
    """Clone a remote repo"""
    remote_url = (
        f"https://{USERNAME}:{GITHUB_TOKEN}@github.com/{USERNAME}/{REPO_NAME}.git"
    )
    logger.info(f"Cloning repo: {REPO_NAME}")
    if not os.path.exists(repo_path):
        cloned_repo = git.Repo.clone_from(remote_url, f"{repo_path}")

        logger.info(f"Cloned repository from {remote_url} to {repo_path}")
        logger.info(f"Repository Name: {cloned_repo.remotes.origin.url}")
        logger.info(f"Current Branch: {cloned_repo.active_branch}")

    elif os.path.exists(f"{repo_path}"):
        logger.info("Repository already exists!")
    else:
        logger.info("Destination path already exists!")


def search_file_paths(repo_path):
    """Search for files in the cloned repository"""

    file_list = ["file1.yaml", "file2.yaml", "file4.yaml"]
    file_paths = []
    logger.info(f"Searching for files: {','.join(file_list)}")
    for filename in file_list:
        for root, _, files in os.walk(repo_path):
            if filename in files:
                file_path = os.path.join(root, filename)
                file_paths.append(file_path)
                logger.info(f"{filename} found!")

    return file_paths


def get_tenant_details():
    """Take input from customer for Tenant data"""

    logger.info("Getting customer details!")
    tenant_data = dict()

    print("Please provide the following details:")
    tenant_data = {
        "customer_region": input("Customer Region (dev, tst, prd, prd_apac, prd_eu): "),
        "customer_name": input("Customer Name: "),
        "customer_realm_name": input("Customer Realm Name: "),
        "customer_realm_id": input("Customer Realm ID: "),
        "customer_instance_end_point": input("Customer Instance Endpoint: "),
    }

    return tenant_data


def modify_files(file_paths, tenant_data):
    """Add Tenant data in the required files"""

    for file_path in file_paths:
        logger.info(f"Modifying file: {[file_path.split('/')][-1]}")
        # Load the YAML content from the file
        with open(file_path) as yaml_file:
            file_data = yaml.safe_load(yaml_file)

        cus_region = tenant_data["customer_region"]
        realm_name = tenant_data["customer_realm_name"]
        realm_id = tenant_data["customer_realm_id"]
        inst_endpoint = tenant_data["customer_instance_end_point"]
        cust_data = {
            "realm": realm_name,
            "realmId": realm_id,
            "instanceEndPoint": inst_endpoint,
        }
        # Modify the nested tag
        file_data["product"]["api"]["byapimEnv"][cus_region]["singleTenant"].append(
            cust_data
        )

        # Save the modified YAML back to the file
        with open(file_path, "w") as yaml_file:
            yaml.dump(file_data, yaml_file, default_flow_style=False)


def git_push_and_pr(repo_path, file_paths, cus_name, region):
    """Commit, Push, and raise Pull Request"""

    # Create a Repo object
    repo = git.Repo(repo_path)

    master_branch = repo.branches["master"]
    master_branch.checkout()

    # Create a new branch from 'master'
    new_branch_name = f"liam_{cus_name}_{region}"
    new_branch = repo.create_head(new_branch_name)

    # Switch to the new branch
    new_branch.checkout()

    logger.info(f"Created and switched to the new branch: {new_branch_name}")

    # Add specific files or all changes to the staging area
    repo.index.add(file_paths)

    # Commit the changes with a commit message
    commit_message = f"Added '{cus_name}' customer details in '{region}'"
    repo.index.commit(commit_message)

    # Push the changes to the remote branch
    repo.git.push("origin", new_branch_name)
    logger.info(f"Code pushed to {new_branch_name}")

    raise_pull_request(commit_message, new_branch_name)


def raise_pull_request(title, new_branch_name):
    """Raise Pull Request from new branch to master branch"""
    # Create a GitHub API instance using your access token
    git_obj = Github(GITHUB_TOKEN)

    # Get the GitHub repository
    repo = git_obj.get_user(USERNAME).get_repo(REPO_NAME)

    pr_description = """Pull Request Description"""

    # Create a pull request
    pull_request = repo.create_pull(
        title=title,
        body=pr_description,
        head=f"{USERNAME}:{new_branch_name}",
        base="master",
    )
    logger.info(f"Pull request created: {pull_request.html_url}")


def main():
    """Control the process"""

    repo_path = f"{BASE_PATH}/{REPO_NAME}"

    # Clone the repository
    clone_repo(repo_path)

    # Get file paths
    file_paths = search_file_paths(repo_path)

    # Get Tenant details
    tenant_data = get_tenant_details()

    # Modify files
    modify_files(file_paths, tenant_data)

    # Commit, Push and raise Pull Request
    git_push_and_pr(
        repo_path,
        file_paths,
        tenant_data["customer_name"],
        tenant_data["customer_region"],
    )


if __name__ == "__main__":
    main()
