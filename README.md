# NucleoSeg3D

**NucleoSeg3D** is a Jupyter-notebook pipeline for the segmentation and quantification of nuclei, cells and fluorescent markers in 3D (and 2D) microscopy images, built on the Napari ecosystem. It targets researchers in bioimage analysis who need a robust, reproducible workflow for volumetric fluorescence data.

Current version: **v1.6.41** (`NucleoSeg3D_v1.6.41.ipynb`). The previous version, **v1.6.4** (`NucleoSeg3D_v1.6.4.ipynb`), is kept with its own validated settings. The LIVE/DEAD notebook is **v1.2.2** (`NucleoSeg3D_LD_v1.2.2.ipynb`).

### What's new in v1.6.41
- **Re-validated settings**: re-tuned on six manually annotated images, each scored as a new image (nuclei mean F1 0.56, F1@0.5 0.77, against 0.43 / 0.69 for the previous tuning round, which had no histogram rule). They are read from `settings/optimal_settings_v1.6.41.json`. See [Validation](#validation).
- **Settings that follow the image quality**: some settings are read off each channel's histogram (background, noise, signal-to-noise ratio) in Cell 8 (`helpers/histogram_adapt.py`). For now this is the nuclei edge fraction: lower in a noisy NUCLEI channel, higher in a clean one. A setting named in `custom_settings` is never changed by these rules.
- **NUCLEI contrast**: the calibrated NUCLEI contrast now uses gamma 1.15 (`nuclei_gamma`) instead of 1.0.
- **Last Z slice kept**: the resampling (Cell 10) repeats the edge voxel instead of padding with zeros (`resample_edge_mode = 'nearest'`), so nuclei at the bottom of a shrunk stack are no longer lost.
- **Cell bodies with their own settings** (Cell 18): the cytoplasm / membrane stains get their own threshold, and every cell is completed by the dim rim of its body (`cyto_grow_um`). These settings (`cyto_*`) were tuned against Cellpose cell bodies of the annotated nuclei.
- Batch mode applies all of the above to every image.

### In all notebooks (v1.6.4, v1.6.41 and LIVE/DEAD v1.2.2)
- **Calibrated contrast by default**: `calibrated_contrast = True` (Cell 3) sets the contrast of the marker channels from each channel's histogram with the calibrated rule, without a napari window. Set it to `False` to set contrast and gamma yourself in napari (Cell 8). It replaces the former `automatic_contrast` setting.
- **Settings files in `settings/`**: the validated settings (`optimal_settings_v<version>.json`) moved from `helpers/` to their own folder.
- **Optional processing steps**: Cells 9–14 (normalization, resampling, denoising, contrast, smoothing, equalization) can each be skipped. A skipped cell passes its input on unchanged and the next cell works on the last image computed. Skipping all of them thresholds the original image of Cell 8 (only rescaled to 0–255). Cell 15 lists the skipped steps, and they are written to the parameters sheet of the histogram Excel file. Without resampling (Cell 10) the image keeps its original voxel size. To change which steps run, re-run from Cell 8. Skipping any step departs from the validated settings.
- **Processing viewer**: the napari viewer of the processing steps shows the original image and only the steps that were run. The last of them, the image that was thresholded, starts visible.
- **Faster with many cells**: the per-cell steps of the segmentation (seeding, re-split of merged clusters, roundness filter, Z split and merge) and of the quantification now work in each cell's bounding box instead of the whole image. The results are the same. Before, these steps grew with cells × voxels, which made images with many cells (typical in LIVE/DEAD) slow, especially at a fine resolution. `helpers/check_speedups.py` compares the old and new code on a synthetic image (see [Usage](#usage)).

### What came in v1.6.4
- **Validated segmentation settings**: every nuclei-segmentation setting (smoothing, threshold, watershed split, size refinement, haze removal, edges, …) was tuned against four manually annotated images (mean F1 0.51, F1@0.5 0.74) and is read from `settings/optimal_settings_v1.6.4.json`. They are no longer edited in the notebook; any one can still be changed by name with `custom_settings` (Cell 4).
- **NUCLEI contrast from the image**: the NUCLEI channel contrast/gamma is always set from its own histogram, with the rule the settings were validated with.
- **Nucleus size from the image**: `nuclei_diameter` is only a starting value; the typical nucleus is measured in each image and the nucleus size, resolution (`scale_factor`) and µm sizes are adapted to it (3D images).
- **New NUCLEI steps**: out-of-focus haze removal slice by slice, optional depth (Z attenuation) correction, trim of Z flares, split of nuclei stacked in Z, nuclei the threshold missed added back, and every nucleus edge redrawn relative to its own brightness.
- **Calibrated contrast rule** for the marker channels: contrast limits picked from each channel's histogram with the rule calibrated on the ground truths.

### LIVE/DEAD notebook: v1.2.2 (`NucleoSeg3D_LD_v1.2.2.ipynb`)
Segments LIVE/DEAD-stained images and calls every cell LIVE or DEAD, with the same workflow as NucleoSeg3D v1.6.4.
- **Separate LIVE and DEAD images**: set `input_file_live` and `input_file_dead` (Cell 3) instead of one stacked `input_file`. The two images must have the same size and voxel size. They are read as one image through a small pair file (`<name>.ldpair`, written next to the LIVE file). The stain table lists their channels as `'LIVE - ...'` and `'DEAD - ...'`. With two folders (batch mode), the images are paired in name order and the pairs are printed. The outputs go to `<LIVE folder>_LD_pairs_output/`.
- **Validated settings of v1.6.4**: read from the same `settings/optimal_settings_v1.6.4.json` and changed by name with `custom_settings` (Cell 4). The nuclei are segmented from the **nuclear** markers. So the contrast of each nuclear marker comes from its own histogram, the typical nucleus is measured in them, and they get the validated nuclei steps. The cell bodies (**cytoplasmic** markers) get the validated smoothing, threshold, watershed split and size refinement. The steps after the watershed (Z split, rescue, edges) were validated on nuclei only, so the cell bodies skip them.
- **Stain table**: it starts with the LIVE and DEAD rows only. Extra stains take the next unused channel, with a guessed localization:
  - **Add LIVE stain** (`LIVE_2`, …) adds another LIVE marker, e.g. a Hoechst counterstain;
  - **Add DEAD stain** (`DEAD_2`, …) adds another DEAD marker;
  - **Add other stain** adds a stain that is segmented and quantified but not part of the call.
- **The call**: a cell positive for any DEAD marker is DEAD; one positive only for LIVE markers is LIVE (`ld_rule = "dead_priority"`). With Hoechst as `LIVE_2`: Hoechst only → LIVE, Hoechst + DEAD → DEAD. A cell positive for no LIVE and no DEAD marker is **UNCLASSIFIED**. It is reported in the summary, plots, napari (grey) and Excel, but left out of the viability, which is LIVE / (LIVE + DEAD). The batch summary has an `UNCLASSIFIED` column.
- **Bright signal only**: LIVE/DEAD stains are binary. After the threshold, the masks of the call markers (LIVE, DEAD and any `LIVE_2` / `DEAD_2`) keep only objects whose peak stands out clearly. The peak must be at least `ld_min_brightness` (0.3) × the typical bright cell above background, and `ld_min_snr` (5) × the noise. Voxels below `ld_edge_brightness` (0.15) × the typical bright cell become background. This drops out-of-focus cells (in 2D, often light from another depth) and halos. A channel with no clearly bright object (e.g. no dead cells) ends up with no positive cells. These defaults are a starting point, not validated values. Set any factor to 0 to turn that test off.
- **Rescue of missed nuclei off**: positivity is read from the threshold masks, so a rescued nucleus would be positive for no marker (`LD_OVERRIDES` in `helpers/optimal_settings_ld.py`; `custom_settings` can switch it back on).
- **Resolution of your choice**: by default the image is resampled so that a nucleus spans 12–19 voxels, the range the settings were tuned at. A `scale_factor` set in `custom_settings` (Cell 4), e.g. `{"scale_factor": 0.75}`, is used as given instead, also in batch mode. Cell 8 then prints how many voxels a nucleus spans at that scale. The run time grows with the number of voxels, about as `scale_factor`³ in 3D.
- The LIVE/DEAD call (`min_positive_fraction`, `ld_rule`) and the bright-signal filter stay experiment choices in Cell 3.

> **Disclaimer:** This repository is freely available for use. The associated pipeline is currently being prepared for publication — please contact [Edoardo Borgiani](https://github.com/edoborgiani) for more information on how to use the pipeline or for collaboration enquiries.

## Features
- **2D and 3D images**: a file without a Z stack (or a ROI with a single Z slice) is detected automatically and processed as a 2D image — segmented in the image plane, with every size reported as an area (µm²) instead of a volume; the 3D-only exports are skipped. Plain TIFFs (no OME metadata) are read by their dimensions: 3 = a 2D image with channels, 4 = a 3D stack with channels.
- **Interactive stain table**: after loading, pick each condition's channel and display color from drop-down menus, type the marker names and tick which markers form the cytoplasm (intracellular / membrane) — no hand-written `stain_dict`. The confirmed table is saved and reused on the next run, and also names and colors the channels of the interactive ROI preview.
- **Batch mode**: set `input_file` to a folder to process every image in it with the same settings; outputs go to `<folder>_output/<image name>/`. Images whose channel list differs from the first one are flagged before the batch starts. 2D and 3D images can be mixed.
- **Automatic splitting of touching nuclei and cells**: a built-in first pass (including splitting a nucleus that forks into separate islands above and below its centre), then a size-based refinement that re-splits oversized labels with increasingly aggressive settings and merges small fragments into their neighbour. In addition:
  - **split gamma**: a gamma > 1 on the intensity used to split makes the dim seams between touching objects darker faster than the signal, so the split zones are more distinct; it grows at every re-split level;
  - **merge of split slivers**: slivers of a few pixels/voxels left by a split are merged into the closest big piece of the same split.
- **Image processing**: normalization, resampling to isotropic voxel size, denoising, contrast, smoothing and equalization (each optional), thresholding, and watershed / StarDist / Cellpose segmentation (3D, or 2D on a 2D image).
- **Interactive ROI selection**: set `interactive_roi = True` to drag a rectangle in a napari window instead of typing pixel coordinates.
- **Validated settings**: the segmentation runs with settings validated against manual ground truths (`settings/optimal_settings_v1.6.41.json`; v1.6.4: `settings/optimal_settings_v1.6.4.json`). The NUCLEI contrast, the nucleus size and (v1.6.41) the settings that depend on the image quality are taken from each image.
- **Calibrated contrast** (Cell 3, default `calibrated_contrast = True`): the contrast limits of the marker channels are picked per channel from its histogram with the calibrated rule, without the napari contrast/gamma viewer. Set `calibrated_contrast = False` to set contrast and gamma yourself in napari in Cell 8 (the viewer starts from the calibrated suggestion). A saved `<name_setup>_setup.csv` is reused either way when `use_setup = True`.
- **Napari integration**: interactive visualization at each processing step.
- **Quantification & export**: per-cell marker statistics (for positive cells and for all cells), spatial and size distributions, Excel reports, per-cell KDE plots and a PDF report, and 3D mesh export (VTK/STL/INP, 3D images only).
- **Helper library** (`helpers/`): all processing, quantification, visualization and export logic lives in Python modules, so the notebook stays short and readable.

## Repository Structure
```
.
├── NucleoSeg3D_v1.6.41.ipynb        # The NucleoSeg3D notebook (current)
├── NucleoSeg3D_v1.6.4.ipynb         # Previous version (v1.6.4 settings)
├── NucleoSeg3D_v1.6.3.ipynb         # Older version
├── NucleoSeg3D_LD_v1.2.2.ipynb      # The LIVE/DEAD notebook (current, v1.6.4 settings)
├── requirements.txt                 # Python dependencies
├── overrides.txt                    # uv --override file (see Prerequisites)
├── README.md                        # This file
├── settings/
│   ├── optimal_settings_v1.6.41.json # Validated settings of v1.6.41 and their scores
│   └── optimal_settings_v1.6.4.json  # Validated settings of v1.6.4 (also LIVE/DEAD) and their scores
└── helpers/
    ├── __init__.py
    ├── notebook_helpers.py          # Core processing, segmentation, and export functions
    ├── notebook_setup_helpers.py    # Package installation and import loader
    ├── optimal_settings.py          # Loads the validated settings of one version and applies them per image
    ├── optimal_settings_ld.py       # The v1.6.4 settings for the LIVE/DEAD notebook (nuclear markers)
    ├── histogram_adapt.py           # Settings read off each channel's histogram (v1.6.41)
    └── check_speedups.py            # Checks that the faster per-cell steps give the same results
```

Each notebook loads its own settings file (`load_optimal_settings(..., version="1.6.41")` in v1.6.41; v1.6.4 and the LIVE/DEAD notebook use the default, `"1.6.4"`), so an older notebook keeps its results.

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

10. **Open the notebook** `NucleoSeg3D_v1.6.41.ipynb` (or `NucleoSeg3D_LD_v1.2.2.ipynb` for LIVE/DEAD images).

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

10. **Open the notebook** `NucleoSeg3D_v1.6.41.ipynb` (or `NucleoSeg3D_LD_v1.2.2.ipynb` for LIVE/DEAD images).

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

10. **Open the notebook** `NucleoSeg3D_v1.6.41.ipynb` (or `NucleoSeg3D_LD_v1.2.2.ipynb` for LIVE/DEAD images).

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
- The segmentation settings live in `settings/optimal_settings_v1.6.41.json` (v1.6.4 and LIVE/DEAD: `settings/optimal_settings_v1.6.4.json`). To change one, name it in `custom_settings` (Cell 4), e.g. `{"nuclei_edge_fraction": 0.3}`, and re-run from Cell 4; an unknown name raises an error listing the valid ones. In v1.6.41 a setting named there is not changed by the histogram rules. A `scale_factor` named there is used as given in the LIVE/DEAD notebook; in v1.6.4 and v1.6.41 it is only the starting value, adapted to the nucleus size measured in each image.
- **Optional processing steps:** to skip one of Cells 9–14, just don't run it and go on with the next one; to start over with other steps, re-run from Cell 8 (see [Detailed Workflow](#4-image-processing-and-segmentation-cells-9-22)).
- **Checking the faster per-cell steps:** from the repository root, run `%run helpers/check_speedups.py` in a notebook cell (or `python helpers/check_speedups.py`). It runs the previous helpers (from git `HEAD`, or another commit given as argument) and the current ones on a synthetic image of touching nuclei, and prints SAME or DIFFERENT with both run times for every step. Run it before committing helper changes, since it compares against the last commit.

### 2D images
2D images (a file without a Z stack, or a ROI with a single Z slice) are handled automatically; the image-loading cell (Cell 5) prints whether the image is 2D or 3D and sets `is_2d`.
- **Loading:** no Z voxel size is asked — the plane is given a 1 µm thickness, so every "volume" the pipeline computes is the area in µm². Resampling never adds planes along Z.
- **Reading plain TIFFs:** a TIFF without OME metadata is read from its own dimensions (singleton axes dropped): 2 = one 2D channel, 3 = a 2D image with channels, 4 = a 3D stack with channels (the smaller of the two extra axes is taken as the channel axis). Channel axes stated by the file (ImageJ hyperstack, RGB samples) are used as they are. OME-TIFFs are read through aicsimageio.
- **Resolution and nucleus size:** the nucleus can't be measured in a single plane, so `nuclei_diameter` (Cell 3) is used as given: set it to the real nucleus size. The resolution (`scale_factor`) is still adapted, with the 3D rule applied to that diameter: a nucleus spans the same 12–19 pixels as on the tuned images, and the image is never upsampled. Haze removal and depth correction are skipped.
- **Processing:** median, Gaussian and Sauvola filters run in 2D on the plane.
- **Segmentation:** nuclei are segmented in the image plane — a watershed seeded at every bright centre separated from its neighbours by an intensity dip (so touching objects that form one round blob are still split), or Cellpose / StarDist in 2D mode — followed by the same size refinement on areas. The cytoplasm is built in the plane (membrane rings closed with a disk, Cellpose in 2D mode).
- **Outputs:** every size is an area (`[um2]` columns, "area" in the summaries, plots and Excel report); the spatial plots show X and Y only; the VTK, STL, single-cell VTK and FEA exports are skipped.

## Detailed Workflow

The cells of `NucleoSeg3D_v1.6.41.ipynb`; v1.6.4 has the same cells, without the steps marked v1.6.41. The LIVE/DEAD notebook follows the same order up to Cell 18, then makes the LIVE/DEAD call (see the notebook's introduction and the [LIVE/DEAD section](#livedead-notebook-v122-nucleoseg3d_ld_v122ipynb) above).

### 1. Import Libraries and Helpers (Cells 1-2)
Cell 1 loads all required imports via `load_nuclei_notebook_setup()`. Cell 2 calls `reload_helpers()` to reload `helpers/notebook_helpers.py` without restarting the kernel.

### 2. Inputs and Setup (Cells 3-6)
- **Cell 3 — Settings.** Together with Cell 4, the only cells to edit for a new dataset:
  - `input_file`: an image file (`.nd2`, `.tif`/`.tiff`/`.ome.tif`, `.czi`, `.lif` or `.oib`; for multi-scene `.czi`/`.lif` only the first scene is read) — or a **folder** for batch mode.
  - `ROI`, `interactive_roi`, `name_setup`, `use_setup`, `calibrated_contrast` (marker channels: `True`, the default = from each channel's histogram with the calibrated rule, `False` = set yourself in napari; the NUCLEI contrast is always set from its histogram, Cell 8).
  - `nuclei_diameter` (approximate: the typical nucleus is measured in the image, Cell 8), `cell_diameter` (in the image plane for a 2D image).
  - Segmentation method: `trig_cellpose`, `trig_stardist` (both `False` = watershed, the validated method) and `trig_cellpose_cyto`.
  - `multilabel`, `aggregate_distance_factor` (cells closer than this × `cell_diameter` form one aggregate), `pcm_thickness_factor` (PCM shell thickness = this × `cell_diameter`). Both are converted to µm, so they don't change with `scale_factor`.
- **Cell 4 — Exports and segmentation settings**, used in single-file and batch mode:
  - `export_vtk`, `export_stl`, `export_fea` (3D exports, Cells 30, 31, 34).
  - `custom_settings`: `{}` keeps all validated settings. `load_optimal_settings(custom_settings, version="1.6.41")` reads them from `settings/optimal_settings_v1.6.41.json` (v1.6.4: `settings/optimal_settings_v1.6.4.json`) into `opt`, which the later cells use. They include `scale_factor` / `zoom_factors` (resampling), `sigma` (Gaussian smoothing), `num_plateaus` / `plateau_factor` (histogram equalization), `threshold_method` and the threshold weights, the nuclei size refinement (`size_reference`, `iterative_split`, `oversize_factor`, `max_split_iterations`, `merge_undersized`, `undersize_factor`), splitting (`split_gamma`, `split_gamma_step`, `min_piece_fraction`, the watershed `nuclei_split_config_overrides`), and the NUCLEI steps added in v1.6.4 (`z_elongation`, `z_bg_radius_um`, `nuclei_flare_trim_factor`, `nuclei_saddle_dip`, `nuclei_edge_fraction`, `nuclei_rescue_contrast`, `z_atten_correction`, …). v1.6.41 adds `nuclei_gamma`, `resample_edge_mode`, the cell-body settings (`cyto_threshold`, `cyto_membrane_close_fraction`, `cyto_membrane_fill_area_factor`, `cyto_mask_close_um`, `cyto_fill_holes`, `cyto_split_by_intensity_gradient`, `cyto_grow_um`) and the histogram rules (`adapt_to_histograms`, `histogram_rules`).
- **Cell 5 — Load image and stain table.**
  - Loads the image with `initialize_dataset()`, automatically choosing lazy (chunked) or eager reading from the file's size, and sets `is_2d` for a single-plane image. With `interactive_roi = True`, `select_roi_interactively()` first opens a napari window with a draggable ROI rectangle (X/Y only); with a saved stain table, its channels are named and colored after the table.
  - Prints the channel list (`print_channel_list()`). In batch mode nothing is loaded: the metadata of every image is read and any image whose channels differ from the first one is flagged.
  - Shows the **interactive stain table** (`edit_stain_dict()`, requires `ipywidgets`, installed with `jupyter`). One row per condition: NUCLEI and CYTOPLASM are fixed, other stains can be added or removed. Choose each condition's channel (`no` = not used) and color (blue, red, green, white, yellow, magenta), type the marker name, tick **Intracellular?** for markers that define the cytoplasm (`cyto_markers`), and **Membrane?** for membrane stains (`membrane_markers`, also included in `cyto_markers`): their rings are filled to get the cytoplasm, and the bright membrane is used as the border between touching cells. The two ticks exclude each other. The table is checked live (e.g. a channel used twice, a missing marker name). **Confirm** saves it to `<name_setup>_stain_dict.json`; with `use_setup = True` it is reloaded, already confirmed, on the next run.
- **Cell 6 — Read the stain table and run the batch.** Reads the confirmed table into `stain_dict` / `cyto_markers`. If it isn't confirmed yet, execution stops with a message (click **Confirm**, then run again from Cell 6). In batch mode, `run_batch_folder()` then processes every image in the folder with the whole pipeline and the settings of Cells 3-4 (`batch_settings(opt)`; every image gets its own NUCLEI contrast and nucleus size; no viewers or plots; 3D exports skipped for 2D images) and stops.

### 3. Preparation and Preview (Cells 7-8)
- `prepare_and_preview()` builds the image stack and the `stain_df` table (channels not used in the stain table are dropped) and opens a napari viewer for channel inspection.
- `prepare_stain_settings()` loads or creates per-channel contrast/gamma settings — reused from `<name_setup>_setup.csv` if it exists, otherwise picked from each channel's histogram with the calibrated rule (`calibrated_contrast = True`, default), or set interactively in napari (`calibrated_contrast = False`; starting from the calibrated suggestion, and checked against it).
- `adapt_to_histograms()` (v1.6.41) reads each channel's histogram (background, noise, signal-to-noise ratio, bright tail; `helpers/histogram_adapt.py`) and sets the settings that follow the image quality from it (`histogram_rules`: for now the nuclei edge fraction, from the NUCLEI signal-to-noise ratio). The features and the changes are printed and written to the histogram Excel file. Settings named in `custom_settings` are kept.
- `set_nuclei_contrast()` then sets the NUCLEI contrast/gamma from the channel's own histogram (the rule the settings were validated with; v1.6.41: gamma `nuclei_gamma` 1.15), and Cell 8 shows the complete stain settings table for review (after the napari window is closed).
- `adapt_to_image()` measures the typical nucleus in the NUCLEI channel and adapts `nuclei_diameter`, `scale_factor` and the µm sizes to it (3D images; the changes are printed and written to the histogram Excel file).
- Cell 8 ends with `reset_processing_steps()`: the processing of Cells 9–14 starts again from the original image.

### 4. Image Processing and Segmentation (Cells 9-22)
- **Preprocessing (Cells 9–14):** optional depth correction (`correct_depth()`, off in the validated settings), normalization (`run_normalize()`), isotropic resampling (`run_resample()`; v1.6.41 keeps the last Z slice, `resample_edge_mode`), median denoising (`run_denoise()`) followed by slice-by-slice removal of the NUCLEI out-of-focus haze (`remove_haze()`), contrast/gamma (`run_contrast_gamma()`), Gaussian smoothing (`run_smooth()`, `sigma`) and histogram equalization (`run_equalize()`, `num_plateaus` / `plateau_factor`); the values come from the validated settings (Cell 4).
- **Optional steps:** each of Cells 9–14 can be skipped. Every step reads the most recent image computed before it (the original image is rescaled to 0–255 first, the range of the contrast settings and the threshold), and later steps that are now outdated are dropped. In Cell 15, `complete_skipped_steps()` lists the skipped steps and gives each one's stage the image of the stage before it, so the later cells find every stage they read. Without resampling, the zoom factors become 1 and the voxel size stays the original one. Skipping Cell 9 also skips the depth correction, skipping Cell 11 also skips the haze removal. Batch mode always runs every step.
- **Thresholding (Cell 15):**
  - Marker channels: `run_threshold()` combines a selectable global method (`threshold_method`: Otsu / median / Huang), local Sauvola thresholding and a statistical-background component (blend weights `global_threshold_weight` / `sauvola_weight` from the validated settings). The histogram marks the global and final thresholds per channel. These masks decide marker positivity.
  - Cytoplasm: `segment_cytoplasm()` uses the **union of the stains** thresholded by `run_threshold()` — the CYTOPLASM channel and/or the intracellular markers, plus the membrane markers with their rings closed and filled (enclosed areas up to ~1.5 cell cross-sections, `build_cytoplasm_mask()`) — and assigns these voxels to the nuclei (v1.6.4: without any growth, so a cell with no stained cytoplasm keeps just its nucleus; v1.6.41: with their own threshold, and every cell is completed by the dim rim of its body, see Cytoplasm / PCM below). Cells are only grown from the nuclei when there is no CYTOPLASM channel and no ticked marker at all.
- **Histogram export:** `export_channel_histograms()` saves the histograms of every stage that was run and a Parameters sheet (including the splitting settings, the skipped steps and, v1.6.41, the histogram features and rules) to Excel.
- **Nuclei:** `segment_nuclei()` with watershed (default), StarDist (`trig_stardist`) or Cellpose (`trig_cellpose`). Splitting is automatic — there is no split profile to choose:
  - the watershed first pass uses a fixed built-in configuration: it also splits touching nuclei where the nuclear signal dips between them, and always splits a nucleus whose z-slices show separate islands (e.g. two lobes above and below its centre);
  - with `split_gamma` > 1 the nuclear intensity used by the watershed (and by the seam test of the fragment merge) is gamma-adjusted first (`apply_split_gamma()`), so the dips between touching nuclei are deeper; Cellpose/StarDist get the original image;
  - the pieces of each split smaller than `min_piece_fraction` × a nucleus are merged into the closest big piece of the same split (`absorb_small_split_pieces()`);
  - then, for every method, a size-based refinement sets a reference nucleus size (`size_reference`), merges fragments smaller than `undersize_factor` × reference into a touching neighbour (only if the result is still one plausible nucleus with no dark seam at the contact), and re-splits labels bigger than `oversize_factor` × reference with increasingly aggressive settings ('aggressive' → 'very aggressive' → 'extreme') and, with `split_gamma_step`, a higher gamma at each level. Labels that can't be fixed are kept, never deleted.
  - after the size refinement (v1.6.4, 3D NUCLEI channel): Z flares are trimmed, labels holding several nuclei are split at an intensity saddle, nuclei stacked in Z are split by size, nuclei the threshold missed are added back, and every nucleus edge is redrawn at `nuclei_edge_fraction` of its own peak. The recap table gives each nucleus's final label.
  - All these settings come from `segmentation_settings(opt)` (Cell 4).
  - On a 2D image the same steps run in the image plane (see [2D images](#2d-images)).
- **Cytoplasm / PCM:** `segment_cytoplasm()` builds the cytoplasm from the CYTOPLASM channel (optionally shaped with Cellpose, `trig_cellpose_cyto = True`), otherwise from the intracellular markers, otherwise by growing the nuclei; touching cells are split where the marker signal fades and where a membrane marker is bright — on intensities gamma-adjusted with `split_gamma`, so the borders between cells are more distinct. v1.6.41 (`cytoplasm_settings(opt)`): the cytoplasm / membrane stains get their own threshold (`cyto_threshold`), the membrane rings are closed and filled with tuned sizes, small gaps in the mask are closed (`cyto_mask_close_um`), and every cell is completed by the dim rim of its body below the stain threshold, up to `cyto_grow_um` µm without overlapping its neighbours. `segment_pcm()` adds the pericellular matrix shell, `pcm_thickness_factor` × `cell_diameter` µm thick.
- **Label assignment and aggregates:** `assign_channel_labels()` links cells to marker channels; `detect_aggregates()` groups cells closer than `aggregate_distance_factor` × `cell_diameter` µm into aggregates.
- **Visualization:** `view_processing_results()` opens napari viewers with the original image, every processing step that was run (the last one, the thresholded image, starts visible) and the segmentation, including "Thresh islands" layers to check the threshold masks.

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

## Validation

The segmentation settings were tuned against manually annotated 3D images (the ground truths). The scores and the tuning records are stored with the settings, in `settings/optimal_settings_v<version>.json`. The tuning scripts and ground-truth images are not part of this repository.

**Score.** Nuclei are matched to the annotation by overlap (IoU). F1@0.5 counts a nucleus as found when it overlaps its annotation by IoU ≥ 0.5; mean F1 averages the F1 over IoU 0.5–0.75, so it also rewards accurate outlines.

### v1.6.41 (`optimal_settings_v1.6.41.json`)

Six ground truths, each scored **as a new image**: calibrated NUCLEI contrast, nucleus size measured in the image and edge fraction from its own NUCLEI histogram.

| Image | Mean F1 | F1@0.5 | Mean F1, previous tuning round |
| --- | --- | --- | --- |
| GT1 | 0.300 | 0.655 | 0.304 |
| GT2 | 0.605 | 0.805 | 0.580 |
| GT3 | 0.565 | 0.771 | 0.391 |
| GT4 | 0.649 | 0.829 | 0.418 |
| GT5 | 0.608 | 0.706 | 0.440 |
| GT6 | 0.629 | 0.829 | 0.465 |
| **All** | **0.559** | **0.766** | **0.433** |

The last column is the previous internal tuning round (no histogram rule, one shared edge fraction) on the same six images, scored the same way.

- **Histogram rule** (nuclei edge fraction from the NUCLEI signal-to-noise ratio): checked leave-one-image-out, i.e. fitted on five images and scored on the sixth. Mean F1 0.552 with the rule, against 0.540 for the best single shared edge fraction. Other candidate rules (NUCLEI gamma, rescue contrast, cell-body threshold and growth) did not beat one shared value and were left out.
- **Cell bodies**: scored against Cellpose (cyto3) cell bodies of the annotated nuclei, as mean cell IoU: 0.556 over the six images with the v1.6.41 cell-body settings (0.477–0.652 per image). These are not manual annotations of the cell bodies, so they measure agreement with Cellpose rather than accuracy.

### v1.6.4 (`optimal_settings_v1.6.4.json`)

Four ground truths: mean F1 0.509, F1@0.5 0.736. These scores used each image's own contrast and edge fraction, so they are not directly comparable with the v1.6.41 scores, where every image is treated as new.

The LIVE/DEAD notebook uses the v1.6.4 settings. Its call (`min_positive_fraction`, `ld_rule`) and bright-signal filter have not been validated against annotations.

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
