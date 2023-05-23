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
    if (anc.tagName === "PRE" || anc.tagName === "CODE") {
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

const drawCharts = () => {
  const statCharts = document.getElementById("statistics-charts");
  const str_data = statCharts.dataset.chart.replaceAll("'", '"');
  const chart_data = JSON.parse(str_data);

  var files = Object.keys(chart_data);

  files.forEach((file) => {
    const div = document.createElement("div");
    div.className = "w-75 shadow";

    const chart_name = document.createElement("p");
    chart_name.innerText = file;
    chart_name.className = "bg-success bg-gradient p-1 mb-1 rounded-1 text-wrap text-break text-white fs-6"; 

    const chart_box = document.createElement("p");
    chart_box.className = "d-flex flex-row p-1";

    const canvas = document.createElement("canvas");
    canvas.id = `chart?${file}`;
    canvas.className = "w-100 p-1";

    // const information = document.createElement("ul");
    // information.className = "p-3 m-3 ms-auto"
    // information.innerHTML = "<li>comments</li> <li>lines of code</li> <li>complexity</li> <li>instability</li>";

    chart_box.appendChild(canvas);
    div.appendChild(chart_name);
    div.appendChild(chart_box);
    statCharts.appendChild(div);

    // draw charts
    const dates = chart_data[file]["created"];

    const chart = new Chart(canvas, {
      type: "line",
      data: {
        labels: dates,
        datasets: [{
          data: chart_data[file]["comment"],
          borderColor: "red",
          label: "comments",
          fill: false
        }, {
          data: chart_data[file]["loc"],
          borderColor: "green",
          label: "lines of code",
          fill: false
        }, {
          data: chart_data[file]["complexity"],
          borderColor: "blue",
          label: "cyclomatic complexity",
          fill: false
        }, {
          data: chart_data[file]["inst"],
          borderColor: "purple",
          label: "instability",
          fill: false
        }]
      },
      options: {
        legend: { display: false }
      }
    });
  })
};


/** Add event listeners on load */
window.onload = () => {
  document.getElementById("sidebar").addEventListener("click", makeActive);

  const stat_headers = document.querySelectorAll(`[id^="stat-box-header"]`);
  stat_headers.forEach((s) => {
    s.addEventListener('click', toggleCodeDisplayOnCLick);
  });

  document.addEventListener('click', hideCodeOnClick);

  document.addEventListener('change', changeDisplay);

  drawCharts();

};
