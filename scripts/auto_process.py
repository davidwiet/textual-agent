import sys, importlib
import time
import os
import re
import json
import argparse
import platform
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional, Any, Dict

# --- DEPENDENCY MANAGEMENT ---
def try_import(module_name: str) -> Any:
    try:
        # Robust import for submodules
        return importlib.import_module(module_name)
    except ImportError:
        return None

# --- CONSTANTS ---
EXTENSION_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_AGENTS_DIR = EXTENSION_ROOT / "Agents"

# --- FULLY AUTONOMOUS WORD LOGIC ---

VBA_FLATTEN = r'''
    Dim i As Long
    Dim NoteText As String
    For i = ActiveDocument.Footnotes.Count To 1 Step -1
        NoteText = ActiveDocument.Footnotes(i).Range.Text
        ActiveDocument.Footnotes(i).Reference.InsertAfter "[[FN]]" & NoteText & "[[/FN]]"
        ActiveDocument.Footnotes(i).Delete
    Next i
'''

VBA_RESTORE = r'''
    Dim myRange As Range
    Dim noteText As String
    Dim tagLength As Integer
    Set myRange = ActiveDocument.Content
    With myRange.Find
        .ClearFormatting
        .MatchWildcards = True
        .Text = "\[\[FN\]\]*\[\[/FN\]\]"
        Do While .Execute
            tagLength = Len(myRange.Text)
            noteText = Mid(myRange.Text, 7, tagLength - 13)
            myRange.Delete
            ActiveDocument.Footnotes.Add Range:=myRange, Text:=noteText
            myRange.Collapse Direction:=wdCollapseEnd
        Loop
    End With
'''

def run_word_automation(file_path: str, task: str) -> bool:
    system = platform.system()
    abs_path = os.path.abspath(file_path)
    vba_code = VBA_FLATTEN if task == "flatten" else VBA_RESTORE
    
    if system == "Darwin":
        script = f'''
        tell application "Microsoft Word"
            activate
            open "{abs_path}"
            set myDoc to active document
            try
                do Visual Basic "{vba_code.replace('"', '""')}"
                save myDoc
            on error errMsg
                log "Automation failed: " & errMsg
            end try
            close myDoc
        end tell
        '''
        try:
            subprocess.run(['osascript', '-e', script], capture_output=True, text=True, check=True)
            return True
        except Exception as e:
            print(f" [WARN] macOS Word automation failed: {e}")
            return False
    elif system == "Windows":
        win32 = try_import("win32com.client")
        if not win32: return False
        try:
            word = win32.Dispatch("Word.Application")
            word.Visible = False
            doc = word.Documents.Open(abs_path)
            try:
                if task == "flatten":
                    for i in range(doc.Footnotes.Count, 0, -1):
                        fn = doc.Footnotes(i)
                        txt = fn.Range.Text
                        fn.Reference.InsertAfter(f"[[FN]]{txt}[[/FN]]")
                        fn.Delete()
                else:
                    rng = doc.Content
                    find = rng.Find
                    find.ClearFormatting()
                    find.MatchWildcards = True
                    find.Text = r"\[\[FN\]\]*\[\[/FN\]\]"
                    while find.Execute():
                        raw_text = rng.Text
                        note_content = raw_text[6:-7]
                        rng.Delete()
                        doc.Footnotes.Add(Range=rng, Text=note_content)
                        rng.Collapse(0)
                doc.Save()
                return True
            except Exception: return False
            finally: doc.Close()
        except Exception: return False
    return False

def clean_json(text: str) -> str:
    """Robustly handle trailing commas in JSON."""
    return re.sub(r',\s*([\]}])', r'\1', text)

def get_file_content(path: Path) -> str:
    if not path.exists(): return ""
    ext = path.suffix.lower()
    if ext == '.docx':
        docx = try_import("docx")
        if docx:
            doc = docx.Document(path)
            return "\n\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    if ext == '.pdf':
        pypdf = try_import("pypdf")
        if pypdf:
            reader = pypdf.PdfReader(path)
            return "\n\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
    try:
        return path.read_text(encoding='utf-8').strip()
    except:
        return path.read_text(encoding='latin-1').strip()

def chunk_text(text: str, limit: int = 12000) -> List[str]:
    if not text: return []
    sep = '\n\n' if text.count('\n\n') > 5 else '\n'
    blocks, current, current_len = [], [], 0
    for p in text.split(sep):
        if current_len + len(p) < limit:
            current.append(p); current_len += len(p)
        else:
            if current: blocks.append(sep.join(current).strip())
            current, current_len = [p], len(p)
    if current: blocks.append(sep.join(current).strip())
    return blocks

