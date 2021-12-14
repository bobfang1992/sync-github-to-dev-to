from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.front_matter import front_matter_plugin
from requests.api import head
from dotenv import load_dotenv, main
from github import Github
import os
import requests
import json

from markdown_it import MarkdownIt

md = MarkdownIt().use(footnote_plugin).use(front_matter_plugin)

# import marko
# from marko.ext.gfm import gfm


load_dotenv()


def get_synced():
    with open('synced.txt', 'r') as f:
        return f.read().splitlines()


def write_synced(synced):
    with open('synced.txt', 'w') as f:
        for line in synced:
            f.write(line + '\n')


def sync(synced, to_sync):
    confirm = input("Sync? (y/n) ")
    if confirm == 'y':
        for file in to_sync:
            print(f"Syncing {file.name}")

            headers = {'Content-type': 'application/json',
                       'api-key': os.getenv("DEVTO_API_KEY")}

            content = md.parse(file.decoded_content.decode('utf-8'))
            print(content)
            breakpoint()
            body = {
            }

            print(headers, body)
            # requests.post(
            #     "https://dev.to/api/articles",
            #     data=json.dumps(body),
            #     headers=headers,
            # )

        write_synced(synced)
        print("Synced")
    else:
        print("Aborted")


def main():
    g = Github(os.getenv("GITHUB_API_KEY"))
    repo = g.get_repo("bobfang1992/personal-blog")
    print(f"Found {repo.name}")
    contents = repo.get_contents("content/blog")
    print(f"Got {len(contents)} blog posts")

    synced = get_synced()
    to_sync = []
    for content in contents:
        print(f"{content.name}")
        file = repo.get_contents(content.path + "/index.md")
        print(f"{file.name}")
        print(f"{file.path}")
        print(f"{file.sha}")
        print(f"{file.decoded_content}")

        if content.name not in synced:
            print(f"{content.name} not in synced")
            synced.append(content.name)
            to_sync.append(file)
    sync(synced, to_sync)


if __name__ == '__main__':
    main()
