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
  var request_select = document.getElementById("request-select");
  var hidden_select = document.getElementById("hidden-select");
  var hidden_input = document.getElementById("hidden-input");
  var request_message = document.getElementById("request-message");
  request_select.addEventListener("change", function () {
    hidden_select.style.display =
      request_select.value === "remove_item" ? "block" : "none";
    hidden_input.style.display =
      request_select.value === "new_category" ? "block" : "none";

    hidden_select.required = request_select.value === "remove_item";
    hidden_input.required = request_select.value === "new_category";
  });

  hidden_input.addEventListener("input", function () {
    var inputValue = hidden_input.value;
    request_message.value = `Add cateogry ${inputValue}`;
  });

  hidden_select.addEventListener("change", function () {
    var selectedOption = productSelect.options[productSelect.selecttedIndex];
    var productId = selectedOption.value;
    var productName = selectedOption.text;
    requestMessage.value = `Remove product ${productName} ID:${productId}`;
  });
});
