let signup = document.querySelector(".signup");
let signup_manager = document.querySelector(".signup_manager");
let slider = document.querySelector(".slider");
let formSection = document.querySelector(".form-section");
 
signup_manager.addEventListener("click", () => {
    slider.classList.add("moveslider");
    formSection.classList.add("form-section-move");
});
 
signup.addEventListener("click", () => {
    slider.classList.remove("moveslider");
    formSection.classList.remove("form-section-move");
});
