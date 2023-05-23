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

/* Change display */
const changeDisplay = function () {
  const selectDisplay = document.getElementById('choose-display');
  const selectedValue = selectDisplay.value;

  const stats = document.getElementById('statistics');
  const charts = document.getElementById('statistics-charts');

  if (selectedValue === "files") {
    stats.style.cssText = 'display:flex !important';
    charts.style.cssText = 'display:none !important';
  } else if (selectedValue === "charts") {
    stats.style.cssText = 'display:none !important';
    charts.style.cssText = 'display:block !important';
  }
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

  document.addEventListener('change', changeDisplay);

  const xValues = [100,200,300,400,500,600,700,800,900,1000];

  const myChart = new Chart("chart", {
    type: "line",
    data: {
      labels: xValues,
      datasets: [{
        data: [860,1140,1060,1060,1070,1110,1330,2210,7830,2478],
        borderColor: "red",
        fill: false
      },{
        data: [1600,1700,1700,1900,2000,2700,4000,5000,6000,7000],
        borderColor: "green",
        fill: false
      },{
        data: [300,700,2000,5000,6000,4000,2000,1000,200,100],
        borderColor: "blue",
        fill: false
      }]
    },
    options: {
      legend: {display: false}
    }
  });
};
