#!/usr/bin/env python3
"""Wire QFT bin synthesis and spectrogram objects into the isolated V5 patch."""

import json
from pathlib import Path


PATH = Path(__file__).resolve().parent / "QMW_QAC_QFT_Spectral_Synthesizer_v5.maxpat"
document = json.loads(PATH.read_text(encoding="utf-8"))
patcher = document["patcher"]
boxes = {entry["box"]["id"]: entry["box"] for entry in patcher["boxes"]}

# Polarization is meaningful bipolar quantum data: -1..1 maps one octave
# below/above 33 Hz, while an unbiased state lands exactly at 33 Hz.
boxes["pitch_map"]["text"] = "expr 33. * pow(2.\\, $f1)"

route = boxes["oroute"]
route["text"] = (
    "o.route /qmw/wavetable/points /qmw/wavetable/status "
    "/qmw/wavetable/error /qmw/wavetable/correlations "
    "/qmw/wavetable/pauli15 /qmw/wavetable/surface_file "
    "/qmw/quantum/features /qmw/quantum/state /qmw/qft/bins "
    "/qmw/qft/amplitudes /qmw/qft/phases"
)
route["numoutlets"] = 12
route["outlettype"] = [""] * 11 + ["FullPacket"]

# The unmatched outlet moves from 8 to 11 after appending three addresses.
for entry in patcher["lines"]:
    line = entry["patchline"]
    if line["source"] == ["oroute", 8] and line["destination"][0] == "print":
        line["source"] = ["oroute", 11]

ids = set(boxes)
if "qft_spectrum_renderer" not in ids:
    additions = [
        {"id": "qft_spectrum_route", "maxclass": "newobj", "text": "o.route /qmw/qft/bins /qmw/qft/amplitudes /qmw/qft/phases", "patching_rect": [1280.0, 500.0, 360.0, 22.0], "numinlets": 1, "numoutlets": 4, "outlettype": ["", "", "", "FullPacket"]},
        {"id": "qft_spectrum_renderer", "maxclass": "newobj", "text": "js qmw_qft_spectrum_renderer_v5.js", "patching_rect": [1280.0, 540.0, 225.0, 22.0], "numinlets": 3, "numoutlets": 3, "outlettype": ["", "jit_matrix", "list"]},
        {"id": "qft_wave_buffer", "maxclass": "newobj", "text": "buffer~ qmw_v5_qft_wave @samps 256 @channels 1", "patching_rect": [1280.0, 580.0, 300.0, 22.0], "numinlets": 1, "numoutlets": 2, "outlettype": ["float", "bang"]},
        {"id": "qft_wave_reader", "maxclass": "newobj", "text": "wave~ qmw_v5_qft_wave", "patching_rect": [1280.0, 620.0, 160.0, 22.0], "numinlets": 3, "numoutlets": 1, "outlettype": ["signal"]},
        {"id": "qft_wave_gain", "maxclass": "newobj", "text": "*~ 0.12", "patching_rect": [1280.0, 655.0, 62.0, 22.0], "numinlets": 2, "numoutlets": 1, "outlettype": ["signal"]},
        {"id": "qft_spectrogram", "maxclass": "jit.pwindow", "patching_rect": [900.0, 620.0, 360.0, 180.0], "presentation": 1, "presentation_rect": [900.0, 620.0, 360.0, 180.0], "numinlets": 1, "numoutlets": 2, "outlettype": ["jit_matrix", ""]},
        {"id": "qft_spectrum_status", "maxclass": "message", "text": "waiting for QFT bins", "patching_rect": [900.0, 805.0, 360.0, 22.0], "presentation": 1, "presentation_rect": [900.0, 805.0, 360.0, 22.0], "numinlets": 2, "numoutlets": 1, "outlettype": [""]},
        {"id": "qft_spectrum_label", "maxclass": "comment", "text": "16-BIN QFT / IQFT SPECTROGRAM + OVERTONE WAVETABLE", "patching_rect": [900.0, 595.0, 360.0, 20.0], "presentation": 1, "presentation_rect": [900.0, 595.0, 360.0, 20.0]},
    ]
    patcher["boxes"].extend({"box": box} for box in additions)
    edges = (
        (["udp", 0], ["qft_spectrum_route", 0]),
        (["qft_spectrum_route", 0], ["qft_spectrum_renderer", 0]),
        (["qft_spectrum_route", 1], ["qft_spectrum_renderer", 1]),
        (["qft_spectrum_route", 2], ["qft_spectrum_renderer", 2]),
        (["qft_spectrum_renderer", 0], ["qft_spectrum_status", 0]),
        (["qft_spectrum_renderer", 1], ["qft_spectrogram", 0]),
        (["phasor", 0], ["qft_wave_reader", 0]),
        (["qft_wave_reader", 0], ["qft_wave_gain", 0]),
        (["qft_wave_gain", 0], ["dac", 0]),
        (["qft_wave_gain", 0], ["dac", 1]),
    )
    patcher["lines"].extend(
        {"patchline": {"source": source, "destination": destination}}
        for source, destination in edges
    )

