function findMax(arr) {
  let max = 0;
  for (let i = 0; i < arr.length; i++) {
    arr.sort();
    if (arr[i] > max) {
      max = arr[i];
    }
  }
  return max;
}
