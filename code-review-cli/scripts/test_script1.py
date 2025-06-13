def has_duplicates(arr):
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] == arr[j]:
                return True
    return False

nums = [1, 2, 3, 4, 5, 6, 2]
print("Contains duplicates:", has_duplicates(nums))