# Upgrade patches created before the dedicated spectrum router was introduced.
if "qft_spectrum_route" not in ids:
    patcher["boxes"].append({"box": {
        "id": "qft_spectrum_route", "maxclass": "newobj",
        "text": "o.route /qmw/qft/bins /qmw/qft/amplitudes /qmw/qft/phases",
        "patching_rect": [1280.0, 500.0, 360.0, 22.0],
        "numinlets": 1, "numoutlets": 4,
        "outlettype": ["", "", "", "FullPacket"],
    }})
    for source, destination in (
        (["udp", 0], ["qft_spectrum_route", 0]),
        (["qft_spectrum_route", 0], ["qft_spectrum_renderer", 0]),
        (["qft_spectrum_route", 1], ["qft_spectrum_renderer", 1]),
        (["qft_spectrum_route", 2], ["qft_spectrum_renderer", 2]),
    ):
        patcher["lines"].append({
            "patchline": {"source": source, "destination": destination}
        })

# The correlations outlet is part of the proven V3/V4 OSC route. V5 also
# accepts a tagged combined QFT frame there, so it works even before Max has
# reconstructed the newer dedicated OSC route outlets.
compatibility_edge = {
    "patchline": {
        "source": ["oroute", 3],
        "destination": ["qft_spectrum_renderer", 0],
    }
}
if compatibility_edge not in patcher["lines"]:
    patcher["lines"].append(compatibility_edge)

# Keep descriptors observable but do not automatically drive the compact-state
# renderer: doing so rewrites the 2D source buffer during playback and masks
# the audible effect of the 2d.wave~ Y scan.
automatic_render_sources = {"controls_unpack", "qft_descriptor_unpack"}
automatic_render_destinations = {"render_spectral", "render_detail", "render_nonlinear"}
patcher["lines"] = [
    entry for entry in patcher["lines"]
    if not (
        entry["patchline"]["source"][0] in automatic_render_sources
        and entry["patchline"]["destination"][0] in automatic_render_destinations
    )
]

# Y scan depth is a performance control. Quantum entropy may be displayed and
# used elsewhere, but must not zero the 2d.wave~ Y signal for low-entropy states.
patcher["lines"] = [
    entry for entry in patcher["lines"]
    if not (
        entry["patchline"]["source"] == ["controls_unpack", 3]
        and entry["patchline"]["destination"] == ["entropy_sig", 0]
    )
]

# Expose the full arrays and reduce them to three normalized, QFT-native
# sonification controls: spectral centroid, entropy, and phase dispersion.
boxes = {entry["box"]["id"]: entry["box"] for entry in patcher["boxes"]}
if "qft_data_route" not in boxes:
    additions = [
        {"id": "qft_data_route", "maxclass": "newobj", "text": "route probabilities magnitudes phases descriptors", "patching_rect": [1280.0, 700.0, 320.0, 22.0], "numinlets": 1, "numoutlets": 5, "outlettype": ["list", "list", "list", "list", ""]},
        {"id": "qft_probability_list", "maxclass": "message", "text": "QFT probabilities", "patching_rect": [1280.0, 735.0, 360.0, 22.0], "numinlets": 2, "numoutlets": 1, "outlettype": [""]},
        {"id": "qft_magnitude_list", "maxclass": "message", "text": "QFT magnitudes", "patching_rect": [1280.0, 765.0, 360.0, 22.0], "numinlets": 2, "numoutlets": 1, "outlettype": [""]},
        {"id": "qft_phase_list", "maxclass": "message", "text": "QFT phases", "patching_rect": [1280.0, 795.0, 360.0, 22.0], "numinlets": 2, "numoutlets": 1, "outlettype": [""]},
        {"id": "qft_descriptor_unpack", "maxclass": "newobj", "text": "unpack f f f", "patching_rect": [1280.0, 830.0, 110.0, 22.0], "numinlets": 1, "numoutlets": 3, "outlettype": ["float", "float", "float"]},
    ]
    patcher["boxes"].extend({"box": box} for box in additions)
    for source, destination in (
        (["qft_spectrum_renderer", 2], ["qft_data_route", 0]),
        (["qft_data_route", 0], ["qft_probability_list", 1]),
        (["qft_data_route", 1], ["qft_magnitude_list", 1]),
        (["qft_data_route", 2], ["qft_phase_list", 1]),
        (["qft_data_route", 3], ["qft_descriptor_unpack", 0]),
    ):
        patcher["lines"].append({"patchline": {"source": source, "destination": destination}})

