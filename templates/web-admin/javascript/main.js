token = localStorage.getItem('accessToken')

function new_table_row(user) {
  let tr = document.createElement("tr");
  tr.setAttribute("data-rowid", user.id);
  let td = document.createElement("td");
  td.className = "text-end";
  td.innerHTML = user.id;
  tr.append(td);
  td = document.createElement("td");
  td.className = "text-start";
  td.innerHTML = user.full_name;
  tr.append(td);
  td = document.createElement("td");
  td.className = "text-start";
  if (user.birthday)
    td.innerHTML = user.birthday.split("-").reverse().join(".");
  else
    td.innerHTML = "";
  tr.append(td);
  td = document.createElement("td");
  td.className = "text-start";
  td.innerHTML = user.email;
  tr.append(td);

  td = document.createElement("td");

  let button = document.createElement("button");
  button.className = "btn btn-outline-secondary btn-edit";
  button.innerHTML = "<span class=\'btn-label\'><i class=\'fa fa-user-edit\'></i></span>";
  button.setAttribute("style", "--bs-btn-padding-y: .2rem; --bs-btn-padding-x: .5rem; " +
    "--bs-btn-font-size: .75rem;");
  button.onclick = async function() {
    await EditContactShow(user.id);
  }
  td.append(button);
  tr.append(td);

  td = document.createElement("td");
  button = document.createElement("button");
  button.className = "btn btn-outline-secondary btn-delete";
  button.innerHTML = "<span class=\'btn-label\'><i class=\'fa fa-user-minus\'></i></span>";
  button.setAttribute("style", "--bs-btn-padding-y: .2rem; --bs-btn-padding-x: .5rem; " +
    "--bs-btn-font-size: .75rem;");
  button.onclick = async function() {
    await DeleteContactShow(user.id);
  }

  td.append(button);
  tr.append(td);

  return tr;
}


window.addEventListener('load', function(){
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState === 4 && this.status === 200) {
      // Код, що потрібно виконати, якщо запит успішний
      var result = JSON.parse(this.responseText);
      var users = document.getElementById("userlist");
      for (user of result) {
        var tr = new_table_row(user)
        users.appendChild(tr)
      }
    }
  };
  xhttp.open('GET', 'http://localhost:8000/api/users/', true);
  xhttp.setRequestHeader('Authorization', 'Bearer ' + localStorage.getItem('accessToken')
  );
  
  xhttp.send();
});


/** contactCreate.addEventListener('submit', async (e) => {
  e.preventDefault()
  const response = await fetch('http://localhost:8000/api/contacts', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      name: contactCreate.name.value,
      surname: contactCreate.surname.value,
      email: contactCreate.email.value,
      phone: contactCreate.phone.value,
      born_date: contactCreate.born_date.value
    }),
  })
  if (response.status === 201) {
    console.log('Ви успішно створили новий контакт')
    get_contacts()
  }
}) */