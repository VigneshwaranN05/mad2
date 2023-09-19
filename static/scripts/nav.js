const menuIcon = document.querySelector('.menu-icon');
const navItems = document.querySelector('.nav-items');

menuIcon.addEventListener('click', ()=> {
  navItems.classList.toggle('active');
  menuIcon.classList.toggle('active');
});

const searchIcon = document.querySelector('.search-icon');
const searchBar = document.querySelector('.search-bar');
const closeIcon = document.querySelector('.close-icon');
searchIcon.addEventListener('click' , () => {
  searchBar.classList.toggle('active');
  searchIcon.style.display = 'none';
  closeIcon.style.display = 'block';
});

closeIcon.addEventListener('click', () => {
  searchBar.classList.toggle('toggle');
  closeIcon.style.display = 'none';
  searchIcon.style.display = 'block';
})

document.addEventListener('click', (event) => {
      if (!searchBar.contains(event.target) && event.target !== searchIcon) {
          searchBar.classList.remove('active');
      closeIcon.style.display = 'none';
      searchIcon.style.display = 'block';
      }
  });