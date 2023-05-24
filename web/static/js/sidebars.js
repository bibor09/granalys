/* global bootstrap: false */
(() => {
  'use strict'
  const tooltipTriggerList = Array.from(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  tooltipTriggerList.forEach(tooltipTriggerEl => {
    new bootstrap.Tooltip(tooltipTriggerEl)
  })
})()

/* Highlight active branch */
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
const changeDisplay = function (event) {
  if (event.target.id != "choose-display") {
    return;
  }

  const selectDisplay = document.getElementById('choose-display');
  const selectedValue = selectDisplay.value;

  const stats = document.getElementById('statistics');
  const charts = document.getElementById('chart-main');

  if (selectedValue === "files") {
    stats.style.cssText = 'display:flex !important';
    charts.style.cssText = 'display:none !important';
  } else if (selectedValue === "charts") {
    stats.style.cssText = 'display:none !important';
    charts.style.cssText = 'display:flex !important';
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

//--------------- CHARTS --------------------------
const getDatesAfter = (fromDateStr, dates) => {
  const fromDate = Date.parse(fromDateStr);
  var newDates = [];

  dates.forEach(date => {
    const d = Date.parse(date);
    if( d >= fromDate){
      newDates.push(date);
    }
  });
  newDates.sort();

  return newDates;
};

const getsetOfDates = (chart_data) => {
  var files = Object.keys(chart_data);
  var set_of_dates = [];

  files.forEach(file => {
    const dates = chart_data[file]["created"];
    dates.forEach(date => {
      if (!set_of_dates.includes(date)) {
        set_of_dates.push(date);
      }
    });
  });

  return set_of_dates;
};

/** Fill Select list with date options */
const fillWithDates = (chart_data) => {
  const chooseDate = document.getElementById("choose-date");

  // TODO: error handling in case of empty data
  const dates = getsetOfDates(chart_data);
  dates.sort();

  dates.forEach((date) => {
    const dateOption = document.createElement("option");
    dateOption.innerText = date;
    dateOption.value = date;
    chooseDate.appendChild(dateOption);
  });

}

const drawChart = (canvas, dates, chart_data, file) => {
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
  return chart;
};

// Initialize Charts
const initCharts = () => {
  const statCharts = document.getElementById("statistics-charts");
  const str_data = statCharts.dataset.chart.replaceAll("'", '"');
  const chart_data = JSON.parse(str_data);

  var files = Object.keys(chart_data);
  var charts = {}

  files.forEach((file) => {
    const div = document.createElement("div");
    div.className = "shadow p-2 m-4";
    div.style.width = "90%";

    const chart_name = document.createElement("p");
    chart_name.innerText = file;
    chart_name.className = "chart-header bg-gradient p-2 mb-1 rounded-1 text-wrap text-break text-white fs-6"; 

    const chart_box = document.createElement("div");
    chart_box.className = "d-flex flex-row p-1";

    const canvas = document.createElement("canvas");
    canvas.id = `chart?${file}`;
    canvas.className = "p-1";

    chart_box.appendChild(canvas);
    div.appendChild(chart_name);
    div.appendChild(chart_box);
    statCharts.appendChild(div);

    const dates = chart_data[file]["created"];
    charts[`${file}`] = drawChart(canvas, dates, chart_data, file);
  })

  return [chart_data, charts];
};

// TODO: error handling in case of empty data
const redrawCharts = (event, chart_data, charts) => {
  if (event.target.id != "choose-date") {
    return;
  }

  const fromSelectedDate = document.getElementById('choose-date').value;

  var files = Object.keys(chart_data);

  files.forEach((file) => {
    const fileCanvas = document.getElementById(`chart?${file}`);

    const dates = getDatesAfter(fromSelectedDate, chart_data[file]["created"]);
    charts[`${file}`].destroy()
    charts[`${file}`] = drawChart(fileCanvas, dates, chart_data, file);
  })
};

// ------------- CHECKBOXES -----------
const displayMetrics = (event) => {
  const idk = document.getElementById('metric?comment');
  const idk2 = document.getElementById('check?comment');

};

// ------------- ON LOAD --------------
/** Add event listeners on load */
window.onload = () => {
  document.getElementById("sidebar").addEventListener("click", makeActive);

  const stat_headers = document.querySelectorAll(`[id^="stat-box-header"]`);
  stat_headers.forEach((s) => {
    s.addEventListener('click', toggleCodeDisplayOnCLick);
  });

  document.addEventListener('click', hideCodeOnClick);

  document.addEventListener('change', changeDisplay);

  const [chart_data, charts] = initCharts();
  fillWithDates(chart_data);
  document.addEventListener('change', (event) => {redrawCharts(event, chart_data, charts)});

};
