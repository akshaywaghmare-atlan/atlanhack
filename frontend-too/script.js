let currentPage = 1;
const formData = {};

function updateFormData() {
    const inputs = document.querySelectorAll('input[type="text"], input[type="password"]');
    inputs.forEach(input => {
        if (input.value) {
            formData[input.id] = input.value;
        }
    });
}

function updateSteps() {
    const steps = document.querySelectorAll('.step');
    steps.forEach((step, index) => {
        const stepNumber = index + 1;
        step.classList.remove('active', 'completed');
        if (stepNumber === currentPage) {
            step.classList.add('active');
        } else if (stepNumber < currentPage) {
            step.classList.add('completed');
        }
    });
}

function goToPage(pageNumber) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });

    // Show selected page
    document.getElementById(`page${pageNumber}`).classList.add('active');

    // Update sidebar steps
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active');
        if (parseInt(step.dataset.step) === pageNumber) {
            step.classList.add('active');
        }
    });
}

function nextPage() {
    const currentPage = document.querySelector('.step.active').dataset.step;
    if (currentPage === '1' && document.getElementById('nextButton').disabled) {
        return; // Don't proceed if connection hasn't been tested successfully
    }

    const nextPageNum = parseInt(currentPage) + 1;
    if (nextPageNum <= 3) {
        goToPage(nextPageNum);
    }
}

function previousPage() {
    const currentPage = document.querySelector('.step.active').dataset.step;
    const prevPageNum = parseInt(currentPage) - 1;
    if (prevPageNum >= 1) {
        goToPage(prevPageNum);
    }
}

async function handleRun() {
    updateFormData();
    try {
        const response = await fetch('https://api.example.com/postgres-assets', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            alert('Operation successful!');
        } else {
            alert('Operation failed. Please try again.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    }
}

async function testConnection() {
    const testButton = document.querySelector('.test-connection');
    const errorElement = document.getElementById('connectionError');
    const nextButton = document.getElementById('nextButton');

    // Get form values
    const payload = {
        host: document.getElementById('host').value,
        port: document.getElementById('port').value,
        username: document.getElementById('username').value,
        password: document.getElementById('password').value,
        database: document.getElementById('database').value
    };

    try {
        // Disable test button and show loading state
        testButton.disabled = true;
        testButton.textContent = 'Testing...';
        errorElement.classList.remove('visible');

        const response = await fetch('/v1/workflows/auth', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.success) {
            // Success case
            testButton.textContent = 'Connection Successful';
            testButton.style.backgroundColor = 'var(--success-color)';
            testButton.style.color = 'white';
            testButton.style.borderColor = 'var(--success-color)';
            nextButton.disabled = false;
            errorElement.classList.remove('visible');
        } else {
            // API returned success = false
            throw new Error(data.message || 'Connection failed');
        }
    } catch (error) {
        // Show error message
        errorElement.textContent = error.message || 'Failed to connect. Please check your credentials and try again.';
        errorElement.classList.add('visible');
        testButton.style.backgroundColor = '';
        testButton.style.color = '';
        testButton.style.borderColor = '';
        nextButton.disabled = true;
    } finally {
        // Re-enable test button
        testButton.disabled = false;
        testButton.textContent = 'Test Connection';
    }
}

// Initialize button states
document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.button-group .btn');
    buttons.forEach(button => {
        button.addEventListener('click', (e) => {
            const group = e.target.closest('.button-group');
            group.querySelectorAll('.btn').forEach(btn => {
                btn.classList.remove('btn-primary');
                btn.classList.add('btn-secondary');
            });
            e.target.classList.remove('btn-secondary');
            e.target.classList.add('btn-primary');
        });
    });
});
