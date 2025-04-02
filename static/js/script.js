document.addEventListener('DOMContentLoaded', function() {
    const parseBtn = document.getElementById('parse-btn');
    const clearBtn = document.getElementById('clear-btn');
    const grammarInput = document.getElementById('grammar-input');
    const stringInput = document.getElementById('string-input');
    const loading = document.getElementById('loading');
    const resultPanel = document.getElementById('result-panel');
    const resultStatus = document.querySelector('.result-status');
    
    // Set default grammar example
    grammarInput.value = 'S->CC\nC->cC\nC->d';
    stringInput.value = 'cdcd';
    
    // Parse button click handler
    parseBtn.addEventListener('click', function() {
        // Show loading
        loading.classList.remove('d-none');
        
        // Get grammar and input string
        const grammar = grammarInput.value.trim().split('\n').filter(line => line.trim() !== '');
        const inputString = stringInput.value.trim();
        
        // Validate inputs
        if (grammar.length === 0 || inputString === '') {
            showError('Please enter both grammar and input string');
            loading.classList.add('d-none');
            return;
        }
        
        // Send request to API
        fetch('/parse', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                grammar: grammar,
                input_string: inputString
            }),
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.detail || 'Failed to parse input');
                });
            }
            return response.json();
        })
        .then(data => {
            // Hide loading
            loading.classList.add('d-none');
            
            // Display result
            displayResult(data);
            
            // Show popup notification
            showResultPopup(data.is_accepted, inputString);
        })
        .catch(error => {
            // Hide loading
            loading.classList.add('d-none');
            
            // Show error
            showError(error.message);
        });
    });
    
    // Clear button click handler
    clearBtn.addEventListener('click', function() {
        grammarInput.value = '';
        stringInput.value = '';
        clearResult();
    });
    
    // Function to display parsing result
    function displayResult(data) {
        // Set status
        if (data.is_accepted) {
            resultStatus.innerHTML = '<span class="badge bg-success">Accepted</span>';
        } else {
            resultStatus.innerHTML = '<span class="badge bg-danger">Rejected</span>';
        }
        
        // Display non-terminals and terminals
        displaySymbols(data.non_terminals, data.terminals);
        
        // Display first/follow sets
        displayFirstFollow(data.first_follow);
        
        // Display parsing table
        displayParseTable(data.parse_table, data.terminals, data.non_terminals);
        
        // Display parsing steps
        displayParsingSteps(data.parsing_steps);
        
        // Display conflicts
        displayConflicts(data.conflicts);
    }
    
    // Function to show popup notification
    function showResultPopup(isAccepted, inputString) {
        // Create popup container if it doesn't exist
        let popup = document.getElementById('result-popup');
        if (!popup) {
            popup = document.createElement('div');
            popup.id = 'result-popup';
            popup.className = 'result-popup';
            document.body.appendChild(popup);
        }
        
        // Set popup content and style based on result
        popup.className = `result-popup ${isAccepted ? 'accepted' : 'rejected'}`;
        popup.innerHTML = `
            <div class="popup-content">
                <div class="popup-header">
                    <span class="popup-icon">${isAccepted ? '✓' : '✗'}</span>
                    <h4>${isAccepted ? 'String Accepted' : 'String Rejected'}</h4>
                </div>
                <div class="popup-body">
                    <p>Input string: <strong>"${inputString}"</strong></p>
                    <p>${isAccepted 
                        ? 'The string is valid according to the grammar.' 
                        : 'The string does not conform to the grammar.'}
                    </p>
                </div>
                <button class="popup-close-btn">OK</button>
            </div>
        `;
        
        // Show popup
        popup.style.display = 'flex';
        
        // Add close button event listener
        popup.querySelector('.popup-close-btn').addEventListener('click', function() {
            popup.style.display = 'none';
        });
        
        // Auto-close after 5 seconds
        setTimeout(() => {
            if (popup.style.display === 'flex') {
                popup.style.display = 'none';
            }
        }, 5000);
    }
    
    // Function to display symbols
    function displaySymbols(nonTerminals, terminals) {
        const ntContainer = document.getElementById('non-terminals');
        const tContainer = document.getElementById('terminals');
        
        ntContainer.innerHTML = '';
        tContainer.innerHTML = '';
        
        nonTerminals.forEach(nt => {
            const span = document.createElement('span');
            span.className = 'symbol-badge';
            span.textContent = nt;
            ntContainer.appendChild(span);
        });
        
        terminals.forEach(t => {
            const span = document.createElement('span');
            span.className = 'symbol-badge';
            span.textContent = t;
            tContainer.appendChild(span);
        });
    }
    
    // Function to display first/follow sets
    function displayFirstFollow(firstFollow) {
        const container = document.getElementById('first-follow-sets');
        container.innerHTML = '';
        
        Object.entries(firstFollow).forEach(([symbol, sets]) => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'first-follow-item';
            
            const header = document.createElement('h6');
            header.textContent = `Non-terminal: ${symbol}`;
            itemDiv.appendChild(header);
            
            const firstDiv = document.createElement('div');
            firstDiv.className = 'mb-2';
            firstDiv.innerHTML = '<strong>FIRST:</strong> ';
            
            sets.first.forEach(item => {
                const span = document.createElement('span');
                span.className = 'set-item';
                span.textContent = item;
                firstDiv.appendChild(span);
            });
            
            const followDiv = document.createElement('div');
            followDiv.innerHTML = '<strong>FOLLOW:</strong> ';
            
            sets.follow.forEach(item => {
                const span = document.createElement('span');
                span.className = 'set-item';
                span.textContent = item;
                followDiv.appendChild(span);
            });
            
            itemDiv.appendChild(firstDiv);
            itemDiv.appendChild(followDiv);
            container.appendChild(itemDiv);
        });
    }
    
    // Function to display parsing table
    function displayParseTable(parseTable, terminals, nonTerminals) {
        const table = document.getElementById('parsing-table');
        table.innerHTML = '';
        
        // Create header row
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        
        // Add state header
        const stateHeader = document.createElement('th');
        stateHeader.textContent = 'State';
        headerRow.appendChild(stateHeader);
        
        // Add terminals and non-terminals headers
        const symbols = [...nonTerminals, ...terminals];
        
        symbols.forEach(symbol => {
            const th = document.createElement('th');
            th.textContent = symbol;
            headerRow.appendChild(th);
        });
        
        thead.appendChild(headerRow);
        table.appendChild(thead);
        
        // Create table body
        const tbody = document.createElement('tbody');
        
        // For each state in the parse table
        Object.entries(parseTable).forEach(([state, actions]) => {
            const row = document.createElement('tr');
            
            // Add state number
            const stateCell = document.createElement('td');
            stateCell.className = 'fw-bold text-center';
            stateCell.textContent = state;
            row.appendChild(stateCell);
            
            // Add actions for each symbol
            symbols.forEach(symbol => {
                const cell = document.createElement('td');
                cell.className = 'action-cell';
                
                if (actions[symbol]) {
                    const action = actions[symbol];
                    
                    if (typeof action === 'string') {
                        if (action === 'accept') {
                            cell.innerHTML = '<span class="accept-action">accept</span>';
                        } else if (!isNaN(action)) {
                            // It's a goto action
                            cell.innerHTML = `<span class="goto-action">${action}</span>`;
                        } else {
                            cell.textContent = action;
                        }
                    } else if (Array.isArray(action)) {
                        action.forEach((act, index) => {
                            if (act.startsWith('s')) {
                                cell.innerHTML += `<span class="shift-action">${act}</span>`;
                            } else if (act.startsWith('r')) {
                                cell.innerHTML += `<span class="reduce-action">${act}</span>`;
                            } else {
                                cell.innerHTML += act;
                            }
                            
                            if (index < action.length - 1) {
                                cell.innerHTML += ', ';
                            }
                        });
                    }
                }
                
                row.appendChild(cell);
            });
            
            tbody.appendChild(row);
        });
        
        table.appendChild(tbody);
    }
    
    // Function to display parsing steps
    function displayParsingSteps(steps) {
        const tbody = document.querySelector('#steps-table tbody');
        tbody.innerHTML = '';
        
        // Clear the table header and recreate it with an action column
        const thead = document.querySelector('#steps-table thead');
        thead.innerHTML = `
            <tr>
                <th>Step</th>
                <th>Stack</th>
                <th>Input</th>
                <th>Action</th>
            </tr>
        `;
        
        steps.forEach((step, index) => {
            const row = document.createElement('tr');
            
            const stepCell = document.createElement('td');
            stepCell.textContent = index + 1;
            row.appendChild(stepCell);
            
            const stackCell = document.createElement('td');
            stackCell.style.fontFamily = 'monospace';
            stackCell.textContent = step.stack;
            row.appendChild(stackCell);
            
            const inputCell = document.createElement('td');
            inputCell.style.fontFamily = 'monospace';
            inputCell.textContent = step.input;
            row.appendChild(inputCell);
            
            // Add action cell
            const actionCell = document.createElement('td');
            let actionClass = '';
            let actionText = step.action || '';
            
            // Format the action text according to specifications
            if (actionText.startsWith('reduce(')) {
                // Extract the production and rule number from the format: reduce(S->CC,r1)
                const match = actionText.match(/reduce\((.*?),(r\d+)\)/);
                if (match && match[1] && match[2]) {
                    const production = match[1];
                    const ruleNumber = match[2];
                    const [left, right] = production.split('->');
                    
                    actionText = `Reduce ${left} → ${right} (${ruleNumber})`;
                    actionClass = 'reduce';
                }
            } else if (actionText.startsWith('shift(')) {
                // Extract the state number from shift(3)
                const match = actionText.match(/shift\((.*?)\)/);
                if (match && match[1]) {
                    const stateNumber = match[1];
                    // Get the symbol that was shifted (it's in the input at previous step)
                    const prevInput = index > 0 ? steps[index - 1].input[0] : '';
                    actionText = `Shift ${prevInput} → s${stateNumber}`;
                    actionClass = 'shift';
                }
            } else if (actionText === 'start') {
                actionClass = '';
                actionText = 'Start';
            } else if (actionText === 'accept') {
                actionClass = 'accept';
                actionText = 'Accept';
            } else if (actionText === 'reject' || actionText === 'error') {
                actionClass = 'reject';
                actionText = 'Reject';
            }
            
            // Apply styling if we have a class
            if (actionClass) {
                actionCell.innerHTML = `<span class="action-label ${actionClass}">${actionText}</span>`;
            } else {
                actionCell.textContent = actionText;
            }
            
            row.appendChild(actionCell);
            tbody.appendChild(row);
        });
    }
    
    // Function to display conflicts
    function displayConflicts(conflicts) {
        const container = document.getElementById('conflicts');
        container.innerHTML = '';
        
        if (conflicts['s/r'] === 0 && conflicts['r/r'] === 0) {
            container.innerHTML = '<div class="alert alert-success">No conflicts detected in the parsing table.</div>';
            return;
        }
        
        let html = '';
        
        if (conflicts['s/r'] > 0) {
            html += `<div class="conflict-item">
                <span class="conflict-badge sr-conflict">${conflicts['s/r']}</span> Shift/Reduce Conflicts
            </div>`;
        }
        
        if (conflicts['r/r'] > 0) {
            html += `<div class="conflict-item">
                <span class="conflict-badge rr-conflict">${conflicts['r/r']}</span> Reduce/Reduce Conflicts
            </div>`;
        }
        
        html += `<div class="alert alert-warning mt-2">
            <i class="bi bi-exclamation-triangle-fill"></i>
            Conflicts may lead to ambiguous parsing. Consider revising your grammar.
        </div>`;
        
        container.innerHTML = html;
    }
    
    // Function to show errors
    function showError(message) {
        resultStatus.innerHTML = `<span class="badge bg-danger">Error</span>`;
        document.getElementById('conflicts').innerHTML = 
            `<div class="alert alert-danger">${message}</div>`;
    }
    
    // Function to clear result
    function clearResult() {
        resultStatus.innerHTML = '';
        document.getElementById('non-terminals').innerHTML = '';
        document.getElementById('terminals').innerHTML = '';
        document.getElementById('first-follow-sets').innerHTML = '';
        document.getElementById('parsing-table').innerHTML = '';
        document.getElementById('steps-table').querySelector('tbody').innerHTML = '';
        document.getElementById('conflicts').innerHTML = '';
    }
}); 