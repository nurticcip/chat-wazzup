document.addEventListener('DOMContentLoaded', function () {
    console.log('New Group modal initialized');

    setupEventListeners();
    loadContacts();

    let isDarkTheme = localStorage.getItem('darkTheme') === 'true';
    if (isDarkTheme) {
        document.body.classList.add('dark-theme');
    }
});

function setupEventListeners() {
    const cancelBtn = document.querySelector('.cancel-btn');
    const saveBtn = document.querySelector('.save-btn');
    const groupNameInput = document.getElementById('group-name');
    const groupPhotoInput = document.getElementById('group-photo');
    const photoPlaceholder = document.querySelector('.photo-placeholder');
    const subgroupSection = document.querySelector('.subgroup-section');

    if (cancelBtn) {
        cancelBtn.addEventListener('click', function () {
            window.parent.postMessage('closeGroupModal', '*');
        });
    }

    if (saveBtn) {
        saveBtn.addEventListener('click', function () {
            const groupName = groupNameInput.value.trim();
            if (!groupName) {
                alert('Group name is required!');
                return;
            }

            const selectedContacts = Array.from(document.querySelectorAll('.contact-checkbox:checked')).map(checkbox => parseInt(checkbox.dataset.index));
            const contacts = JSON.parse(localStorage.getItem('chatContacts') || '[]');
            const groupMembers = selectedContacts.map(index => contacts[index]);

            const newGroup = {
                name: groupName,
                members: groupMembers,
                photo: photoPlaceholder.querySelector('img').src === 'images/camera.png' ? 'images/group-icon.png' : photoPlaceholder.querySelector('img').src
            };

            const groups = JSON.parse(localStorage.getItem('chatGroups') || '[]');
            groups.push(newGroup);
            localStorage.setItem('chatGroups', JSON.stringify(groups));

            window.parent.postMessage('refreshChatList', '*');
            window.parent.postMessage('closeGroupModal', '*');
        });
    }

    if (groupPhotoInput && photoPlaceholder) {
        photoPlaceholder.addEventListener('click', function () {
            groupPhotoInput.click();
        });

        groupPhotoInput.addEventListener('change', function (event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    const img = photoPlaceholder.querySelector('img');
                    img.src = e.target.result;
                    img.classList.remove('camera-icon');
                };
                reader.readAsDataURL(file);
            }
        });
    }

    if (subgroupSection) {
        subgroupSection.addEventListener('click', function () {
            alert('Subgroup creation coming soon!');
        });
    }

    window.addEventListener('message', function (event) {
        console.log('New Group modal received message:', event.data);

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

function loadContacts() {
    const contactsList = document.querySelector('.contacts-list');
    const contacts = JSON.parse(localStorage.getItem('chatContacts') || '[]');

    if (contacts.length === 0) {
        contactsList.innerHTML = '<div class="no-contacts">No contacts available</div>';
        return;
    }

    contacts.forEach((contact, index) => {
        const contactDiv = document.createElement('div');
        contactDiv.className = 'contact-item';

        const fullName = `${contact.firstName || ''} ${contact.lastName || ''}`.trim();
        const photo = contact.photo || 'images/avatar.png';

        contactDiv.innerHTML = `
            <input type="checkbox" class="contact-checkbox" data-index="${index}">
            <div class="contact-avatar">
                <img src="${photo}" alt="${fullName}">
            </div>
            <div class="contact-info">
                <div class="contact-name">${fullName}</div>
            </div>
        `;

        contactsList.appendChild(contactDiv);
    });
}