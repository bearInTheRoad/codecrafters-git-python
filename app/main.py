import sys
import os
import zlib
import hashlib


def hash_file(file_path: str):
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

    return sha_hash


def hash_folder(folder_path: str):
    dir_b_string = b"tree"
    dir_size = 0
    content_string_list = []
    for f_object in sorted(os.scandir(folder_path), key=lambda e: e.name):
        if f_object.name.startswith(".git"):
            continue
        if f_object.is_dir():
            sha_hash, folder_size = hash_folder(f_object.path)
            mode = "40000"
            dir_size += folder_size
        else:
            sha_hash = hash_file(f_object.path)
            mode = "100755" if os.access(f_object.path, os.X_OK) else "100644"
            dir_size += f_object.stat().st_size

        content_string_list.append(f"{mode} {f_object.name}\0{sha_hash}".encode())

    dir_b_string = (
        dir_b_string
        + b" "
        + str(dir_size).encode()
        + b"\0"
        + b"".join(content_string_list)
    )

    raw = zlib.compress(dir_b_string)

    sha_hash = str(hashlib.sha1(dir_b_string).hexdigest())

    path_name = sha_hash[:2]
    file_name = sha_hash[2:]

    os.makedirs(f"./.git/objects/{path_name}", exist_ok=True)

    with open(f"./.git/objects/{path_name}/{file_name}", "wb") as file:
        file.write(raw)

    return sha_hash, dir_size


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
        dir_hash, _ = hash_folder("./")

        sys.stdout.write(dir_hash)

    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
