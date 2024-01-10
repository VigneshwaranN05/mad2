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
function updateCard() {
  function getValueById(elementId) {
    var element = document.getElementById(elementId);
    return element ? element.value || "" : "";
  }

  // Get input values
  var productName = getValueById("productNameInput");
  var category = getValueById("categoryInput");
  var price = getValueById("priceInput");
  var stock = getValueById("stockInput");
  var unit = getValueById("unitInput");
  var expireDate = getValueById("expireDateInput");

  document.getElementById("name").innerText = productName;
  document.getElementById("pricePerUnit").innerText =
    "Price : " + price + (unit ? " per " + unit : "");
  document.getElementById("stock").innerText =
    "Stock : " + stock + " " + unit + (unit ? "(s)" : "");
  document.getElementById("category").innerText = "Category: " + category;
  document.getElementById("expire-date").innerText =
    "Expire Date :" + expireDate + "\n(yyyy-mm-dd)";
}

function formatAndSetStock() {
  var stockInput = document.getElementById("stockInput");
  if (stockInput) {
    // Format the stock value to allow only two decimal places
    var formattedStock = stockInput.value.replace(/(\.\d{2})\d+/g, "$1");
    stockInput.value = formattedStock;
    updateCard(); // Call updateCard after formatting the stock value
  }
}

function handleImage() {
  var fileInput = document.getElementById("fileInput");
  var productImage = document.getElementById("productImage");

  if (fileInput && fileInput.files && fileInput.files.length > 0) {
    var file = fileInput.files[0];
    var fileName = file.name.toLowerCase();
    var validExtensions = [".png", ".jpeg", ".jpg"];

    if (validExtensions.some((ext) => fileName.endsWith(ext))) {
      var reader = new FileReader();

      reader.onload = function (e) {
        if (productImage) {
          productImage.src = e.target.result;
        } else {
          console.error("productImage element not found.");
        }
      };

      reader.readAsDataURL(file);
    } else {
      // Display an error or inform the user about invalid file format
      alert("Invalid file format. Please select a .png or .jpeg file.");
      fileInput.value = ""; // Clear the file input
    }
  }
}

var currentDate = new Date();
var tomorrowDate = new Date(currentDate);
tomorrowDate.setDate(currentDate.getDate() + 1);
var tomorrowDateFormatted = tomorrowDate.toISOString().split("T")[0];

document.getElementById("expireDateInput").min = tomorrowDateFormatted;
