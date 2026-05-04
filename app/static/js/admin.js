document.addEventListener('DOMContentLoaded', function() {
    // ================= 1. ГЛОБАЛЬНАЯ ФУНКЦИЯ УВЕДОМЛЕНИЙ =================
    window.showToast = function(message, type = 'info', duration = 5000) {
        let notifications = document.querySelector('.notifications');
        if (!notifications) {
            notifications = document.createElement('div');
            notifications.className = 'notifications';
            document.body.appendChild(notifications);
        }
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        notifications.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'toast-out 0.5s ease forwards';
            setTimeout(() => toast.remove(), 500);
        }, duration);
    };

    // Инициализация СЕРВЕРНЫХ уведомлений (Jinja flash messages)
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach((toast, index) => {
        toast.style.animationDelay = `${index * 0.2}s`;
        setTimeout(() => {
            toast.style.animation = 'toast-out 0.5s ease forwards';
            setTimeout(() => toast.remove(), 500);
        }, 5000);
    });

    // ================= 2. ИНИЦИАЛИЗАЦИЯ ТАБЛИЦЫ (Анимация и Подсветка) =================
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach((row, index) => {
        // Задержка появления
        row.style.animationDelay = `${index * 0.05}s`;

        // Эффект при наведении на строку (из старого кода)
        row.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });

        // Подсветка ролей при загрузке страницы
        const roleCell = row.querySelector('.user-role');
        if (roleCell) {
            const role = roleCell.textContent.trim().toLowerCase();
            switch(role) {
                case 'admin':
                    roleCell.style.color = '#ff6b6b';
                    roleCell.style.fontWeight = '600';
                    break;
                case 'moderator':
                    roleCell.style.color = '#4cff9a';
                    roleCell.style.fontWeight = '600';
                    break;
                default:
                    roleCell.style.color = '#aaa';
            }
        }
    });

    // ================= 3. ЛОГИКА КАСТОМНОГО СЕЛЕКТА РОЛЕЙ В МОДАЛКЕ =================
    const selectWrapper = document.getElementById('roleSelectWrapper');
    let customSelectTrigger, customSelectText, hiddenSelect, customOptions;

    if (selectWrapper) {
        customSelectTrigger = selectWrapper.querySelector('.custom-select__trigger');
        customSelectText = document.getElementById('roleSelectText');
        hiddenSelect = document.getElementById('edit-role');
        customOptions = selectWrapper.querySelectorAll('.custom-option');

        customSelectTrigger.addEventListener('click', (e) => {
            e.stopPropagation();
            selectWrapper.classList.toggle('open');
        });

        customOptions.forEach(option => {
            option.addEventListener('click', function() {
                const value = this.dataset.value;
                hiddenSelect.value = value;
                customSelectText.textContent = value.charAt(0).toUpperCase() + value.slice(1);
                
                selectWrapper.classList.remove('open');
                
                customOptions.forEach(opt => opt.classList.remove('selected'));
                this.classList.add('selected');

                // Анимация выбора (из старого кода)
                this.style.transform = 'scale(0.95)';
                setTimeout(() => this.style.transform = 'scale(1)', 150);
            });
        });

        document.addEventListener('click', (e) => {
            if (!selectWrapper.contains(e.target)) {
                selectWrapper.classList.remove('open');
            }
        });
    }

    // ================= 4. ЛОГИКА МОДАЛЬНОГО ОКНА И КЛАВИАТУРЫ =================
    const modal = document.getElementById('editModal');
    const closeModalBtn = document.getElementById('closeModal');
    const editUserForm = document.getElementById('editUserForm');

    if (modal && editUserForm) {
        // Открытие модалки
        document.addEventListener('click', function(e) {
            if (e.target.closest('.btn-edit-user')) {
                const btn = e.target.closest('.btn-edit-user');
                
                document.getElementById('edit-user-id').value = btn.dataset.id;
                document.getElementById('edit-username').value = btn.dataset.username;
                document.getElementById('edit-email').value = btn.dataset.email;
                
                const balanceInput = document.getElementById('edit-balance');
                balanceInput.value = btn.dataset.balance;
                balanceInput.className = parseFloat(btn.dataset.balance) < 0 ? 'negative' : 'positive';
                
                document.getElementById('edit-txcount').value = btn.dataset.txcount;

                const currentRole = btn.dataset.role;
                hiddenSelect.value = currentRole;
                customSelectText.textContent = currentRole.charAt(0).toUpperCase() + currentRole.slice(1);
                customOptions.forEach(opt => {
                    opt.classList.toggle('selected', opt.dataset.value === currentRole);
                });

                modal.classList.add('active');
                
                // Фокус на первый инпут для удобства
                setTimeout(() => document.getElementById('edit-username').focus(), 100);
            }
        });

        const closeModal = () => {
            modal.classList.remove('active');
            if (selectWrapper) selectWrapper.classList.remove('open');
        };

        closeModalBtn.addEventListener('click', closeModal);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });

        // Глобальная обработка клавиатуры (Escape)
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                if (selectWrapper && selectWrapper.classList.contains('open')) {
                    selectWrapper.classList.remove('open');
                } else if (modal.classList.contains('active')) {
                    closeModal();
                }
            }
        });

        // Отправка формы по Enter
        editUserForm.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.ctrlKey && !e.shiftKey) {
                e.preventDefault();
                document.getElementById('saveUserBtn').click();
            }
        });

        // ================= 5. AJAX: РЕДАКТИРОВАНИЕ ПОЛЬЗОВАТЕЛЯ =================
        editUserForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitBtn = document.getElementById('saveUserBtn');
            const originalText = submitBtn.textContent;
            
            // Визуальный отклик кнопки (из старого кода)
            submitBtn.classList.add('loading');
            submitBtn.textContent = 'Сохранение...';
            submitBtn.disabled = true;

            const userId = document.getElementById('edit-user-id').value;
            const payload = {
                username: document.getElementById('edit-username').value,
                email: document.getElementById('edit-email').value,
                role: document.getElementById('edit-role').value
            };

            fetch(`/admin/edit/${userId}`, {
                method: 'POST', 
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                if (data.ok) {
                    showToast(data.message || 'Пользователь успешно обновлен', 'success');
                    closeModal();
                    
                    const row = document.querySelector(`tr[data-user-id="${userId}"]`);
                    if (row) {
                        row.querySelector('.user-username').textContent = payload.username;
                        row.querySelector('.user-email').textContent = payload.email;
                        
                        const roleCell = row.querySelector('.user-role');
                        roleCell.textContent = payload.role;
                        
                        roleCell.style.color = payload.role === 'admin' ? '#ff6b6b' : (payload.role === 'moderator' ? '#4cff9a' : '#aaa');
                        roleCell.style.fontWeight = payload.role !== 'user' ? '600' : 'normal';

                        const editBtn = row.querySelector('.btn-edit-user');
                        editBtn.dataset.username = payload.username;
                        editBtn.dataset.email = payload.email;
                        editBtn.dataset.role = payload.role;

                        row.style.background = 'rgba(76, 255, 154, 0.1)';
                        setTimeout(() => row.style.background = '', 1500);
                    }
                } else {
                    showToast(data.message || 'Ошибка при сохранении', 'error');
                }
            })
            .catch(err => {
                console.error(err);
                showToast('Ошибка сети', 'error');
            })
            .finally(() => {
                submitBtn.classList.remove('loading');
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            });
        });
    }

    // ================= 6. КАСТОМНОЕ ПОДТВЕРЖДЕНИЕ И AJAX: УДАЛЕНИЕ =================
    const deleteModal = document.getElementById('deleteConfirmModal');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const deleteUserNameSpan = document.getElementById('delete-user-name');

    let userToDelete = null; // Переменная для хранения данных удаляемого юзера

    if (deleteModal) {
        // 1. Открытие красивого окна удаления
        document.addEventListener('click', function(e) {
            if (e.target.closest('.btn-delete-user')) {
                const btn = e.target.closest('.btn-delete-user');
                
                // Запоминаем, кого удаляем
                userToDelete = {
                    id: btn.dataset.id,
                    username: btn.dataset.username,
                    row: btn.closest('tr')
                };

                // Вставляем имя в модалку и показываем её
                deleteUserNameSpan.textContent = `@${userToDelete.username}`;
                deleteModal.classList.add('active');
            }
        });

        // 2. Логика закрытия окна
        const closeDeleteModal = () => {
            deleteModal.classList.remove('active');
            userToDelete = null;
        };

        cancelDeleteBtn.addEventListener('click', closeDeleteModal);
        
        deleteModal.addEventListener('click', (e) => {
            if (e.target === deleteModal) closeDeleteModal();
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && deleteModal.classList.contains('active')) {
                closeDeleteModal();
            }
        });

        // 3. Отправка AJAX запроса при подтверждении
        confirmDeleteBtn.addEventListener('click', function() {
            if (!userToDelete) return;

            const originalHtml = confirmDeleteBtn.innerHTML;
            confirmDeleteBtn.innerHTML = 'Удаление...';
            confirmDeleteBtn.disabled = true;

            fetch(`/admin/delete/${userToDelete.id}`, {
                method: 'POST',
                headers: { 'Accept': 'application/json' }
            })
            .then(res => res.json())
            .then(data => {
                if (data.ok) {
                    showToast(data.message || 'Пользователь удален', 'success');
                    
                    // 1. СОХРАНЯЕМ ссылку на строку, пока userToDelete еще не очищен!
                    const rowToRemove = userToDelete.row;
                    
                    // 2. Прячем модалку (здесь userToDelete становится null)
                    closeDeleteModal();

                    // 3. Плавно удаляем сохраненную строку
                    rowToRemove.style.animation = 'slideOutLeft 0.4s cubic-bezier(0.2, 0.8, 0.2, 1) forwards';
                    setTimeout(() => rowToRemove.remove(), 400);
                } else {
                    showToast(data.message || 'Ошибка удаления', 'error');
                }
            })
            .catch(err => {
                console.error(err);
                showToast('Ошибка сети', 'error');
            })
            .finally(() => {
                // Возвращаем кнопку в исходное состояние
                confirmDeleteBtn.innerHTML = originalHtml;
                confirmDeleteBtn.disabled = false;
            });
        });
    }

    // ================= 7. ЭФФЕКТ ПАРАЛЛАКСА =================
    document.addEventListener('mousemove', function(e) {
        const x = e.clientX / window.innerWidth;
        const y = e.clientY / window.innerHeight;
        document.body.style.backgroundPosition = `${x * 10}% ${y * 10}%`;
    });
});