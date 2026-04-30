import random

def get_random_64bit():
    return (random.randint(0, 0xFFFF) | 
            (random.randint(0, 0xFFFF) << 16) | 
            (random.randint(0, 0xFFFF) << 32) | 
            (random.randint(0, 0xFFFF) << 48))

def get_magic_candidate():
    return get_random_64bit() & get_random_64bit() & get_random_64bit()
