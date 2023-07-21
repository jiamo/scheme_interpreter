def decode(r):
    r = r.decode().strip("\n")
    if r == "#t":
        r = True
    elif r == "#f":
        r = False
    else:
        r = int(r)
    return r