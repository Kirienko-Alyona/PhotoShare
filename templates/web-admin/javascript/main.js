token = localStorage.getItem('accessToken')

const get_contacts = async () => {
  const response = await fetch('http://localhost:8000/api/contacts', {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
  console.log(response.status, response.statusText)
  if (response.status === 200) {
    result = await response.json()
    for (contact of result) {
      el = document.createElement('li')
      el.className = 'list-group-item'
      el.innerHTML = `ID: ${contact.id} name: <b>${contact.name}</b> surname: ${contact.name} email: ${contact.email} phone: ${contact.phone} born_date: ${contact.born_date}`
      contacts.appendChild(el)
    }
  }
}



window.addEventListener('load', function(){
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState === 4 && this.status === 200) {
      // Код, що потрібно виконати, якщо запит успішний
      var result = JSON.parse(this.responseText);
      //  var data = xmlhttp.responseText;
      for (contact of result) {
        el = document.createElement('li')
        el.className = 'list-group-item'
        el.innerHTML = `ID: ${user.id} first_name: <b>${first_name}</b> username: ${username} email: ${email} password: ${password} birthday: ${birthday} refresh_token: ${refresh_token} avatar: ${avatar} roles: ${roles} confirmed: ${confirmed} active: ${active} created_at: ${created_at} updated_at: ${updated_at}`
        contacts.appendChild(el)
      }
    }
  };
  xhttp.open('GET', 'http://localhost:8000/api/users/me', true);
  xhttp.setRequestHeader('Authorization', 'Bearer ' + localStorage.getItem('accessToken')
  );
  
  xhttp.send();
});


contactCreate.addEventListener('submit', async (e) => {
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
})