def verify_integrity(source: str, output: str, matrix: Dict) -> Tuple[bool, str]:
    source_fn, output_fn = source.count('[[FN]]'), output.count('[[FN]]')
    if output_fn < source_fn:
        return False, f"Data Loss: Footnote count dropped ({output_fn} < {source_fn})."
    for tag in ['[[TEXT]]', '[[/TEXT]]']:
        if source.count(tag) != output.count(tag):
            return False, f"Boundary Violation: {tag} mismatch."
    ban_list = matrix.get('lexicon', {}).get('filters', {}).get('ban_list', [])
    for word in ban_list:
        if word in output:
            return False, f"Matrix Violation: Banned word '{word}' detected."
    return True, "OK"

def run_pipeline(args):
    genai = try_import("google.genai")
    if not genai:
        print("[ERR] 'google-genai' library required."); sys.exit(1)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[ERR] GEMINI_API_KEY environment variable not set."); sys.exit(1)
    client = genai.Client(api_key=api_key)
    
    source_path = Path(args.input).resolve()
    temp_dir, output_dir = Path.cwd() / "Temp_Build", Path.cwd() / "Output_Files"
    for d in [temp_dir, output_dir]: d.mkdir(exist_ok=True)
    
    is_docx = source_path.suffix.lower() == '.docx'
    if is_docx:
        temp_path = temp_dir / f"{source_path.stem}_temp.docx"
        shutil.copy(source_path, temp_path)
        print(f" -> Automatically tagging footnotes: {source_path.name}")
        run_word_automation(str(temp_path), "flatten")
        working_text = get_file_content(temp_path)
    else:
        working_text = get_file_content(source_path)

    if not working_text:
        print("[ERR] Source is empty."); sys.exit(1)

    agent_path = Path(args.agent)
    if not agent_path.exists():
        agent_path = DEFAULT_AGENTS_DIR / f"{args.agent.replace('.txt', '')}.txt"
    agent_instr = get_file_content(agent_path)
    
    matrix_path = Path(args.matrix) if args.matrix else Path.cwd() / "StyleMatrix.json"
    matrix_raw = get_file_content(matrix_path)
    matrix = json.loads(clean_json(matrix_raw)) if matrix_raw else {}
    
    blocks = chunk_text(working_text)
    print(f" -> Processing {len(blocks)} segments using {args.model}...")
    
    final_output = []
    for i, block in enumerate(blocks):
        print(f"    [Block {i+1}/{len(blocks)}] ", end="", flush=True)
        prompt = f"### SYSTEM MATRIX\n{json.dumps(matrix)}\n\n### MISSION\n{agent_instr}\n\n### TARGET\n{block}"
        
        attempts, success, txt = 0, False, ""
        # Improved backoff logic
        backoff = 35
        while attempts < 3:
            try:
                response = client.models.generate_content(model=args.model, contents=prompt)
                txt = "".join([p.text for p in response.candidates[0].content.parts if p.text])
                valid, msg = verify_integrity(block, txt, matrix)
                if valid:
                    final_output.append(txt); print("PASS"); success = True; break
                else:
                    attempts += 1; print(f"FAIL ({msg}) - Retrying...")
                    prompt += f"\n\n### AUDIT_FAILURE_WARNING\n{msg}. Maintain zero data loss."
            except Exception as e:
                if "429" in str(e):
                    print(f"RATE LIMIT (429) - Sleeping {backoff}s...")
                    time.sleep(backoff); backoff *= 1.5
                elif "404" in str(e):
                    print(f"FATAL: Model {args.model} not found."); sys.exit(1)
                else:
                    print(f"ERR ({e})"); time.sleep(5)
                attempts += 1
        if not success: final_output.append(txt)

    out_txt = output_dir / f"{source_path.stem}_{agent_path.stem}.txt"
    out_txt.write_text("\n\n".join(final_output), encoding='utf-8')
    
    if is_docx:
        docx = try_import("docx")
        if docx:
            out_docx = output_dir / f"{source_path.stem}_{agent_path.stem}.docx"
            new_doc = docx.Document()
            for chunk in final_output:
                for p in chunk.split('\n\n'):
                    para = new_doc.add_paragraph(p); para.alignment = 2
            new_doc.save(out_docx)
            print(f" -> Automatically restoring footnotes: {out_docx.name}")
            run_word_automation(str(out_docx), "restore")

    print(f"\nCOMPLETED: {out_txt.name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--agent", required=True)
    parser.add_argument("--matrix")
    parser.add_argument("--registry")
    parser.add_argument("--model", default="gemini-2.0-flash")
    args = parser.parse_args()
    try: run_pipeline(args)
    except KeyboardInterrupt: print("\n[SYSTEM] Terminated.")
    except Exception as e: print(f"\n[FATAL] {e}")
