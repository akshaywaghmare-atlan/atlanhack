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
    // Get current page
    const currentPageNum = parseInt(document.querySelector('.step.active').dataset.step);

    // Prevent unauthorized navigation
    if (pageNumber > currentPageNum) {
        // Check if trying to go past page 1 without authentication
        if (pageNumber > 1 && !sessionStorage.getItem('authenticationComplete')) {
            return;
        }

        // Check if trying to go past page 2
        if (pageNumber > 2) {
            const connectionName = document.getElementById('connectionName').value.trim();
            if (!connectionName) {
                return;
            }
        }
    }

    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });

    // Hide all navigation buttons
    document.querySelectorAll('.nav-buttons').forEach(nav => {
        nav.style.display = 'none';
    });

    // Show selected page
    document.getElementById(`page${pageNumber}`).classList.add('active');

    // Show corresponding navigation buttons
    document.getElementById(`page${pageNumber}-nav`).style.display = 'flex';

    // Update sidebar steps
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active');
        if (parseInt(step.dataset.step) === pageNumber) {
            step.classList.add('active');
        }
    });

    // Update current page
    currentPage = pageNumber;
}

async function nextPage() {
    const currentPageNum = parseInt(document.querySelector('.step.active').dataset.step);

    // If on page 1, ensure authentication is complete
    if (currentPageNum === 1) {
        // Check if authentication is already complete
        if (!sessionStorage.getItem('authenticationComplete')) {
            // If not authenticated, run test connection
            const success = await testConnection();
            if (!success) {
                return; // Don't proceed if authentication fails
            }
        }
        // If authenticated (either previously or just now), proceed to next page
        goToPage(2);
        updateSteps();
        return;
    }

    // For other pages
    const nextPageNum = currentPageNum + 1;
    if (nextPageNum <= 3) {
        // Add any additional validation for page 2 if needed
        if (currentPageNum === 2) {
            const connectionName = document.getElementById('connectionName').value.trim();
            if (!connectionName) {
                return; // Don't proceed if connection name is empty
            }
        }

        goToPage(nextPageNum);
        updateSteps();
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

    try {
        // Disable test button and show loading state
        testButton.disabled = true;
        testButton.textContent = 'Testing...';
        errorElement.classList.remove('visible');

        const success = await performConnectionTest();

        if (success) {
            // Success case
            testButton.innerHTML = `Connection Successful <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="20" height="20" style="margin-left: 8px">
                <path fill-rule="evenodd" d="M8.603 3.799A4.49 4.49 0 0112 2.25c1.357 0 2.573.6 3.397 1.549a4.49 4.49 0 013.498 1.307 4.491 4.491 0 011.307 3.497A4.49 4.49 0 0121.75 12a4.49 4.49 0 01-1.549 3.397 4.491 4.491 0 01-1.307 3.497 4.491 4.491 0 01-3.497 1.307A4.49 4.49 0 0112 21.75a4.49 4.49 0 01-3.397-1.549 4.49 4.49 0 01-3.498-1.306 4.491 4.491 0 01-1.307-3.498A4.49 4.49 0 012.25 12c0-1.357.6-2.573 1.549-3.397a4.49 4.49 0 011.307-3.497 4.49 4.49 0 013.497-1.307zm7.007 6.387a.75.75 0 10-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 00-1.06 1.06l2.25 2.25a.75.75 0 001.14-.094l3.75-5.25z" clip-rule="evenodd" />
            </svg>`;
            testButton.style.backgroundColor = 'var(--success-color)';
            testButton.style.color = 'white';
            testButton.style.borderColor = 'var(--success-color)';
            testButton.classList.add('success');
            nextButton.disabled = false;
            errorElement.classList.remove('visible');

            // Store authentication state
            sessionStorage.setItem('authenticationComplete', 'true');
            return true;
        } else {
            throw new Error('Connection failed');
        }
    } catch (error) {
        // Show error message
        errorElement.textContent = error.message || 'Failed to connect. Please check your credentials and try again.';
        errorElement.classList.add('visible');
        testButton.style.backgroundColor = '';
        testButton.style.color = '';
        testButton.style.borderColor = '';
        testButton.textContent = 'Test Connection';
        testButton.classList.remove('success');
        nextButton.disabled = true;
        sessionStorage.removeItem('authenticationComplete');
        return false;
    } finally {
        testButton.disabled = false;
    }
}

// Add a helper function to perform the actual connection test
async function performConnectionTest() {
    const payload = {
        host: document.getElementById('host').value,
        port: document.getElementById('port').value,
        user: document.getElementById('user').value,
        password: document.getElementById('password').value,
        database: document.getElementById('database').value
    };

    try {
        const response = await fetch('/workflows/v1/auth', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        return data.success;
    } catch (error) {
        throw new Error('Connection failed');
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

    // Add validation for page 2
    const connectionNameInput = document.getElementById('connectionName');
    if (connectionNameInput) {
        // Initial validation
        validatePage2();

        // Add input event listener
        connectionNameInput.addEventListener('input', validatePage2);
    }

    // Update step click handlers
    document.querySelectorAll('.step').forEach(step => {
        step.addEventListener('click', (e) => {
            const targetPage = parseInt(step.dataset.step);
            goToPage(targetPage);
        });
    });

    // Clear authentication state on page load
    sessionStorage.removeItem('authenticationComplete');
});

function validatePage2() {
    const connectionName = document.getElementById('connectionName').value.trim();
    const page2Next = document.getElementById('page2Next');

    // Enable the next button if connectionName has a value
    page2Next.disabled = !connectionName;
}

// Add these new functions

let metadataOptions = {
    include: new Map(),
    exclude: new Map()
};

function processMetadataResponse(data) {
    // Group by TABLE_CATALOG instead of database
    const databases = new Map();
    console.log(data)

    data.forEach(item => {
        if (!databases.has(item.TABLE_CATALOG)) {
            databases.set(item.TABLE_CATALOG, new Set());
        }
        databases.get(item.TABLE_CATALOG).add(item.TABLE_SCHEMA);
    });

    console.log(databases);
    return databases;
}

async function fetchMetadata() {
    try {
        // Gather credentials from page 1
        const payload = {
            host: document.getElementById('host').value,
            port: document.getElementById('port').value,
            user: document.getElementById('user').value,
            password: document.getElementById('password').value,
            database: document.getElementById('database').value
        };

        const response = await fetch('/workflows/v1/metadata', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error('Failed to fetch metadata');
        }

        const data = await response.json();
        return processMetadataResponse(data.data);
    } catch (error) {
        console.error('Error fetching metadata:', error);
        // You might want to show an error message to the user
        return new Map(); // Return empty map in case of error
    }
}

function toggleDropdown(id) {
    const dropdown = document.getElementById(id);
    const content = dropdown.querySelector('.dropdown-content');
    content.classList.toggle('show');
}

function updateDropdownHeader(type, tableCatalog, totalSchemas, selectedCount) {
    const dropdown = document.getElementById(`${type}Metadata`);
    const header = dropdown.querySelector('.dropdown-header span');

    // Get all selected databases and their schemas
    const selectedDatabases = [];
    metadataOptions[type].forEach((schemas, database) => {
        if (schemas.size > 0) {
            selectedDatabases.push(`${database} (${schemas.size} schemas)`);
        }
    });

    if (selectedDatabases.length === 0) {
        header.textContent = 'Select databases and schemas';
    } else if (selectedDatabases.length === 1) {
        header.textContent = selectedDatabases[0];
    } else {
        // Show first database and count of others
        header.textContent = `${selectedDatabases[0]} +${selectedDatabases.length - 1} more`;
    }

    // Add tooltip for full list when multiple databases are selected
    if (selectedDatabases.length > 1) {
        header.title = selectedDatabases.join('\n');
    } else {
        header.title = '';
    }
}

async function populateMetadataDropdowns() {
    // Show loading state
    ['include', 'exclude'].forEach(type => {
        const dropdown = document.getElementById(`${type}Metadata`);
        const header = dropdown.querySelector('.dropdown-header span');
        const content = dropdown.querySelector('.dropdown-content');
        header.textContent = 'Loading...';
        content.innerHTML = ''; // Clear existing content
    });

    // Clear existing selections
    metadataOptions.include.clear();
    metadataOptions.exclude.clear();

    const databases = await fetchMetadata();

    ['include', 'exclude'].forEach(type => {
        const dropdown = document.getElementById(`${type}Metadata`);
        const content = dropdown.querySelector('.dropdown-content');
        const header = dropdown.querySelector('.dropdown-header span');

        // Reset content
        content.innerHTML = '';

        // Update header text based on whether we got data
        if (databases.size === 0) {
            header.textContent = 'No databases available';
            return;
        }

        // Reset to default text
        header.textContent = 'Select databases and schemas';

        databases.forEach((schemas, tableCatalog) => {
            // Create database container
            const dbContainer = document.createElement('div');
            dbContainer.className = 'database-container';

            // Create database header
            const dbDiv = document.createElement('div');
            dbDiv.className = 'database-item';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `${type}-${tableCatalog}`;

            const label = document.createElement('label');
            label.textContent = tableCatalog;
            label.htmlFor = `${type}-${tableCatalog}`;

            const schemaCount = document.createElement('span');
            schemaCount.className = 'selected-count';
            schemaCount.textContent = `0/${schemas.size}`;

            dbDiv.appendChild(checkbox);
            dbDiv.appendChild(label);
            dbDiv.appendChild(schemaCount);

            // Create schema list
            const schemaList = document.createElement('div');
            schemaList.className = 'schema-list';

            schemas.forEach(schemaName => {
                const schemaDiv = document.createElement('div');
                schemaDiv.className = 'schema-item';

                const schemaCheckbox = document.createElement('input');
                schemaCheckbox.type = 'checkbox';
                schemaCheckbox.id = `${type}-${tableCatalog}-${schemaName}`;

                const schemaLabel = document.createElement('label');
                schemaLabel.textContent = schemaName;
                schemaLabel.htmlFor = `${type}-${tableCatalog}-${schemaName}`;

                schemaDiv.appendChild(schemaCheckbox);
                schemaDiv.appendChild(schemaLabel);
                schemaList.appendChild(schemaDiv);

                schemaCheckbox.addEventListener('change', (e) => {
                    handleSchemaSelection(type, tableCatalog, schemaName, e.target.checked);
                    updateSelectionCount(type, tableCatalog, schemas.size);
                });
            });

            // Add all elements to the container
            dbContainer.appendChild(dbDiv);
            dbContainer.appendChild(schemaList);
            content.appendChild(dbContainer);

            // Add database checkbox event listener
            checkbox.addEventListener('change', (e) => {
                handleDatabaseSelection(type, tableCatalog, Array.from(schemas), e.target.checked);
                schemaList.querySelectorAll('input[type="checkbox"]')
                    .forEach(cb => cb.checked = e.target.checked);
                updateSelectionCount(type, tableCatalog, schemas.size);
            });

            // Add click event to toggle schema list
            dbDiv.addEventListener('click', (e) => {
                if (e.target.type !== 'checkbox') {
                    schemaList.classList.toggle('show');
                }
            });
        });
    });
}

function handleDatabaseSelection(type, tableCatalog, schemas, isSelected) {
    if (!metadataOptions[type].has(tableCatalog)) {
        metadataOptions[type].set(tableCatalog, new Set());
    }

    if (isSelected) {
        schemas.forEach(schema => {
            metadataOptions[type].get(tableCatalog).add(schema);
        });
    } else {
        metadataOptions[type].get(tableCatalog).clear();
    }

    // Update the header with the new selection
    updateDropdownHeader(type);
}

function handleSchemaSelection(type, tableCatalog, tableSchema, isSelected) {
    if (!metadataOptions[type].has(tableCatalog)) {
        metadataOptions[type].set(tableCatalog, new Set());
    }

    if (isSelected) {
        metadataOptions[type].get(tableCatalog).add(tableSchema);
    } else {
        metadataOptions[type].get(tableCatalog).delete(tableSchema);
    }

    // Update the header with the new selection
    updateDropdownHeader(type);
}

function updateSelectionCount(type, tableCatalog, totalSchemas) {
    const selectedCount = metadataOptions[type].get(tableCatalog)?.size || 0;

    // Find the count span using more compatible selectors
    const dbContainer = document.querySelector(`#${type}Metadata`);
    const dbItems = dbContainer.querySelectorAll('.database-item');
    let countSpan;

    // Find the matching database item
    dbItems.forEach(item => {
        const label = item.querySelector('label');
        if (label && label.textContent === tableCatalog) {
            countSpan = item.querySelector('.selected-count');
        }
    });

    if (countSpan) {
        countSpan.textContent = `${selectedCount}/${totalSchemas}`;
    }

    // Update header
    let totalSelected = 0;
    metadataOptions[type].forEach(schemas => {
        totalSelected += schemas.size;
    });
    updateDropdownHeader(type, null, null, totalSelected);
}

// Update the page 3 initialization
function initializePage3() {
    // Initialize metadata dropdowns when page 3 is shown
    const page3 = document.getElementById('page3');
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.target.classList.contains('active')) {
                // Always fetch fresh metadata when page 3 is shown
                populateMetadataDropdowns();
            }
        });
    });

    observer.observe(page3, { attributes: true, attributeFilter: ['class'] });
}

