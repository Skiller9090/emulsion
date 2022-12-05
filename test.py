import fnmatch

exclude = ["assets", "*.md"]
files = [
    "assets/readme.md",
    "magic.txt"
]
folders = [
    "assets",
    "perfection"
]

files = filter(
            lambda f: not any([fnmatch.fnmatch(f, e) for e in exclude]),
            files
        )
folders = filter(
        lambda f: not any([fnmatch.fnmatch(f, e) for e in exclude]),
        folders
    )

print(list(files))
print(list(folders))