# Stable parallel IR return: unity dry plus a bounded 20% convolved return.
if "ir_wet_return_trim" not in ids:
    patcher["boxes"].append({"box": {
        "id": "ir_wet_return_trim", "maxclass": "newobj", "text": "*~ 0.2",
        "patching_rect": [520.0, 1140.0, 62.0, 22.0],
        "numinlets": 2, "numoutlets": 1, "outlettype": ["signal"],
    }})
    patcher["lines"] = [
        entry for entry in patcher["lines"]
        if not (
            entry["patchline"]["source"] == ["ir_wet_mul", 0]
            and entry["patchline"]["destination"] == ["ir_mix_sum", 1]
        )
    ]
    patcher["lines"].extend([
        {"patchline": {"source": ["ir_wet_mul", 0], "destination": ["ir_wet_return_trim", 0]}},
        {"patchline": {"source": ["ir_wet_return_trim", 0], "destination": ["ir_mix_sum", 1]}},
    ])

# Independent post-convolution gain and perceptual IR-size controls.
boxes = {entry["box"]["id"]: entry["box"] for entry in patcher["boxes"]}
boxes["ir_wet_return_trim"]["text"] = "*~ 0.5"
if "ir_return_gain" not in boxes:
    additions = [
        {"id": "ir_return_gain", "maxclass": "flonum", "minimum": 0.0, "maximum": 1.0, "text": "", "patching_rect": [300.0, 1080.0, 75.0, 22.0], "presentation": 1, "presentation_rect": [300.0, 1038.0, 75.0, 22.0], "numinlets": 1, "numoutlets": 2, "outlettype": ["", "bang"]},
        {"id": "ir_return_gain_label", "maxclass": "comment", "text": "IR return gain", "patching_rect": [380.0, 1082.0, 95.0, 20.0], "presentation": 1, "presentation_rect": [380.0, 1040.0, 95.0, 20.0]},
        {"id": "ir_return_gain_default", "maxclass": "newobj", "text": "loadmess 0.5", "patching_rect": [300.0, 1110.0, 82.0, 22.0], "numinlets": 1, "numoutlets": 1, "outlettype": [""]},
        {"id": "ir_size", "maxclass": "flonum", "minimum": 0.1, "maximum": 1.0, "text": "", "patching_rect": [490.0, 1080.0, 75.0, 22.0], "presentation": 1, "presentation_rect": [490.0, 1038.0, 75.0, 22.0], "numinlets": 1, "numoutlets": 2, "outlettype": ["", "bang"]},
        {"id": "ir_size_label", "maxclass": "comment", "text": "IR size / decay", "patching_rect": [570.0, 1082.0, 105.0, 20.0], "presentation": 1, "presentation_rect": [570.0, 1040.0, 105.0, 20.0]},
        {"id": "ir_size_default", "maxclass": "newobj", "text": "loadmess 1.", "patching_rect": [490.0, 1110.0, 78.0, 22.0], "numinlets": 1, "numoutlets": 1, "outlettype": [""]},
        {"id": "ir_size_prepend", "maxclass": "newobj", "text": "prepend irsize", "patching_rect": [575.0, 1110.0, 95.0, 22.0], "numinlets": 1, "numoutlets": 1, "outlettype": [""]},
    ]
    patcher["boxes"].extend({"box": box} for box in additions)
    for source, destination in (
        (["ir_return_gain_default", 0], ["ir_return_gain", 0]),
        (["ir_return_gain", 0], ["ir_wet_return_trim", 1]),
        (["ir_size_default", 0], ["ir_size", 0]),
        (["ir_size", 0], ["ir_size_prepend", 0]),
        (["ir_size_prepend", 0], ["v3_renderer", 0]),
    ):
        patcher["lines"].append({"patchline": {"source": source, "destination": destination}})

