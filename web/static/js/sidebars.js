/* global bootstrap: false */
(() => {
  'use strict'
  const tooltipTriggerList = Array.from(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  tooltipTriggerList.forEach(tooltipTriggerEl => {
    new bootstrap.Tooltip(tooltipTriggerEl)
  })
})()

function loadScript(url)
{    
    var head = document.getElementsByTagName('head')[0];
    var script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = url;
    head.appendChild(script);
}

loadScript('/js/third-party/prism-python.js');

/* Highlight actibve branch */
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

/* Display code on click */
const toggleCodeDisplayOnCLick = () => {
  const code = document.querySelector('#code-box');
  if (code.style.display === '') {
    code.style.display = 'block';
  } else {
    code.style.display = (code.style.display === 'none') ? 'block' : 'none';
  }
};

const hideCodeOnClick = (event) => {
  const code = document.querySelector('#code-box');
  const header = document.querySelector('#stat-box-header');
  if (event.target !== code && event.target !== header) {
    code.style.display = 'none';
  }
};

/** Add event listeners on load */
window.onload = () => {
  document.getElementById("sidebar").addEventListener("click", makeActive);
  
  document.getElementById("stat-box-header").addEventListener('click', toggleCodeDisplayOnCLick);

  document.addEventListener('click', hideCodeOnClick);
};
