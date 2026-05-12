import sys
import os
import zlib
import hashlib


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    # TODO: Uncomment the code below to pass the first stage
    #
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
        raw = zlib.compress(
            b"blob " + str(len(content)).encode() + b"\0" + content.encode()
        )

        sha_hash = str(hashlib.sha1(raw).hexdigest())
        path_name = sha_hash[:2]
        file_name = sha_hash[2:]

        os.makedirs(f"./.git/objects/{path_name}", exist_ok=True)

        with open(f"./.git/objects/{path_name}/{file_name}", "wb") as file:
            file.write(raw)

        sys.stdout.write(sha_hash)

    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
