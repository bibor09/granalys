/* global bootstrap: false */
(() => {
  'use strict'
  const tooltipTriggerList = Array.from(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  tooltipTriggerList.forEach(tooltipTriggerEl => {
    new bootstrap.Tooltip(tooltipTriggerEl)
  })
})()

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
const toggleCodeDisplayOnCLick = (event) => {
  const id = event.target.id
  const statFileId = id.split('?')[1]

  const other_codes = document.querySelectorAll(`[id^="code-box"]`);
  other_codes.forEach(code => {
    code.style.display = 'none';
  });

  const currentCode = document.querySelector(`[id="code-box?${statFileId}"]`);
  currentCode.style.display = 'block';
};

const hideCodeOnClick = (event) => {
  const id = event.target.id
  const statFileId = id.split('?')[1]
  const codes = document.querySelectorAll(`[id^="code-box"]`);

  let isSuccsOfCodeOrPre = false
  let anc = event.target;
  while (anc !== null) {
    if ( anc.tagName === "PRE" || anc.tagName === "CODE") {
      isSuccsOfCodeOrPre = true;
      break;
    }
    anc = anc.parentNode;
  }

  codes.forEach(c => {
    if (c.id.split('?')[1] !== statFileId && !isSuccsOfCodeOrPre) {
      c.style.display = 'none';
    }
  });

};

/** Add event listeners on load */
window.onload = () => {
  document.getElementById("sidebar").addEventListener("click", makeActive);
  
  const stat_headers = document.querySelectorAll(`[id^="stat-box-header"]`);
  stat_headers.forEach((s)=>{
    s.addEventListener('click', toggleCodeDisplayOnCLick);
  });

  document.addEventListener('click', hideCodeOnClick);
};
