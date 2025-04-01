from collections import OrderedDict
from typing import List, Dict, Tuple, Set, Any, Optional
import json

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

class Item(str):
    def __new__(cls, item, lookahead=None):
        self = str.__new__(cls, item)
        self.lookahead = lookahead or []
        return self

    def __str__(self):
        return super(Item, self).__str__() + ", " + '|'.join(self.lookahead)

class State:
    _id = 0
    def __init__(self, closure):
        self.closure = closure
        self.no = State._id
        State._id += 1

class CLRParser:
    def __init__(self):
        self.production_list = []
        self.nt_list = OrderedDict()  # Non-terminals
        self.t_list = OrderedDict()   # Terminals
        self.parsing_steps = []
        self.is_accepted = False
        self.parsing_table = {}
        
    def parse_grammar(self, grammar: List[str]):
        """Parse the grammar productions"""
        self.production_list = []
        self.nt_list = OrderedDict() 
        self.t_list = OrderedDict()
        
        for production in grammar:
            if not production or production.lower() == 'end':
                continue
                
            self.production_list.append(production)
            head, body = production.split('->')
            
            # Add head to non-terminals if not already there
            if head not in self.nt_list:
                self.nt_list[head] = NonTerminal(head)
            
            # Add all terminals in body
            for symbol in body:
                if not (65 <= ord(symbol) <= 90):  # Not uppercase letter
                    if symbol not in self.t_list:
                        self.t_list[symbol] = Terminal(symbol)
                elif symbol not in self.nt_list:
                    self.nt_list[symbol] = NonTerminal(symbol)
    
    def compute_first(self, symbol):
        """Compute FIRST set for a given symbol"""
        # If symbol is a terminal, return itself
        if symbol in self.t_list:
            return {symbol}
            
        # If we've already computed FIRST for this non-terminal, return it
        if symbol in self.nt_list and self.nt_list[symbol].first:
            return self.nt_list[symbol].first
            
        # Compute FIRST set for non-terminal
        for prod in self.production_list:
            head, body = prod.split('->')
            
            if head != symbol:
                continue
                
            # If X -> ε is a production, add ε to FIRST(X)
            if body == '':
                self.nt_list[symbol].add_first('ε')
                continue
                
            # For each production X -> Y1 Y2 ... Yn
            for i, Y in enumerate(body):
                # Skip if Y is the same as X (left recursion)
                if Y == symbol:
                    continue
                    
                # Add FIRST(Y) - {ε} to FIRST(X)
                first_y = self.compute_first(Y)
                self.nt_list[symbol].add_first(first_y - {'ε'})
                
                # If ε is not in FIRST(Y), break
                if 'ε' not in first_y:
                    break
                    
                # If Y1...Yn all have ε in their FIRST sets, add ε to FIRST(X)
                if i == len(body) - 1:
                    self.nt_list[symbol].add_first({'ε'})
                    
        return self.nt_list[symbol].first
    
    def compute_follow(self, symbol):
        """Compute FOLLOW set for a given non-terminal"""
        # If symbol is a terminal, return None
        if symbol in self.t_list:
            return None
            
        # If we're computing FOLLOW for the start symbol, add $ to its FOLLOW set
        if symbol == list(self.nt_list.keys())[0]:
            self.nt_list[symbol].add_follow({'$'})
            
        # For each production in the grammar
        for prod in self.production_list:
            head, body = prod.split('->')
            
            # For each occurrence of symbol in the body
            for i, B in enumerate(body):
                if B != symbol:
                    continue
                    
                # If A -> αBβ, add FIRST(β) - {ε} to FOLLOW(B)
                if i < len(body) - 1:
                    first_beta = self.compute_first(body[i+1])
                    self.nt_list[symbol].add_follow(first_beta - {'ε'})
                    
                    # If ε is in FIRST(β), add FOLLOW(A) to FOLLOW(B)
                    if 'ε' in first_beta and B != head:
                        self.nt_list[symbol].add_follow(self.compute_follow(head))
                
                # If A -> αB, add FOLLOW(A) to FOLLOW(B)
                elif i == len(body) - 1 and B != head:
                    self.nt_list[symbol].add_follow(self.compute_follow(head))
                    
        return self.nt_list[symbol].follow
    
    def augment_grammar(self):
        """Augment the grammar with a new start symbol"""
        for i in range(ord('Z'), ord('A')-1, -1):
            if chr(i) not in self.nt_list:
                start_prod = self.production_list[0]
                self.production_list.insert(0, chr(i) + '->' + start_prod.split('->')[0])
                self.nt_list[chr(i)] = NonTerminal(chr(i))
                return
    
    def closure(self, items):
        """Compute the closure of a set of items"""
        def exists(newitem, items):
            for i in items:
                if i == newitem and sorted(i.lookahead) == sorted(newitem.lookahead):
                    return True
            return False
        
        while True:
            flag = 0
            for i in items:
                # Skip if dot is at the end
                if i.index('.') == len(i) - 1:
                    continue
                
                # Get the symbol after the dot
                Y = i.split('->')[1].split('.')[1][0]
                
                # Compute lookahead for this symbol
                if i.index('.') + 1 < len(i) - 1:
                    next_symbol = i[i.index('.') + 2]
                    lastr = list(self.compute_first(next_symbol) - {'ε'})
                else:
                    lastr = i.lookahead
                
                # Add items of the form Y -> .γ to the closure
                for prod in self.production_list:
                    head, body = prod.split('->')
                    
                    if head != Y:
                        continue
                    
                    newitem = Item(Y + '->.' + body, lastr)
                    
                    if not exists(newitem, items):
                        items.append(newitem)
                        flag = 1
            
            if flag == 0:
                break
        
        return items
    
    def goto(self, items, symbol):
        """Compute the goto set for a set of items and a symbol"""
        initial = []
        
        for i in items:
            # Skip if dot is at the end
            if i.index('.') == len(i) - 1:
                continue
            
            head, body = i.split('->')
            seen, unseen = body.split('.')
            
            # Check if the next symbol is the one we're looking for
            if unseen[0] == symbol:
                initial.append(Item(head + '->' + seen + unseen[0] + '.' + unseen[1:], i.lookahead))
        
        return self.closure(initial)
    
    def calc_states(self):
        """Calculate the collection of sets of LR(1) items"""
        def contains(states, t):
            for s in states:
                if len(s) != len(t):
                    continue
                
                if sorted(s) == sorted(t):
                    for i in range(len(s)):
                        if s[i].lookahead != t[i].lookahead:
                            break
                    else:
                        return True
            
            return False
        
        # Get the start symbol and its production
        head, body = self.production_list[0].split('->')
        
        # Initialize with the closure of {[S' -> .S, $]}
        states = [self.closure([Item(head + '->.' + body, ['$'])])]
        
        # Compute the collection of sets of LR(1) items
        while True:
            flag = 0
            for s in states:
                # For each symbol in the grammar
                for symbol in list(self.nt_list.keys()) + list(self.t_list.keys()):
                    # Compute the goto set
                    t = self.goto(s, symbol)
                    
                    # Skip if empty or already in states
                    if not t or contains(states, t):
                        continue
                    
                    # Add to states
                    states.append(t)
                    flag = 1
            
            if flag == 0:
                break
        
        # Convert to State objects
        State._id = 0
        return [State(s) for s in states]
    
    def make_table(self, states):
        """Make the CLR(1) parsing table"""
        def getstateno(t):
            for s in states:
                if len(s.closure) != len(t):
                    continue
                
                if sorted(s.closure) == sorted(t):
                    for i in range(len(s.closure)):
                        if s.closure[i].lookahead != t[i].lookahead:
                            break
                    else:
                        return s.no
            
            return -1
        
        def getprodno(closure):
            closure = ''.join(closure).replace('.', '')
            return self.production_list.index(closure)
        
        # Initialize the parsing table
        parsing_table = OrderedDict()
        
        for s in states:
            parsing_table[s.no] = OrderedDict()
            
            for item in s.closure:
                head, body = item.split('->')
                
                # If item is of the form A -> α.
                if body == '.':
                    for term in item.lookahead:
                        if term not in parsing_table[s.no]:
                            parsing_table[s.no][term] = {'r' + str(getprodno(item))}
                        else:
                            parsing_table[s.no][term] |= {'r' + str(getprodno(item))}
                    continue
                
                # Get the symbol after the dot
                nextsym = body.split('.')[1]
                
                # If item is of the form A -> α.β where β is not empty
                if nextsym:
                    nextsym = nextsym[0]
                    t = self.goto(s.closure, nextsym)
                    
                    if t:
                        # If nextsym is a terminal, add shift action
                        if nextsym in self.t_list:
                            if nextsym not in parsing_table[s.no]:
                                parsing_table[s.no][nextsym] = {'s' + str(getstateno(t))}
                            else:
                                parsing_table[s.no][nextsym] |= {'s' + str(getstateno(t))}
                        # If nextsym is a non-terminal, add goto action
                        else:
                            parsing_table[s.no][nextsym] = str(getstateno(t))
                    
                    continue
                
                # If item is of the form A -> α., it's a reduction item
                # If it's the augmented start production, add accept action
                if getprodno(item) == 0:
                    parsing_table[s.no]['$'] = 'accept'
                else:
                    for term in item.lookahead:
                        if term not in parsing_table[s.no]:
                            parsing_table[s.no][term] = {'r' + str(getprodno(item))}
                        else:
                            parsing_table[s.no][term] |= {'r' + str(getprodno(item))}
        
        return parsing_table
    
    def count_conflicts(self):
        """Count shift/reduce and reduce/reduce conflicts in the parsing table"""
        sr, rr = 0, 0
        
        for state, actions in self.parsing_table.items():
            for symbol, action in actions.items():
                if isinstance(action, set) and len(action) > 1:
                    action_list = list(action)
                    r_count = sum(1 for a in action_list if a[0] == 'r')
                    s_count = sum(1 for a in action_list if a[0] == 's')
                    
                    if r_count > 0 and s_count > 0:
                        sr += 1
                    elif r_count > 1:
                        rr += 1
        
        return {'s/r': sr, 'r/r': rr}
    
    def parse_input(self, input_string):
        """Parse an input string using the CLR parsing table"""
        # Add end marker to input
        input_string = input_string + '$'
        input_chars = list(input_string)
        
        # Initialize stack with state 0
        stack = ['0']
        self.parsing_steps = []
        self.parsing_steps.append({'stack': ''.join(stack), 'input': ''.join(input_chars), 'action': 'start'})
        
        try:
            while input_chars:
                # Get current state and input symbol
                current_state = int(stack[-1])
                current_symbol = input_chars[0]
                
                # Check if action exists for this state and symbol
                if current_symbol not in self.parsing_table[current_state]:
                    self.is_accepted = False
                    self.parsing_steps.append({'stack': ''.join(stack), 'input': ''.join(input_chars), 'action': 'reject'})
                    return False
                
                # Get action
                action = self.parsing_table[current_state][current_symbol]
                
                # Handle different action types
                if isinstance(action, set):
                    # In case of conflict, take the first action
                    action = next(iter(action))
                
                if action == 'accept':
                    # Make sure we've fully consumed the input (should just be '$' left)
                    if len(input_chars) == 1 and input_chars[0] == '$':
                        # Accept the input
                        self.is_accepted = True
                        self.parsing_steps.append({'stack': ''.join(stack), 'input': ''.join(input_chars), 'action': 'accept'})
                        return True
                    else:
                        self.is_accepted = False
                        self.parsing_steps.append({'stack': ''.join(stack), 'input': ''.join(input_chars), 'action': 'reject'})
                        return False
                
                elif action.startswith('s'):
                    # Shift action - add action info before modifying stack/input
                    action_info = f"shift({action[1:]})"
                    
                    # Shift action
                    stack.append(current_symbol)
                    stack.append(action[1:])
                    input_chars = input_chars[1:]
                    self.parsing_steps.append({'stack': ''.join(stack), 'input': ''.join(input_chars), 'action': action_info})
                
                elif action.startswith('r'):
                    # Reduce action - capture info before modifying stack
                    prod_idx = int(action[1:])
                    prod = self.production_list[prod_idx]
                    # Include the rule number in the action info
                    action_info = f"reduce({prod},r{prod_idx})"
                    
                    # Reduce action
                    head, body = prod.split('->')
                    
                    # Pop 2*len(body) symbols from the stack
                    pop_count = 2 * len(body) if body else 0
                    stack = stack[:-pop_count] if pop_count > 0 else stack
                    
                    # Get the goto state
                    goto_state = self.parsing_table[int(stack[-1])][head]
                    
                    # Push the non-terminal and new state
                    stack.append(head)
                    stack.append(goto_state)
                    self.parsing_steps.append({'stack': ''.join(stack), 'input': ''.join(input_chars), 'action': action_info})
                
                else:
                    # Goto action (shouldn't happen here)
                    self.is_accepted = False
                    self.parsing_steps.append({'stack': ''.join(stack), 'input': ''.join(input_chars), 'action': 'error'})
                    return False
            
            # If we've consumed all input but haven't reached 'accept', it's an error
            self.is_accepted = False
            self.parsing_steps.append({'stack': ''.join(stack), 'input': ''.join(input_chars), 'action': 'reject'})
            return False
        
        except Exception as e:
            print(f"Error during parsing: {e}")
            self.is_accepted = False
            return False
    
    def initialize_parser(self, grammar):
        """Initialize the parser with a grammar"""
        # Parse the grammar
        self.parse_grammar(grammar)
        
        # Compute FIRST and FOLLOW sets for all non-terminals
        for nt in self.nt_list:
            self.compute_first(nt)
            self.compute_follow(nt)
        
        # Augment the grammar
        self.augment_grammar()
        
        # Calculate states
        states = self.calc_states()
        
        # Create parsing table
        self.parsing_table = self.make_table(states)
    
    def get_first_follow_sets(self):
        """Get FIRST and FOLLOW sets for all non-terminals"""
        result = {}
        
        for nt, obj in self.nt_list.items():
            result[nt] = {
                'first': obj.first,
                'follow': obj.follow
            }
        
        return result
    
    def get_parsing_table(self):
        """Get the CLR parsing table in a serializable format"""
        result = {}
        
        for state, actions in self.parsing_table.items():
            result[str(state)] = {}
            for symbol, action in actions.items():
                result[str(state)][symbol] = action
        
        return result
    
    def get_result(self):
        """Get the complete parsing result"""
        return {
            'non_terminals': list(self.nt_list.keys()),
            'terminals': list(self.t_list.keys()) + ['$'],
            'first_follow': self.get_first_follow_sets(),
            'parse_table': self.get_parsing_table(),
            'parsing_steps': self.parsing_steps,
            'is_accepted': self.is_accepted,
            'conflicts': self.count_conflicts()
        } 