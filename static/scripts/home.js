const menuIcon = document.querySelector('.menu-icon');
const navItems = document.querySelector('.nav-items');

menuIcon.addEventListener('click', ()=> {
  navItems.classList.toggle('active');
  menuIcon.classList.toggle('active');
});
window.onscroll = function() {
    if (window.scrollY > 50) {
        document.querySelector('.sticky-top').style.backgroundColor = 'black';
      console.log('Made change');
    }
  else{
    document.querySelector('.sticky-top').style.backgroundColor = '' ;
  }
};
