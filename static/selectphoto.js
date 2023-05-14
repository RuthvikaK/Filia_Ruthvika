/* Aaloki */
const selectPhotoBtn = document.getElementById("select-photo-btn");
const fileInput = document.getElementById("photo");
const preview = document.getElementById("preview");

selectPhotoBtn.addEventListener("click", () => {
  fileInput.click();
});

fileInput.addEventListener("change", () => {
  if (fileInput.files.length > 0) {
    const reader = new FileReader();
    reader.onload = (e) => {
      preview.src = e.target.result;
    };
    reader.readAsDataURL(fileInput.files[0]);
  }
});
