#!/usr/bin/env python3
import sys
import os
import subprocess
import pkgutil

# ---------------------------
# Dependency check + installer
# ---------------------------
REQUIRED_PKGS = ["PIL"]  # Pillow provides the "PIL" package name

def has_tkinter():
    try:
        import tkinter  # type: ignore
        return True
    except Exception:
        return False

def check_requirements():
    missing = []
    for pkg in REQUIRED_PKGS:
        if not pkgutil.find_loader(pkg):
            missing.append(pkg)
    if not has_tkinter():
        missing.append("tkinter")
    return missing

def prompt_yes_no(question):
    try:
        ans = input(f"{question} [y/N]: ").strip().lower()
    except EOFError:
        return False
    return ans in ("y", "yes", "y\n")

def install_packages(pkgs):
    python = sys.executable
    cmd = [python, "-m", "pip", "install", "--upgrade"] + pkgs
    print("Running:", " ".join(cmd))
    try:
        proc = subprocess.run(cmd, check=False)
        return proc.returncode == 0
    except Exception as e:
        print("Install failed:", e)
        return False

def main_check():
    missing = check_requirements()
    if not missing:
        return True
    print("Missing dependencies detected:", ", ".join(missing))
    if not prompt_yes_no("Install missing dependencies now?"):
        print("Exiting. Install required packages and re-run the script.")
        return False

    pip_install = [m for m in missing if m != "tkinter"]
    ok = True
    if pip_install:
        ok = install_packages(pip_install)

    if "tkinter" in missing:
        print("\nNote: 'tkinter' is usually a system package and not installable via pip.")
        print("Examples to install tkinter:")
        print("  Debian/Ubuntu: sudo apt install python3-tk")
        print("  Fedora/RHEL:   sudo dnf install python3-tkinter")
        print("  Arch:          sudo pacman -S tk")
        print("  macOS: Use the official Python installer or Homebrew's python which includes Tk")
        if not prompt_yes_no("Have you installed the system package for tkinter now?"):
            return False

    if not ok:
        print("Some pip installs failed. Please install them manually and re-run.")
        return False

    # Re-exec the script so newly-installed packages can be imported
    print("Re-launching script to apply changes...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

if __name__ == "__main__":
    if not main_check():
        sys.exit(1)

# ---------------------------
# Main app imports and code
# ---------------------------
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageOps, ImageTk

SUPPORTED_EXTS = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp")

def invert_image(im: Image.Image) -> Image.Image:
    im_conv = im.convert("RGBA")
    r, g, b, a = im_conv.split()
    rgb = Image.merge("RGB", (r, g, b))
    inv_rgb = ImageOps.invert(rgb)
    inv_image = Image.merge("RGBA", (*inv_rgb.split(), a))
    return inv_image

def grayscale_image(im: Image.Image) -> Image.Image:
    has_alpha = im.mode in ("RGBA", "LA") or im.info.get("transparency") is not None
    if has_alpha:
        im_conv = im.convert("RGBA")
        r, g, b, a = im_conv.split()
        gray = ImageOps.grayscale(Image.merge("RGB", (r, g, b)))
        gray_rgba = Image.merge("RGBA", (gray, gray, gray, a))
        return gray_rgba
    else:
        return ImageOps.grayscale(im).convert("RGBA")

def save_image(img: Image.Image, out_path: str, fmt="PNG"):
    img.save(out_path, format=fmt)

def open_folder(path):
    try:
        if sys.platform.startswith("darwin"):
            os.system(f'open "{path}"')
        elif os.name == "nt":
            os.startfile(path)
        else:
            os.system(f'xdg-open "{path}"')
    except Exception:
        pass

def show_temporary_message(title, info_text, seconds=10):
    win = tk.Toplevel(root)
    win.title(title)
    win.resizable(False, False)
    win.attributes("-topmost", True)

    frm = tk.Frame(win, padx=16, pady=12)
    frm.pack()

    lbl_icon = tk.Label(frm, text="✅", font=("Segoe UI", 28), fg="green")
    lbl_icon.grid(row=0, column=0, rowspan=2, padx=(0,12))

    lbl_title = tk.Label(frm, text=title, font=("Segoe UI", 12, "bold"))
    lbl_title.grid(row=0, column=1, sticky="w")

    lbl_info = tk.Label(frm, text=info_text, justify="left", anchor="w")
    lbl_info.grid(row=1, column=1, sticky="w")

    win.update_idletasks()
    x = root.winfo_rootx() + (root.winfo_width() - win.winfo_width()) // 2
    y = root.winfo_rooty() + (root.winfo_height() - win.winfo_height()) // 2
    win.geometry(f"+{x}+{y}")

    def close_after():
        time.sleep(seconds)
        try:
            win.destroy()
        except Exception:
            pass

    threading.Thread(target=close_after, daemon=True).start()

def load_folder_files(folder):
    files = [f for f in os.listdir(folder)
             if f.lower().endswith(SUPPORTED_EXTS) and os.path.isfile(os.path.join(folder, f))]
    files.sort()
    listbox_files.delete(0, tk.END)
    for f in files:
        listbox_files.insert(tk.END, f)
    status_var.set(f"{len(files)} image(s) loaded")
    clear_preview()

def select_folder():
    folder = filedialog.askdirectory(title="Select folder with images")
    if not folder:
        return
    folder_var.set(folder)
    load_folder_files(folder)

def on_list_select(evt):
    sel = listbox_files.curselection()
    if not sel:
        return
    idx = sel[0]
    fname = listbox_files.get(idx)
    path = os.path.join(folder_var.get(), fname)
    show_preview(path)

def show_preview(path):
    try:
        with Image.open(path) as im:
            preview_w, preview_h = 360, 360
            im.thumbnail((preview_w, preview_h), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(im.convert("RGBA"))
            preview_label.config(image=tk_img)
            preview_label.image = tk_img
            preview_name.config(text=os.path.basename(path))
    except Exception as e:
        preview_label.config(image="")
        preview_label.image = None
        preview_name.config(text=f"Cannot preview: {e}")

def clear_preview():
    preview_label.config(image="")
    preview_label.image = None
    preview_name.config(text="No file selected")

def remove_selected():
    sel = listbox_files.curselection()
    if not sel:
        messagebox.showinfo("Remove file", "No file selected to remove.")
        return
    idx = sel[0]
    fname = listbox_files.get(idx)
    listbox_files.delete(idx)
    status_var.set(f"Removed: {fname}")

def process_folder(folder, files, do_grayscale, do_invert, open_after, out_format):
    if not (do_grayscale or do_invert):
        messagebox.showwarning("No option", "Please select an option to continue")
        return

    # ensure the bar is visible for this run
    try:
        progress_bar.pack(fill="x", padx=0)
    except Exception:
        pass

    btn_convert.config(state="disabled")
    btn_remove.config(state="disabled")
    btn_browse.config(state="disabled")
    listbox_files.config(state="disabled")

    total_steps = 0
    if do_grayscale:
        total_steps += len(files)
    if do_invert:
        total_steps += len(files)
    progress_var.set(0)
    progress_bar["maximum"] = total_steps

    errors = []
    step = 0

    for fname in files:
        base, _ = os.path.splitext(fname)
        src_path = os.path.join(folder, fname)

        if do_grayscale:
            out_name = f"{base} - Grayscale.{out_format.lower()}"
            out_path = os.path.join(folder, out_name)
            try:
                with Image.open(src_path) as im_orig:
                    img_gray = grayscale_image(im_orig)
                    save_image(img_gray, out_path, fmt=out_format.upper())
            except Exception as e:
                errors.append(f"Grayscale {fname}: {e}")
            step += 1
            progress_var.set(step)

        if do_invert:
            if do_grayscale:
                src_for_invert = os.path.join(folder, f"{base} - Grayscale.{out_format.lower()}")
                if not os.path.isfile(src_for_invert):
                    src_for_invert = src_path
            else:
                src_for_invert = src_path

            out_name = f"{base} - Inverted.{out_format.lower()}"
            out_path = os.path.join(folder, out_name)
            try:
                with Image.open(src_for_invert) as src_im:
                    img_inv = invert_image(src_im)
                    save_image(img_inv, out_path, fmt=out_format.upper())
            except Exception as e:
                errors.append(f"Invert {fname}: {e}")
            step += 1
            progress_var.set(step)

    progress_var.set(progress_bar["maximum"])
    time.sleep(0.1)

    folder_name = os.path.basename(folder) or folder
    info_text = f"Folder: {folder_name}\nPath: {folder}"
    show_temporary_message("Conversion Complete", info_text, 10)

    if errors:
        print("Errors during processing:")
        for err in errors:
            print(err)
        status_var.set(f"Completed with {len(errors)} errors.")
    else:
        status_var.set(f"Conversion finished: {len(files)} file(s) processed.")

    # schedule clearing/hiding of the progress bar after 10 seconds (main thread)
    def _clear_progress():
        try:
            progress_var.set(0)
            progress_bar.pack_forget()
        except Exception:
            pass

    root.after(10_000, _clear_progress)

    btn_convert.config(state="normal")
    btn_remove.config(state="normal")
    btn_browse.config(state="normal")
    listbox_files.config(state="normal")

    if open_after:
        open_folder(folder)

def on_convert_click():
    folder = folder_var.get()
    if not folder or not os.path.isdir(folder):
        messagebox.showwarning("No folder", "Please select a valid folder first.")
        return
    files = list(listbox_files.get(0, tk.END))
    if not files:
        messagebox.showinfo("No files", "No files to convert.")
        return
    do_invert = invert_var.get()
    do_grayscale = gray_var.get()
    out_format = out_format_var.get() or "PNG"
    threading.Thread(target=process_folder, args=(folder, files, do_grayscale, do_invert, open_var.get(), out_format), daemon=True).start()

def create_gui():
    global root, folder_var, listbox_files, preview_label, preview_name
    global status_var, btn_convert, btn_remove, btn_browse, progress_var, progress_bar
    global invert_var, gray_var, open_var, out_format_var

    root = tk.Tk()
    root.title("Batch Invert / Grayscale Images")
    root.geometry("1000x560")
    root.minsize(900, 520)

    left = tk.Frame(root, padx=12, pady=12)
    left.pack(side="left", fill="y")

    lbl = tk.Label(left, text="Select a folder to batch convert images:")
    lbl.pack(anchor="w")

    top_row = tk.Frame(left)
    top_row.pack(fill="x", pady=6)

    folder_var = tk.StringVar()
    entry = tk.Entry(top_row, textvariable=folder_var, width=56)
    entry.pack(side="left", padx=(0,8), fill="x", expand=True)

    btn_browse = tk.Button(top_row, text="Browse...", command=select_folder, width=12)
    btn_browse.pack(side="right")

    open_var = tk.BooleanVar(value=True)
    chk_open = tk.Checkbutton(left, text="Open output folder after conversion", variable=open_var)
    chk_open.pack(anchor="w", pady=6)

    opts_frame = tk.LabelFrame(left, text="Options", padx=8, pady=8)
    opts_frame.pack(fill="x", pady=6)

    invert_var = tk.BooleanVar(value=True)
    gray_var = tk.BooleanVar(value=False)
    chk_inv = tk.Checkbutton(opts_frame, text='Invert images and save as " - Inverted"', variable=invert_var)
    chk_inv.pack(anchor="w")
    chk_gray = tk.Checkbutton(opts_frame, text='Convert to grayscale and save as " - Grayscale"', variable=gray_var)
    chk_gray.pack(anchor="w")

    fmt_frame = tk.Frame(left)
    fmt_frame.pack(fill="x", pady=(6,0))
    tk.Label(fmt_frame, text="Output format:").pack(side="left")
    out_format_var = tk.StringVar(value="PNG")
    out_format_menu = ttk.Combobox(fmt_frame, textvariable=out_format_var, values=["PNG", "JPEG", "WEBP"], width=8, state="readonly")
    out_format_menu.pack(side="left", padx=(6,0))

    btn_convert = tk.Button(left, text="Convert Images", width=20, bg="#0078D7", fg="white", command=on_convert_click)
    btn_convert.pack(anchor="w", pady=6)

    btn_remove = tk.Button(left, text="Remove Selected File", width=20, command=remove_selected)
    btn_remove.pack(anchor="w", pady=4)

    status_var = tk.StringVar(value="No folder selected")
    lbl_status = tk.Label(left, textvariable=status_var, anchor="w")
    lbl_status.pack(fill="x", pady=4)

    note = tk.Label(left, text='Outputs are saved as "<original name> - Inverted.<ext>" and/or "<original name> - Grayscale.<ext>".', wraplength=320, justify="left")
    note.pack(fill="x", pady=4)

    progress_frame = tk.Frame(left, pady=6)
    progress_frame.pack(fill="x")
    progress_var = tk.IntVar(value=0)
    progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate", variable=progress_var)
    progress_bar.pack(fill="x", padx=0)

    right = tk.Frame(root, padx=12, pady=12)
    right.pack(side="right", fill="both", expand=True)

    files_frame = tk.LabelFrame(right, text="Files in folder", padx=8, pady=8)
    files_frame.pack(side="left", fill="y", padx=0, pady=4)

    listbox_files = tk.Listbox(files_frame, width=40, height=24)
    listbox_files.pack(side="left", fill="y")
    listbox_files.bind("<<ListboxSelect>>", on_list_select)

    scroll = tk.Scrollbar(files_frame, orient="vertical", command=listbox_files.yview)
    scroll.pack(side="right", fill="y")
    listbox_files.config(yscrollcommand=scroll.set)

    preview_frame = tk.LabelFrame(right, text="Preview", padx=8, pady=8)
    preview_frame.pack(side="left", fill="both", expand=True, pady=4)

    preview_name = tk.Label(preview_frame, text="No file selected", anchor="w")
    preview_name.pack(anchor="nw")

    preview_label = tk.Label(preview_frame, bd=2, relief="sunken", width=56, height=28, bg="black")
    preview_label.pack(fill="both", expand=True, pady=6)

    return root

if __name__ == "__main__":
    try:
        root = create_gui()
        root.mainloop()
    except Exception:
        import traceback, tkinter.messagebox as mb
        mb.showerror("Startup error", traceback.format_exc())
        raise
