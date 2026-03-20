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
        except Exception: return False
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
    return re.sub(r',\s*([\]}])', r'\1', text)

def get_file_content(path: Path) -> str:
    if not path.exists(): return ""
    ext = path.suffix.lower()
    if ext == '.docx':
        docx = try_import("docx")
        if docx:
            doc = docx.Document(path)
            return "\n\n".join([p.text for p in doc.paragraphs if p.text.strip()])
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

# --- ACTIONS ---

def cmd_prepare(args):
    source_path = Path(args.input).resolve()
    temp_dir = Path.cwd() / "Temp_Build" / "Chunks"
    if temp_dir.exists(): shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)
    
    is_docx = source_path.suffix.lower() == '.docx'
    if is_docx:
        temp_docx = Path.cwd() / "Temp_Build" / f"{source_path.stem}_temp.docx"
        shutil.copy(source_path, temp_docx)
        print(f" -> Tagging footnotes: {source_path.name}")
        run_word_automation(str(temp_docx), "flatten")
        working_text = get_file_content(temp_docx)
    else:
        working_text = get_file_content(source_path)

    if not working_text:
        print("[ERR] Source empty."); sys.exit(1)

    blocks = chunk_text(working_text)
    for i, block in enumerate(blocks):
        chunk_file = temp_dir / f"chunk_{i+1:03d}.txt"
        chunk_file.write_text(block, encoding='utf-8')
    
    print(f"SUCCESS: Split into {len(blocks)} chunks in Temp_Build/Chunks/")

def cmd_verify(args):
    source = Path(args.source).read_text(encoding='utf-8')
    output = Path(args.output).read_text(encoding='utf-8')
    
    # Footnote Integrity
    source_fn, output_fn = source.count('[[FN]]'), output.count('[[FN]]')
    if output_fn < source_fn:
        print(f"[FAIL] Data Loss: Footnotes dropped ({output_fn}/{source_fn})")
        sys.exit(1)

    # Tag Integrity
    for tag in ['[[TEXT]]', '[[/TEXT]]']:
        if source.count(tag) != output.count(tag):
            print(f"[FAIL] Boundary Violation: {tag} mismatch")
            sys.exit(1)
    
    # Matrix Compliance
    if args.matrix:
        matrix_path = Path(args.matrix)
        if matrix_path.exists():
            matrix_raw = matrix_path.read_text(encoding='utf-8')
            matrix = json.loads(clean_json(matrix_raw))
            ban_list = matrix.get('lexicon', {}).get('filters', {}).get('ban_list', [])
            for word in ban_list:
                if word in output:
                    print(f"[FAIL] Matrix Violation: Banned word '{word}' found")
                    sys.exit(1)
    
    print("[PASS] Integrity verified.")

def cmd_finalize(args):
    chunks_dir = Path(args.chunks_dir)
    output_dir = Path.cwd() / "Output_Files"
    output_dir.mkdir(exist_ok=True)
    
    processed_files = sorted(chunks_dir.glob("processed_*.txt"))
    if not processed_files:
        print("[ERR] No processed chunks found."); sys.exit(1)
        
    final_text = "\n\n".join([f.read_text(encoding='utf-8') for f in processed_files])
    out_base = Path(args.input).stem
    out_txt = output_dir / f"{out_base}_final.txt"
    out_txt.write_text(final_text, encoding='utf-8')
    
    if Path(args.input).suffix.lower() == '.docx':
        docx = try_import("docx")
        if docx:
            out_docx = output_dir / f"{out_base}_final.docx"
            doc = docx.Document()
            for p_text in final_text.split('\n\n'):
                p = doc.add_paragraph(p_text); p.alignment = 2
            doc.save(out_docx)
            print(f" -> Restoring footnotes: {out_docx.name}")
            run_word_automation(str(out_docx), "restore")
            
    print(f"SUCCESS: Saved to {out_txt.name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TextualAgent CLI Utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Prepare
    p_prep = subparsers.add_parser("prepare")
    p_prep.add_argument("--input", required=True)

    # Verify
    p_ver = subparsers.add_parser("verify")
    p_ver.add_argument("--source", required=True)
    p_ver.add_argument("--output", required=True)
    p_ver.add_argument("--matrix")

    # Finalize
    p_fin = subparsers.add_parser("finalize")
    p_fin.add_argument("--input", required=True)
    p_fin.add_argument("--chunks_dir", required=True)

    args = parser.parse_args()
    try:
        if args.command == "prepare": cmd_prepare(args)
        elif args.command == "verify": cmd_verify(args)
        elif args.command == "finalize": cmd_finalize(args)
    except KeyboardInterrupt: print("\n[SYSTEM] Terminated.")
    except Exception as e: print(f"\n[FATAL] {e}")
