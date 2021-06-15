const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);



const listenToUI = function () {
  
};

const listenToSocket = function () {
  socket.on("connected", function () {
    console.log("verbonden met socket webserver");
  });

  socket.on("B2F_get_all_books_and_authors", function (jsonObject) {
    console.log("These are all the books");
    console.log(jsonObject);
    const grid = document.querySelector(".js-books");
    let tableHTML = ``;
    
    for(const row of jsonObject.books){
      
        tableHTML += `
        <article class="js-book o-layout__item u-1-of-2 u-1-of-3-bp1 u-1-of-4-bp2" data-idbook=${row.BookID} data-idauthor=${row.AuthorID}>
              <img class="c-figure" src="${row.ImgPath}" alt="cover of ${row.Title}">
              <div class="c-figure-title">${row.Title}</div>
              <div class="c-figure-author">${row.FirstName} ${row.LastName}</div>
            </article>`;
    }
    // console.log(tableHTML);
    grid.innerHTML = tableHTML;
  });

  };

document.addEventListener("DOMContentLoaded", function () {
  console.info("DOM geladen");
  socket.emit("F2B_get_all_books_and_authors");
  listenToSocket();
  listenToUI();
});
