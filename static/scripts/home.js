const menuIcon = document.querySelector('.menu-icon');
const navItems = document.querySelector('.nav-items');

menuIcon.addEventListener('click', ()=> {
  navItems.classList.toggle('active');
  menuIcon.classList.toggle('active');
});
