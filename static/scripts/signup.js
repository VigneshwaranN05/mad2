let signup = document.querySelector(".signup");
let signup_manager = document.querySelector(".signup_manager");
let slider = document.querySelector(".slider");
let formSection = document.querySelector(".form-section");
let backBtn = document.querySelector('.backbtn'); 
signup_manager.addEventListener("click", () => {
    slider.classList.add("moveslider");
    signup_manager.style.color = "white";
    signup.style.color = 'black';
    formSection.classList.add("form-section-move");
});
 
signup.addEventListener("click", () => {
    slider.classList.remove("moveslider");
    signup.style.color = "white";
    signup_manager.style.color='black';
    formSection.classList.remove("form-section-move");
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

const message = Vue.createApp({
  data() {
    return {
      toastIsActive: true,
    };
  },
  created() {
    setTimeout(() => {
      this.toastIsActive = false;
    }, 5000);
  },
});
message.mount('.message');
