function deleteMember(id) {
  fetch("/delete-member", {
    method: "POST",
    body: JSON.stringify({ id: id }),
  }).then((_res) => {
    window.location.href = "/admin";
  });
}

// jika form-prevent disubmit maka disable button-prevent dan tampilkan spinner
(function () {
  $(".form-prevent").on("submit", function () {
    $(".button-prevent").attr("disabled", "true");
    $(".spinner").show();
    $(".hide-text").hide();
  });
})();
