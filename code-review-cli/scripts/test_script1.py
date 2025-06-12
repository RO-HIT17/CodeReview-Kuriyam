import math

def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

def get_primes(nums):
    return [num for num in nums if is_prime(num)]

numbers = list(range(1, 30))
print(get_primes(numbers))
