function openSwapModal(userId, skillName, skillId) {
    const modal = document.getElementById('swapModal');
    const receiverIdInput = document.getElementById('receiver_id');
    const receiverSkillIdInput = document.getElementById('receiver_skill_id');
    const skillNameSpan = document.getElementById('skill_name');
    const skillSelect = document.getElementById('requester_skill_id');
    const modalError = document.getElementById('modalError');
    const modalLoading = document.getElementById('modalLoading');

    // Reset modal state
    modalError.classList.add('hidden');
    modalError.textContent = '';
    skillSelect.innerHTML = '<option value="" disabled selected>Loading skills...</option>';
    modalLoading.classList.remove('hidden');
    modal.classList.remove('hidden');

    // Set modal data
    receiverIdInput.value = userId;
    receiverSkillIdInput.value = skillId;
    skillNameSpan.textContent = skillName;

    // Fetch user's offered skills
    fetch('/api/skills/offered')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch skills');
            }
            return response.json();
        })
        .then(skills => {
            modalLoading.classList.add('hidden');
            skillSelect.innerHTML = '<option value="" disabled selected>Select a skill</option>';
            if (skills.length === 0) {
                modalError.textContent = 'You have no skills offered. Add some in your profile first.';
                modalError.classList.remove('hidden');
                skillSelect.disabled = true;
            } else {
                skills.forEach(skill => {
                    const option = document.createElement('option');
                    option.value = skill.id;
                    option.textContent = skill.skill;
                    skillSelect.appendChild(option);
                });
                skillSelect.disabled = false;
            }
        })
        .catch(error => {
            modalLoading.classList.add('hidden');
            modalError.textContent = 'Error loading skills. Please try again.';
            modalError.classList.remove('hidden');
            skillSelect.disabled = true;
        });
}

function closeSwapModal() {
    document.getElementById('swapModal').classList.add('hidden');
    document.getElementById('modalError').classList.add('hidden');
    document.getElementById('modalError').textContent = '';
    document.getElementById('modalLoading').classList.add('hidden');
}

function downloadReport() {
    const loading = document.createElement('span');
    loading.className = 'ml-2 text-blue-300';
    loading.innerHTML = '<svg class="animate-spin h-5 w-5 inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path></svg>';
    document.querySelector('a[href="/admin/report"]').appendChild(loading);

    fetch('/admin/report')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to download report');
            }
            return response.json();
        })
        .then(data => {
            const blob = new Blob([data.report], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'skill_swap_report.txt';
            a.click();
            window.URL.revokeObjectURL(url);
            loading.remove();
        })
        .catch(error => {
            loading.remove();
            alert('Error downloading report. Please try again.');
        });
}

// Confirm critical actions
document.addEventListener('DOMContentLoaded', () => {
    // Confirm skill deletion
    document.querySelectorAll('form input[name="delete_skill"]').forEach(form => {
        form.closest('form').addEventListener('submit', (e) => {
            if (!confirm('Are you sure you want to delete this skill?')) {
                e.preventDefault();
            }
        });
    });

    // Confirm swap deletion
    document.querySelectorAll('form input[name="action"][value="delete"]').forEach(form => {
        form.closest('form').addEventListener('submit', (e) => {
            if (!confirm('Are you sure you want to delete this swap request?')) {
                e.preventDefault();
            }
        });
    });

    // Confirm swap accept
    document.querySelectorAll('form input[name="action"][value="accept"]').forEach(form => {
        form.closest('form').addEventListener('submit', (e) => {
            if (!confirm('Are you sure you want to accept this swap request?')) {
                e.preventDefault();
            }
        });
    });

    // Confirm swap reject
    document.querySelectorAll('form input[name="action"][value="reject"]').forEach(form => {
        form.closest('form').addEventListener('submit', (e) => {
            if (!confirm('Are you sure you want to reject this swap request?')) {
                e.preventDefault();
            }
        });
    });

    // Confirm swap form submission
    document.getElementById('swapForm')?.addEventListener('submit', (e) => {
        const skillSelect = document.getElementById('requester_skill_id');
        if (!skillSelect.value) {
            e.preventDefault();
            document.getElementById('modalError').textContent = 'Please select a skill to offer.';
            document.getElementById('modalError').classList.remove('hidden');
        }
    });
});