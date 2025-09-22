# Batch Image Converter

Batch Image Converter is a small GUI tool (Tkinter + Pillow) for batch-processing images in a folder. It can convert images to grayscale and/or invert their colors while preserving transparency. Outputs are saved next to the originals with clear suffixes.

- GUI: Tkinter
- Image processing: Pillow (PIL)
- License: GNU GPL v3.0

## Features
- Batch convert common image formats: JPG, JPEG, PNG, BMP, GIF, TIFF, WEBP.
- Preserve alpha/transparency when converting.
- Two operations: Grayscale and Invert (can run either or both).
- Outputs saved with suffixes:
  - <original name> - Grayscale.<ext>
  - <original name> - Inverted.<ext>
- Option to open output folder automatically after conversion.
- Progress bar during processing (auto-hides 10 seconds after completion).
- Preview pane for selected files.
- Choose output format: PNG, JPEG, or WEBP.

## Requirements
- Python 3.8+ (3.9+ recommended)
- Pillow

Install dependencies:
```
pip install pillow
```

## Usage
1. Run the app:
   ```
   python batch_image_converter.py
   ```
2. Click "Browse..." and select a folder containing images.
3. The file list will populate with supported images.
4. Select options:
   - Check "Convert to grayscale" to create grayscale outputs.
   - Check "Invert images" to create inverted-color outputs.
   - Select an output format (PNG recommended to preserve alpha).
   - Optionally check "Open output folder after conversion".
5. Click "Convert Images" to start.
6. Monitor progress in the progress bar. When finished a small popup confirms completion; the progress bar resets and hides after 10 seconds.
7. Converted files are saved in the same folder with the suffixes shown above.

Notes:
- If both operations are selected, the app uses the grayscale output as the input for the invert step (so "Invert" after "Grayscale" yields an inverted grayscale image).
- JPEG does not support alpha; when choosing JPEG the alpha channel will be flattened.

## Example
Original: photo.jpg  
Outputs:
- photo - Grayscale.png
- photo - Inverted.png

If you choose JPEG as output format:
- photo - Grayscale.jpeg
- photo - Inverted.jpeg

## Troubleshooting
- Preview may fail for some files (palette GIFs, malformed images); conversion will still attempt to process files.
- Check the terminal/console for error lines if any files fail during processing.
- On Linux, ensure xdg-open is available for the "Open output folder" feature.

## Development / Contributing
Contributions, bug reports and suggestions are welcome. Possible enhancements:
- Recursive folder processing
- Drag-and-drop support
- Incremental filename collision resolution
- CLI batch mode

To contribute:
1. Fork the repository
2. Create a branch for your feature/fix
3. Open a pull request describing your changes

## License — GNU GENERAL PUBLIC LICENSE v3.0
This project is licensed under the GNU GPL v3.0. A copy of the license follows.

[Full license text begins here]

GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.

... (full license text) ...

To view the full license, see: https://www.gnu.org/licenses/gpl-3.0.en.html

You should include a LICENSE file in your repository containing the full GPLv3 text and add the appropriate copyright notice, for example:

Copyright (C) 2025 Your Name

Replace "Your Name" with your name or organization.

## Files
- batch_image_converter.py — main script
- README.md — this file
- LICENSE — GNU GPL v3.0 full text

## Contact
Create issues or pull requests on the repository. Include a short description and steps to reproduce for bugs.