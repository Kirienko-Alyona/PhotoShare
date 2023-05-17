token = localStorage.getItem('accessToken')

async function editUser(user_id) {
  const birthday = document.getElementById("birthday").value;
  const last_name = document.getElementById("last_name").value;
  const address = document.getElementById("address").value;

  const token = localStorage.getItem('accessToken');

  const response = await fetch(`/api/users/${user_id}`, {
    method: (user_id === "" ? "POST" : "PUT"),
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({
      first_name: document.getElementById("first_name").value,
      birthday: birthday ? birthday : null,
      email: document.getElementById("email").value,
    })
  });
  if (response.ok === true) {
    const user = await response.json();
    if (user_id === "")
      document.querySelector("tbody").append(new_table_row(user));
    else
      document.querySelector(`tr[data-rowid='${user.id}']`).replaceWith(new_table_row(user));
  }
  else {
    if (response.status === 401)
      alert("Not authenticated");
    else if (response.status === 422)
      alert("Input data is invalid");
    else {
      const error = await response.json();
      alert(error.detail);
    }
  }
  return response.ok;
}

async function deleteUser(id) {
  const token = localStorage.getItem('accessToken');

  const response = await fetch(`/api/users/${id}`, {
    method: "DELETE",
    headers: {
      "Accept": "application/json",
      Authorization: `Bearer ${token}`
    },

  });
  if (response.ok === true) {
    document.querySelector(`tr[data-rowid='${id}']`).remove();
  }
  else {
    if (response.status === 401)
      alert("Not authenticated");
    else {
      const error = await response.json();
      alert(error.detail);
    }
  }
  return response.ok;
}

async function DeleteUserShow(user_id) {
  const modal_form = document.getElementById("DeleteUser")
  const modal = new bootstrap.Modal(modal_form);

  const submit_btn = modal_form.querySelector(".btn-danger");
  submit_btn.onclick = async function () {
    if (await deleteUser(user_id))
      modal.hide();
  };
  modal.show();
}

async function EditUserShow(user_id) {
  const modal_form = document.getElementById("EditUser")
  const modal = new bootstrap.Modal(modal_form);
  if (user_id === "") {
    modal_form.querySelector("#first_name").value = "";
    modal_form.querySelector("#last_name").value = "";
    modal_form.querySelector("#birthday").value = "";
    modal_form.querySelector("#email").value = "";
    modal_form.querySelector("#phones").value = "";
    modal_form.querySelector("#address").value = "";
  }
  else{
    const response = await getUser(user_id);
    if (response.ok === true) {
      const user = await response.json();
      modal_form.querySelector("#first_name").value = user.first_name;
      modal_form.querySelector("#birthday").value = user.birthday;
      modal_form.querySelector("#email").value = user.email;
    } else {
      const error = await response.json();
      alert(error.detail);
      return;
    }
  }
  const submit_btn = modal_form.querySelector(".btn-primary");
  submit_btn.onclick = async function () {
    if (await editUser(user_id))
      modal.hide();
  };
  modal.show();
}

async function getUser(id) {
  const token = localStorage.getItem('accessToken');

  return(await fetch(`/api/users/${id}`, {
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
    await EditUserShow(user.id);
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
    await DeleteUserShow(user.id);
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


/** userCreate.addEventListener('submit', async (e) => {
  e.preventDefault()
  const response = await fetch('http://localhost:8000/api/users', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      name: userCreate.name.value,
      surname: userCreate.surname.value,
      email: userCreate.email.value,
      phone: userCreate.phone.value,
      born_date: userCreate.born_date.value
    }),
  })
  if (response.status === 201) {
    console.log('Ви успішно створили новий контакт')
    get_users()
  }
}) */