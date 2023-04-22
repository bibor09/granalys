/* global bootstrap: false */
(() => {
  'use strict'
  const tooltipTriggerList = Array.from(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  tooltipTriggerList.forEach(tooltipTriggerEl => {
    new bootstrap.Tooltip(tooltipTriggerEl)
  })
})()


const makeActive = function (e) {
  const clicked = e.target;
  if (!clicked || !clicked.classList.contains("nav-link")) {
    return;
  }

  items = document.querySelectorAll(".nav-link.text-white.active");
  items.forEach(item => {
    item.classList.remove("active");
  });

  clicked.classList.add("active");
};

window.onload = () => {
  document.getElementById("sidebar").addEventListener("click", makeActive);
};
