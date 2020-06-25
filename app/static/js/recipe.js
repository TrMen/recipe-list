/* eslint-disable linebreak-style */

const addTagForm = document.getElementById('add-tag-form');
if (addTagForm) {
  document.getElementById('expand-add-tag').addEventListener('click', () => {
    if (addTagForm.classList.contains('expanded')) addTagForm.classList.remove('expanded');
    else {
      addTagForm.classList.add('expanded');
      document.getElementById('tag_name').focus();
    }
  });
  addTagForm.addEventListener('submit', () => {
    addTagForm.classList.remove('expanded');
  });
}

const left = document.getElementById('left');
const right = document.getElementById('right');
const image = document.getElementById('image');
let currentImage = 0;

function mod(n, m) { // Because apparently JS modulo returns negative numbers for negative inputs...
  return ((n % m) + m) % m;
}

if (image && left && right) {
  left.addEventListener('click', (e) => {
    currentImage = mod((currentImage + 1), pyVars.imageUrls.length);
    image.src = pyVars.imageUrls[currentImage];
    e.preventDefault(); // To stop double click from selecting something
  });
  right.addEventListener('click', (e) => {
    currentImage = mod((currentImage - 1), pyVars.imageUrls.length);
    image.src = pyVars.imageUrls[currentImage];
    e.preventDefault();
  });
}

const deleteBtn = document.getElementById('delete-submit');
const deleteForm = document.getElementById('delete-form');

if (deleteBtn && deleteForm) {
  deleteForm.addEventListener('submit', (event) => {
    if (!confirm('Do you really want to delete this recipe? This cannot be reversed.')) {
      event.preventDefault();
    }
  });
}
