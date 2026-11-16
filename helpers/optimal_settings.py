"""Optimal (validated) settings of the nuclei segmentation, for the user notebook.

`NucleoSeg3D_v1.6.4.ipynb` asks the user only what depends on the
experiment (file, ROI, stain table, cell size, method, exports). Every
setting of the nuclei segmentation itself was chosen by
``validation/tune_segmentation.py`` against manual ground truths and is read
here from ``optimal_settings_v1.6.4.json`` (next to this file):

- the NUCLEI contrast of every image is set from its own histogram
  (calibrated rule, `calibrated_contrast`);
- the nucleus size, `scale_factor` and the um sizes are measured / adapted
  in each image (`adapt_settings_to_image`);
- everything else (smoothing, threshold, watershed split configuration,
  size refinement, Z elongation, haze removal, flare trim, saddle / tall
  split, rescue of missed nuclei, edges) is the validated value.

Any of them can still be changed by name with ``custom_settings`` (Cell 4).
The full validation notebook (`NucleoSeg3D_v1.6.4_validation.ipynb`)
exposes them all.
"""

import json
from pathlib import Path

SETTINGS_FILE = Path(__file__).with_name("optimal_settings_v1.6.4.json")

# segment_nuclei keywords taken from the settings (besides the user's own)
_SEGMENT_KEYS = (
    "size_reference", "iterative_split", "oversize_factor", "max_split_iterations",
    "merge_undersized", "undersize_factor", "split_gamma", "split_gamma_step",
    "min_piece_fraction", "z_elongation", "nuclei_expand_um", "nuclei_flare_trim_factor",
    "nuclei_saddle_dip", "nuclei_edge_fraction", "nuclei_edge_margin_um",
    "nuclei_tall_volume_factor", "nuclei_tall_elongation_factor", "nuclei_rescue_contrast",
    "nuclei_rescue_grow_fraction")
# run_batch_folder(nuclei_options=...) keys
_BATCH_OPTION_KEYS = (
    "z_atten_strength", "z_atten_conditions", "z_bg_radius_um", "z_bg_percentile",
    "global_threshold_weight", "sauvola_weight", "z_elongation", "nuclei_expand_um",
    "nuclei_flare_trim_factor", "nuclei_saddle_dip", "nuclei_edge_fraction",
    "nuclei_edge_margin_um", "nuclei_tall_volume_factor", "nuclei_tall_elongation_factor",
    "nuclei_rescue_contrast", "nuclei_rescue_grow_fraction", "nuclei_contrast")


def load_optimal_settings(custom_settings=None, path=None, verbose=True):
    """The validated settings as a dict (``opt``), with ``custom_settings``
    (``{name: value}``) applied on top. ``nuclei_split_config_overrides`` in
    ``custom_settings`` is merged into the validated one. Adds
    ``nuclei_split_config`` (for `segment_nuclei`)."""
    from helpers.notebook_helpers import get_nuclei_split_config
    path = Path(path) if path else SETTINGS_FILE
    record = json.loads(path.read_text(encoding="utf-8"))
    opt = dict(record["settings"])
    custom = dict(custom_settings or {})
    unknown = set(custom) - set(opt)
    if unknown:
        raise ValueError(f"Unknown setting(s) in custom_settings: {sorted(unknown)}. "
                         f"Known: {sorted(opt)}")
    if "nuclei_split_config_overrides" in custom:
        custom["nuclei_split_config_overrides"] = {
            **opt["nuclei_split_config_overrides"], **custom["nuclei_split_config_overrides"]}
    opt.update(custom)
    if opt["nuclei_contrast"] not in ("calibrated", None):
        raise ValueError("nuclei_contrast must be 'calibrated' or None (None = as the other "
                         "channels: setup file, napari or automatic_contrast)")
    opt["nuclei_split_config"] = get_nuclei_split_config(
        profile="balanced", **opt["nuclei_split_config_overrides"])
    if verbose:
        v = record.get("validation", {})
        print(f"Optimal settings v{record.get('version')} ({path.name}), validated on "
              f"{len(record.get('ground_truths', []))} manual ground truths "
              f"(mean F1 {v.get('all', {}).get('mean_f1')}, F1@0.5 "
              f"{v.get('all', {}).get('f1_50')}).")
        if custom:
            print("Changed by custom_settings: " + ", ".join(
                f"{k} = {custom[k]!r}" for k in sorted(custom)))
    return opt


def set_nuclei_contrast(im_original, stain_complete_df, original_stain_complete_df, opt):
    """Cell 8: the NUCLEI contrast / gamma from the image's own histogram
    (``opt['nuclei_contrast'] == 'calibrated'``), in both stain tables."""
    if opt["nuclei_contrast"] != "calibrated" or "NUCLEI" not in stain_complete_df.index:
        return None
    from helpers.notebook_helpers import calibrated_contrast
    contrast = calibrated_contrast(im_original[..., stain_complete_df.index.get_loc("NUCLEI")])
    for col, value in contrast.items():
        stain_complete_df.loc["NUCLEI", col] = value
        original_stain_complete_df.loc["NUCLEI", col] = value
    print(f"NUCLEI contrast from the image's own histogram: Cont_min {contrast['Cont_min']}, "
          f"Cont_max {contrast['Cont_max']}, Gamma {contrast['Gamma']:g} (the segmentation "
          "settings were validated with this rule).")
    return contrast