if "ir_scale" not in boxes:
    additions = [
        {"id": "ir_scale", "maxclass": "flonum", "minimum": 1.0, "maximum": 8.0, "text": "", "patching_rect": [680.0, 1080.0, 75.0, 22.0], "presentation": 1, "presentation_rect": [680.0, 1038.0, 75.0, 22.0], "numinlets": 1, "numoutlets": 2, "outlettype": ["", "bang"]},
        {"id": "ir_scale_label", "maxclass": "comment", "text": "IR buffer scale", "patching_rect": [760.0, 1082.0, 100.0, 20.0], "presentation": 1, "presentation_rect": [760.0, 1040.0, 100.0, 20.0]},
        {"id": "ir_scale_default", "maxclass": "newobj", "text": "loadmess 3.", "patching_rect": [680.0, 1110.0, 78.0, 22.0], "numinlets": 1, "numoutlets": 1, "outlettype": [""]},
        {"id": "ir_scale_prepend", "maxclass": "newobj", "text": "prepend irscale", "patching_rect": [765.0, 1110.0, 98.0, 22.0], "numinlets": 1, "numoutlets": 1, "outlettype": [""]},
    ]
    patcher["boxes"].extend({"box": box} for box in additions)
    for source, destination in (
        (["ir_scale_default", 0], ["ir_scale", 0]),
        (["ir_scale", 0], ["ir_scale_prepend", 0]),
        (["ir_scale_prepend", 0], ["v3_renderer", 0]),
    ):
        patcher["lines"].append({"patchline": {"source": source, "destination": destination}})

# Preserve the local/IBM crossfade and add an independently controlled
# IBM-minus-local residual voice.
boxes = {entry["box"]["id"]: entry["box"] for entry in patcher["boxes"]}
if "difference_buffer" not in boxes:
    additions = [
        {"id": "difference_buffer", "maxclass": "newobj", "text": "buffer~ qmw_v5_difference @samps 1024 @channels 1", "patching_rect": [880.0, 1110.0, 310.0, 22.0], "numinlets": 1, "numoutlets": 2, "outlettype": ["float", "bang"]},
        {"id": "difference_wave", "maxclass": "newobj", "text": "2d.wave~ qmw_v5_difference", "patching_rect": [880.0, 1140.0, 175.0, 22.0], "numinlets": 3, "numoutlets": 1, "outlettype": ["signal"]},
        {"id": "difference_gain", "maxclass": "flonum", "minimum": 0.0, "maximum": 2.0, "text": "", "patching_rect": [870.0, 1080.0, 75.0, 22.0], "presentation": 1, "presentation_rect": [870.0, 1038.0, 75.0, 22.0], "numinlets": 1, "numoutlets": 2, "outlettype": ["", "bang"]},
        {"id": "difference_gain_label", "maxclass": "comment", "text": "IBM-local residual", "patching_rect": [950.0, 1082.0, 125.0, 20.0], "presentation": 1, "presentation_rect": [950.0, 1040.0, 125.0, 20.0]},
        {"id": "difference_gain_sig", "maxclass": "newobj", "text": "sig~ 0.", "patching_rect": [1065.0, 1140.0, 52.0, 22.0], "numinlets": 1, "numoutlets": 1, "outlettype": ["signal"]},
        {"id": "difference_mul", "maxclass": "newobj", "text": "*~", "patching_rect": [1125.0, 1140.0, 42.0, 22.0], "numinlets": 2, "numoutlets": 1, "outlettype": ["signal"]},
        {"id": "comparison_sum", "maxclass": "newobj", "text": "+~", "patching_rect": [700.0, 1180.0, 42.0, 22.0], "numinlets": 2, "numoutlets": 1, "outlettype": ["signal"]},
    ]
    patcher["boxes"].extend({"box": box} for box in additions)
    # Downstream processing receives crossfaded source plus optional residual.
    for entry in patcher["lines"]:
        line=entry["patchline"]
        if line["source"] == ["source_sum", 0] and line["destination"][0] in {"ir_convolver", "ir_mix_sum"}:
            line["source"]=["comparison_sum", 0]
    for source, destination in (
        (["phasor", 0], ["difference_wave", 0]),
        (["rows", 0], ["difference_wave", 0]),
        (["y_depth_mul", 0], ["difference_wave", 1]),
        (["difference_gain", 0], ["difference_gain_sig", 0]),
        (["difference_wave", 0], ["difference_mul", 0]),
        (["difference_gain_sig", 0], ["difference_mul", 1]),
        (["source_sum", 0], ["comparison_sum", 0]),
        (["difference_mul", 0], ["comparison_sum", 1]),
    ):
        patcher["lines"].append({"patchline": {"source": source, "destination": destination}})

PATH.write_text(json.dumps(document, indent="\t") + "\n", encoding="utf-8")
print(f"updated {PATH.name}")
