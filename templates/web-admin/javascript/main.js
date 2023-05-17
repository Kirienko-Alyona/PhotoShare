token = localStorage.getItem('accessToken')

async function DeleteContactShow(cnt_id) {
  const modal_form = document.getElementById("DeleteContact")
  const modal = new bootstrap.Modal(modal_form);

  const submit_btn = modal_form.querySelector(".btn-danger");
  submit_btn.onclick = async function () {
    if (await deleteContact(cnt_id))
      modal.hide();
  };
  modal.show();
}

async function EditContactShow(cnt_id) {
  const modal_form = document.getElementById("EditContact")
  const modal = new bootstrap.Modal(modal_form);
  if (cnt_id === "") {
    modal_form.querySelector("#first_name").value = "";
    modal_form.querySelector("#last_name").value = "";
    modal_form.querySelector("#birthday").value = "";
    modal_form.querySelector("#email").value = "";
    modal_form.querySelector("#phones").value = "";
    modal_form.querySelector("#address").value = "";
  }
  else{
    const response = await getContact(cnt_id);
    if (response.ok === true) {
      const contact = await response.json();
      modal_form.querySelector("#first_name").value = contact.first_name;
      modal_form.querySelector("#last_name").value = contact.last_name;
      modal_form.querySelector("#birthday").value = contact.birthday;
      modal_form.querySelector("#email").value = contact.email;
      modal_form.querySelector("#phones").value = phones_to_str(contact.phones);
      modal_form.querySelector("#address").value = contact.address;
    } else {
      const error = await response.json();
      alert(error.detail);
      return;
    }
  }
}

async function getContact(id) {
  const token = localStorage.getItem('accessToken');

  return(await fetch(`/api/contacts/${id}`, {
    method: "GET",
    headers: {
      "Accept": "application/json",
      Authorization: `Bearer ${token}`,
    }
  }));
}

function new_table_row(user) {
  let tr = document.createElement("tr");
  tr.setAttribute("data-rowid", user.id);
  tr.className = "table-secondary";
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
  button.innerHTML = "<span class=\'btn-label\'><i class=\'fa fa-user-edit\'>Edit</i></span>";
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
  button.innerHTML = "<span class=\'btn-label\'><i class=\'fa fa-user-minus\'>Delete</i></span>";
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