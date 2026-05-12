import sys
import os
import zlib


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
        content = zlib.decompress(raw).split(b"\0", 1)[1].strip(b"b'")

        print(content)

    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
