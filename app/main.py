import sys
import os
import zlib
import hashlib


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
        with open(file_path, "r") as file:
            content = file.read()
        raw_b_string = b"blob " + str(len(content)).encode() + b"\0" + content.encode()

        raw = zlib.compress(raw_b_string)

        sha_hash = str(hashlib.sha1(raw_b_string).hexdigest())
        path_name = sha_hash[:2]
        file_name = sha_hash[2:]

        os.makedirs(f"./.git/objects/{path_name}", exist_ok=True)

        with open(f"./.git/objects/{path_name}/{file_name}", "wb") as file:
            file.write(raw)

        sys.stdout.write(sha_hash)

    elif command == "ls-tree":
        is_name_only = sys.argv[2]
        tree_sha1 = sys.argv[3]

        path_name = tree_sha1[:2]
        file_name = tree_sha1[2:]

        with open(f"./.git/objects/{path_name}/{file_name}", "rb") as file:
            raw = file.read()

        raw_b_string = zlib.decompress(raw)

        content_list = raw_b_string.split(b"\0")

        b_tree_name, b_tree_size = content_list[0].split(b" ")

        dir_list = [element.split(b" ")[1].decode() for element in content_list[1::2]]

        return dir_list

    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