// Add this to your DOMContentLoaded event listener
document.addEventListener('DOMContentLoaded', () => {
    // ... existing code ...

    initializePage3();
});

// Add these new functions for preflight checks
function formatFilters(metadataOptions) {
    const formatFilter = (selections) => {
        const filter = {};
        selections.forEach((schemas, database) => {
            if (schemas.size > 0) {
                // Add ^ to start and $ to end of database name
                const dbPattern = `^${database}$`;
                // Add ^ to start and $ to end of each schema name
                filter[dbPattern] = Array.from(schemas).map(schema => `^${schema}$`);
            }
        });
        return JSON.stringify(filter);
    };

    return {
        include_filter: formatFilter(metadataOptions.include),
        exclude_filter: formatFilter(metadataOptions.exclude),
    };
}

async function runPreflightChecks() {
    const checkButton = document.getElementById('runPreflightChecks');
    checkButton.disabled = true;
    checkButton.textContent = 'Checking...';

    // Reset previous results
    document.querySelectorAll('.check-status').forEach(status => {
        status.innerHTML = '';
        status.className = 'check-status';
    });

    try {
        const filters = formatFilters(metadataOptions);
        const payload = {
            credentials: {
                host: document.getElementById('host').value,
                port: parseInt(document.getElementById('port').value),
                user: document.getElementById('user').value,
                password: document.getElementById('password').value,
                database: document.getElementById('database').value
            },
            form_data: {
                ...filters,
                temp_table_regex: ""
            }
        };

        const response = await fetch('/workflows/v1/check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        // debugger
        const responseJson = await response.json();
        console.log('Received response:', responseJson); // Debug log

        // Update each check result
        ['databaseSchemaCheck', 'tablesCheck'].forEach(checkType => {
            const result = responseJson.data[checkType];
            const statusElement = document.querySelector(`#${checkType} .check-status`);

            if (!statusElement) return;

            if (result.success) {
                statusElement.innerHTML = `
                    <span>${result.successMessage}</span>
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                        <path fill-rule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm13.36-1.814a.75.75 0 10-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 00-1.06 1.06l2.25 2.25a.75.75 0 001.14-.094l3.75-5.25z" clip-rule="evenodd" />
                    </svg>
                `;
                statusElement.classList.add('success');
            } else {
                statusElement.innerHTML = `
                    <span>${result.failureMessage || 'Check failed'}</span>
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                        <path fill-rule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25zm-1.72 6.97a.75.75 0 10-1.06 1.06L10.94 12l-1.72 1.72a.75.75 0 101.06 1.06L12 13.06l1.72 1.72a.75.75 0 101.06-1.06L13.06 12l1.72-1.72a.75.75 0 10-1.06-1.06L12 10.94l-1.72-1.72z" clip-rule="evenodd" />
                    </svg>
                `;
                statusElement.classList.add('error');
            }
        });

    } catch (error) {
        console.error('Preflight check failed:', error);
        // Show error state for all checks
        document.querySelectorAll('.check-status').forEach(status => {
            status.innerHTML = `
                <span>Failed to perform check</span>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                    <path fill-rule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25zm-1.72 6.97a.75.75 0 10-1.06 1.06L10.94 12l-1.72 1.72a.75.75 0 101.06 1.06L12 13.06l1.72 1.72a.75.75 0 101.06-1.06L13.06 12l1.72-1.72a.75.75 0 10-1.06-1.06L12 10.94l-1.72-1.72z" clip-rule="evenodd" />
                </svg>
            `;
            status.classList.add('error');
        });
    } finally {
        checkButton.disabled = false;
        checkButton.textContent = 'Check';
    }
}

// Update the event listener setup
function setupPreflightCheck() {
    const checkButton = document.getElementById('runPreflightChecks');
    if (checkButton) {
        checkButton.addEventListener('click', async () => {
            await runPreflightChecks();
        });
    }
}

// Update your DOMContentLoaded listener
document.addEventListener('DOMContentLoaded', () => {
    // ... existing code ...
    setupPreflightCheck();
});

function createConfetti() {
    const colors = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6'];
    const confettiCount = 100;

    for (let i = 0; i < confettiCount; i++) {
        const confetti = document.createElement('div');
        confetti.classList.add('confetti');

        // Random position and color
        confetti.style.left = Math.random() * 100 + 'vw';
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.transform = `rotate(${Math.random() * 360}deg)`;
        confetti.style.animationDuration = `${Math.random() * 2 + 2}s`; // Random duration between 2-4s

        document.body.appendChild(confetti);

        // Remove confetti after animation
        setTimeout(() => confetti.remove(), 4000);
    }
}

async function handleRunWorkflow() {
    const runButton = document.querySelector('#runWorkflowButton');
    if (!runButton) return;

    runButton.addEventListener('click', async () => {
        try {
            runButton.disabled = true;
            runButton.textContent = 'Starting...';

            // Get credentials from page 1
            const credentials = {
                host: document.getElementById('host').value,
                port: parseInt(document.getElementById('port').value),
                user: document.getElementById('user').value,
                password: document.getElementById('password').value,
                database: document.getElementById('database').value
            };

            // Get connection name from page 2
            const connection = {
                connection: document.getElementById('connectionName').value
            };

            // Get metadata filters from page 3
            const filters = formatFilters(metadataOptions);

            const payload = {
                credentials,
                connection,
                metadata: {
                    ...filters,
                    temp_table_regex: "",
                    advanced_config_strategy: "default",
                    use_source_schema_filtering: "false",
                    use_jdbc_internal_methods: "true",
                    authentication: "BASIC"
                }
            };

            const response = await fetch('/workflows/v1/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error('Failed to start workflow');
            }

            const data = await response.json();

            // Show success state
            runButton.textContent = 'Started Successfully';
            runButton.classList.add('success');

            // Show modal and create confetti
            const modal = document.getElementById('successModal');
            modal.classList.add('show');
            createConfetti();

        } catch (error) {
            console.error('Failed to start workflow:', error);
            runButton.textContent = 'Failed to Start';
            runButton.classList.add('error');

            const errorMessage = document.querySelector('.error-message');
            if (errorMessage) {
                errorMessage.textContent = 'Failed to start workflow. Please try again.';
                errorMessage.classList.add('visible');
            }
        } finally {
            setTimeout(() => {
                runButton.disabled = false;
                runButton.textContent = 'Run';
                runButton.classList.remove('success', 'error');
            }, 3000);
        }
    });
}

// Add to your DOMContentLoaded event listener
document.addEventListener('DOMContentLoaded', () => {
    // ... existing code ...
    handleRunWorkflow();
});
