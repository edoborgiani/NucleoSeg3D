# NucleoSeg3D

**NucleoSeg3D** is a Jupyter-notebook pipeline for the segmentation and quantification of nuclei, cells and fluorescent markers in 3D (and 2D) microscopy images, built on the Napari ecosystem. It targets researchers in bioimage analysis who need a robust, reproducible workflow for volumetric fluorescence data.

Current version: **v1.6.4** (`NucleoSeg3D_v1.6.4.ipynb`).

### What's new in v1.6.4
- **Validated segmentation settings**: every nuclei-segmentation setting (smoothing, threshold, watershed split, size refinement, haze removal, edges, …) was tuned against four manually annotated images (mean F1 0.51, F1@0.5 0.74) and is read from `helpers/optimal_settings_v1.6.4.json`. They are no longer edited in the notebook; any one can still be changed by name with `custom_settings` (Cell 4).
- **NUCLEI contrast from the image**: the NUCLEI channel contrast/gamma is always set from its own histogram, with the rule the settings were validated with.
- **Nucleus size from the image**: `nuclei_diameter` is only a starting value; the typical nucleus is measured in each image and the nucleus size, resolution (`scale_factor`) and µm sizes are adapted to it (3D images).
- **New NUCLEI steps**: out-of-focus haze removal slice by slice, optional depth (Z attenuation) correction, trim of Z flares, split of nuclei stacked in Z, nuclei the threshold missed added back, and every nucleus edge redrawn relative to its own brightness.
- **Calibrated automatic contrast** for the marker channels: `automatic_contrast = 'calibrated'`.
- Batch mode applies all of the above to every image.

