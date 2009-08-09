def base32_to_int(s):
    """Convert a base 32 string to an integer"""
    s = s.replace('i', '1').replace('j', 'i').replace('k', 'j').replace('l', '1').replace('m', 'k').replace('n', 'l').replace('o', '0').replace('p', 'm').replace('q', 'n').replace('r', 'o').replace('s', 'p').replace('t', 'q').replace('v', 'r').replace('w', 's').replace('x', 't').replace('y', 'u').replace('z', 'v')
    return int(s, 32)

def int_to_base32(i):
    """Converts an integer to a base32 string"""
    digits = "0123456789abcdefghjkmnpqrstvwxyz"
    factor = 0
    # Find starting factor
    while True:
        factor += 1
        if i < 32 ** factor:
            factor -= 1
            break
    base32 = []
    # Construct base32 representation
    while factor >= 0:
        j = 32 ** factor
        base32.append(digits[i / j])
        i = i % j
        factor -= 1
    return ''.join(base32)

