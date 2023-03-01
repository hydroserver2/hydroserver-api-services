let currentModal;
const modalButtons = document.querySelectorAll('.modal-button');

//Open modal onclick
modalButtons.forEach(button => {
  button.addEventListener('click', () => {
    const modalId = button.dataset.modal;
    currentModal = document.getElementById(modalId);
    currentModal.style.display = 'block';
  });
});

// Close modal onclick
const closeButtons = document.querySelectorAll('.close');
closeButtons.forEach(closeButton => {
  closeButton.addEventListener('click', () => {
    currentModal.style.display = 'none';
  });
});

// Close modal onclick anywhere outside of modal
window.addEventListener('click', event => {
  if (event.target === currentModal) {
    currentModal.style.display = 'none';
  }
});