function deleteMember(id) {
  fetch("/delete-member", {
    method: "POST",
    body: JSON.stringify({ id: id }),
  }).then((_res) => {
    window.location.href = "/admin";
  });
}
