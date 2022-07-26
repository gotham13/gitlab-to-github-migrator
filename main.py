import time

from github import Github
import gitlab
GITHUB_USERNAME = ""
GITLAB_TOKEN = ""
GITHUB_TOKEN = ""
GITLAB_ORG_NAME = ""
GITHUB_ORG_NAME = ""

gl = gitlab.Gitlab(private_token=GITLAB_TOKEN)
gh = Github(GITHUB_TOKEN)
def fetchReposFromGitlabOrg():
    gitlab_org = gl.groups.get(GITLAB_ORG_NAME)
    project_objects = gitlab_org.projects.list(all=True)
    projects = list(map(lambda x:gl.projects.get(x.id),project_objects))
    return projects

def checkGithubRepoExists(github_org,name):
    try:
        repo = github_org.get_repo(name)
        time.sleep(1)
        return repo
    except Exception as e:
        return False

def createReposInGithubOrg(projects):

    github_org = gh.get_organization(GITHUB_ORG_NAME)
    for project in projects:
        print(project)
        repo = checkGithubRepoExists(github_org,project.path)
        print(repo)
        if not repo:
            description = project.description
            if description is not None:
                repo = github_org.create_repo(project.path,description=project.description,private=True,auto_init=False)
            else:
                repo = github_org.create_repo(project.path, private=True,
                                              auto_init=False)
            time.sleep(5)
        github_url = repo.git_url
        github_url = github_url.replace("git://",f'https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@')
        print(github_url)
        found = False
        for mirror in project.remote_mirrors.list():
            if mirror.url.split("@")[1] == github_url.split("@")[1] and mirror.enabled:
                found = True
        if not found:
            project.remote_mirrors.create({'url': github_url, 'enabled': True,'keep_divergent_refs':True})
        try:
            project.branches.create({'branch': 'trigger_mirror',
                                          'ref': project.branches.list()[0].name})
        except Exception as e:
            print(e)

if __name__ == '__main__':
    repos = fetchReposFromGitlabOrg()
    createReposInGithubOrg(repos)