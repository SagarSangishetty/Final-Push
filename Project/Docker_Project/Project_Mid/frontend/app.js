async function loadUsers() {
    const res = await fetch('/api/users');
    const data = await res.json();

    const list = document.getElementById("list");
    list.innerHTML = "";

    (data.users || []).forEach(u => {
        const li = document.createElement("li");
        li.innerText = u;
        list.appendChild(li);
    });
}

async function addUser() {
    const name = document.getElementById("username").value;
    await fetch(`/api/users/${name}`, {method:'POST'});
    loadUsers();
}

loadUsers();