def adapt_to_image(im_original, stain_complete_df, voxel_size_zyx, nuclei_diameter,
                   cell_diameter, opt, is_2d=False):
    """Cell 8: measure the typical nucleus in the NUCLEI channel and adapt
    ``nuclei_diameter``, ``opt['scale_factor']`` and the um sizes to it
    (``opt['auto_adapt_settings']``). Updates ``opt`` in place. Returns
    ``(nuclei_diameter, zooms, cyto_factor, changes)``."""
    changes = []
    if not opt["auto_adapt_settings"]:
        print("Settings not adapted to the image (auto_adapt_settings = False).")
    elif is_2d:
        print("2D image: settings not adapted (the measure needs a 3D stack).")
    elif "NUCLEI" not in stain_complete_df.index:
        print("No NUCLEI channel: settings not adapted.")
    else:
        from helpers.notebook_helpers import adapt_settings_to_image
        adapted, changes = adapt_settings_to_image(
            im_original, stain_complete_df, tuple(voxel_size_zyx),
            {"nuclei_diameter": nuclei_diameter, "scale_factor": opt["scale_factor"],
             "z_bg_radius_um": opt["z_bg_radius_um"],
             "nuclei_edge_margin_um": opt["nuclei_edge_margin_um"]})
        nuclei_diameter = adapted["nuclei_diameter"]
        for k in ("scale_factor", "z_bg_radius_um", "nuclei_edge_margin_um"):
            opt[k] = adapted[k]
    zooms = [z * opt["scale_factor"] for z in opt["zoom_factors"]]
    if is_2d:
        zooms[0] = 1.0  # as initialize_dataset: never resample a single plane along Z
    cyto_factor = int(round(cell_diameter / nuclei_diameter))
    return nuclei_diameter, zooms, cyto_factor, changes


def correct_depth(im_final_stack, stain_complete_df, opt, voxel_z=None):
    """Cell 9: compensate the signal lost with depth when
    ``opt['z_atten_correction']`` (off in the validated settings)."""
    if not opt["z_atten_correction"] or im_final_stack['Original image'].shape[0] <= 2:
        return im_final_stack
    from helpers.notebook_helpers import correct_z_attenuation, plot_z_attenuation
    conds = list(stain_complete_df.index) if opt["z_atten_conditions"] == "all" else \
        [c for c in opt["z_atten_conditions"] if c in stain_complete_df.index]
    channels = [stain_complete_df.index.get_loc(c) for c in conds]
    im_final_stack['Original image'], profiles = correct_z_attenuation(
        im_final_stack['Original image'], model=opt["z_atten_model"],
        strength=opt["z_atten_strength"], channels=channels, inplace=True)
    plot_z_attenuation(profiles, names=conds, voxel_z=voxel_z)
    return im_final_stack


def remove_haze(im_final_stack, stain_complete_df, opt, voxel_size_zyx):
    """Cell 11: remove the out-of-focus haze of the NUCLEI channel slice by
    slice (``opt['z_bg_radius_um']``)."""
    if opt["z_bg_radius_um"] <= 0 or im_final_stack['Denoised image'].shape[0] <= 1 \
            or "NUCLEI" not in stain_complete_df.index:
        return im_final_stack
    from helpers.notebook_helpers import correct_z_background
    im_final_stack['Denoised image'] = correct_z_background(
        im_final_stack['Denoised image'], opt["z_bg_radius_um"], tuple(voxel_size_zyx),
        percentile=opt["z_bg_percentile"], channels=[stain_complete_df.index.get_loc("NUCLEI")])
    print(f"NUCLEI haze removed slice by slice (radius {opt['z_bg_radius_um']:.3g} um).")
    return im_final_stack


def processing_settings(opt):
    """Cells 13-15: ``sigma``, ``num_plateaus``, ``plateau_factor``,
    ``threshold_method`` and the threshold weights."""
    return {k: opt[k] for k in ("sigma", "num_plateaus", "plateau_factor", "threshold_method",
                                "global_threshold_weight", "sauvola_weight")}


def segmentation_settings(opt):
    """Cell 17: keyword arguments of `segment_nuclei`."""
    return {"nuclei_split_config": opt["nuclei_split_config"],
            **{k: opt[k] for k in _SEGMENT_KEYS}}


def batch_settings(opt):
    """Cell 6: keyword arguments of `run_batch_folder` (every image gets its
    own NUCLEI contrast and size adaptation)."""
    options = {k: opt[k] for k in _BATCH_OPTION_KEYS}
    options["z_atten_model"] = opt["z_atten_model"] if opt["z_atten_correction"] else "off"
    options["auto_adapt"] = opt["auto_adapt_settings"]
    return {"scale_factor": opt["scale_factor"], "zoom_factors": opt["zoom_factors"],
            "nuclei_split_config": opt["nuclei_split_config"],
            **{k: opt[k] for k in ("size_reference", "iterative_split", "oversize_factor",
                                   "max_split_iterations", "merge_undersized",
                                   "undersize_factor", "split_gamma", "split_gamma_step",
                                   "min_piece_fraction", "sigma", "num_plateaus",
                                   "plateau_factor", "threshold_method")},
            "nuclei_options": options}


def settings_for_report(opt, adapt_changes=()):
    """Cell 16: the settings written to the histogram Excel file."""
    skip = {"nuclei_split_config", "nuclei_split_config_overrides"}
    report = {f"Optimal setting {k}": (str(v) if isinstance(v, (list, dict)) else v)
              for k, v in opt.items() if k not in skip}
    report["Watershed split config"] = str(opt["nuclei_split_config_overrides"])
    report["Settings adapted to the image"] = (
        "; ".join(f"{n} {o} -> {v}" for n, o, v, _ in adapt_changes) or
        ("no change" if opt["auto_adapt_settings"] else "off"))
    return report
