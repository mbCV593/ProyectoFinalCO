import tkinter as tk
from tkinter import scrolledtext, Frame, Label, END, ttk, Button
import re

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip, add="+")
        widget.bind("<Leave>", self.hide_tip, add="+")

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        try:
            x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        except tk.TclError: 
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{int(x)}+{int(y)}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,background="#ffffe0", relief=tk.SOLID, borderwidth=1,font=("tahoma", "18", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None

class GrammarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Gramática con Eliminación de Recursividad Izquierda")
        self.bg_color = "#e0f0ff" 
        self.label_fg_color = "#333333" 
        self.listbox_bg = "#ffffff" 
        self.listbox_select_bg = "#a0c4ff" 
        self.instruction_fg = "navy" 
        self.error_fg = "red" 
        self.textbox_bg = "#f8f8f8" 
        self.root.config(bg=self.bg_color)
        main_app_frame = Frame(root, padx=12, pady=12, bg=self.bg_color)
        main_app_frame.pack(fill=tk.BOTH, expand=True)
        input_controls_frame = Frame(main_app_frame, bg=self.bg_color, pady=10)
        input_controls_frame.pack(side=tk.TOP, fill=tk.X)
        header_line_frame = Frame(input_controls_frame, bg=self.bg_color)
        header_line_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        Label(header_line_frame, text="ENTRADA (Definición Gramática)",bg=self.bg_color, fg=self.label_fg_color, font=('Arial', 20, 'bold')).pack(side=tk.LEFT, anchor=tk.W, padx=(0,15))
        button_name_vertical_padding = (4, 0) 
        self.f5_button = Button(
            header_line_frame, text="F5", command=self.process_grammar_event,
            font=('Arial', 16, 'bold'), relief=tk.RAISED, borderwidth=2,
            padx=10, pady=2 
        )
        self.f5_button.pack(side=tk.LEFT, padx=(0, 5), pady=button_name_vertical_padding)
        ToolTip(self.f5_button, "EJECUTAR (F5)")
    
        Label(header_line_frame, 
            text="Christian Velásquez\t090 - 22 - 7443        Preciona F5 o el Boton F5",
            fg=self.instruction_fg, bg=self.bg_color, font=('Arial', 16, 'italic')
        ).pack(side=tk.LEFT, padx=(5, 20), pady=button_name_vertical_padding)
        self.text_editor = scrolledtext.ScrolledText(
            input_controls_frame, wrap=tk.WORD, height=4, width=5,
            relief=tk.SUNKEN, borderwidth=1, font=('Consolas', 18),
            bg=self.textbox_bg 
        )
        self.text_editor.pack(fill=tk.X, expand=True, pady=(5, 5))
        instruction_display_frame = Frame(input_controls_frame, bg=self.bg_color)
        instruction_display_frame.pack(fill=tk.X, pady=(5,0))
        display_area_frame = Frame(main_app_frame, bg=self.bg_color)
        display_area_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(10,0))
        self.original_grammar_frame = Frame(display_area_frame, bg=self.bg_color, padx=5)
        self.original_grammar_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        Label(self.original_grammar_frame, text="Gramática Original",
            bg=self.bg_color, fg=self.label_fg_color, font=('Arial', 18, 'bold')
        ).pack(pady=(0,5))
        self.listbox_v_orig, self.listbox_t_orig, self.tree_orig = \
            self._create_grammar_display_widgets(self.original_grammar_frame, is_transformed_section=False)
        self.transformed_grammar_frame = Frame(display_area_frame, bg=self.bg_color, padx=5)
        self.transformed_grammar_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        Label(self.transformed_grammar_frame, text="Gramática Sin Recursividad por Izquierda",
            bg=self.bg_color, fg=self.label_fg_color, font=('Arial', 18, 'bold')
        ).pack(pady=(0,5))
        self.transformed_grammar_textbox = scrolledtext.ScrolledText(
            self.transformed_grammar_frame, wrap=tk.WORD, height=5, 
            relief=tk.SUNKEN, borderwidth=1, font=('Consolas', 16),
            state=tk.DISABLED, bg=self.textbox_bg
        )
        self.transformed_grammar_textbox.pack(fill=tk.X, expand=False, pady=(2, 10))
        self.listbox_v_transformed, self.listbox_t_transformed, self.tree_transformed = \
            self._create_grammar_display_widgets(self.transformed_grammar_frame, is_transformed_section=True)
        self.root.bind("<F5>", self.process_grammar_event)
        style = ttk.Style()
        style.configure("Treeview", font=('Arial', 16), rowheight=22)
        style.configure("Treeview.Heading", font=('Arial', 16, 'bold'))

    def _create_grammar_display_widgets(self, parent_frame, is_transformed_section=False):
        vt_frame = Frame(parent_frame, bg=self.bg_color)
        vt_frame.pack(side=tk.TOP, fill=tk.X, pady=(0,5))
        var_term_frame = Frame(vt_frame, bg=self.bg_color)
        var_term_frame.pack(fill=tk.X)
        listbox_v = self._create_listbox_in_frame(var_term_frame, "V")
        listbox_t = self._create_listbox_in_frame(var_term_frame, "T")
        Label(parent_frame, text="Matriz de Producciones", font=('Arial', 18, 'bold'),
            bg=self.bg_color, fg=self.label_fg_color).pack(pady=(5, 5))
        tree_height = 7 if not is_transformed_section else 5 
        tree = ttk.Treeview(parent_frame, columns=("var", "prod"), show="headings", height=tree_height)
        tree.heading("var", text="V")
        tree.heading("prod", text="Producciones")
        tree.column("var", width=70, anchor='w') 
        tree.column("prod", width=300, anchor='w')
        tree.pack(fill=tk.BOTH, expand=True, padx=5)
        return listbox_v, listbox_t, tree

    def _create_listbox_in_frame(self, parent, title):
        frame = Frame(parent, bg=self.bg_color)
        frame.pack(side=tk.LEFT, fill=tk.Y, expand=True, padx=5)
        Label(frame, text=title, font=('Arial', 18, 'bold'),
            bg=self.bg_color, fg=self.label_fg_color).pack()
        listbox = tk.Listbox(
            frame, height=9, width=8, exportselection=False,
            bg=self.listbox_bg, fg=self.label_fg_color,
            selectbackground=self.listbox_select_bg, relief=tk.FLAT, font=('Arial', 16)
        )
        listbox.pack(fill=tk.BOTH, expand=True)
        return listbox

    def process_grammar_event(self, event=None):
        print("\n--- Processing Grammar ---") 
        self.process_grammar()

    def _parse_input_grammar(self, grammar_text):
        lines = grammar_text.strip().splitlines()
        parsed_rules_kvp = {} 
        initial_variable = None
        ordered_lhs = []
        lhs_pattern = re.compile(r"^\s*([a-zA-Z0-9_]+(?:[!']*)?)\s*(?:=|->)\s*(.*)$")

        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith("#"): continue 
            
            match = lhs_pattern.match(line)
            if not match:
                print(f"ERROR LÉXICO (LHS): Línea {line_num+1}: Malformación en '{line}'. LHS debe ser un identificador (ej: 'Var', 'Var1', 'S!', 's1').")
                continue
            
            lhs = match.group(1).strip()
            rhs_full_str = match.group(2).strip()

            if not rhs_full_str:
                print(f"ERROR SINTÁCTICO: Línea {line_num+1}: RHS vacío para la regla '{line}'.")
                continue

            if initial_variable is None: initial_variable = lhs
            if lhs not in parsed_rules_kvp:
                parsed_rules_kvp[lhs] = []
                ordered_lhs.append(lhs) 

            rhs_options = [opt.strip() for opt in rhs_full_str.split('|')]
            valid_rhs_options = [opt for opt in rhs_options if opt]
            if not valid_rhs_options and rhs_full_str: 
                 print(f"ERROR SINTÁCTICO: Línea {line_num+1}: Opciones RHS inválidas en '{line}'.")
                 continue
            if not valid_rhs_options and not rhs_full_str: 
                 continue

            parsed_rules_kvp[lhs].extend(valid_rhs_options)
            
        return parsed_rules_kvp, initial_variable, ordered_lhs

    def _normalize_rhs_for_internal(self, rhs_str, defined_variables_set):
        tokens = []
        idx = 0
        temp_rhs = rhs_str.strip() 
        while idx < len(temp_rhs):
            original_idx_loop_start = idx
            if temp_rhs[idx].isspace():
                idx += 1
                if tokens and tokens[-1] != " ":
                    tokens.append(" ")
                while idx < len(temp_rhs) and temp_rhs[idx].isspace(): 
                    idx += 1
                continue 

            # 1. Variables (longest match first)
            matched_token_value = None
            sorted_vars = sorted(list(defined_variables_set), key=len, reverse=True)
            for var_cand in sorted_vars:
                if temp_rhs.startswith(var_cand, idx):
                    matched_token_value = var_cand
                    idx += len(var_cand)
                    break
            if matched_token_value:
                if tokens and tokens[-1] != " ": tokens.append(" ")
                tokens.append(matched_token_value)
                if idx < len(temp_rhs) and not temp_rhs[idx].isspace(): tokens.append(" ")
                continue

            # 2. Quoted terminals
            match_q = re.match(r"'([^']*)'", temp_rhs[idx:])
            if match_q:
                if tokens and tokens[-1] != " ": tokens.append(" ")
                tokens.append(match_q.group(0)) 
                idx += len(match_q.group(0))
                if idx < len(temp_rhs) and not temp_rhs[idx].isspace(): tokens.append(" ")
                continue
            
            # 3. 'ee' -> ε
            if temp_rhs.startswith("ee", idx) and \
            (idx + 2 == len(temp_rhs) or not temp_rhs[idx+2].isalnum()):
                if tokens and tokens[-1] != " ": tokens.append(" ")
                tokens.append("ε")
                idx += 2
                if idx < len(temp_rhs) and not temp_rhs[idx].isspace(): tokens.append(" ")
                continue
            
            # 4. 'e' or 'ε' -> ε
            is_eps = False
            if temp_rhs.startswith("ε", idx):
                is_eps = True
                eps_len = 1
            elif temp_rhs.startswith("e", idx) and \
                (idx + 1 == len(temp_rhs) or not temp_rhs[idx+1].isalnum()):
                is_eps = True
                eps_len = 1
            if is_eps:
                if tokens and tokens[-1] != " ": tokens.append(" ")
                tokens.append("ε")
                idx += eps_len
                if idx < len(temp_rhs) and not temp_rhs[idx].isspace(): tokens.append(" ")
                continue
            
            # 5. Other unquoted sequences (potential errors, handled by _analyze_grammar_for_display)
            #    For normalization, just grab the next chunk of non-space characters.
            start_others = idx
            while idx < len(temp_rhs) and not temp_rhs[idx].isspace():
                is_var_start_here = any(temp_rhs.startswith(v_c,idx) for v_c in sorted_vars)
                is_term_start_here = temp_rhs.startswith("'",idx)
                is_eps_forms_start_here = temp_rhs.startswith("ee",idx) or temp_rhs.startswith("e",idx) or temp_rhs.startswith("ε",idx)
                if idx > start_others and (is_var_start_here or is_term_start_here or is_eps_forms_start_here) : break
                idx += 1
            token = temp_rhs[start_others:idx]
            if token: 
                if tokens and tokens[-1] != " ": tokens.append(" ")
                tokens.append(token)
                if idx < len(temp_rhs) and not temp_rhs[idx].isspace(): tokens.append(" ")
            if idx == original_idx_loop_start and idx < len(temp_rhs): # Failsafe for stuck loop
                print(f"WARN (_normalize_rhs): Failsafe advance on char '{temp_rhs[idx]}'")
                if tokens and tokens[-1] != " ": tokens.append(" ")
                tokens.append(temp_rhs[idx]) # Add the problematic char to see it
                idx+=1
        normalized_rhs = "".join(tokens).strip()
        return re.sub(r'\s+', ' ', normalized_rhs)

    def _analyze_grammar_for_display(self, rules_kvp_internal, grammar_start_symbol, is_input_phase=True):
        current_lhs_symbols = set(rules_kvp_internal.keys()) 
        variables = set(current_lhs_symbols) 
        terminals = set()
        processed_productions_for_tree = []
        ordered_lhs_display_keys = sorted(list(current_lhs_symbols))
        if grammar_start_symbol and grammar_start_symbol in ordered_lhs_display_keys:
            ordered_lhs_display_keys.remove(grammar_start_symbol)
            ordered_lhs_display_keys.insert(0, grammar_start_symbol)
        for lhs in ordered_lhs_display_keys:
            if lhs not in rules_kvp_internal: continue 
            is_first_production_for_this_lhs = True
            for rhs_str_internal in rules_kvp_internal[lhs]:
                idx = 0
                temp_rhs_for_analysis = rhs_str_internal 
                
                while idx < len(temp_rhs_for_analysis):
                    char_processed_in_token_loop = False
                    if temp_rhs_for_analysis[idx].isspace():
                        idx += 1
                        continue
                    sorted_known_nts = sorted(list(current_lhs_symbols.union(variables)), key=len, reverse=True)
                    for nt_candidate in sorted_known_nts:
                        if temp_rhs_for_analysis.startswith(nt_candidate, idx):
                            variables.add(nt_candidate) 
                            idx += len(nt_candidate)
                            char_processed_in_token_loop = True
                            break
                    if char_processed_in_token_loop: continue
                    match_q = re.match(r"'([^']*)'", temp_rhs_for_analysis[idx:])
                    if match_q:
                        term_content = match_q.group(1)
                        if term_content == "ε" or term_content == "e": 
                            terminals.add("ε")
                        elif term_content: 
                            terminals.add(term_content) 
                        elif is_input_phase: 
                            print(f"ERROR LÉXICO: Terminal vacío '' en RHS '{rhs_str_internal}' para LHS '{lhs}'.")
                        idx += len(match_q.group(0))
                        char_processed_in_token_loop = True
                        continue
                    if temp_rhs_for_analysis[idx:].startswith("ε"):
                        terminals.add("ε")
                        idx += 1 # Length of 'ε'
                        char_processed_in_token_loop = True
                        continue
                    if is_input_phase:
                        if temp_rhs_for_analysis.startswith("e", idx) and \
                        (idx + 1 == len(temp_rhs_for_analysis) or not temp_rhs_for_analysis[idx+1].isalnum()):
                            is_var_prefix = any(v.startswith(temp_rhs_for_analysis[idx:]) and len(v) > 1 for v in sorted_known_nts if v.startswith('e'))
                            if not is_var_prefix:
                                terminals.add("ε")
                                idx += 1
                                char_processed_in_token_loop = True
                                continue
                        start_unquoted_segment = idx
                        while idx < len(temp_rhs_for_analysis) and not temp_rhs_for_analysis[idx].isspace():
                            is_next_var = any(temp_rhs_for_analysis.startswith(v_c,idx) for v_c in sorted_known_nts)
                            is_next_quoted = temp_rhs_for_analysis.startswith("'",idx)
                            if idx > start_unquoted_segment and (is_next_var or is_next_quoted): break
                            idx += 1
                        unquoted_segment = temp_rhs_for_analysis[start_unquoted_segment:idx]
                        if unquoted_segment:
                            if not any(unquoted_segment == v for v in sorted_known_nts): 
                                print(f"ERROR LÉXICO/SINTÁCTICO: Símbolo '{unquoted_segment}' en RHS '{rhs_str_internal}' para LHS '{lhs}' no es Variable definida ni Terminal válido (no entre comillas y no es 'e'/'ε').")
                            char_processed_in_token_loop = True
                            continue
                    if not char_processed_in_token_loop : 
                        if is_input_phase:
                            print(f"ERROR LÉXICO: Símbolo inesperado '{temp_rhs_for_analysis[idx]}' en RHS '{rhs_str_internal}' para LHS '{lhs}'.")
                        idx += 1 
                display_lhs_tree = lhs
                if lhs == grammar_start_symbol and is_first_production_for_this_lhs:
                    display_lhs_tree = f"→ {lhs}"
                all_known_variables_for_formatting = current_lhs_symbols.union(variables)
                formatted_rhs_for_display = self._format_rhs_for_display(rhs_str_internal, all_known_variables_for_formatting)
                processed_productions_for_tree.append((display_lhs_tree, formatted_rhs_for_display))
                is_first_production_for_this_lhs = False
        final_display_vars = []
        all_vars_for_display_list = sorted(list(variables))
        if grammar_start_symbol and grammar_start_symbol in all_vars_for_display_list:
            final_display_vars.append(f"→ {grammar_start_symbol}")
            for v_item in all_vars_for_display_list:
                if v_item != grammar_start_symbol: final_display_vars.append(v_item)
        elif all_vars_for_display_list: 
            final_display_vars.append(f"→ {all_vars_for_display_list[0]}")
            final_display_vars.extend(all_vars_for_display_list[1:])
        final_display_terminals = sorted([t for t in list(terminals) if t and t != "ε"])
        if "ε" in terminals: 
            if 'e' not in final_display_terminals: final_display_terminals.append("e")
            final_display_terminals.sort()
        return final_display_vars, final_display_terminals, processed_productions_for_tree

    def _format_rhs_for_display(self, internal_rhs_str, defined_variables_set):
        if not internal_rhs_str: return ""
        if internal_rhs_str == "ε": return "e" 
        display_tokens = []
        idx = 0
        temp_rhs = internal_rhs_str 
        while idx < len(temp_rhs):
            original_idx_loop_start = idx
            if temp_rhs[idx].isspace():
                idx += 1
                if display_tokens and display_tokens[-1] != " ":
                    display_tokens.append(" ")
                while idx < len(temp_rhs) and temp_rhs[idx].isspace(): 
                    idx += 1
                continue
            matched_this_pass = False
            # 1. Variables (longest match first)
            sorted_vars = sorted(list(defined_variables_set), key=len, reverse=True)
            for var_cand in sorted_vars:
                if temp_rhs.startswith(var_cand, idx):
                    if display_tokens and display_tokens[-1] != " ": display_tokens.append(" ")
                    display_tokens.append(var_cand)
                    idx += len(var_cand)
                    matched_this_pass = True
                    break
            if matched_this_pass: continue
            # 2. Quoted terminals (internal) -> unquoted for display
            match_q = re.match(r"'([^']*)'", temp_rhs[idx:])
            if match_q:
                term_content = match_q.group(1)
                if display_tokens and display_tokens[-1] != " ": display_tokens.append(" ")
                display_tokens.append(term_content) 
                idx += len(match_q.group(0)) 
                matched_this_pass = True
                continue
            # 3. Epsilon 'ε' or 'e' (if it appears internally not as the sole RHS string)
            if temp_rhs.startswith("ε", idx):
                if display_tokens and display_tokens[-1] != " ": display_tokens.append(" ")
                display_tokens.append("e")
                idx += 1
                matched_this_pass = True
                continue
            # Check for 'e' as epsilon, ensuring it's not a prefix of a variable
            if temp_rhs.startswith("e", idx) and \
            (idx + 1 == len(temp_rhs) or not temp_rhs[idx+1].isalnum()):
                is_var_prefix = any(v.startswith(temp_rhs[idx:]) and len(v) > 1 and v[0] == 'e' for v in sorted_vars)
                if not is_var_prefix:
                    if display_tokens and display_tokens[-1] != " ": display_tokens.append(" ")
                    display_tokens.append("e")
                    idx += 1
                    matched_this_pass = True
                    continue
            # 4. Fallback: Grab next chunk of non-space characters
            # This handles symbols that might not be explicitly tokenized above but are part of the internal string.
            # (e.g. operators that were part of an alpha/beta string directly)
            if idx < len(temp_rhs):
                start_fallback = idx
                while idx < len(temp_rhs) and not temp_rhs[idx].isspace():
                    is_next_var = any(temp_rhs.startswith(v_c, idx) for v_c in sorted_vars)
                    is_next_quoted = temp_rhs.startswith("'", idx)
                    if idx > start_fallback and (is_next_var or is_next_quoted) : break
                    idx += 1
                token = temp_rhs[start_fallback:idx]
                if token:
                    if display_tokens and display_tokens[-1] != " ": display_tokens.append(" ")
                    display_tokens.append(token)
                    matched_this_pass = True
            if not matched_this_pass and idx == original_idx_loop_start : # Failsafe
                if idx < len(temp_rhs): # Should not be space here
                    if display_tokens and display_tokens[-1] != " ": display_tokens.append(" ")
                    display_tokens.append(temp_rhs[idx])
                    idx += 1
                else: 
                    break
        final_str = "".join(display_tokens).strip()
        return re.sub(r'\s+', ' ', final_str)

    def _remove_direct_left_recursion(self, productions_map_internal, ordered_lhs_input):
        new_productions = {lhs: list(rhss) for lhs, rhss in productions_map_internal.items()}
        all_defined_lhs_ever = set(new_productions.keys()) 
        processing_order = list(ordered_lhs_input)
        for lhs_key in productions_map_internal:
            if lhs_key not in processing_order:
                processing_order.append(lhs_key)
        for i in range(len(processing_order)):
            Ai = processing_order[i]
            if Ai not in new_productions: continue
            # Step 1: Substitute productions from Aj (j < i) into Ai
            for j in range(i):
                Aj = processing_order[j]
                if Aj not in new_productions: continue
                current_Ai_rules = list(new_productions.get(Ai, []))
                rules_after_substitution_for_Ai = []
                made_change_by_substitution = False
                for ai_rhs in current_Ai_rules:
                    if ai_rhs.startswith(Aj) and \
                    (len(ai_rhs) == len(Aj) or \
                        not (ai_rhs[len(Aj)].isalnum() or ai_rhs[len(Aj)] in ["'", "!"])): 
                        gamma = ai_rhs[len(Aj):].strip()
                        made_change_by_substitution = True
                        for aj_rhs_delta in new_productions.get(Aj, []):
                            if aj_rhs_delta == "ε":
                                new_substituted_rhs = gamma if gamma else "ε"
                            else:
                                new_substituted_rhs = f"{aj_rhs_delta} {gamma}".strip() if gamma else aj_rhs_delta
                            
                            rules_after_substitution_for_Ai.append(new_substituted_rhs if new_substituted_rhs else "ε")
                    else:
                        rules_after_substitution_for_Ai.append(ai_rhs)
                if made_change_by_substitution:
                    new_productions[Ai] = list(dict.fromkeys(rules_after_substitution_for_Ai))
            # Step 2: Eliminate direct left recursion for Ai
            rules_for_Ai_after_subs = new_productions.get(Ai, [])
            recursive_alphas = []
            non_recursive_betas = []
            has_direct_recursion = False
            for rhs_str in rules_for_Ai_after_subs:
                is_recursive_for_Ai = False
                if rhs_str.startswith(Ai):
                    if len(rhs_str) == len(Ai):
                        is_recursive_for_Ai = True
                    elif not (rhs_str[len(Ai)].isalnum() or rhs_str[len(Ai)] in ["'", "!"]):
                        is_recursive_for_Ai = True
                if is_recursive_for_Ai:
                    has_direct_recursion = True
                    alpha_part = rhs_str[len(Ai):].strip()
                    recursive_alphas.append(alpha_part if alpha_part else "ε")
                else:
                    non_recursive_betas.append(rhs_str if rhs_str else "ε") 
            if has_direct_recursion:
                Ai_prime = Ai + "'" 
                while Ai_prime in all_defined_lhs_ever: 
                    Ai_prime += "'"
                all_defined_lhs_ever.add(Ai_prime)
                # Form Ai -> beta Ai' rules
                if not non_recursive_betas: 
                    new_productions[Ai] = [Ai_prime]
                    print(f"INFO: Variable '{Ai}' has only direct recursive rules. Transformed to '{Ai} -> {Ai_prime}'.")
                else:
                    new_Ai_rules = []
                    for beta in non_recursive_betas:
                        if beta == "ε":
                            new_Ai_rules.append(Ai_prime)
                        else:
                            new_Ai_rules.append(f"{beta} {Ai_prime}".strip())
                    new_productions[Ai] = list(dict.fromkeys(new_Ai_rules)) if new_Ai_rules else [Ai_prime]
                # Form Ai' -> alpha Ai' | epsilon rules
                new_Ai_prime_rules = []
                for alpha in recursive_alphas:
                    if alpha == "ε":
                        new_Ai_prime_rules.append(Ai_prime)
                    else:
                        new_Ai_prime_rules.append(f"{alpha} {Ai_prime}".strip())
                new_Ai_prime_rules.append("ε") 
                new_productions[Ai_prime] = list(dict.fromkeys(new_Ai_prime_rules))
            elif not has_direct_recursion and non_recursive_betas:
                new_productions[Ai] = list(dict.fromkeys(non_recursive_betas))
            elif not new_productions.get(Ai):
                new_productions[Ai] = ["ε"]
                print(f"INFO: Variable '{Ai}' has no productions after attempting LR removal. Setting to derive ε.")
        # Final cleanup: ensure no variable has an empty production list
        final_cleaned_productions = {}
        for lhs, rhss in new_productions.items():
            if not rhss:
                final_cleaned_productions[lhs] = ["ε"]
            else:
                cleaned_rhss = [rhs if rhs else "ε" for rhs in rhss]
                final_cleaned_productions[lhs] = list(dict.fromkeys(cleaned_rhss)) # Remove duplicates
        return final_cleaned_productions

    def process_grammar(self):
        grammar_text = self.text_editor.get("1.0", tk.END)
        print("\n--- Iniciando Procesamiento de Gramática ---")
        parsed_rules_initial_structure, initial_start_symbol, ordered_lhs_original = \
            self._parse_input_grammar(grammar_text)
        if not parsed_rules_initial_structure or not initial_start_symbol:
            for listbox in [self.listbox_v_orig, self.listbox_t_orig, self.listbox_v_transformed, self.listbox_t_transformed]:
                self._update_listbox(listbox, [])
            for tree_view in [self.tree_orig, self.tree_transformed]:
                self._update_treeview(tree_view, [])
            self.transformed_grammar_textbox.config(state=tk.NORMAL)
            self.transformed_grammar_textbox.delete("1.0", tk.END)
            self.transformed_grammar_textbox.config(state=tk.DISABLED)
            print("ERROR FATAL: Gramática de entrada vacía o sin símbolo inicial válido. Procesamiento detenido.")
            return
        internal_rules_kvp = {}
        all_lhs_vars_for_norm = set(parsed_rules_initial_structure.keys())
        for lhs, rhs_list in parsed_rules_initial_structure.items():
            internal_rules_kvp[lhs] = [self._normalize_rhs_for_internal(rhs, all_lhs_vars_for_norm) 
                                    for rhs in rhs_list if rhs] 
        v_orig, t_orig, p_orig_tree = self._analyze_grammar_for_display(
            internal_rules_kvp, initial_start_symbol, is_input_phase=True
        )
        self._update_listbox(self.listbox_v_orig, v_orig)
        self._update_listbox(self.listbox_t_orig, t_orig)
        self._update_treeview(self.tree_orig, p_orig_tree)

        # Remove Left Recursion
        # Pass copies to avoid modifying original internal_rules_kvp if it's used later
        transformed_rules_kvp_internal = self._remove_direct_left_recursion(
            {k: list(v) for k,v in internal_rules_kvp.items()}, 
            list(ordered_lhs_original) 
        )
        
        # Populate the new textbox for transformed grammar rules
        transformed_grammar_display_lines = []
        transformed_vars_set = set(transformed_rules_kvp_internal.keys())
        
        # Determine display order for LHS in the textbox
        ordered_lhs_for_textbox = []
        # Prioritize original start symbol and its derivatives
        if initial_start_symbol:
            # Add original start symbol if still present
            if initial_start_symbol in transformed_vars_set:
                ordered_lhs_for_textbox.append(initial_start_symbol)
            # Add its primed versions next
            temp_prime_check = initial_start_symbol
            while True:
                temp_prime_check += "'"
                if temp_prime_check in transformed_vars_set and temp_prime_check not in ordered_lhs_for_textbox:
                    ordered_lhs_for_textbox.append(temp_prime_check)
                else:
                    # Stop if prime not found or if it's a very long chain (safety)
                    if temp_prime_check.count("'") > 5 : break 
                    # also check for `!` if that was used
                    if not temp_prime_check.endswith("!'"): # Avoid adding S'' if S!' was already added
                        temp_prime_check_bang = temp_prime_check.replace("'", "!") 
                        if temp_prime_check_bang in transformed_vars_set and temp_prime_check_bang not in ordered_lhs_for_textbox:
                             ordered_lhs_for_textbox.append(temp_prime_check_bang)
                        elif temp_prime_check.count("'") > 5: break # break if we already broke from prime check
                    if temp_prime_check.count("'") > 5 : break

        # Add remaining original LHS symbols in their order
        for lhs in ordered_lhs_original:
            if lhs in transformed_vars_set and lhs not in ordered_lhs_for_textbox:
                ordered_lhs_for_textbox.append(lhs)
        # Add any other new LHS symbols (like T', F') sorted alphabetically
        remaining_lhs = sorted([lhs for lhs in transformed_vars_set if lhs not in ordered_lhs_for_textbox])
        ordered_lhs_for_textbox.extend(remaining_lhs)


        for lhs_disp in ordered_lhs_for_textbox:
            if lhs_disp not in transformed_rules_kvp_internal: continue # Should not happen
            
            rhs_display_parts = [self._format_rhs_for_display(internal_rhs, transformed_vars_set) 
                                 for internal_rhs in transformed_rules_kvp_internal[lhs_disp]]
            transformed_grammar_display_lines.append(f"{lhs_disp} = {' | '.join(rhs_display_parts)}")

        self.transformed_grammar_textbox.config(state=tk.NORMAL)
        self.transformed_grammar_textbox.delete("1.0", tk.END)
        self.transformed_grammar_textbox.insert("1.0", "\n".join(transformed_grammar_display_lines))
        self.transformed_grammar_textbox.config(state=tk.DISABLED)
        
        # Analyze and Display Transformed Grammar for V, T, and Production Matrix
        v_transformed, t_transformed, p_transformed_tree = \
            self._analyze_grammar_for_display(transformed_rules_kvp_internal, initial_start_symbol, is_input_phase=False)
        self._update_listbox(self.listbox_v_transformed, v_transformed)
        self._update_listbox(self.listbox_t_transformed, t_transformed)
        self._update_treeview(self.tree_transformed, p_transformed_tree)
        print("--- Procesamiento Completado ---")

    def _update_listbox(self, listbox, items):
        listbox.delete(0, END)
        for item in items: listbox.insert(END, item)

    def _update_treeview(self, tree, productions_list_with_arrows):
        for row in tree.get_children(): tree.delete(row)
        for var_display, prod_rhs_display in productions_list_with_arrows:
            tree.insert('', END, values=(var_display, prod_rhs_display))

if __name__ == "__main__":
    root = tk.Tk()
    app = GrammarApp(root)
    root.geometry("1250x800") 
    root.mainloop()
