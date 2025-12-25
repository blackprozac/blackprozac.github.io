const grid = document.querySelector('.gallery-grid');
const lightbox = document.getElementById('lightbox');
const lightboxImg = document.querySelector('.lightbox-img');
const closeBtn = document.querySelector('.close');
const prevBtn = document.querySelector('.prev');
const nextBtn = document.querySelector('.next');


const images = Array.from(document.querySelectorAll('.gallery-grid img'));
let currentIndex = 0;


images.forEach((img) => {
  const fullSrc = img.src;
  

  const filename = fullSrc.split('/').pop().replace(/\.[^/.]+$/, "");
  const thumbSrc = `photos/thumb/${filename}.webp`;


  img.dataset.full = fullSrc;
  

  img.src = thumbSrc;
  img.style.cursor = "pointer";
});


const preloadImage = (index) => {
  if (index >= 0 && index < images.length) {
    const img = new Image();
    img.src = images[index].dataset.full;
  }
};


function updateLightboxImage() {
  const targetImage = images[currentIndex];

  const imageSrc = targetImage.dataset.full || targetImage.src;
  
  lightboxImg.src = imageSrc;


  const nextIndex = (currentIndex + 1) % images.length;
  const prevIndex = (currentIndex - 1 + images.length) % images.length;
  preloadImage(nextIndex);
  preloadImage(prevIndex);
}

function openLightbox(index) {
  currentIndex = index;
  updateLightboxImage();
  lightbox.classList.remove('hidden');
}

function closeLightbox() {
  lightbox.classList.add('hidden');
  lightboxImg.src = ""; 
}

function showNext(e) {
  if(e) e.stopPropagation();
  currentIndex = (currentIndex + 1) % images.length;
  updateLightboxImage();
}

function showPrev(e) {
  if(e) e.stopPropagation();
  currentIndex = (currentIndex - 1 + images.length) % images.length;
  updateLightboxImage();
}


grid.addEventListener('click', (e) => {
  if (e.target.tagName === 'IMG') {
    const index = images.indexOf(e.target);
    if (index !== -1) {
      openLightbox(index);
    }
  }
});


closeBtn.addEventListener('click', closeLightbox);
nextBtn.addEventListener('click', showNext);
prevBtn.addEventListener('click', showPrev);

document.addEventListener('keydown', (e) => {
  if (lightbox.classList.contains('hidden')) return; // Don't run if closed
  
  if (e.key === 'Escape') closeLightbox();
  if (e.key === 'ArrowRight') showNext();
  if (e.key === 'ArrowLeft') showPrev();
});

lightbox.addEventListener('click', (e) => {
  if (e.target === lightbox) {
    closeLightbox();
  }
});