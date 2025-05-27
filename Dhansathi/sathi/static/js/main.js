// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add fade-in animation to cards
    document.querySelectorAll('.card').forEach(card => {
        card.classList.add('fade-in');
    });

    // Handle form submissions with AJAX
    document.querySelectorAll('form[data-ajax="true"]').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitButton = this.querySelector('[type="submit"]');
            const originalText = submitButton.innerHTML;
            
            // Disable submit button and show loading state
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';

            fetch(this.action, {
                method: this.method,
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('success', data.message);
                    if (data.redirect) {
                        window.location.href = data.redirect;
                    }
                } else {
                    showAlert('danger', data.message || 'An error occurred');
                }
            })
            .catch(error => {
                showAlert('danger', 'An error occurred. Please try again.');
                console.error('Error:', error);
            })
            .finally(() => {
                // Reset submit button
                submitButton.disabled = false;
                submitButton.innerHTML = originalText;
            });
        });
    });

    // Function to show alerts
    function showAlert(type, message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const container = document.querySelector('main.container');
        container.insertBefore(alertDiv, container.firstChild);

        // Auto dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    // Handle expense form validation
    const expenseForm = document.getElementById('expenseForm');
    if (expenseForm) {
        expenseForm.addEventListener('submit', function(e) {
            const amount = document.getElementById('amount').value;
            const category = document.getElementById('category').value;
            
            if (!amount || amount <= 0) {
                e.preventDefault();
                showAlert('danger', 'Please enter a valid amount');
                return;
            }
            
            if (!category) {
                e.preventDefault();
                showAlert('danger', 'Please select a category');
                return;
            }
        });
    }

    // Handle dashboard charts if Chart.js is present
    if (typeof Chart !== 'undefined') {
        // Sample chart initialization - customize based on your data
        const ctx = document.getElementById('expenseChart');
        if (ctx) {
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Food', 'Transport', 'Entertainment', 'Bills', 'Others'],
                    datasets: [{
                        data: [30, 20, 15, 25, 10],
                        backgroundColor: [
                            '#2ecc71',
                            '#3498db',
                            '#9b59b6',
                            '#e74c3c',
                            '#f1c40f'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
    }

    // Handle profile form submission
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        // Load profile data when the form is present
        fetch('/api/profile/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        })
        .then(response => response.json())
        .then(data => {
            // Populate form fields with profile data
            Object.keys(data).forEach(key => {
                const input = document.getElementById(key);
                if (input) {
                    input.value = data[key];
                }
            });
        })
        .catch(error => {
            console.error('Error loading profile:', error);
        });

        // Handle form submission
        profileForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitButton = this.querySelector('[type="submit"]');
            const originalText = submitButton.innerHTML;
            
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';

            // Convert FormData to JSON
            const jsonData = {};
            formData.forEach((value, key) => {
                jsonData[key] = value;
            });

            fetch('/api/profile/save/', {
                method: 'POST',
                body: JSON.stringify(jsonData),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                showAlert('success', 'Profile saved successfully');
            })
            .catch(error => {
                showAlert('danger', 'Error saving profile. Please try again.');
                console.error('Error:', error);
            })
            .finally(() => {
                submitButton.disabled = false;
                submitButton.innerHTML = originalText;
            });
        });
    }
}); 