> **Disclaimer:** This repository is freely available for use. The associated pipeline is currently being prepared for publication — please contact [Edoardo Borgiani](https://github.com/edoborgiani) for more information on how to use the pipeline or for collaboration enquiries.

## Features
- **2D and 3D images**: a file without a Z stack (or a ROI with a single Z slice) is detected automatically and processed as a 2D image — segmented in the image plane, with every size reported as an area (µm²) instead of a volume; the 3D-only exports are skipped. Plain TIFFs (no OME metadata) are read by their dimensions: 3 = a 2D image with channels, 4 = a 3D stack with channels.
- **Interactive stain table**: after loading, pick each condition's channel and display color from drop-down menus, type the marker names and tick which markers form the cytoplasm (intracellular / membrane) — no hand-written `stain_dict`. The confirmed table is saved and reused on the next run, and also names and colors the channels of the interactive ROI preview.
- **Batch mode**: set `input_file` to a folder to process every image in it with the same settings; outputs go to `<folder>_output/<image name>/`. Images whose channel list differs from the first one are flagged before the batch starts. 2D and 3D images can be mixed.
- **Automatic splitting of touching nuclei and cells**: a built-in first pass (including splitting a nucleus that forks into separate islands above and below its centre), then a size-based refinement that re-splits oversized labels with increasingly aggressive settings and merges small fragments into their neighbour. In addition:
  - **split gamma**: a gamma > 1 on the intensity used to split makes the dim seams between touching objects darker faster than the signal, so the split zones are more distinct; it grows at every re-split level;
  - **merge of split slivers**: slivers of a few pixels/voxels left by a split are merged into the closest big piece of the same split.
- **Image processing**: normalization, resampling to isotropic voxel size, denoising, thresholding, and watershed / StarDist / Cellpose segmentation (3D, or 2D on a 2D image).
- **Interactive ROI selection**: set `interactive_roi = True` to drag a rectangle in a napari window instead of typing pixel coordinates.
- **Validated settings**: the nuclei segmentation runs with settings validated against manual ground truths (`helpers/optimal_settings_v1.6.4.json`); the NUCLEI contrast and the nucleus size are taken from each image.
- **Automatic contrast**: set `automatic_contrast = 'calibrated'` (or `True` for the older histogram rule) to skip the interactive napari contrast/gamma viewer for the marker channels and pick contrast limits per channel from the histogram.
- **Napari integration**: interactive visualization at each processing step.
- **Quantification & export**: per-cell marker statistics (for positive cells and for all cells), spatial and size distributions, Excel reports, per-cell KDE plots and a PDF report, and 3D mesh export (VTK/STL/INP, 3D images only).
- **Helper library** (`helpers/`): all processing, quantification, visualization and export logic lives in Python modules, so the notebook stays short and readable.

## Repository Structure
```
.
├── NucleoSeg3D_v1.6.4.ipynb        # The NucleoSeg3D notebook (current)
├── NucleoSeg3D_v1.6.3.ipynb        # Previous version
├── requirements.txt                # Python dependencies
├── overrides.txt                   # uv --override file (see Prerequisites)
├── README.md                       # This file
└── helpers/
    ├── __init__.py
    ├── notebook_helpers.py         # Core processing, segmentation, and export functions
    ├── notebook_setup_helpers.py   # Package installation and import loader
    ├── optimal_settings.py         # Loads the validated settings and applies them per image
    └── optimal_settings_v1.6.4.json # Validated segmentation settings and their scores
```

## Getting Started

Type (or paste) **one command at a time**, press **Enter**, and wait for it to finish before the next one.

### Prerequisites

- **Python 3.10–3.14** (3.10/3.11 are the most tested; avoid 3.15+). Download from [python.org/downloads](https://www.python.org/downloads/).
  - On **Python 3.14**, StarDist (`trig_stardist`) and `.czi` files are unavailable (no TensorFlow / `aicspylibczi` wheels). Use 3.10–3.13 if you need them.
- **Git**, to download the repository. Download from [git-scm.com/downloads](https://git-scm.com/downloads).
- **[`uv`](https://github.com/astral-sh/uv)** is installed in the steps below. It is used instead of plain `pip` because it is much faster, and because its `--override` flag is needed to install on Python 3.13 (`aicsimageio` pins an `lxml` with no 3.13 wheels). On other versions the flag does nothing, so the same command works everywhere.

### Windows

> **Use PowerShell, not Command Prompt.** Open the Start menu and search for "PowerShell" (dark blue icon with `>_`). The VS Code terminal and Windows Terminal also use PowerShell by default.

1. **Check that Python is installed** — it should print `Python 3.1x.x`:
   ```powershell
   python --version
   ```
   If `python` is not recognized, use the Python Launcher instead: replace `python` with `py -3.11` (or your version) in step 5.

2. **Go to the folder where you want the project** (e.g. Documents):
   ```powershell
   cd $HOME\Documents
   ```

3. **Download the repository:**
   ```powershell
   git clone https://github.com/edoborgiani/NucleoSeg3D.git
   ```

4. **Enter the project folder:**
   ```powershell
   cd NucleoSeg3D
   ```

5. **Create a virtual environment** (an isolated Python for this project):
   ```powershell
   python -m venv .venv
   ```

6. **Activate it** — `(.venv)` appears at the start of the prompt:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
   If you get an error about *running scripts being disabled*, run the command below once, answer `Y`, then repeat step 6:
   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
   ```

7. **Install `uv`:**
   ```powershell
   pip install uv
   ```

8. **Install the dependencies** (takes a few minutes):
   ```powershell
   uv pip install -r requirements.txt --override overrides.txt
   ```

9. **Launch Jupyter** — it opens in your browser:
   ```powershell
   jupyter notebook
   ```

10. **Open the notebook** `NucleoSeg3D_v1.6.4.ipynb`.

**Next time**, open PowerShell in the project folder and repeat only step 6 (activate) and step 9 (launch Jupyter).

---

### macOS

Open the **Terminal** app (Applications → Utilities → Terminal).

1. **Check that Python is installed** — it should print `Python 3.1x.x`:
   ```bash
   python3 --version
   ```

2. **Go to the folder where you want the project** (e.g. Documents):
   ```bash
   cd ~/Documents
   ```

3. **Download the repository:**
   ```bash
   git clone https://github.com/edoborgiani/NucleoSeg3D.git
   ```

4. **Enter the project folder:**
   ```bash
   cd NucleoSeg3D
   ```

5. **Create a virtual environment** (an isolated Python for this project):
   ```bash
   python3 -m venv .venv
   ```

6. **Activate it** — `(.venv)` appears at the start of the prompt:
   ```bash
   source .venv/bin/activate
   ```

7. **Install `uv`:**
   ```bash
   pip install uv
   ```

8. **Install the dependencies** (takes a few minutes):
   ```bash
   uv pip install -r requirements.txt --override overrides.txt
   ```

9. **Launch Jupyter** — it opens in your browser:
   ```bash
   jupyter notebook
   ```

10. **Open the notebook** `NucleoSeg3D_v1.6.4.ipynb`.

**Next time**, open Terminal in the project folder and repeat only step 6 (activate) and step 9 (launch Jupyter).

#### Apple Silicon (M1/M2/M3): if step 8 fails

If step 8 fails with build errors for `tetgen` or `meshlib`, install [Miniforge](https://github.com/conda-forge/miniforge) and use a conda environment instead of steps 5–6:

- **Create the environment:**

  ```bash
  conda create -n nucleoseg3d python=3.10
  ```

- **Activate it** (this replaces step 6, also next time):

  ```bash
  conda activate nucleoseg3d
  ```

- Then continue from step 7.

---

### Linux

Open a terminal.

1. **Check that Python is installed** — it should print `Python 3.1x.x`:
   ```bash
   python3 --version
   ```

2. **Go to the folder where you want the project** (e.g. your home folder):
   ```bash
   cd ~
   ```

3. **Download the repository:**
   ```bash
   git clone https://github.com/edoborgiani/NucleoSeg3D.git
   ```

4. **Enter the project folder:**
   ```bash
   cd NucleoSeg3D
   ```

5. **Create a virtual environment** (an isolated Python for this project):
   ```bash
   python3 -m venv .venv
   ```
   On Debian/Ubuntu, if this fails with `ensurepip is not available`, run the command below (use e.g. `python3.11-venv` for a non-default version), then repeat step 5:
   ```bash
   sudo apt-get install python3-venv
   ```

6. **Activate it** — `(.venv)` appears at the start of the prompt:
   ```bash
   source .venv/bin/activate
   ```

7. **Install `uv`:**
   ```bash
   pip install uv
   ```

8. **Install the dependencies** (takes a few minutes):
   ```bash
   uv pip install -r requirements.txt --override overrides.txt
   ```

9. **Launch Jupyter** — it opens in your browser:
   ```bash
   jupyter notebook
   ```

10. **Open the notebook** `NucleoSeg3D_v1.6.4.ipynb`.

**Next time**, open a terminal in the project folder and repeat only step 6 (activate) and step 9 (launch Jupyter).

#### Headless servers only

On a server without a display (e.g. an HPC cluster over SSH), napari needs a virtual display. Not needed on a desktop Linux installation. Before step 9:

- **Install the virtual display:**

  ```bash
  sudo apt-get install libxcb-xinerama0 xvfb
  ```

- **Point napari to it:**

  ```bash
  export DISPLAY=:99
  ```

- **Start it in the background:**

  ```bash
  Xvfb :99 -screen 0 1024x768x24 &
  ```

## Usage

- Run the notebook cells in order. Each code cell has a one-line description right above it (**Cell N** — title), each setting is explained by a short comment on its line, and the notebook is divided into six sections: imports → inputs and setup → preparation → processing and segmentation → quantification → export.
- The first cell calls `load_nuclei_notebook_setup()` to import all required libraries in one step; the second calls `reload_helpers()` so edits to the helper file take effect without restarting the kernel.
- Use Napari for interactive visualization at any step.
- All processing logic lives in `helpers/notebook_helpers.py` — customize functions there rather than in the notebook.
- The segmentation settings live in `helpers/optimal_settings_v1.6.4.json`. To change one, name it in `custom_settings` (Cell 4), e.g. `{"nuclei_edge_fraction": 0.3}`, and re-run from Cell 4; an unknown name raises an error listing the valid ones.

### 2D images
2D images (a file without a Z stack, or a ROI with a single Z slice) are handled automatically; the image-loading cell (Cell 5) prints whether the image is 2D or 3D and sets `is_2d`.
- **Loading:** no Z voxel size is asked — the plane is given a 1 µm thickness, so every "volume" the pipeline computes is the area in µm². Resampling never adds planes along Z.
- **Reading plain TIFFs:** a TIFF without OME metadata is read from its own dimensions (singleton axes dropped): 2 = one 2D channel, 3 = a 2D image with channels, 4 = a 3D stack with channels (the smaller of the two extra axes is taken as the channel axis). Channel axes stated by the file (ImageJ hyperstack, RGB samples) are used as they are. OME-TIFFs are read through aicsimageio.
- **Processing:** median, Gaussian and Sauvola filters run in 2D on the plane.
- **Segmentation:** nuclei are segmented in the image plane — a watershed seeded at every bright centre separated from its neighbours by an intensity dip (so touching objects that form one round blob are still split), or Cellpose / StarDist in 2D mode — followed by the same size refinement on areas. The cytoplasm is built in the plane (membrane rings closed with a disk, Cellpose in 2D mode).
- **Outputs:** every size is an area (`[um2]` columns, "area" in the summaries, plots and Excel report); the spatial plots show X and Y only; the VTK, STL, single-cell VTK and FEA exports are skipped.

## Detailed Workflow

### 1. Import Libraries and Helpers (Cells 1-2)
Cell 1 loads all required imports via `load_nuclei_notebook_setup()`. Cell 2 calls `reload_helpers()` to reload `helpers/notebook_helpers.py` without restarting the kernel.

### 2. Inputs and Setup (Cells 3-6)
- **Cell 3 — Settings.** Together with Cell 4, the only cells to edit for a new dataset:
  - `input_file`: an image file (`.nd2`, `.tif`/`.tiff`/`.ome.tif`, `.czi`, `.lif` or `.oib`; for multi-scene `.czi`/`.lif` only the first scene is read) — or a **folder** for batch mode.
  - `ROI`, `interactive_roi`, `name_setup`, `use_setup`, `automatic_contrast` (marker channels: `False` = set in napari, `'calibrated'` = from each channel's histogram; the NUCLEI contrast is always set from its histogram, Cell 8).
  - `nuclei_diameter` (approximate: the typical nucleus is measured in the image, Cell 8), `cell_diameter` (in the image plane for a 2D image).
  - Segmentation method: `trig_cellpose`, `trig_stardist` (both `False` = watershed, the validated method) and `trig_cellpose_cyto`.
  - `multilabel`, `aggregate_distance_factor` (cells closer than this × `cell_diameter` form one aggregate), `pcm_thickness_factor` (PCM shell thickness = this × `cell_diameter`). Both are converted to µm, so they don't change with `scale_factor`.
- **Cell 4 — Exports and segmentation settings**, used in single-file and batch mode:
  - `export_vtk`, `export_stl`, `export_fea` (3D exports, Cells 30, 31, 34).
  - `custom_settings`: `{}` keeps all validated settings. `load_optimal_settings()` reads them from `helpers/optimal_settings_v1.6.4.json` into `opt`, which the later cells use. They include `scale_factor` / `zoom_factors` (resampling), `sigma` (Gaussian smoothing), `num_plateaus` / `plateau_factor` (histogram equalization), `threshold_method` and the threshold weights, the nuclei size refinement (`size_reference`, `iterative_split`, `oversize_factor`, `max_split_iterations`, `merge_undersized`, `undersize_factor`), splitting (`split_gamma`, `split_gamma_step`, `min_piece_fraction`, the watershed `nuclei_split_config_overrides`), and the NUCLEI steps added in v1.6.4 (`z_elongation`, `z_bg_radius_um`, `nuclei_flare_trim_factor`, `nuclei_saddle_dip`, `nuclei_edge_fraction`, `nuclei_rescue_contrast`, `z_atten_correction`, …).
- **Cell 5 — Load image and stain table.**
  - Loads the image with `initialize_dataset()`, automatically choosing lazy (chunked) or eager reading from the file's size, and sets `is_2d` for a single-plane image. With `interactive_roi = True`, `select_roi_interactively()` first opens a napari window with a draggable ROI rectangle (X/Y only); with a saved stain table, its channels are named and colored after the table.
  - Prints the channel list (`print_channel_list()`). In batch mode nothing is loaded: the metadata of every image is read and any image whose channels differ from the first one is flagged.
  - Shows the **interactive stain table** (`edit_stain_dict()`, requires `ipywidgets`, installed with `jupyter`). One row per condition: NUCLEI and CYTOPLASM are fixed, other stains can be added or removed. Choose each condition's channel (`no` = not used) and color (blue, red, green, white, yellow, magenta), type the marker name, tick **Intracellular?** for markers that define the cytoplasm (`cyto_markers`), and **Membrane?** for membrane stains (`membrane_markers`, also included in `cyto_markers`): their rings are filled to get the cytoplasm, and the bright membrane is used as the border between touching cells. The two ticks exclude each other. The table is checked live (e.g. a channel used twice, a missing marker name). **Confirm** saves it to `<name_setup>_stain_dict.json`; with `use_setup = True` it is reloaded, already confirmed, on the next run.
- **Cell 6 — Read the stain table and run the batch.** Reads the confirmed table into `stain_dict` / `cyto_markers`. If it isn't confirmed yet, execution stops with a message (click **Confirm**, then run again from Cell 6). In batch mode, `run_batch_folder()` then processes every image in the folder with the whole pipeline and the settings of Cells 3-4 (`batch_settings(opt)`; every image gets its own NUCLEI contrast and nucleus size; no viewers or plots; 3D exports skipped for 2D images) and stops.

### 3. Preparation and Preview (Cells 7-8)
- `prepare_and_preview()` builds the image stack and the `stain_df` table (channels not used in the stain table are dropped) and opens a napari viewer for channel inspection.
- `prepare_stain_settings()` loads or creates per-channel contrast/gamma settings — reused from `<name_setup>_setup.csv` if it exists, otherwise set interactively in napari (starting from the calibrated suggestion, and checked against it), or picked automatically from the histogram if `automatic_contrast = 'calibrated'`.
- `set_nuclei_contrast()` then sets the NUCLEI contrast/gamma from the channel's own histogram (the rule the settings were validated with), and Cell 8 shows the complete stain settings table for review (after the napari window is closed).
- `adapt_to_image()` measures the typical nucleus in the NUCLEI channel and adapts `nuclei_diameter`, `scale_factor` and the µm sizes to it (3D images; the changes are printed and written to the histogram Excel file).

### 4. Image Processing and Segmentation (Cells 9-22)
- **Preprocessing:** optional depth correction (`correct_depth()`, off in the validated settings), normalization (`run_normalize()`), isotropic resampling (`run_resample()`), median denoising (`run_denoise()`) followed by slice-by-slice removal of the NUCLEI out-of-focus haze (`remove_haze()`), contrast/gamma (`run_contrast_gamma()`), Gaussian smoothing (`run_smooth()`, `sigma`) and histogram equalization (`run_equalize()`, `num_plateaus` / `plateau_factor`); the values come from the validated settings (Cell 4).
- **Thresholding (Cell 15):**
  - Marker channels: `run_threshold()` combines a selectable global method (`threshold_method`: Otsu / median / Huang), local Sauvola thresholding and a statistical-background component (blend weights `global_threshold_weight` / `sauvola_weight` from the validated settings). The histogram marks the global and final thresholds per channel. These masks decide marker positivity.
  - Cytoplasm: `segment_cytoplasm()` uses the **union of the stains** thresholded by `run_threshold()` — the CYTOPLASM channel and/or the intracellular markers, plus the membrane markers with their rings closed and filled (enclosed areas up to ~1.5 cell cross-sections, `build_cytoplasm_mask()`) — and assigns exactly these voxels to the nuclei, without any growth (a cell with no stained cytoplasm keeps just its nucleus). Cells are only grown from the nuclei when there is no CYTOPLASM channel and no ticked marker at all.
- **Histogram export:** `export_channel_histograms()` saves every stage's histograms and a Parameters sheet (including the splitting settings) to Excel.
- **Nuclei:** `segment_nuclei()` with watershed (default), StarDist (`trig_stardist`) or Cellpose (`trig_cellpose`). Splitting is automatic — there is no split profile to choose:
  - the watershed first pass uses a fixed built-in configuration: it also splits touching nuclei where the nuclear signal dips between them, and always splits a nucleus whose z-slices show separate islands (e.g. two lobes above and below its centre);
  - with `split_gamma` > 1 the nuclear intensity used by the watershed (and by the seam test of the fragment merge) is gamma-adjusted first (`apply_split_gamma()`), so the dips between touching nuclei are deeper; Cellpose/StarDist get the original image;
  - the pieces of each split smaller than `min_piece_fraction` × a nucleus are merged into the closest big piece of the same split (`absorb_small_split_pieces()`);
  - then, for every method, a size-based refinement sets a reference nucleus size (`size_reference`), merges fragments smaller than `undersize_factor` × reference into a touching neighbour (only if the result is still one plausible nucleus with no dark seam at the contact), and re-splits labels bigger than `oversize_factor` × reference with increasingly aggressive settings ('aggressive' → 'very aggressive' → 'extreme') and, with `split_gamma_step`, a higher gamma at each level. Labels that can't be fixed are kept, never deleted.
  - after the size refinement (v1.6.4, 3D NUCLEI channel): Z flares are trimmed, labels holding several nuclei are split at an intensity saddle, nuclei stacked in Z are split by size, nuclei the threshold missed are added back, and every nucleus edge is redrawn at `nuclei_edge_fraction` of its own peak. The recap table gives each nucleus's final label.
  - All these settings come from `segmentation_settings(opt)` (Cell 4).
  - On a 2D image the same steps run in the image plane (see [2D images](#2d-images)).
- **Cytoplasm / PCM:** `segment_cytoplasm()` builds the cytoplasm from the CYTOPLASM channel (optionally shaped with Cellpose, `trig_cellpose_cyto = True`), otherwise from the intracellular markers, otherwise by growing the nuclei; touching cells are split where the marker signal fades and where a membrane marker is bright — on intensities gamma-adjusted with `split_gamma`, so the borders between cells are more distinct. `segment_pcm()` adds the pericellular matrix shell, `pcm_thickness_factor` × `cell_diameter` µm thick.
- **Label assignment and aggregates:** `assign_channel_labels()` links cells to marker channels; `detect_aggregates()` groups cells closer than `aggregate_distance_factor` × `cell_diameter` µm into aggregates.
- **Visualization:** `view_processing_results()` opens napari viewers with every stage and the segmentation, including "Thresh islands" layers to check the threshold masks.

### 5. Quantification and Analysis (Cells 23-29)
Marker intensity is reported both for **positive cells** (cells that passed that marker's threshold) and for **all cells**. Sizes are volumes, or areas for a 2D image.
- `compute_percell_marker_intensity_df()` and `build_labels_df()`: per-cell marker intensity, overlap, size and position.
- `print_population_summary()`: counts and percentages per condition.
- `build_full_labels_df()`: the full table at original (non-resampled) resolution for export.
- `build_histogram_report()`: per-nucleus KDE plots and a PDF report.
- `plot_spatial_distributions()` (X/Y/Z, X/Y for a 2D image), `plot_size_distributions()` and `plot_marker_intensity_clouds()` (flow-cytometry-style intensity vs cytoplasm size plot, saved as PNG).

### 6. Export (Cells 30-34)
Each 3D export can be switched off in Cell 4 (`export_vtk`, `export_stl`, `export_fea`).
- **3D meshes (3D images only):** VTK volumes (`build_vtk_volumes()`) and per-marker STL meshes (`export_marker_stl()`) for ParaView or similar. Set `export_nuc_3D_vtk = True` in Cell 32 itself to also export a single cell as a VTK sub-volume.
- **Excel:** full quantification tables, stain settings and processing parameters (`export_quantification_to_excel()`, saved as `<file>_segmentation.xlsx`), with areas instead of volumes for a 2D image.
- **FEA (3D images only):** Abaqus `.inp` mesh via tetrahedralization (`export_fea_mesh()`, using `tetgen`), saved as `<file>_FEA.inp`: node coordinates in µm (X, Y, Z), one element set per nucleus (`cell1`, `cell2`, …).

## Requirements
See `requirements.txt` for the full list. Key dependencies:
- `napari[all]`, `numpy`, `scipy`, `scikit-image`, `matplotlib`, `pandas`
- `jupyter` (includes `ipywidgets`, used by the interactive stain table), with `ipykernel<7`: with ipykernel 7 napari windows don't open (Windows) or freeze (macOS). On an existing environment, run `uv pip install "ipykernel<7"` and restart the kernel.
- `aicsimageio[nd2]`, `nd2reader`, `aicspylibczi` + `fsspec`, `readlif`, `oiffile` — image readers (ND2, TIFF/OME-TIFF, CZI, LIF, OIB); plain TIFFs are read with `tifffile`, installed with aicsimageio
- `tensorflow`, `csbdeep`, `stardist`, `cellpose` — segmentation models
- `pyvista`, `SimpleITK`
- `meshio`, `tetgen`, `meshlib`
- `xlsxwriter`, `reportlab`, `Pillow`

## Contributing
Contributions are welcome. Please open issues or pull requests for bug fixes, improvements, or new features.

## License
This project is licensed under the MIT License.

## Acknowledgments
- Napari team and contributors
- scikit-image, numpy, scipy, and matplotlib communities

---
For questions or support, please open an [issue on GitHub](https://github.com/edoborgiani/NucleoSeg3D/issues).
