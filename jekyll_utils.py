# oyaml is a drop-in replacement for PyYAML which preserves dict ordering
# import before everything so python-frontmatter uses oyaml
import oyaml as yaml 

import frontmatter

import os
import json

from collections import defaultdict
from datetime import datetime

from pydriller import Repository


post_directory = "_posts"


def get_changelog():
    # changelog dict to group entries by date
    changelog = defaultdict(list)

    if os.path.isfile("_data/changelog.json"):
        # load changelog entries from file
        with open("_data/changelog.json", "r") as f:
            entries = json.load(f)["entries"]

        # get latest changelog date from file as datetime
        since = datetime.strptime(
            max([entry["date"] for entry in entries]), 
            "%Y-%m-%d"
        )

        changelog = {item["date"] : item["entries"] for item in entries}
    else:
        since = None
    
    for commit in Repository('.', since=since).traverse_commits():
        changelog[
            commit.author_date.date().isoformat()
        ].append(commit.msg)

    with open("_data/changelog.json", "w") as f:
        f.write(json.dumps({
            "entries": [{"date": key, "entries": value} for key, value in changelog.items()]
        }, indent=4))


def update_posts():
    # inspired by: https://landscapearchaeology.org/2019/frontmatter/
    for file_name in os.listdir(post_directory):
        # get file path to post within post directory
        file_path = os.path.join(post_directory, file_name)

        # check if object is nested subfolder, if so, skip
        if not os.path.isfile(file_path): continue

        # load post with python-frontmatter
        post = frontmatter.load(file_path)

        # if post["type"] in ["recipe", "project"]:
        #     post["layout"] = post["type"]

        tags = post.get("tags")

        if tags and "Mains" in tags:
            tags[tags.index("Mains")] = "Main Courses"

        # if post.get("category") == "Garden":
        #     post["category"] = "Posts"

        # if post.get("categories"):
        #     category = post.get("categories")
        #     del post["categories"]

        #     post["category"] = category

        # if post.get("categories") and post["categories"] in ["Articles", "Notes", "Stubs", "Lists"]:
        #     # post["categories"] = "Garden"
        #     del post["categories"]

        #     post["category"] = "Garden"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post))

if __name__ == "__main__":
    # update_posts()

    get_changelog()