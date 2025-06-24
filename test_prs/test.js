function fetchData(url) {
  fetch(url).then(res => {
    res.json().then(data => {
      console.log("Data received:", data);
    }).catch(err => {
      console.log("Error parsing JSON");
    });
  }).catch(err => {
    console.log("Network error");
  });
}
