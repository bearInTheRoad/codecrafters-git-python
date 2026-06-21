import sys
import os
import zlib
import hashlib


def store_git(raw_b_string: bytes):
    # compress
    raw = zlib.compress(raw_b_string)

    # sha1 hash, then do a digest
    # The SHA-1 hash is 40 characters long, and is the 40-character hexadecimal SHA-1 hash of the object.
    sha_hash = str(hashlib.sha1(raw_b_string).hexdigest())

    # split into the path name and file name
    # first 2 characters are the path name
    # the rest is the file name
    path_name = sha_hash[:2]
    file_name = sha_hash[2:]

    os.makedirs(f"./.git/objects/{path_name}", exist_ok=True)

    with open(f"./.git/objects/{path_name}/{file_name}", "wb") as file:
        file.write(raw)

    return sha_hash


def hash_file(file_path: str):
    # construct the raw bytestring in a git way
    # file style, before zlib compress: blob <size>\0<content>
    with open(file_path, "r") as file:
        content = file.read()
    raw_b_string = b"blob " + str(len(content)).encode() + b"\0" + content.encode()

    return store_git(raw_b_string)


def hash_folder(folder_path: str):
    # construct the raw bytestring in a git way
    # folder style, before zlib compress (no new line in the actual hash)
    # tree <size>\0
    # <mode> <name>\0<20_byte_sha>
    # <mode> <name>\0<20_byte_sha>
    dir_b_string = b"tree"
    content_string_list = []

    # Simplified file mode different
    # 100644 - Regular file
    # 100755 - Executable file
    # 40000 - Directory (Tree object)
    for f_object in sorted(os.scandir(folder_path), key=lambda e: e.name):
        if f_object.name.startswith(".git"):
            continue
        if f_object.is_dir():
            sha_hash = hash_folder(f_object.path)
            mode = "40000"
        else:
            sha_hash = hash_file(f_object.path)
            mode = "100755" if os.access(f_object.path, os.X_OK) else "100644"

        content_string_list.append(
            f"{mode} {f_object.name}\0".encode() + bytes.fromhex(sha_hash)
        )

    dir_b_string = (
        dir_b_string
        + b" "
        + str(len(b"".join(content_string_list))).encode()
        + b"\0"
        + b"".join(content_string_list)
    )

    return store_git(dir_b_string)


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    command = sys.argv[1]
    if command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Initialized git directory")

    elif command == "cat-file":
        sha_hash = sys.argv[3]
        path_name = sha_hash[:2]
        file_name = sha_hash[2:]

        with open(f"./.git/objects/{path_name}/{file_name}", "rb") as file:
            raw = file.read()
        content = zlib.decompress(raw).split(b"\0", 1)[1].decode()

        sys.stdout.write(content)

    elif command == "hash-object":
        file_path = sys.argv[3]

        sha_hash = hash_file(file_path)

        sys.stdout.write(sha_hash)

    elif command == "ls-tree":
        tree_sha1 = sys.argv[3]

        path_name = tree_sha1[:2]
        file_name = tree_sha1[2:]

        with open(f"./.git/objects/{path_name}/{file_name}", "rb") as file:
            raw = file.read()

        raw_b_string = zlib.decompress(raw)

        content_list = raw_b_string.split(b"\0")

        b_tree_name, b_tree_size = content_list[0].split(b" ")
        b_first_mode, b_first_name = content_list[1].split(b" ")
        dir_list = [b_first_name.decode()]

        for element in content_list[2:]:
            if len(element) > 20:
                mode, name = element[20:].split(b" ")
                dir_list.append(name.decode())

        sys.stdout.write("\n".join(dir_list) + "\n")

    elif command == "write-tree":
        dir_hash = hash_folder("./")

        sys.stdout.write(dir_hash)

    elif command == "commit-tree":
        # commit tree style, before zlib compress
        # There's a blank line between the metadata and the commit message.
        # The timestamp format is: <seconds_since_epoch> <timezone_offset> (e.g., 1234567890 +0000).

        # commit <size>\0tree <tree_sha>
        # parent <parent_sha>
        # author <name> <<email>> <timestamp> <timezone>
        # committer <name> <<email>> <timestamp> <timezone>

        # <commit message>

        # The tree and parent SHAs are in hexadecimal format (40 characters),
        # unlike with tree objects, where they're 20 bytes.

        # size is the number of bytes in content, starting from tree <tree_sha> till the end of the commit object.

        # The output of git commit-tree is the 40-character SHA-1 hash of the commit object that was written to .git/objects.

        # ./your_program.sh commit-tree <tree_sha> -p <commit_sha> -m <message>

        commit_sha1 = sys.argv[4]
        tree_sha1 = sys.argv[2]

        # leave a placeholder here, will calculate and replace in the end

        commit_b_string_list = [
            b"commit",
            b"0",
            b"\0tree ",
            tree_sha1.encode(),
            b"\nparent ",
            commit_sha1.encode(),
            b"\nauthor dylan <dylan@123.com> 1234567890 +0000\ncommitter dylan <dylan@123.com> 1234567890 +0000\n",
            b"Hello World",
        ]

        size = len(b"".join(commit_b_string_list[2:]))
        commit_b_string_list[1] = str(size).encode()

        commit_object = b"".join(commit_b_string_list)

        sha_hash = store_git(commit_object)

        sys.stdout.write(sha_hash)

    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
