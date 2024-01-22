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
        window.location.href =
          "/search?query=" + encodeURIComponent(this.searchInput);
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

document.addEventListener("DOMContentLoaded", function () {
  // Function to update the visibility and requirements
  function updateFormElements() {
    hiddenSelect.style.display =
      requestSelect.value === "remove_item" ? "block" : "none";
    hiddenInput.style.display =
      requestSelect.value === "new_category" ? "block" : "none";

    hiddenSelect.required = requestSelect.value === "remove_item";
    hiddenInput.required = requestSelect.value === "new_category";

    // Trigger the change event when the display state changes
    if (hiddenSelect.style.display === "block") {
      hiddenSelect.dispatchEvent(new Event("change"));
    } else if (hiddenInput.style.display === "block") {
      hiddenInput.dispatchEvent(new Event("change"));
    }
  }

  var requestSelect = document.getElementById("request-select");
  var hiddenSelect = document.getElementById("hidden-select");
  var hiddenInput = document.getElementById("hidden-input");
  var requestMessage = document.getElementById("request-message");

  // Call the function on initial load
  updateFormElements();

  requestSelect.addEventListener("change", function () {
    // Call the function when the requestSelect value changes
    updateFormElements();
  });

  function updateRequestMessage() {
    var selectedOption = hiddenSelect.options[hiddenSelect.selectedIndex];
    var productId = selectedOption.value;
    var productName = selectedOption.text;
    requestMessage.value = `Remove product ${productName} ID:${productId}`;
  }
  hiddenInput.addEventListener("input", function () {
    var inputValue = hiddenInput.value;
    requestMessage.value = `Add category ${inputValue}`;
  });

  hiddenSelect.addEventListener("change", updateRequestMessage);

  updateRequestMessage();
});
