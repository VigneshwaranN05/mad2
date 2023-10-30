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


const profileDropdownTrigger = document.getElementById('profile-dropdown-trigger');
const profileDropdown = document.getElementById('profile-dropdown');

// Toggle the dropdown when the profile image is clicked
profileDropdownTrigger.addEventListener('click', function() {
  if (profileDropdown.style.display === 'block') {
    profileDropdown.style.display = 'none';
  } else {
    profileDropdown.style.display = 'block';
  }
});

// Close the dropdown if the user clicks outside of it
window.addEventListener('click', function(event) {
  if (!event.target.matches('#profile-dropdown-trigger')) {
    if (profileDropdown.style.display === 'block') {
      profileDropdown.style.display = 'none';
    }
  }
});

