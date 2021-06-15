const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

function addZero(i) {
  if (i < 10) {
    i = "0" + i;
  }
  return i;
}
const showTempChart = function(data){
  console.log(data);

  let converted_labels = [];
  let converted_data = [];
  for (const row of data){
    // console.log(row);
    date = new Date(row['EntryDate'])
    converted_labels.push(`${addZero(date.getHours())}:${addZero(date.getMinutes())}`);
    converted_data.push(row['Value']);
  }
  drawTempChart(converted_labels,converted_data)
}


const drawTempChart = function(labels, data){
  let ctx = document.getElementById('temperatureChart').getContext('2d');

  let config = {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label : 'Temperature',
          backgroundColor: '#EBEDF2',
          borderColor: '#14213D',
          data: data,
          fill: true,
          
        }
      ]
    },
    options: {
      responsive: true,
      title: {
        display: false,
        text: 'Temperature'
      },
      tooltips: {
        mode: 'index',
        intersect: true
      },
      hover: {
        mode: 'nearest',
        intersect: true
      },
      scales: {
        xAxes: [
          {
            display: true,
            scaleLabel: {
              display: true,
              labelString: 'Time'
            },
            ticks: {
              maxTicksLimit: 12
            }
          }
        ],
        yAxes: [
          {
            display: true,
            scaleLabel: {
              display: true,
              labelString: '°C'
            },
            ticks: {
              suggestedMin: 0,
              suggestedMax: 40
            }
          }
        ]
      }
    }
  };
  let TempChart = new Chart(ctx, config)
};

const showHumidChart = function(data){
  console.log(data);

  let converted_labels = [];
  let converted_data = [];
  for (const row of data){
    // console.log(row);
    date = new Date(row['EntryDate'])
    converted_labels.push(`${addZero(date.getHours())}:${addZero(date.getMinutes())}`);
    converted_data.push(row['Value']);
  }
  drawHumidChart(converted_labels,converted_data)
}


const drawHumidChart = function(labels, data){
  let ctx = document.getElementById('humidityChart').getContext('2d');

  let config = {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label : 'Humidity',
          backgroundColor: '#EBEDF2',
          borderColor: '#14213D',
          data: data,
          fill: true,
          
        }
      ]
    },
    options: {
      responsive: true,
      title: {
        display: false,
        text: 'Humidity'
      },
      tooltips: {
        mode: 'index',
        intersect: true
      },
      hover: {
        mode: 'nearest',
        intersect: true
      },
      scales: {
        xAxes: [
          {
            display: true,
            scaleLabel: {
              display: true,
              labelString: 'Time'
            },
            ticks: {
              maxTicksLimit: 12
            }
          }
        ],
        yAxes: [
          {
            display: true,
            scaleLabel: {
              display: true,
              labelString: 'Percentage'
            },
            ticks: {
              suggestedMin: 0,
              suggestedMax: 100
            }
          }
        ]
      }
    }
  };
  let HumidChart = new Chart(ctx, config)
};

const showChart = function(data){
  console.log(data);

  let converted_labels = [];
  let converted_data = [];
  for (const row of data){
    // console.log(row);
    date = new Date(row['EntryDate'])
    converted_labels.push(`${addZero(date.getHours())}:${addZero(date.getMinutes())}`);
    converted_data.push(row['Value']);
  }
  drawChart(converted_labels,converted_data)
}
const drawChart = function(labels, data){
  let ctx = document.getElementById('lightChart').getContext('2d');

  let config = {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label : 'Luminance',
          backgroundColor: '#EBEDF2',
          borderColor: '#14213D',
          data: data,
          fill: true,
          
        }
      ]
    },
    options: {
      responsive: true,
      title: {
        display: false,
        text: 'Luminance'
      },
      tooltips: {
        mode: 'index',
        intersect: true
      },
      hover: {
        mode: 'nearest',
        intersect: true
      },
      scales: {
        xAxes: [
          {
            display: true,
            scaleLabel: {
              display: true,
              labelString: 'Time'
            },
            ticks: {
              maxTicksLimit: 12
            }
          }
        ],
        yAxes: [
          {
            display: true,
            scaleLabel: {
              display: true,
              labelString: 'Percentage'
            },
            ticks: {
              suggestedMin: 0,
              suggestedMax: 100
            }
          }
        ]
      }
    }
  };
  let lightChart = new Chart(ctx, config)
};

const listenToUI = function () {
  // const knop = document.querySelector(".js-power-btn");
  //   knop.addEventListener("click", function () {
  //       console.log('btn pressed');
  //       socket.emit("F2B_get_light");
  //   });
  // const knopdht = document.querySelector(".js-dht-btn");
  //   knopdht.addEventListener("click", function () {
  //       console.log('btn pressed');
  //       socket.emit("F2B_get_temperature_and_humidity");
  //   });

  };
  
const listenToSocket = function () {
  socket.on("connected", function () {
    console.log("verbonden met socket webserver");
  });

  socket.on("B2F_light_history", function (jsonObject) {
    console.log("This is the history of the amount of light");
    // console.log(jsonObject);
    // const table = document.querySelector(".js-tablelight");
    // let tableHTML = `
    // <tr>
    // <th>Date</th>
    // <th>Time</th>
    // <th>Amount of light</th>
    // </tr>`;
    
    // for(const row of jsonObject.lights){
    //     let date = new Date(row.EntryDate)
    //     tableHTML += `
    //     <tr class="c-row">
    //         <td>${date.getFullYear()}-${addZero(date.getMonth())}-${addZero(date.getDay())}</td>
    //         <td>${addZero(date.getHours())}:${addZero(date.getMinutes())}:${addZero(date.getSeconds())}</td>
    //         <td>${row.Value} %</td>
    //     </tr>`;
    // }
    // table.innerHTML = tableHTML
    showChart(jsonObject.today)
  });
  socket.on("B2F_temperature_and_humidity_history", function (jsonObject) {
    console.log("This is the history of the temperature");
    showTempChart(jsonObject.today)
    console.log('This is the history of humidity')
    showHumidChart(jsonObject.humiditytoday)
  });
  };

document.addEventListener("DOMContentLoaded", function () {
  console.info("DOM geladen");
  socket.emit("F2B_get_light");
  socket.emit("F2B_get_temperature_and_humidity");
  // listenToUI();
  listenToSocket();
})
