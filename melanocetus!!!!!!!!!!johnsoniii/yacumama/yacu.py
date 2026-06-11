import sys
from PIL import Image

def decode(fn):
    im = Image.open(fn)
    d = im.tobytes()

    # Convert bytes to ternary digits
    tern = [b % 9 for b in d]

    raw = []
    i = 0
    L = len(tern)

    while i + 2 < L:
        A, B, C = tern[i], tern[i+1], tern[i+2]
        i += 3

        # Terminator triple
        if A == 3 and B == 1 and C == 6:
            break

        byte = A*81 + B*9 + C
        if byte > 255:
            print("decoder error: invalid byte", byte)
            return None

        raw.append(byte)

    return bytes(raw)


def cat_payload(raw):
    pos = 0

    # Read argc
    argc = int.from_bytes(raw[pos:pos+4], "little")
    pos += 4

    # Skip args
    for _ in range(argc):
        ln = int.from_bytes(raw[pos:pos+4], "little")
        pos += 4 + ln

    # Remaining bytes = Python code
    code = raw[pos:].decode("latin-1")

    print(code)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python yacumama.py <image.png>")
        sys.exit(1)

    raw = decode(sys.argv[1])
    if raw is not None:
        cat_payload(raw)
