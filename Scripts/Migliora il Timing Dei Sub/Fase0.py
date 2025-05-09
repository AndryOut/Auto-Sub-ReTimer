import os
import re
import pysrt
from tkinter import Tk, filedialog, Button, Label, Frame, Scrollbar, Canvas, IntVar, font, messagebox
from tkinter.ttk import Style

class SubtitleProcessor:
    def __init__(self):
        self.root = Tk()
        self.root.withdraw()
        
        # Tag configuration for sign detection
        self.STRONG_TAGS = [
            r'\\pos\([^)]+\)', r'\\org\([^)]+\)', r'\\kf\d+',
            r'\\move\([^)]+\)', r'\\clip\([^)]+\)', r'\\iclip\([^)]+\)',
            r'\\fscy\d+\.?\d*', r'\\frz?-?\d+\.?\d*', r'\\p[1-9]'
        ]
        
        self.MEDIUM_TAGS = [
            r'\\blur\d+\.?\d*', r'\\fscx\d+\.?\d*', r'\\be\d+',
            r'\\bord\d+\.?\d*', r'\\fs\d+\.?\d*', r'\\fad\([^)]+\)',
            r'\\shad\d+\.?\d*'
        ]
        
        self.FALSE_POSITIVES = ['top', 'bottom', 'oped', 'operator', 
                               'editor', 'speed', 'special', 'response', 
                               'operation', 'signature', 'sopra', 'subtitle', 'copy', 'copia']
        
        # UI Setup
        self.setup_styles()
        
    def setup_styles(self):
        self.style = Style()
        self.style.theme_use('clam')
        
        # Dark theme colors
        self.root.tk_setPalette(
            background='#333333',
            foreground='white',
            activeBackground='#444444',
            activeForeground='white'
        )
        
        self.style.configure('TFrame', background='#333333')
        self.style.configure('TLabel', background='#333333', foreground='white')
        self.style.configure('TButton', 
                           background='#555555', 
                           foreground='white',
                           font=('Helvetica', 9),
                           padding=5)
        
        self.bold_font = font.Font(family='Helvetica', size=9, weight='bold')
        self.mono_font = font.Font(family='Courier New', size=9)
        
    def run(self):
        messagebox.showinfo("Subtitle Processor", "Upload your sub ASS or SRT.")
        file_path = self.load_file()
        if not file_path:
            return
            
        output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        
        if file_path.lower().endswith('.ass'):
            # First process signs/dialogues/comments separation
            self.process_ass_file_separation(file_path, output_dir)
            
            # Then process the dialogues for top alignment
            dialogues_path = os.path.join(output_dir, "Dialoghi.ass")
            if os.path.exists(dialogues_path):
                self.process_ass_file_top_alignment(dialogues_path, output_dir)
        else:
            self.process_srt_file(file_path, output_dir)
        
    def load_file(self):
        return filedialog.askopenfilename(
            title="Select Subtitle File",
            filetypes=[("Subtitle files", "*.ass *.srt"), ("All files", "*.*")]
        )

    # ==================== ASS Separation Functions ====================
    def clean_text(self, text):
        cleaned = text
        tags_to_remove = [
            r'\\an[1-9]', r'\\q[0-4]', r'\\i[01]', r'\\b[01]',
            r'\\u1', r'\\s1', r'\\r[^\\]*', r'\\fe\d+'
        ]
        for tag in tags_to_remove:
            cleaned = re.sub(tag, '', cleaned)
        return cleaned

    def count_tags(self, text, tags):
        return sum(1 for tag in tags if re.search(tag, text))

    def is_sign(self, text):
        cleaned = self.clean_text(text)
        strong = self.count_tags(cleaned, self.STRONG_TAGS)
        medium = self.count_tags(cleaned, self.MEDIUM_TAGS)
        
        special = [
            '\\pos(' in cleaned and '\\an' in text,
            '\\p1' in cleaned and 'm ' in cleaned,
            bool(re.search(r'\\t\([^)]*(\\pos|\\move|\\fscx|\\fscy)', cleaned))
        ]
        
        return (strong >= 1 or medium >= 2 or any(special))

    def is_empty_event(self, line):
        if line.startswith(('Comment:', 'Dialogue:')):
            parts = line.split(',', 9)
            return len(parts) < 10 or not parts[9].strip()
        return False

    class ReviewDialog:
        def __init__(self, parent, lines):
            self.parent = parent
            self.lines = lines
            self.choices = []
            self.button_pairs = []
            self.line_indices = []  # Store original line indices
            
            self.setup_ui()
        
        def setup_ui(self):
            self.parent.title("Review Ambiguous Lines")
            self.parent.geometry("1000x700")
            
            # Main frame with scrollbar
            main_frame = Frame(self.parent)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            canvas = Canvas(main_frame, bg='#333333', highlightthickness=0)
            scrollbar = Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            self.scrollable_frame = Frame(canvas, bg='#333333')
            
            self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Bind mouse wheel for scrolling
            canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Add lines to review
            self.add_lines_to_review()
            
            # Control buttons
            control_frame = Frame(self.parent, bg='#333333')
            control_frame.pack(fill="x", pady=10)
            
            Button(control_frame, text="Confirm Choices", 
                  command=self.confirm_choices, bg="#4CAF50", fg="white",
                  font=('Helvetica', 10, 'bold')).pack(side="right", padx=10)
        
        def add_lines_to_review(self):
            for i, line in enumerate(self.lines):
                frame = Frame(self.scrollable_frame, bd=1, relief="solid", padx=5, pady=5, bg='#444444')
                frame.pack(fill="x", pady=2)
                
                parts = line.split(',', 9)
                if len(parts) >= 10:
                    style_name = parts[3].strip()
                    text = parts[9].strip()
                    
                    # Display style name and text
                    style_label = Label(frame, text=f"Style: {style_name}", 
                                      font=('Helvetica', 9, 'bold'), 
                                      bg='#444444', fg='white')
                    style_label.pack(anchor="w")
                    
                    text_display = Label(frame, text=text, wraplength=900, 
                                       justify="left", font=('Courier New', 9), 
                                       bg='#444444', fg='white', anchor="w")
                    text_display.pack(fill="x", expand=True, padx=5)
                    
                    # Choice variable and store original index
                    choice = IntVar(value=-1)
                    self.choices.append((choice, line, i))  # Now storing index too
                    
                    # Choice buttons
                    btn_frame = Frame(frame, bg='#444444')
                    btn_frame.pack(side="right", padx=5)
                    
                    btn_sign = Button(btn_frame, text="SIGN", width=8,
                                     command=lambda idx=len(self.choices)-1: self.make_choice(idx, 1),
                                     bg='#4CAF50', fg='white', font=('Helvetica', 9, 'bold'),
                                     activebackground='#45a049', relief='flat')
                    btn_dialogue = Button(btn_frame, text="DIALOGUE", width=8,
                                        command=lambda idx=len(self.choices)-1: self.make_choice(idx, 0),
                                        bg='#F44336', fg='white', font=('Helvetica', 9, 'bold'),
                                        activebackground='#e53935', relief='flat')
                    
                    btn_sign.pack(side="left", padx=2)
                    btn_dialogue.pack(side="left", padx=2)
                    
                    self.button_pairs.append((btn_sign, btn_dialogue))
        
        def make_choice(self, idx, choice):
            # Reset both buttons
            self.button_pairs[idx][0].config(relief='flat', bg='#4CAF50')
            self.button_pairs[idx][1].config(relief='flat', bg='#F44336')
            
            # Highlight selected button
            if choice == 1:
                self.button_pairs[idx][0].config(relief='sunken', bg='#2E7D32')
                self.choices[idx] = (IntVar(value=1), self.choices[idx][1], self.choices[idx][2])
            else:
                self.button_pairs[idx][1].config(relief='sunken', bg='#C62828')
                self.choices[idx] = (IntVar(value=0), self.choices[idx][1], self.choices[idx][2])
        
        def confirm_choices(self):
            # Check all choices are made
            for choice, _, _ in self.choices:
                if choice.get() == -1:
                    return
            
            # Create dictionaries to store the decisions by original index
            self.parent.choices_by_index = {idx: (line, choice.get()) 
                                          for choice, line, idx in self.choices}
            self.parent.completed = True
            self.parent.quit()
            self.parent.destroy()

    def process_ass_file_separation(self, file_path, output_dir):
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()

        # Extract sections
        header, styles, events = [], [], []
        current_section = None
        special_styles = set()  # Contiene OP/ED/Episode/Title/Titolo/Sign/Cartelli
        sign_keywords = {'sign', 'signs', 'cartello', 'cartelli'}
        episode_keywords = {'episode', 'ep', 'title', 'titolo'}

        for line in lines:
            line = line.strip('\n')
            if line.startswith('['):
                current_section = line
            
            if current_section in ('[Script Info]', '[Aegisub Project Garbage]'):
                header.append(line + '\n')
            elif current_section == '[V4+ Styles]':
                styles.append(line + '\n')
                if line.startswith('Style:'):
                    style_name = line.split(',')[0].replace('Style:', '').strip().lower()
                    # Aggiungi controllo per OP/ED/Episode/Title/Sign
                    if ('op' in style_name or 'ed' in style_name or 
                        'opening' in style_name or 'ending' in style_name or
                        any(keyword in style_name for keyword in sign_keywords) or
                        any(keyword in style_name for keyword in episode_keywords)):
                        special_styles.add(style_name)
            elif current_section == '[Events]':
                if line.startswith('Format:'):
                    format_line = line + '\n'  # Salva SOLO la riga Format
                elif line.strip() == '[Events]':
                    pass 
                else:
                    events.append((len(events), line + '\n'))

        # Classification
        signs = {}
        dialogues = {}
        comments = {}
        ambiguous_lines = []

        for idx, line in events:
            if line.startswith('Comment:') or self.is_empty_event(line):
                comments[idx] = line
            elif line.startswith('Dialogue:'):
                parts = line.split(',', 9)
                if len(parts) >= 10:
                    style = parts[3].strip().lower()
                    text = parts[9].strip()
                    
                    # Check special styles (OP/ED/Episode/Title/Sign)
                    is_special_style = (style in special_styles or
                                       'opening' in style or 'ending' in style)
                    is_sign_style = any(keyword in style for keyword in sign_keywords)
                    is_episode_style = any(keyword in style for keyword in episode_keywords)
                    is_fp = any(fp in style for fp in self.FALSE_POSITIVES)
                    
                    if (is_special_style or is_sign_style or is_episode_style) and not is_fp:
                        signs[idx] = line
                    else:
                        cleaned = self.clean_text(text)
                        strong = self.count_tags(cleaned, self.STRONG_TAGS)
                        medium = self.count_tags(cleaned, self.MEDIUM_TAGS)
                        
                        if medium == 2 and strong == 0:
                            ambiguous_lines.append((idx, line))
                        elif self.is_sign(text):
                            signs[idx] = line
                        else:
                            dialogues[idx] = line
            else:
                dialogues[idx] = line

        # Show review dialog if needed
        if ambiguous_lines:
            review_root = Tk()
            review_root.configure(bg='#333333')
            # Pass only the lines, not the indices
            dialog = self.ReviewDialog(review_root, [line for idx, line in ambiguous_lines])
            review_root.mainloop()
            
            if hasattr(review_root, 'completed') and review_root.completed:
                # Apply the choices while maintaining original order
                for i, (idx, line) in enumerate(ambiguous_lines):
                    if i in review_root.choices_by_index:
                        line, choice = review_root.choices_by_index[i]
                        if choice == 1:
                            signs[idx] = line
                        else:
                            dialogues[idx] = line
        
        # Save files in original order
        self.save_separated_files(output_dir, header, styles, format_line, signs, dialogues, comments)

    def save_separated_files(self, output_dir, header, styles, format_line, signs, dialogues, comments):
        os.makedirs(output_dir, exist_ok=True)
        
        # Combine all lines in original order
        all_indices = set(signs.keys()) | set(dialogues.keys()) | set(comments.keys())
        
        # Prepare the three output files
        signs_lines = []
        dialogues_lines = []
        comments_lines = []
        
        for idx in sorted(all_indices):
            if idx in signs:
                signs_lines.append((idx, signs[idx]))
            if idx in dialogues:
                dialogues_lines.append((idx, dialogues[idx]))
            if idx in comments:
                comments_lines.append((idx, comments[idx]))
        
        # Write files in original order
        for name, content in [
            ("Signs.ass", sorted(signs_lines, key=lambda x: x[0])),
            ("Dialoghi.ass", sorted(dialogues_lines, key=lambda x: x[0])),
            ("Comments.ass", sorted(comments_lines, key=lambda x: x[0]))
        ]:
            with open(os.path.join(output_dir, name), 'w', encoding='utf-8') as f:
                f.writelines(header)
                f.writelines(styles)
                f.write('[Events]\n')
                f.write(format_line)
                f.writelines([line for idx, line in content])

    # ==================== Top Alignment Functions ====================
    def read_ass_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            return file.readlines()

    def filter_dialogue_by_alignment(self, dialogue):
        filtered_dialogue = []
        discarded_dialogue = []

        for line in dialogue:
            if '\\an8' in line:  # Cerca "{\an8}" ovunque all'interno della riga, indipendentemente dai tag
                filtered_dialogue.append(line)
            else:
                discarded_dialogue.append(line)

        return filtered_dialogue, discarded_dialogue

    def write_ass_file(self, header, dialogue, format_line, file_path):
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(header + [format_line] + dialogue)

    def write_srt_file_from_ass(self, discarded_dialogue, file_path):
        from pysrt import SubRipFile, SubRipTime
        subs = SubRipFile()

        for idx, line in enumerate(discarded_dialogue):
            parts = line.split(',')

            # Calcolo dei tempi di inizio
            start_time_parts = parts[1].strip().split(':')
            start_hours = int(start_time_parts[0])
            start_minutes = int(start_time_parts[1])
            start_seconds = float(start_time_parts[2])
            start_time = SubRipTime(
                start_hours,
                start_minutes,
                int(start_seconds),
                int((start_seconds - int(start_seconds)) * 1000)
            )

            # Calcolo dei tempi di fine
            end_time_parts = parts[2].strip().split(':')
            end_hours = int(end_time_parts[0])
            end_minutes = int(end_time_parts[1])
            end_seconds = float(end_time_parts[2])
            end_time = SubRipTime(
                end_hours,
                end_minutes,
                int(end_seconds),
                int((end_seconds - int(end_seconds)) * 1000)
            )

            # Testo
            text = ','.join(parts[9:]).strip()

            # Crea il sottotitolo
            sub = pysrt.SubRipItem(index=idx + 1, start=start_time, end=end_time, text=text)
            subs.append(sub)

        # Salvataggio file .srt
        subs.save(file_path, encoding='utf-8')

    def find_top_alignments(self, styles, dialogue):
        top_alignments = ['7', '8', '9']
        top_styles = []
        alignment_index = None
        for line in styles:
            if line.startswith('Format:'):
                format_parts = [x.strip() for x in line.split(':')[1].split(',')]
                if 'Alignment' in format_parts:
                    alignment_index = format_parts.index('Alignment')
            elif line.startswith('Style:') and alignment_index is not None:
                style_parts = line.split(',')
                alignment = style_parts[alignment_index].strip()
                if alignment in top_alignments:
                    style_name = style_parts[0].replace('Style:', '').strip()
                    top_styles.append(style_name)

        if not top_styles or not any(line.split(',')[3].strip() in top_styles for line in dialogue):
            top_styles = self.find_alignments_in_dialogue(dialogue, top_alignments)

        return top_styles

    def find_alignments_in_dialogue(self, dialogue, top_alignments):
        dialogue_with_alignments = []
        for line in dialogue:
            if any(alignment in line for alignment in top_alignments) or '{\\an8}' in line:
                dialogue_with_alignments.append(line)
        return dialogue_with_alignments

    def filter_dialogue_by_style(self, dialogue, top_styles):
        filtered_dialogue = [line for line in dialogue if line.split(',')[3].strip() in top_styles or '{\\an8}' in line]
        discarded_dialogue = [line for line in dialogue if line.split(',')[3].strip() not in top_styles and '{\\an8}' not in line]
        return filtered_dialogue, discarded_dialogue

    def write_discarded_ass_file(self, header, discarded_dialogue, format_line, file_path):
        with open(file_path, 'w', encoding='utf-8') as file:
            # Scrive l'header e il formato degli eventi
            file.writelines(header + [format_line] + discarded_dialogue)

    def process_ass_file_top_alignment(self, file_path, output_dir):
        lines = self.read_ass_file(file_path)
        header_section = []
        dialogue_section = []
        capture_dialogue = False
        capture_styles = False
        styles_section = []
        format_line_events = ""
        format_line_styles = ""

        for line in lines:
            if line.startswith('[V4+ Styles]'):
                capture_styles = True
                header_section.append(line)
                continue
            if line.startswith('[Events]'):
                capture_styles = False
                capture_dialogue = True
                header_section.append(line)
                continue
            if capture_dialogue and line.startswith('Dialogue:'):
                dialogue_section.append(line)
            elif not capture_dialogue:
                header_section.append(line)
            if capture_styles and line.startswith('Format:'):
                format_line_styles = line
            if not capture_styles and line.startswith('Format:'):
                format_line_events = line
            if capture_styles:
                styles_section.append(line)

        # Usa le funzioni per filtrare i dialoghi
        top_styles = self.find_top_alignments(styles_section, dialogue_section)
        filtered_dialogue, discarded_dialogue = self.filter_dialogue_by_style(dialogue_section, top_styles)

        # Percorsi di output
        output_ass_file_path = os.path.join(output_dir, 'On Top.ass')
        output_srt_file_path = os.path.join(output_dir, 'Sub.srt')
        discarded_ass_file_path = os.path.join(output_dir, 'Dialoghi.ass')

        # Scrive i file di output
        self.write_ass_file(header_section, filtered_dialogue, format_line_events, output_ass_file_path)
        self.write_srt_file_from_ass(discarded_dialogue, output_srt_file_path)
        self.write_discarded_ass_file(header_section, discarded_dialogue, format_line_events, discarded_ass_file_path)

    # ==================== SRT Processing Functions ====================
    def process_srt_file(self, file_path, output_dir):
        subs = pysrt.open(file_path, encoding='utf-8')
        filtered_subs = pysrt.SubRipFile()
        discarded_subs = pysrt.SubRipFile()

        for sub in subs:
            if '\\an8' in sub.text:  # Filtra i sottotitoli con "{\an8}"
                filtered_subs.append(sub)
            else:
                discarded_subs.append(sub)

        filtered_output = os.path.join(output_dir, 'On Top.srt')
        discarded_output = os.path.join(output_dir, 'Sub.srt')

        filtered_subs.save(filtered_output, encoding='utf-8')
        discarded_subs.save(discarded_output, encoding='utf-8')

if __name__ == '__main__':
    processor = SubtitleProcessor()
    processor.run()