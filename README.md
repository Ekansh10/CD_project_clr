## Commands to run
```cmd
cd CLR-Parser

pip install -r requirements.txt

python server.py
```
# CLR Parser Web Application - Technical Documentation

This document provides a comprehensive explanation of the CLR(1) Parser web application, including details about the parser implementation, the web interface, and the interaction between them.

## Table of Contents

1. [System Overview](#system-overview)
2. [Backend Implementation](#backend-implementation)
   - [Core Classes](#core-classes)
   - [Parsing Algorithm](#parsing-algorithm)
   - [Grammar Processing](#grammar-processing)
   - [API Integration](#api-integration)
3. [Frontend Implementation](#frontend-implementation)
   - [User Interface](#user-interface)
   - [Interactive Components](#interactive-components)
   - [Visualization Features](#visualization-features)
4. [Implementation Details](#implementation-details)
   - [CLR(1) Parsing Steps](#clr1-parsing-steps)
   - [Conflict Detection](#conflict-detection)
   - [Error Handling](#error-handling)
5. [Code Explanation](#code-explanation)
   - [standalone_parser.py](#standalone_parserpy)
   - [app_with_frontend.py](#app_with_frontendpy)
   - [static/js/script.js](#staticjsscriptjs)
   - [static/css/styles.css](#staticcssstylesjs)
   - [templates/index.html](#templatesindexhtml)

## System Overview

The CLR Parser web application is a tool for parsing context-free grammars using the CLR(1) parsing technique. It allows users to:

1. Input grammar productions and test strings
2. Visualize the parsing process step-by-step
3. Inspect the CLR(1) parsing table
4. View the First and Follow sets for non-terminals
5. Detect parsing conflicts

The system consists of a Python backend using FastAPI and a JavaScript frontend. The backend implements the CLR(1) parsing algorithm, while the frontend provides a user-friendly interface for interacting with the parser.

## Backend Implementation

### Core Classes

The backend parser implementation is based on several key classes:

#### `Terminal` and `NonTerminal`

These classes represent terminal and non-terminal symbols in the grammar. NonTerminal objects maintain their First and Follow sets.

```python
class Terminal:
    def __init__(self, symbol):
        self.symbol = symbol

class NonTerminal:
    def __init__(self, symbol):
        self.symbol = symbol
        self.first = set()
        self.follow = set()

    def add_first(self, symbols): 
        self.first |= set(symbols)

    def add_follow(self, symbols): 
        self.follow |= set(symbols)
```

#### `Item`

Represents an LR(1) item, which consists of a production with a dot position and a lookahead set.

```python
class Item(str):
    def __new__(cls, item, lookahead=None):
        self = str.__new__(cls, item)
        self.lookahead = lookahead or []
        return self

    def __str__(self):
        return super(Item, self).__str__() + ", " + '|'.join(self.lookahead)
```

#### `State`

Represents a state in the CLR(1) automaton, containing a set of LR(1) items (closure).

```python
class State:
    _id = 0
    def __init__(self, closure):
        self.closure = closure
        self.no = State._id
        State._id += 1
```

#### `standalone_parser.py`

The main parser class that implements the CLR(1) parsing algorithm.

### Parsing Algorithm

The CLR(1) parsing algorithm is implemented in the following steps:

1. **Grammar Analysis**: 
   - Parsing grammar productions
   - Computing First and Follow sets for non-terminals
   - Augmenting the grammar

2. **State Generation**:
   - Calculating LR(1) item closures
   - Building the collection of LR(1) item sets
   - Creating the CLR(1) parsing table

3. **Parsing Process**:
   - Using the parsing table to determine actions
   - Maintaining a stack for parsing
   - Recording each step of the parsing process

### Grammar Processing

The parser processes the grammar in several steps:

1. **Parsing Production Rules**:
   ```python
   def parse_grammar(self, grammar: List[str]):
       """Parse the grammar productions"""
       # Implementation details...
   ```

2. **Computing First Sets**:
   ```python
   def compute_first(self, symbol):
       """Compute FIRST set for a given symbol"""
       # Implementation details...
   ```

3. **Computing Follow Sets**:
   ```python
   def compute_follow(self, symbol):
       """Compute FOLLOW set for a given non-terminal"""
       # Implementation details...
   ```

4. **Augmenting the Grammar**:
   ```python
   def augment_grammar(self):
       """Augment the grammar with a new start symbol"""
       # Implementation details...
   ```

### API Integration

The FastAPI application (`app_with_frontend.py`) provides the following endpoints:

1. **`GET /`**: Serves the HTML frontend
2. **`GET /api`**: Provides API information
3. **`POST /parse`**: Parses an input string using the CLR(1) algorithm

The `/parse` endpoint accepts a JSON request containing:
- `grammar`: List of grammar productions
- `input_string`: String to be parsed

And returns a JSON response with:
- Non-terminals and terminals
- First and Follow sets
- Parsing table
- Parsing steps
- Acceptance status
- Conflict information

## Frontend Implementation

### User Interface

The frontend provides a clean, intuitive interface with the following sections:

1. **Input Panel**:
   - Grammar input textarea
   - Input string field
   - Parse and Clear buttons

2. **Result Panel**:
   - Status indicator (Accepted/Rejected)
   - Tabbed display for:
     - Symbols (terminals and non-terminals)
     - First and Follow sets
     - Parsing table
     - Parsing steps

3. **Conflicts Panel**:
   - Display of shift/reduce and reduce/reduce conflicts

4. **Result Popup**:
   - Notification showing whether the string was accepted or rejected

### Interactive Components

The frontend includes several interactive features:

1. **Tabbed Navigation**: Allows users to switch between different views of the parsing results.

2. **Color-Coded Parsing Steps**: Visual differentiation between shift, reduce, accept, and reject actions.

3. **Popup Notifications**: Immediate feedback on parsing results.

4. **Mobile-Friendly Design**: Responsive layout that works on various screen sizes.

### Visualization Features

The frontend visualizes the parsing process in several ways:

1. **Symbol Display**: Shows terminals and non-terminals as badges.

2. **First/Follow Sets**: Displays each non-terminal's First and Follow sets.

3. **Parsing Table**: Interactive table showing the CLR(1) parsing actions.

4. **Parsing Steps**: Step-by-step display of the parsing process, including:
   - Stack contents
   - Remaining input
   - Current action (shift, reduce, accept, reject)

## Implementation Details

### CLR(1) Parsing Steps

The parsing process is implemented in the `parse_input` method:

```python
def parse_input(self, input_string):
    """Parse an input string using the CLR parsing table"""
    # Implementation details...
```

Each step of the parsing process records:
- The current stack contents
- The remaining input
- The action taken (shift, reduce, accept, reject)

### Conflict Detection

The parser detects and reports two types of conflicts:

1. **Shift/Reduce Conflicts**: When a state has both shift and reduce actions for the same symbol.

2. **Reduce/Reduce Conflicts**: When a state has multiple reduce actions for the same symbol.

Conflicts are counted in the `count_conflicts` method:

```python
def count_conflicts(self):
    """Count shift/reduce and reduce/reduce conflicts in the parsing table"""
    # Implementation details...
```

### Error Handling

The application implements error handling at multiple levels:

1. **Backend Error Handling**:
   - Exception handling in parsing methods
   - HTTP error responses for API failures

2. **Frontend Error Handling**:
   - Input validation
   - API error handling
   - User-friendly error messages

## Code Explanation

### standalone_parser.py

This file contains the complete implementation of the CLR(1) parser.

#### Key Methods:

1. **`initialize_parser(grammar)`**:
   - Entry point for initializing the parser with a grammar
   - Calls the necessary methods for parsing the grammar, computing First and Follow sets, augmenting the grammar, calculating states, and creating the parsing table

2. **`closure(items)`**:
   - Computes the closure of a set of LR(1) items
   - Adds items of the form Y → .γ to the closure for each item with a dot before symbol Y

3. **`goto(items, symbol)`**:
   - Computes the goto set for a set of items and a symbol
   - Moves the dot past the given symbol and computes the closure

4. **`calc_states()`**:
   - Calculates the collection of sets of LR(1) items
   - Starting from the initial item, repeatedly applies goto to generate all states

5. **`make_table(states)`**:
   - Creates the CLR(1) parsing table from the collection of states
   - Adds shift, reduce, goto, and accept actions to the table

6. **`parse_input(input_string)`**:
   - Parses an input string using the CLR parsing table
   - Maintains a stack and tracks the parsing steps

### app_with_frontend.py

This file implements the FastAPI application that serves both the API and the frontend.

#### Key Components:

1. **API Endpoints**:
   - `GET /`: Serves the HTML frontend
   - `GET /api`: Provides API information
   - `POST /parse`: Parses an input string using the CLR(1) algorithm

2. **Request/Response Models**:
   - `ParserRequest`: Model for the parse request
   - JSON Response: Data structure returned by the `/parse` endpoint

3. **Static File Serving**:
   - Mounts the static directory for serving CSS and JS files
   - Uses Jinja2Templates for serving HTML templates

### static/js/script.js

This file handles the frontend functionality, including user interaction and result visualization.

#### Key Functions:

1. **`displayResult(data)`**:
   - Main function for displaying parsing results
   - Calls specialized functions for displaying different aspects of the results

2. **`displayParsingSteps(steps)`**:
   - Displays the step-by-step parsing process
   - Formats the action column to show detailed information about shift, reduce, accept, and reject actions

3. **`showResultPopup(isAccepted, inputString)`**:
   - Shows a popup notification with the parsing result
   - Provides feedback on whether the string was accepted or rejected

4. **Event Handlers**:
   - `parseBtn.addEventListener('click', function() {...})`: Handles the parse button click
   - `clearBtn.addEventListener('click', function() {...})`: Handles the clear button click

### static/css/styles.css

This file contains the CSS styles for the frontend, including layout, colors, and animations.

#### Key Style Groups:

1. **General Styles**:
   - Basic styling for the body, cards, and headers

2. **Table Styles**:
   - Styling for the parsing table and steps table

3. **Symbol and Set Displays**:
   - Styling for terminal and non-terminal symbols
   - Styling for First and Follow sets

4. **Action Labels**:
   - Color-coded styling for shift, reduce, accept, and reject actions

5. **Popup Styles**:
   - Styling for the result popup
   - Animation for popup appearance

### templates/index.html

This file contains the HTML structure for the frontend, including the input form, result display, and tabbed navigation.

#### Key Sections:

1. **Input Form**:
   - Grammar input textarea
   - Input string field
   - Parse and Clear buttons

2. **Result Display**:
   - Tabbed navigation for different result views
   - Status indicator
   - Panels for symbols, First/Follow sets, parsing table, and parsing steps

3. **Scripts and Styles**:
   - Links to Bootstrap CSS and JS
   - Links to custom CSS and JS files

## Conclusion

The CLR Parser web application provides a comprehensive tool for working with context-free grammars and CLR(1) parsing. The backend implements the full CLR(1) parsing algorithm, while the frontend provides an intuitive interface for interacting with the parser and visualizing the results.

By combining a powerful parser implementation with a user-friendly interface, the application serves as both a practical tool and an educational resource for understanding CLR(1) parsing. 

## Sample Grammars to test

S->E

E->E+E

E->E*E

E->(E)

E->a

