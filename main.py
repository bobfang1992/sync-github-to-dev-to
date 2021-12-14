from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.front_matter import front_matter_plugin
from requests.api import head
from dotenv import load_dotenv, main
from github import Github
import os
import requests
import json
from markdown_it.tree import SyntaxTreeNode

from markdown_it import MarkdownIt
import frontmatter
import re
import time

image_extract = "!\[(?P<alt>.*)\]\((?P<filename>.*)\)"

image_extract_str = re.compile(image_extract)


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
            print(f"Syncing  {file.path}/{file.name}")

            headers = {'Content-type': 'application/json',
                       'api-key': os.getenv("DEVTO_API_KEY")}

            content = file.decoded_content.decode('utf-8')

            def replacement(match):
                if match.group('filename').startswith('./'):
                    new_file_name = file.path.replace(
                        "index.md", match.group('filename').replace('./', ''))
                    raw_file = f"https://raw.githubusercontent.com/bobfang1992/personal-blog/master/{new_file_name}"
                    return f"![{match.group('alt')}]({raw_file})"

            content = image_extract_str.sub(replacement, content)

            print(content)
            frontmatter_data = frontmatter.loads(content)
            title = frontmatter_data['title']
            print("title:", title)
            print("content:", frontmatter_data.content)

            body = {
                "article": {
                    "title": title,
                    "body_markdown": frontmatter_data.content,
                    "published": True,
                    "tags": []
                }
            }

            resp = requests.post(
                "https://dev.to/api/articles",
                data=json.dumps(body),
                headers=headers,
            )
            if resp.status_code != 201:
                print(resp.status_code)
                print(resp.text)
                raise Exception("Error")
            time.sleep(30)
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
