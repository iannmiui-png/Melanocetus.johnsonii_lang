import sys
from PIL import Image

# ---------------------------------------------------------
# LOW-LEVEL DECODER (shared by run() and cat())
# ---------------------------------------------------------

def decode_raw(fn):
    im = Image.open(fn)
    d = im.tobytes()

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


# ---------------------------------------------------------
# MODE 1: cat — print embedded Python code
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# MODE 2: run — execute embedded Python code
# ---------------------------------------------------------

def run(fn):
    raw = decode_raw(fn)
    if raw is None:
        return

    pos = 0
    argc = int.from_bytes(raw[pos:pos+4], "little")
    pos += 4

    args = []
    for _ in range(argc):
        ln = int.from_bytes(raw[pos:pos+4], "little")
        pos += 4
        arg = raw[pos:pos+ln].decode("latin-1")
        pos += ln
        args.append(arg)

    code = raw[pos:].decode("latin-1")

    sys.argv = [fn] + args
    namespace = {"__name__": "__main__", "sys": sys}
    exec(code, namespace)


# ---------------------------------------------------------
# MODE 3: enc — encode Python + args into image
# ---------------------------------------------------------

def enc(input_image, python_file, output_image, args):
    im = Image.open(input_image)
    d = list(im.tobytes())

    code = open(python_file, "rb").read()

    payload = bytearray()

    # Store argument count
    payload += len(args).to_bytes(4, "little")

    # Store each argument
    for a in args:
        ab = a.encode("latin-1")
        payload += len(ab).to_bytes(4, "little")
        payload += ab

    # Store Python code
    payload += code

    # Convert payload to ternary digits
    tern = []
    for b in payload:
        tern.append(b // 81)
        tern.append((b // 9) % 9)
        tern.append(b % 9)

    # Terminator triple
    tern.extend([3, 1, 6])

    if len(tern) > len(d):
        print("Image too small to hold encoded data")
        return

    for i, t in enumerate(tern):
        d[i] = (d[i] // 9) * 9 + t
        if d[i] >= 256:
            d[i] -= 9

    Image.frombytes(im.mode, im.size, bytes(d)).save(output_image)


# ---------------------------------------------------------
# MAIN DISPATCH
# ---------------------------------------------------------

if __name__ == "__main__":
    a = sys.argv

    # Decode + execute
    if len(a) == 2:
        run(a[1])

    # Decode + cat (print code)
    elif len(a) == 3 and a[1] == "--cat":
        raw = decode_raw(a[2])
        if raw is not None:
            cat_payload(raw)

    # Encode
    elif len(a) >= 4:
        input_image = a[1]
        python_file = a[2]
        output_image = a[3]
        args = a[4:]
        enc(input_image, python_file, output_image, args)

    else:
        print("Usage:")
        print("  python yacumama.py <image>              # decode + run")
        print("  python yacumama.py --cat <image>        # decode + print code")
        print("  python yacumama.py <in> <py> <out> [args...]  # encode")
