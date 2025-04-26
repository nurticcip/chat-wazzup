document.addEventListener('DOMContentLoaded', function () {
    console.log('New Contact modal initialized');

    setupEventListeners();

    let isDarkTheme = localStorage.getItem('darkTheme') === 'true';
    if (isDarkTheme) {
        document.body.classList.add('dark-theme');
    }
});

function setupEventListeners() {
    const cancelBtn = document.querySelector('.cancel-btn');
    const saveBtn = document.querySelector('.save-btn');
    const firstNameInput = document.getElementById('first-name');
    const lastNameInput = document.getElementById('last-name');
    const emailInput = document.getElementById('email');

    if (cancelBtn) {
        cancelBtn.addEventListener('click', function () {
            window.parent.postMessage('closeContactModal', '*');
        });
    }

    if (saveBtn) {
        saveBtn.addEventListener('click', function () {
            const firstName = firstNameInput.value.trim();
            const lastName = lastNameInput.value.trim();
            const email = emailInput.value.trim();

            if (!firstName || !email) {
                alert('First name and email are required!');
                return;
            }

            const newContact = {
                firstName: firstName,
                lastName: lastName,
                email: email,
                photo: 'images/avatar.png'
            };

            const contacts = JSON.parse(localStorage.getItem('chatContacts') || '[]');
            contacts.push(newContact);
            localStorage.setItem('chatContacts', JSON.stringify(contacts));

            window.parent.postMessage('refreshChatList', '*');
            window.parent.postMessage('closeContactModal', '*');
        });
    }

    window.addEventListener('message', function (event) {
        console.log('New Contact modal received message:', event.data);

        if (event.data && event.data.type === 'toggleTheme') {
            const isDarkTheme = event.data.isDarkTheme;
            if (isDarkTheme) {
                document.body.classList.add('dark-theme');
            } else {
                document.body.classList.remove('dark-theme');
            }
        }
    });
}