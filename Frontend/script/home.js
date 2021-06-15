const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

let fanBtnHTML, lockBtnHtml;
let tableBooks

const listenToUI = function () {
      const fanBtn = document.querySelector(".js-fan-btn");
        fanBtn.addEventListener("click", function () {
            console.log('btn fan pressed');
            const id = this.dataset.idcomponent
            // console.log(id);
            socket.emit("F2B_change_fan", { "component_id": id});
        });
      // const lockBtn = document.querySelector(".js-lock-btn");
      //   lockBtn.addEventListener("click", function () {
      //       console.log('btn lock pressed');
      //       const id = this.dataset.idcomponent
      //       // console.log(id);
      //       socket.emit("F2B_change_lock", { "component_id": id});
      //   });
    };

const listenToSocket = function () {
  socket.on("connected", function () {
    console.log("verbonden met socket webserver");
  });

  socket.on("B2F_books_in_chamber", function (jsonObject) {
    tableBooks = document.querySelector(".js-books")
    let tableHTML = `
    <caption>Books present in chamber</caption>
    <tr>
    <th>Title</th>
     <th>Author</th>
    </tr>`;
    
    for(const row of jsonObject.books){
        tableHTML += `
        <tr class="c-row">
            <td>${row.Title}</td>
            <td>${row.FirstName} ${row.LastName}</td>
        </tr>`;
    }
    tableBooks.innerHTML = tableHTML
  });
      
  socket.on("B2F_get_fan_and_lock", function (jsonObject) {
    fanBtnHTML = document.querySelector(".js-fan-btn")
    // lockBtnHTML = document.querySelector(".js-lock-btn")
    console.log(jsonObject);
    if(jsonObject.fan[0]['Action']==0){
      fanBtnHTML.innerHTML = "Activate Fan"
    }
    else if(jsonObject.fan[0]['Action']==1){
      fanBtnHTML.innerHTML = "Deactivate Fan"
    }

    // if(jsonObject.lock[0]['Action']==0){
    //   lockBtnHTML.innerHTML = "Open Lock"
    // }
    // else if(jsonObject.lock[0]['Action']==1){
    //   lockBtnHTML.innerHTML = "Close Lock"
    // }

  });
      
  socket.on("B2F_current_stats", function (jsonObject){
    console.log(jsonObject);
    temperature = jsonObject.temperature[0]['Value']
    tempHTML = document.querySelector(".js-temp")
    let stringTemp = `${temperature} °C`
    tempHTML.innerHTML = stringTemp

    humidity = jsonObject.humidity[0]['Value']
    humidHTML = document.querySelector(".js-humid")
    let stringHumid = `${humidity} %`
    humidHTML.innerHTML = stringHumid

    luminosity = jsonObject.luminosity[0]['Value']
    luminHTML = document.querySelector(".js-lumin")
    let stringLumin = `${luminosity} %`
    luminHTML.innerHTML = stringLumin
  } );

  socket.on("B2F_change_fan", function(jsonObject){
    console.log(jsonObject);
    fanBtnHTML = document.querySelector(".js-fan-btn")
    if (jsonObject.fan == 0){
      fanBtnHTML.innerHTML = "Activate Fan"
    }
    else if (jsonObject.fan == 1){
      fanBtnHTML.innerHTML = "Deactivate Fan"
    }
  })

  // socket.on("B2F_change_lock", function(jsonObject){
  //   console.log(jsonObject);
  //   lockBtnHTML = document.querySelector(".js-lock-btn")
  //   if (jsonObject.lock == 0){
  //     lockBtnHTML.innerHTML = "Open Lock"
  //   }
  //   else if (jsonObject.lock == 1){
  //     lockBtnHTML.innerHTML = "Close Lock"
  //   }
  // })
};
      
document.addEventListener("DOMContentLoaded", function () {
  console.info("DOM geladen");
  socket.emit("F2B_get_current_stats")
  socket.emit("F2B_get_fan_and_lock");
  socket.emit("F2B_books_in_chamber")
  listenToUI();
  listenToSocket();
});