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

function showPassword(password1, password2) {
  var x = document.getElementById(password1);
  var y = document.getElementById(password2);
  if (x.type === "password") {
    x.type = "text";
  } else {
    x.type = "password";
  }
  if (y.type === "password") {
    y.type = "text";
  } else {
    y.type = "password";
  }
}
