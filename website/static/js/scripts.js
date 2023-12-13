const burger = document.querySelector(".icon");
const navbar = document.querySelector(".topnav");

burger.addEventListener("click", () => {
  if (navbar.className === "topnav") {
    navbar.className += " responsive";
  } else {
    navbar.className = "topnav";
  }
});


// Star Rating
$(":radio").change(function () {
  console.log("New star rating: " + this.value);
});