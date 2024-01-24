const app = Vue.createApp({
  data() {
    return {
      floatingScreenIsActive: false,
      filterOptionsIsActive: false,
      profileDropdownIsActive: false,
      searchInput: "",
    };
  },
  methods: {
    toggleFloatingScreen() {
      this.floatingScreenIsActive = !this.floatingScreenIsActive;
      this.filterOptionsIsActive = false;
      this.profileDropdownIsActive = false;
    },
    toggleFilterOptions() {
      this.filterOptionsIsActive = !this.filterOptionsIsActive;
      this.floatingScreenIsActive = false;
      this.profileDropdownIsActive = false;
    },
    toggleProfileDropdown() {
      this.profileDropdownIsActive = !this.profileDropdownIsActive;
      this.filterOptionsIsActive = false;
      this.floatingScreenIsActive = false;
    },
    closeFloatingScreen(event) {
      if (!event.target.closest(".floating-screen")) {
        this.floatingScreenIsActive = false;
      }
    },
    search() {
      if (this.searchInput.trim() !== "") {
        // Get the current URL string
        let currentUrl = window.location.href;

        // Check if there are existing parameters
        if (currentUrl.includes("?")) {
          // Append the search parameter using "&" if other parameters already exist
          currentUrl += `&search=${encodeURIComponent(this.searchInput)}`;
        } else {
          // Append the search parameter using "?" if there are no existing parameters
          currentUrl += `?search=${encodeURIComponent(this.searchInput)}`;
        }

        // Navigate to the updated URL
        window.location.href = currentUrl;
      }
    },
  },
  beforeMount() {
    this.floatingScreenIsActive = false;
    this.filterOptionsIsActive = false;
    this.profileDropdownIsActive = false;
  },
});

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

app.mount("#app");
message.mount(".message");
