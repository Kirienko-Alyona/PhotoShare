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

get_contacts()

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