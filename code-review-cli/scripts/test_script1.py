def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True

def get_primes(nums):
    primes = []
    for num in nums:
        if is_prime(num):
            primes.append(num)
    return primes

numbers = list(range(1, 30))
print(get_primes(numbers))
