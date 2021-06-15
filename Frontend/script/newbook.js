const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);



const listenToUI = function () {
  const saveBtn = document.querySelector('.js-save')
  saveBtn.addEventListener("click", function () {
    console.log('btn save pressed');
    let inchamber;
    if (document.querySelector("#no").checked){
      inchamber = 0
    }
    if (document.querySelector("#yes").checked){
      inchamber = 1
    }
    let title = document.querySelector("#title").value;
    let firstname = document.querySelector("#fname").value;
    let lastname = document.querySelector("#lname").value;
    let language = document.querySelector("#language").value;
    let pages = document.querySelector("#pages").value;
    let isbn = document.querySelector("#isbn").value;
    let rfid = document.querySelector("#rfid").value;
    if (title != '' & firstname != '' & lastname != 0 & language != '' & pages != '' & isbn != '' & rfid != ''){
      const jsonObject = {
      title: title,
      firstname: firstname,
      lastname: lastname,
      language: language,
      pages: pages,
      isbn: isbn,
      rfid: rfid,
      inchamber: inchamber
    }
    console.log(jsonObject);
    socket.emit("F2B_savebook", {"book":jsonObject});
    }
    
  });
};

const listenToSocket = function () {
  socket.on("connected", function () {
    console.log("verbonden met socket webserver");
    
  });

  socket.on("B2F_rfidtag", function(jsonObject){
      console.log(jsonObject);
      document.querySelector("#rfid").value = jsonObject.tag;
  });

  socket.on("B2F_savebook", function(jsonObject){
    if (jsonObject['status']=='succes'){
      window.location.href = window.location.origin +"/books.html" 
    }
  })
};

document.addEventListener("DOMContentLoaded", function () {
  console.info("DOM geladen");
  socket.emit("F2B_rfidtag");
  listenToSocket();
  listenToUI();
});
