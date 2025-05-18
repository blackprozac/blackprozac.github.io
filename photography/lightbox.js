const images = document.querySelectorAll('.gallery-grid img');
const lightbox = document.getElementById('lightbox');
const lightboxImg = document.querySelector('.lightbox-img');
const closeBtn = document.querySelector('.close');
const prevBtn = document.querySelector('.prev');
const nextBtn = document.querySelector('.next');

let currentIndex = 0;

// Open lightbox with full-size image
function openLightbox(index) {
  currentIndex = index;
  lightboxImg.src = images[currentIndex].dataset.full || images[currentIndex].src;
  lightbox.classList.remove('hidden');
}

function closeLightbox() {
  lightbox.classList.add('hidden');
}

function showNext() {
  currentIndex = (currentIndex + 1) % images.length;
  lightboxImg.src = images[currentIndex].dataset.full || images[currentIndex].src;
}

function showPrev() {
  currentIndex = (currentIndex - 1 + images.length) % images.length;
  lightboxImg.src = images[currentIndex].dataset.full || images[currentIndex].src;
}

// Replace images with thumbnails and store full-size source
images.forEach((img, index) => {
  const fullSrc = img.src;
  const filename = fullSrc.split('/').pop().replace(/\.[^/.]+$/, "");
  const thumbSrc = `photos/thumb/${filename}.webp`;

  img.dataset.full = fullSrc;
  img.src = thumbSrc;
  img.style.cursor = "pointer";

  img.addEventListener('click', () => openLightbox(index));
});

closeBtn.addEventListener('click', closeLightbox);
nextBtn.addEventListener('click', showNext);
prevBtn.addEventListener('click', showPrev);

// Optional: ESC and arrow key navigation
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeLightbox();
  if (e.key === 'ArrowRight') showNext();
  if (e.key === 'ArrowLeft') showPrev();
});
lightbox.addEventListener('click', (e) => {
  if (e.target === lightbox) {
    closeLightbox();
  }
});