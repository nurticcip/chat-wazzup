document.addEventListener('DOMContentLoaded', function () {
    console.log('Profile modal initialized');

    setupEventListeners();

    let isDarkTheme = localStorage.getItem('darkTheme') === 'true';
    if (isDarkTheme) {
        document.body.classList.add('dark-theme');
    }

    window.parent.postMessage({ type: 'requestUserData' }, '*');
});

function setupEventListeners() {
    const cancelBtn = document.getElementById('cancel-btn');
    const saveBtn = document.getElementById('save-btn');
    const avatarInput = document.getElementById('avatar-input');
    const changeAvatarBtn = document.getElementById('change-avatar-btn');
    const avatarImg = document.getElementById('avatar-img');

    if (cancelBtn) {
        cancelBtn.addEventListener('click', function () {
            window.parent.postMessage('closeProfileModal', '*');
        });
    }

    if (saveBtn) {
        saveBtn.addEventListener('click', function () {
            const nameInput = document.getElementById('user-name');
            const emailInput = document.getElementById('email');
            const passwordInput = document.getElementById('password');

            const userData = {
                name: nameInput.value.trim(),
                email: emailInput.value.trim(),
                password: passwordInput.value.trim(),
                avatar: avatarImg.src
            };

            if (!userData.name || !userData.email) {
                alert('Name and email are required!');
                return;
            }

            localStorage.setItem('userProfile', JSON.stringify(userData));
            window.parent.postMessage({ type: 'updateUserProfile', data: userData }, '*');
            window.parent.postMessage('closeProfileModal', '*');
        });
    }

    if (changeAvatarBtn && avatarInput) {
        changeAvatarBtn.addEventListener('click', function () {
            avatarInput.click();
        });
    }

    if (avatarInput && avatarImg) {
        avatarInput.addEventListener('change', function (event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    avatarImg.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    window.addEventListener('message', function (event) {
        console.log('Profile modal received message:', event.data);

        if (event.data && event.data.type === 'userData') {
            const userData = event.data.data;
            document.getElementById('user-name').value = userData.name || '';
            document.getElementById('email').value = userData.email || '';
            document.getElementById('avatar-img').src = userData.avatar || 'images/avatar.png';
        }

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