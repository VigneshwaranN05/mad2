let login = document.querySelector(".login");
let login_manager = document.querySelector(".login_manager");
let slider = document.querySelector(".slider");
let formSection = document.querySelector(".form-section");
let backBtn = document.querySelector('.backbtn'); 
login_manager.addEventListener("click", () => {
    slider.classList.add("moveslider");
    login_manager.style.color='white';
    login.style.color='black';
    formSection.classList.add("form-section-move");
});
 
login.addEventListener("click", () => {
    slider.classList.remove("moveslider");
    formSection.classList.remove("form-section-move");
    login.style.color='white';
    login_manager.style.color='black';
});

backBtn.addEventListener("click" , ()=>{ 
    window.location.href="/";
});

// Function to check if passwords match
function onChange() {
    const password = document.querySelector('input[name=password]');
    const confirm = document.querySelector('input[name=confirm]');
    if (confirm.value === password.value) {
      confirm.setCustomValidity('');
    } else {
        
      confirm.setCustomValidity('Passwords do not match');
    }
  }

function onChangeManager() {
    const password = document.querySelector('input[name=manager-password]');
    const confirm = document.querySelector('input[name=manager-confirm]');
    if (confirm.value === password.value) {
      confirm.setCustomValidity('');
    } else {
        
      confirm.setCustomValidity('Passwords do not match');
    }
  }
