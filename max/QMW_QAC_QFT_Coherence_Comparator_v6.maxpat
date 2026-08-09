{
	"patcher": {
		"fileversion": 1,
		"appversion": {
			"major": 9,
			"minor": 0,
			"revision": 5,
			"architecture": "x64",
			"modernui": 1
		},
		"classnamespace": "box",
		"rect": [
			203.0,
			100.0,
			1275.0,
			816.0
		],
		"openinpresentation": 1,
		"gridsize": [
			15.0,
			15.0
		],
		"boxes": [
			{
				"box": {
					"id": "obj-5",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						160.0,
						944.0,
						79.0,
						22.0
					],
					"text": "phasor~ 0.15"
				}
			},
			{
				"box": {
					"fontsize": 18.0,
					"id": "title",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						28.0,
						22.0,
						850.0,
						27.0
					],
					"presentation": 1,
					"presentation_rect": [
						10.0,
						22.0,
						850.0,
						27.0
					],
					"text": "QAC QFT SPECTRAL SYNTHESIZER V5 \u2192 COMPACT STATE \u2192 DUAL RENDERERS",
					"textcolor": [
						0.85,
						0.93,
						1.0,
						1.0
					]
				}
			},
			{
				"box": {
					"id": "instructions",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						28.0,
						56.0,
						880.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						10.0,
						56.0,
						880.0,
						20.0
					],
					"text": "Design locally and press SEND QASM. Python bridge mode determines local-only or one confirmed IBM hardware job.",
					"textcolor": [
						0.65,
						0.72,
						0.82,
						1.0
					]
				}
			},
			{
				"box": {
					"id": "qac",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						28.0,
						835.0,
						235.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						10.0,
						78.0,
						235.0,
						22.0
					],
					"text": "och.microqiskit qc 4 4 sim 256 1"
				}
			},
			{
				"box": {
					"id": "sender",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						285.0,
						835.0,
						180.0,
						22.0
					],
					"text": "qac_wavetable_sender_v1"
				}
			},
			{
				"box": {
					"id": "sendstatus",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						485.0,
						835.0,
						360.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						477.0,
						885.0,
						440.0,
						22.0
					],
					"text": "sender ready"
				}
			},
			{
				"box": {
					"id": "udp",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						28.0,
						540.0,
						132.0,
						22.0
					],
					"text": "udpreceive 7412"
				}
			},
			{
				"box": {
					"id": "oroute",
					"linecount": 2,
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 13,
					"outlettype": [
						"",
						"",
						"",
						"",
						"",
						"",
						"",
						"",
						"",
						"",
						"",
						"",
						"FullPacket"
					],
					"patching_rect": [
						175.0,
						540.0,
						703.0,
						35.0
					],
					"text": "o.route /qmw/wavetable/points /qmw/wavetable/status /qmw/wavetable/error /qmw/wavetable/correlations /qmw/wavetable/pauli15 /qmw/wavetable/surface_file /qmw/quantum/features /qmw/quantum/state /qmw/qft/bins /qmw/qft/amplitudes /qmw/qft/phases /qmw/workshop/density_lines"
				}
			},
			{
				"box": {
					"id": "rawprint",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						625.0,
						580.0,
						135.0,
						22.0
					],
					"text": "print WTABLE_RAW"
				}
			},
			{
				"box": {
					"id": "loader",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": [
						"",
						"",
						""
					],
					"patching_rect": [
						28.0,
						590.0,
						195.0,
						22.0
					],
					"saved_object_attributes": {
						"filename": "qmw_wavetable_receiver_v4.js",
						"parameter_enable": 0
					},
					"text": "js qmw_wavetable_receiver_v4.js"
				}
			},
			{
				"box": {
					"id": "buffer",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"float",
						"bang"
					],
					"patching_rect": [
						28.0,
						635.0,
						290.0,
						22.0
					],
					"text": "buffer~ qmw_wavetable @samps 1024 @channels 1"
				}
			},
			{
				"box": {
					"bgcolor": [
						0.08,
						0.1,
						0.14,
						1.0
					],
					"id": "display",
					"maxclass": "multislider",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
					"parameter_enable": 0,
					"patching_rect": [
						28.0,
						740.0,
						880.0,
						100.0
					],
					"presentation": 1,
					"presentation_rect": [
						10.0,
						740.0,
						880.0,
						100.0
					],
					"size": 256,
					"slidercolor": [
						0.34,
						0.78,
						1.0,
						1.0
					]
				}
			},
			{
				"box": {
					"format": 6,
					"id": "freq",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						28.0,
						855.0,
						75.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						15.0,
						854.0,
						75.0,
						22.0
					]
				}
			},
			{
				"box": {
					"id": "freqlabel",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						110.0,
						855.0,
						95.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						92.0,
						855.0,
						95.0,
						20.0
					],
					"text": "frequency Hz",
					"textcolor": [
						0.7,
						0.76,
						0.84,
						1.0
					]
				}
			},
			{
				"box": {
					"id": "phasor",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						28.0,
						895.0,
						78.0,
						22.0
					],
					"text": "phasor~ 110."
				}
			},
			{
				"box": {
					"id": "gain",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						458.0,
						960.0,
						52.0,
						22.0
					],
					"text": "*~ 1."
				}
			},
			{
				"box": {
					"id": "dac",
					"maxclass": "ezdac~",
					"numinlets": 2,
					"numoutlets": 0,
					"patching_rect": [
						240.0,
						944.0,
						45.0,
						45.0
					],
					"presentation": 1,
					"presentation_rect": [
						327.0,
						885.0,
						45.0,
						45.0
					]
				}
			},
			{
				"box": {
					"id": "statuslabel",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						430.0,
						855.0,
						62.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						407.0,
						840.0,
						62.0,
						20.0
					],
					"text": "STATUS",
					"textcolor": [
						0.34,
						0.78,
						1.0,
						1.0
					]
				}
			},
			{
				"box": {
					"id": "status",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						500.0,
						852.0,
						408.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						482.0,
						852.0,
						408.0,
						22.0
					],
					"text": "waiting for wavetable"
				}
			},
			{
				"box": {
					"id": "print",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						780.0,
						540.0,
						150.0,
						22.0
					],
					"text": "print WTABLE_OTHER"
				}
			},
			{
				"box": {
					"id": "corr_unpack",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 4,
					"outlettype": [
						"int",
						"float",
						"float",
						"float"
					],
					"patching_rect": [
						505.0,
						580.0,
						90.0,
						22.0
					],
					"text": "unpack i f f f"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "xx",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						610.0,
						580.0,
						65.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						592.0,
						635.0,
						65.0,
						22.0
					]
				}
			},
			{
				"box": {
					"format": 6,
					"id": "yy",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						690.0,
						580.0,
						65.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						672.0,
						635.0,
						65.0,
						22.0
					]
				}
			},
			{
				"box": {
					"format": 6,
					"id": "zz",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						770.0,
						580.0,
						65.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						770.0,
						635.0,
						65.0,
						22.0
					]
				}
			},
			{
				"box": {
					"id": "corr_label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						610.0,
						608.0,
						230.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						592.0,
						662.0,
						230.0,
						20.0
					],
					"text": "XX                 YY                 ZZ",
					"textcolor": [
						0.51,
						0.81,
						1.0,
						1.0
					]
				}
			},
			{
				"box": {
					"filename": "qmw_qac_wavetable_designer_v1.js",
					"id": "designer",
					"jsarguments": [
						"qmw_qac_wavetable_designer_v1.js"
					],
					"maxclass": "jsui",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
					"parameter_enable": 0,
					"patching_rect": [
						28.0,
						100.0,
						780.0,
						390.0
					],
					"presentation": 1,
					"presentation_rect": [
						10.0,
						100.0,
						780.0,
						390.0
					]
				}
			},
			{
				"box": {
					"id": "designer_status_label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						820.0,
						110.0,
						120.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						926.0,
						536.0,
						120.0,
						20.0
					],
					"text": "DESIGNER STATUS",
					"textcolor": [
						0.34,
						0.78,
						1.0,
						1.0
					]
				}
			},
			{
				"box": {
					"id": "designer_status",
					"linecount": 2,
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						820.0,
						138.0,
						140.0,
						35.0
					],
					"presentation": 1,
					"presentation_linecount": 2,
					"presentation_rect": [
						926.0,
						564.0,
						140.0,
						35.0
					],
					"text": "\"sent 2 gates \u2192 QASM bridge\""
				}
			},
			{
				"box": {
					"id": "safety",
					"linecount": 8,
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						820.0,
						230.0,
						143.0,
						114.0
					],
					"presentation": 1,
					"presentation_linecount": 6,
					"presentation_rect": [
						735.0,
						1.0,
						231.0,
						87.0
					],
					"text": "LOCAL MODE:\nSEND freely.\n\nBOTH MODE:\nEvery SEND QASM creates an IBM job. Submit deliberately, then stop the bridge.",
					"textcolor": [
						1.0,
						0.68,
						0.3,
						1.0
					]
				}
			},
			{
				"box": {
					"id": "pauli_label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						28.0,
						505.0,
						880.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						10.0,
						505.0,
						880.0,
						20.0
					],
					"text": "PAULI-15 EXPECTATIONS   XI YI ZI | IX IY IZ | XX XY XZ YX YY YZ ZX ZY ZZ",
					"textcolor": [
						0.51,
						0.81,
						1.0,
						1.0
					]
				}
			},
			{
				"box": {
					"bgcolor": [
						0.08,
						0.1,
						0.14,
						1.0
					],
					"id": "pauli_display",
					"maxclass": "multislider",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
					"parameter_enable": 0,
					"patching_rect": [
						28.0,
						530.0,
						880.0,
						90.0
					],
					"presentation": 1,
					"presentation_rect": [
						10.0,
						532.0,
						880.0,
						90.0
					],
					"setstyle": 1,
					"size": 15,
					"slidercolor": [
						0.95,
						0.55,
						0.25,
						1.0
					],
					"spacing": 10
				}
			},
			{
				"box": {
					"id": "pauli_slice",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
					"patching_rect": [
						600.0,
						895.0,
						62.0,
						22.0
					],
					"text": "zl.slice 1"
				}
			},
			{
				"box": {
					"id": "surface_loader",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
					"patching_rect": [
						600.0,
						865.0,
						220.0,
						22.0
					],
					"saved_object_attributes": {
						"filename": "qmw_pauli_surface_receiver_v1.js",
						"parameter_enable": 0
					},
					"text": "js qmw_pauli_surface_receiver_v1.js"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "morph",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						76.0,
						944.0,
						75.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						202.0,
						855.0,
						75.0,
						22.0
					]
				}
			},
			{
				"box": {
					"id": "morph_label",
					"linecount": 3,
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						441.0,
						895.0,
						190.0,
						47.0
					],
					"presentation": 1,
					"presentation_rect": [
						477.0,
						828.0,
						390.0,
						20.0
					],
					"text": "spectral view: 0=direct  .33=shifted  .67=stretched  1=reversed",
					"textcolor": [
						0.51,
						0.81,
						1.0,
						1.0
					]
				}
			},
			{
				"box": {
					"id": "morph_line",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 2,
					"outlettype": [
						"signal",
						"bang"
					],
					"patching_rect": [
						300.0,
						885.0,
						42.0,
						22.0
					],
					"text": "line~"
				}
			},
			{
				"box": {
					"id": "two_d",
					"maxclass": "newobj",
					"numinlets": 4,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						185.0,
						895.0,
						185.0,
						22.0
					],
					"text": "2d.wave~ qmw_wavetable"
				}
			},
			{
				"box": {
					"id": "rows",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						550.0,
						948.5,
						44.0,
						22.0
					],
					"text": "rows 4"
				}
			},
			{
				"box": {
					"id": "rows_load",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"bang"
					],
					"patching_rect": [
						550.0,
						885.0,
						60.0,
						22.0
					],
					"text": "loadbang"
				}
			},
			{
				"box": {
					"id": "surface_replace",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						830.0,
						865.0,
						105.0,
						22.0
					],
					"text": "prepend replace"
				}
			},
			{
				"box": {
					"id": "surface_slice",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
					"patching_rect": [
						830.0,
						835.0,
						62.0,
						22.0
					],
					"text": "zl.slice 1"
				}
			},
			{
				"box": {
					"id": "controls_slice",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
					"patching_rect": [
						690.0,
						930.0,
						62.0,
						22.0
					],
					"text": "zl.slice 1"
				}
			},
			{
				"box": {
					"id": "controls_unpack",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 4,
					"outlettype": [
						"float",
						"float",
						"float",
						"float"
					],
					"patching_rect": [
						760.0,
						930.0,
						105.0,
						22.0
					],
					"text": "unpack f f f f"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "entanglement_display",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						125.0,
						945.0,
						72.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						107.0,
						945.0,
						72.0,
						22.0
					]
				}
			},
			{
				"box": {
					"id": "theta_label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						680.0,
						800.0,
						287.0,
						20.0
					],
					"presentation": 1,
					"presentation_linecount": 3,
					"presentation_rect": [
						815.5,
						396.5,
						126.0,
						47.0
					],
					"text": "PARAMETERIZED: choose RX / RY / RZ, then theta"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "theta_control",
					"maxclass": "flonum",
					"maximum": 1.0,
					"minimum": 0.0,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						680.0,
						825.0,
						70.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						820.0,
						451.0,
						70.0,
						22.0
					]
				}
			},
			{
				"box": {
					"id": "theta_send",
					"maxclass": "button",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						760.0,
						825.0,
						24.0,
						24.0
					],
					"presentation": 1,
					"presentation_rect": [
						900.0,
						451.0,
						24.0,
						24.0
					]
				}
			},
			{
				"box": {
					"id": "theta_send_label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						790.0,
						827.0,
						158.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						966.0,
						481.0,
						158.0,
						20.0
					],
					"text": "SEND 2-QUBIT TEMPLATE"
				}
			},
			{
				"box": {
					"id": "theta_qasm",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
					"patching_rect": [
						680.0,
						970.0,
						205.0,
						22.0
					],
					"saved_object_attributes": {
						"filename": "qmw_parameterized_bell_v1.js",
						"parameter_enable": 0
					},
					"text": "js qmw_parameterized_bell_v1.js"
				}
			},
			{
				"box": {
					"id": "axis_rx",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						680.0,
						855.0,
						35.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						820.0,
						480.0,
						35.0,
						22.0
					],
					"text": "rx"
				}
			},
			{
				"box": {
					"id": "axis_ry",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						720.0,
						855.0,
						35.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						860.0,
						480.0,
						35.0,
						22.0
					],
					"text": "ry"
				}
			},
			{
				"box": {
					"id": "axis_rz",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						760.0,
						855.0,
						35.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						900.0,
						480.0,
						35.0,
						22.0
					],
					"text": "rz"
				}
			},
			{
				"box": {
					"id": "axis_note",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						805.0,
						855.0,
						184.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						820.0,
						507.0,
						184.0,
						20.0
					],
					"text": "Main SEND applies local rotation"
				}
			},
			{
				"box": {
					"id": "feature_label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						28.0,
						920.0,
						450.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						10.0,
						920.0,
						450.0,
						20.0
					],
					"text": "RAW QUANTUM FEATURES (dimensionless)"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "polarization_display",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						23.0,
						944.0,
						72.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						10.0,
						942.0,
						72.0,
						22.0
					]
				}
			},
			{
				"box": {
					"id": "polarization_label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						28.0,
						970.0,
						90.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						10.0,
						970.0,
						90.0,
						20.0
					],
					"text": "polarization"
				}
			},
			{
				"box": {
					"id": "entanglement_label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						125.0,
						970.0,
						90.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						107.0,
						970.0,
						90.0,
						20.0
					],
					"text": "entanglement"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "correlation_display",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						225.0,
						945.0,
						72.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						207.0,
						945.0,
						72.0,
						22.0
					]
				}
			},
			{
				"box": {
					"id": "correlation_label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						225.0,
						970.0,
						100.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						207.0,
						970.0,
						100.0,
						20.0
					],
					"text": "correlation RMS"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "entropy_display",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						335.0,
						945.0,
						72.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						317.0,
						945.0,
						72.0,
						22.0
					]
				}
			},
			{
				"box": {
					"id": "entropy_label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						335.0,
						970.0,
						100.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						317.0,
						970.0,
						100.0,
						20.0
					],
					"text": "Z entropy"
				}
			},
			{
				"box": {
					"id": "mapping_label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						470.0,
						920.0,
						480.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						452.0,
						920.0,
						480.0,
						20.0
					],
					"text": "EXPLICIT SONIFICATION CHOICES: pitch min/max Hz | scan min/max Hz"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "pitch_min",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						470.0,
						945.0,
						72.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						452.0,
						945.0,
						72.0,
						22.0
					]
				}
			},
			{
				"box": {
					"format": 6,
					"id": "pitch_max",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						550.0,
						945.0,
						72.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						532.0,
						945.0,
						72.0,
						22.0
					]
				}
			},
			{
				"box": {
					"format": 6,
					"id": "scan_min",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						670.0,
						945.0,
						72.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						652.0,
						945.0,
						72.0,
						22.0
					]
				}
			},
			{
				"box": {
					"format": 6,
					"id": "scan_max",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						750.0,
						945.0,
						72.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						732.0,
						945.0,
						72.0,
						22.0
					]
				}
			},
			{
				"box": {
					"id": "pitch_map",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						470.0,
						995.0,
						280.0,
						22.0
					],
					"text": "expr 33. * pow(2.\\, $f1)"
				}
			},
			{
				"box": {
					"id": "scan_map",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						760.0,
						995.0,
						220.0,
						22.0
					],
					"text": "expr 0.05 + 0.95 * $f1"
				}
			},
			{
				"box": {
					"id": "entropy_sig",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						335.0,
						1025.0,
						44.0,
						22.0
					],
					"text": "sig~ 1."
				}
			},
			{
				"box": {
					"id": "y_depth_mul",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						380.0,
						1025.0,
						42.0,
						22.0
					],
					"text": "*~"
				}
			},
			{
				"box": {
					"id": "gain_map",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						470.0,
						1055.0,
						220.0,
						22.0
					],
					"text": "expr $f1 * ($f3 - $f2) + $f2"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "gain_min",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						850.0,
						945.0,
						60.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						832.0,
						945.0,
						60.0,
						22.0
					]
				}
			},
			{
				"box": {
					"format": 6,
					"id": "gain_max",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						915.0,
						945.0,
						60.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						897.0,
						945.0,
						60.0,
						22.0
					]
				}
			},
			{
				"box": {
					"id": "gain_label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						850.0,
						970.0,
						139.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						832.0,
						970.0,
						139.0,
						20.0
					],
					"text": "correlation gain min/max"
				}
			},
			{
				"box": {
					"id": "gain_min_default",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						700.0,
						1055.0,
						90.0,
						22.0
					],
					"text": "loadmess 0.03"
				}
			},
			{
				"box": {
					"id": "gain_max_default",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						800.0,
						1055.0,
						85.0,
						22.0
					],
					"text": "loadmess 0.2"
				}
			},
			{
				"box": {
					"id": "rotation_layer",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
					"patching_rect": [
						680.0,
						1090.0,
						225.0,
						22.0
					],
					"saved_object_attributes": {
						"filename": "qmw_qasm_rotation_layer_v2.js",
						"parameter_enable": 0
					},
					"text": "js qmw_qasm_rotation_layer_v2.js"
				}
			},
			{
				"box": {
					"id": "rotation_target",
					"maxclass": "number",
					"maximum": 3,
					"minimum": 0,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						820.0,
						535.0,
						50.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						820.0,
						535.0,
						50.0,
						22.0
					]
				}
			},
			{
				"box": {
					"id": "rotation_target_label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						875.0,
						535.0,
						75.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						791.0,
						81.0,
						75.0,
						20.0
					],
					"text": "target qubit"
				}
			},
			{
				"box": {
					"id": "rotation_enable",
					"maxclass": "toggle",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"int"
					],
					"parameter_enable": 0,
					"patching_rect": [
						820.0,
						565.0,
						24.0,
						24.0
					],
					"presentation": 1,
					"presentation_rect": [
						820.0,
						565.0,
						24.0,
						24.0
					]
				}
			},
			{
				"box": {
					"id": "rotation_enable_label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						850.0,
						567.0,
						150.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						791.0,
						110.0,
						150.0,
						20.0
					],
					"text": "apply to designer circuit"
				}
			},
			{
				"box": {
					"id": "rotation_target_prepend",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						910.0,
						1090.0,
						95.0,
						22.0
					],
					"text": "prepend target"
				}
			},
			{
				"box": {
					"id": "rotation_enable_prepend",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						910.0,
						1120.0,
						95.0,
						22.0
					],
					"text": "prepend enable"
				}
			},
			{
				"box": {
					"id": "rotation_theta_prepend",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						910.0,
						1150.0,
						95.0,
						22.0
					],
					"text": "prepend theta"
				}
			},
			{
				"box": {
					"id": "rotation_enable_default",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						820.0,
						1120.0,
						80.0,
						22.0
					],
					"text": "loadmess 1"
				}
			},
			{
				"box": {
					"id": "v3_renderer",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 7,
					"outlettype": [
						"",
						"",
						"",
						"",
						"",
						"",
						""
					],
					"patching_rect": [
						20.0,
						1090.0,
						255.0,
						22.0
					],
					"saved_object_attributes": {
						"filename": "qmw_compact_state_renderer_v6.js",
						"parameter_enable": 0
					},
					"text": "js qmw_compact_state_renderer_v6.js"
				}
			},
			{
				"box": {
					"id": "v3_local_buffer",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"float",
						"bang"
					],
					"patching_rect": [
						20.0,
						1120.0,
						280.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						12.0,
						644.0,
						280.0,
						22.0
					],
					"text": "buffer~ qmw_v6_local @samps 1024 @channels 1"
				}
			},
			{
				"box": {
					"id": "v3_ibm_buffer",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"float",
						"bang"
					],
					"patching_rect": [
						300.0,
						1120.0,
						274.0,
						22.0
					],
					"text": "buffer~ qmw_v6_ibm @samps 1024 @channels 1"
				}
			},
			{
				"box": {
					"id": "v3_local_wave",
					"maxclass": "newobj",
					"numinlets": 4,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						20.0,
						1150.0,
						160.0,
						22.0
					],
					"text": "2d.wave~ qmw_v6_local"
				}
			},
			{
				"box": {
					"id": "v3_ibm_wave",
					"maxclass": "newobj",
					"numinlets": 4,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						190.0,
						1150.0,
						155.0,
						22.0
					],
					"text": "2d.wave~ qmw_v6_ibm"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "source_xfade",
					"maxclass": "flonum",
					"maximum": 1.0,
					"minimum": 0.0,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						30.0,
						1005.0,
						75.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						12.0,
						1005.0,
						75.0,
						22.0
					]
				}
			},
			{
				"box": {
					"id": "source_xfade_label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						110.0,
						1007.0,
						210.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						92.0,
						1007.0,
						210.0,
						20.0
					],
					"text": "source: 0=LOCAL   1=IBM"
				}
			},
			{
				"box": {
					"id": "source_xfade_pack",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						360.0,
						1150.0,
						75.0,
						22.0
					],
					"text": "pack 0. 50"
				}
			},
			{
				"box": {
					"id": "source_xfade_line",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 2,
					"outlettype": [
						"signal",
						"bang"
					],
					"patching_rect": [
						440.0,
						1150.0,
						42.0,
						22.0
					],
					"text": "line~"
				}
			},
			{
				"box": {
					"id": "source_xfade_inverse",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						490.0,
						1150.0,
						52.0,
						22.0
					],
					"text": "!-~ 1."
				}
			},
			{
				"box": {
					"id": "source_local_mul",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						550.0,
						1150.0,
						42.0,
						22.0
					],
					"text": "*~"
				}
			},
			{
				"box": {
					"id": "source_ibm_mul",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						600.0,
						1150.0,
						42.0,
						22.0
					],
					"text": "*~"
				}
			},
			{
				"box": {
					"id": "source_sum",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						650.0,
						1150.0,
						42.0,
						22.0
					],
					"text": "+~"
				}
			},
			{
				"box": {
					"id": "render_mode_ifft",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						340.0,
						1005.0,
						70.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						322.0,
						996.0,
						70.0,
						22.0
					],
					"text": "mode ifft"
				}
			},
			{
				"box": {
					"id": "render_mode_spline",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						415.0,
						1005.0,
						85.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						397.0,
						996.0,
						85.0,
						22.0
					],
					"text": "mode spline"
				}
			},
			{
				"box": {
					"id": "render_mode_density",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						505.0,
						1005.0,
						90.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						487.0,
						996.0,
						90.0,
						22.0
					],
					"text": "mode density"
				}
			},
			{
				"box": {
					"id": "render_mode_hybrid",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						600.0,
						1005.0,
						85.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						582.0,
						996.0,
						85.0,
						22.0
					],
					"text": "mode hybrid"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "render_spectral",
					"maxclass": "flonum",
					"maximum": 1.0,
					"minimum": 0.0,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						340.0,
						1040.0,
						65.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						322.0,
						1028.0,
						65.0,
						22.0
					]
				}
			},
			{
				"box": {
					"id": "render_spectral_label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						410.0,
						1042.0,
						125.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						392.0,
						1030.0,
						125.0,
						20.0
					],
					"text": "spectral -> spatial"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "render_detail",
					"maxclass": "flonum",
					"maximum": 1.0,
					"minimum": 0.0,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						540.0,
						1040.0,
						65.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						522.0,
						1028.0,
						65.0,
						22.0
					]
				}
			},
			{
				"box": {
					"id": "render_detail_label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						610.0,
						1042.0,
						120.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						592.0,
						1030.0,
						120.0,
						20.0
					],
					"text": "smooth -> detailed"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "render_nonlinear",
					"maxclass": "flonum",
					"maximum": 1.0,
					"minimum": 0.0,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						735.0,
						1040.0,
						65.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						717.0,
						1028.0,
						65.0,
						22.0
					]
				}
			},
			{
				"box": {
					"id": "render_nonlinear_label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						805.0,
						1042.0,
						150.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						805.0,
						1030.0,
						150.0,
						20.0
					],
					"text": "stable -> nonlinear"
				}
			},
			{
				"box": {
					"id": "render_spectral_prepend",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						700.0,
						1090.0,
						105.0,
						22.0
					],
					"text": "prepend spectral"
				}
			},
			{
				"box": {
					"id": "render_detail_prepend",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						810.0,
						1090.0,
						95.0,
						22.0
					],
					"text": "prepend detail"
				}
			},
			{
				"box": {
					"id": "render_nonlinear_prepend",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						910.0,
						1090.0,
						115.0,
						22.0
					],
					"text": "prepend nonlinear"
				}
			},
			{
				"box": {
					"id": "v3_local_xyz_unpack",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": [
						"float",
						"float",
						"float"
					],
					"patching_rect": [
						280.0,
						1090.0,
						105.0,
						22.0
					],
					"text": "unpack f f f"
				}
			},
			{
				"box": {
					"id": "v3_ibm_xyz_unpack",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": [
						"float",
						"float",
						"float"
					],
					"patching_rect": [
						390.0,
						1090.0,
						105.0,
						22.0
					],
					"text": "unpack f f f"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "ibm_xx",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						610.0,
						690.0,
						65.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						592.0,
						690.0,
						65.0,
						22.0
					]
				}
			},
			{
				"box": {
					"format": 6,
					"id": "ibm_yy",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						690.0,
						690.0,
						65.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						672.0,
						690.0,
						65.0,
						22.0
					]
				}
			},
			{
				"box": {
					"format": 6,
					"id": "ibm_zz",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						770.0,
						690.0,
						65.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						770.0,
						690.0,
						65.0,
						22.0
					]
				}
			},
			{
				"box": {
					"id": "v3_xyz_labels",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						610.0,
						715.0,
						295.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						592.0,
						715.0,
						295.0,
						20.0
					],
					"text": "LOCAL XX / YY / ZZ above     IBM XX / YY / ZZ below"
				}
			},
			{
				"box": {
					"id": "ir_local_buffer",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"float",
						"bang"
					],
					"patching_rect": [
						20.0,
						1180.0,
						306.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						15.0,
						672.0,
						306.0,
						22.0
					],
					"text": "buffer~ qmw_v6_ir_local @samps 262144 @channels 1"
				}
			},
			{
				"box": {
					"id": "ir_ibm_buffer",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"float",
						"bang"
					],
					"patching_rect": [
						330.0,
						1180.0,
						301.0,
						22.0
					],
					"text": "buffer~ qmw_v6_ir_ibm @samps 262144 @channels 1"
				}
			},
			{
				"box": {
					"id": "ir_convolver",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"signal",
						"signal"
					],
					"patching_rect": [
						20.0,
						1210.0,
						190.0,
						22.0
					],
					"text": "multiconvolve~ 1 2 medium"
				}
			},
			{
				"box": {
					"id": "ir_set_local",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						220.0,
						1210.0,
						180.0,
						22.0
					],
					"text": "set 1 1 qmw_v6_ir_local 1"
				}
			},
			{
				"box": {
					"id": "ir_set_ibm",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						410.0,
						1210.0,
						175.0,
						22.0
					],
					"text": "set 1 2 qmw_v6_ir_ibm 1"
				}
			},
			{
				"box": {
					"id": "ir_local_mul",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						20.0,
						1240.0,
						42.0,
						22.0
					],
					"text": "*~"
				}
			},
			{
				"box": {
					"id": "ir_ibm_mul",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						70.0,
						1240.0,
						42.0,
						22.0
					],
					"text": "*~"
				}
			},
			{
				"box": {
					"id": "ir_wet_sum",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						120.0,
						1240.0,
						42.0,
						22.0
					],
					"text": "+~"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "ir_drywet",
					"maxclass": "flonum",
					"maximum": 1.0,
					"minimum": 0.0,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						30.0,
						1080.0,
						75.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						948.5,
						797.0,
						75.0,
						22.0
					]
				}
			},
			{
				"box": {
					"id": "ir_drywet_label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						110.0,
						1082.0,
						180.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						948.5,
						820.0,
						180.0,
						20.0
					],
					"text": "quantum IR: 0=dry  1=wet"
				}
			},
			{
				"box": {
					"id": "ir_drywet_pack",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						180.0,
						1240.0,
						75.0,
						22.0
					],
					"text": "pack 0. 50"
				}
			},
			{
				"box": {
					"id": "ir_drywet_line",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 2,
					"outlettype": [
						"signal",
						"bang"
					],
					"patching_rect": [
						265.0,
						1240.0,
						42.0,
						22.0
					],
					"text": "line~"
				}
			},
			{
				"box": {
					"id": "ir_dry_inverse",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						315.0,
						1240.0,
						52.0,
						22.0
					],
					"text": "!-~ 1."
				}
			},
			{
				"box": {
					"id": "ir_dry_mul",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						375.0,
						1240.0,
						42.0,
						22.0
					],
					"text": "*~"
				}
			},
			{
				"box": {
					"id": "ir_wet_mul",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						425.0,
						1240.0,
						42.0,
						22.0
					],
					"text": "*~"
				}
			},
			{
				"box": {
					"id": "ir_mix_sum",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						475.0,
						1240.0,
						42.0,
						22.0
					],
					"text": "+~"
				}
			},
			{
				"box": {
					"id": "ir_dry_sqrt",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						525.0,
						1240.0,
						42.0,
						22.0
					],
					"text": "sqrt~"
				}
			},
			{
				"box": {
					"id": "ir_wet_sqrt",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						575.0,
						1240.0,
						42.0,
						22.0
					],
					"text": "sqrt~"
				}
			},
			{
				"box": {
					"id": "local_monitor_gain",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						20.0,
						1185.0,
						62.0,
						22.0
					],
					"text": "*~ 0.12"
				}
			},
			{
				"box": {
					"id": "qft_selector_label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						900.0,
						455.0,
						190.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						923.0,
						385.0,
						190.0,
						20.0
					],
					"text": "POST-CIRCUIT TRANSFORM"
				}
			},
			{
				"box": {
					"id": "qft_none",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						900.0,
						480.0,
						55.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						900.0,
						480.0,
						55.0,
						22.0
					],
					"text": "none"
				}
			},
			{
				"box": {
					"id": "qft_qft",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						960.0,
						480.0,
						55.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						1004.0,
						409.0,
						55.0,
						22.0
					],
					"text": "qft"
				}
			},
			{
				"box": {
					"id": "qft_iqft",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1020.0,
						480.0,
						55.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						1064.0,
						409.0,
						55.0,
						22.0
					],
					"text": "iqft"
				}
			},
			{
				"box": {
					"id": "qft_pack",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"FullPacket"
					],
					"patching_rect": [
						900.0,
						515.0,
						220.0,
						22.0
					],
					"text": "o.pack /qmw/wavetable/transform"
				}
			},
			{
				"box": {
					"id": "qft_udp",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						900.0,
						550.0,
						165.0,
						22.0
					],
					"text": "udpsend 127.0.0.1 7411"
				}
			},
			{
				"box": {
					"id": "qft_default",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1080.0,
						480.0,
						85.0,
						22.0
					],
					"text": "loadmess qft"
				}
			},
			{
				"box": {
					"id": "qft_active",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						900.0,
						580.0,
						180.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						944.0,
						439.0,
						180.0,
						22.0
					],
					"text": "ACTIVE: qft"
				}
			},
			{
				"box": {
					"id": "qft_active_prepend",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1080.0,
						550.0,
						135.0,
						22.0
					],
					"text": "prepend set ACTIVE:"
				}
			},
			{
				"box": {
					"id": "qft_spectrum_renderer",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 3,
					"outlettype": [
						"",
						"",
						""
					],
					"patching_rect": [
						1280.0,
						540.0,
						225.0,
						22.0
					],
					"saved_object_attributes": {
						"filename": "qmw_qft_spectrum_renderer_v5.js",
						"parameter_enable": 0
					},
					"text": "js qmw_qft_spectrum_renderer_v5.js"
				}
			},
			{
				"box": {
					"id": "qft_wave_buffer",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"float",
						"bang"
					],
					"patching_rect": [
						1280.0,
						580.0,
						300.0,
						22.0
					],
					"text": "buffer~ qmw_v6_qft_wave @samps 256 @channels 1"
				}
			},
			{
				"box": {
					"id": "qft_wave_reader",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1280.0,
						620.0,
						160.0,
						22.0
					],
					"text": "wave~ qmw_v6_qft_wave"
				}
			},
			{
				"box": {
					"id": "qft_wave_gain",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1280.0,
						655.0,
						62.0,
						22.0
					],
					"text": "*~ 0.12"
				}
			},
			{
				"box": {
					"id": "qft_spectrogram",
					"maxclass": "jit.pwindow",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"jit_matrix",
						""
					],
					"patching_rect": [
						900.0,
						620.0,
						360.0,
						180.0
					],
					"presentation": 1,
					"presentation_rect": [
						795.0,
						167.0,
						360.0,
						180.0
					],
					"sync": 1
				}
			},
			{
				"box": {
					"id": "qft_spectrum_status",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						900.0,
						805.0,
						360.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						795.0,
						352.0,
						360.0,
						22.0
					],
					"text": "waiting for QFT bins"
				}
			},
			{
				"box": {
					"id": "qft_spectrum_label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						900.0,
						595.0,
						362.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						795.0,
						142.0,
						362.0,
						20.0
					],
					"text": "16-BIN QFT / IQFT SPECTROGRAM + OVERTONE WAVETABLE"
				}
			},
			{
				"box": {
					"id": "qft_spectrum_route",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 4,
					"outlettype": [
						"",
						"",
						"",
						"FullPacket"
					],
					"patching_rect": [
						1280.0,
						500.0,
						360.0,
						22.0
					],
					"text": "o.route /qmw/qft/bins /qmw/qft/amplitudes /qmw/qft/phases"
				}
			},
			{
				"box": {
					"id": "ir_wet_return_trim",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						520.0,
						1140.0,
						62.0,
						22.0
					],
					"text": "*~ 0.5"
				}
			},
			{
				"box": {
					"id": "qft_data_route",
					"maxclass": "newobj",
					"numinlets": 5,
					"numoutlets": 5,
					"outlettype": [
						"",
						"",
						"",
						"",
						""
					],
					"patching_rect": [
						1280.0,
						700.0,
						320.0,
						22.0
					],
					"text": "route probabilities magnitudes phases descriptors"
				}
			},
			{
				"box": {
					"id": "qft_probability_list",
					"linecount": 3,
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1280.0,
						735.0,
						360.0,
						49.0
					],
					"text": "0.0625 0.045588 0.018306 0.02167 0.0625 0.10333 0.106694 0.079412 0.0625 0.079412 0.106694 0.10333 0.0625 0.02167 0.018306 0.045588"
				}
			},
			{
				"box": {
					"id": "qft_magnitude_list",
					"linecount": 3,
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1280.0,
						765.0,
						360.0,
						49.0
					],
					"text": "0.25 0.213513 0.135299 0.147207 0.25 0.32145 0.326641 0.281802 0.25 0.281802 0.326641 0.32145 0.25 0.147207 0.135299 0.213513"
				}
			},
			{
				"box": {
					"id": "qft_phase_list",
					"linecount": 3,
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1280.0,
						795.0,
						362.0,
						49.0
					],
					"text": "0. 0.358584 0.392699 -0.141352 0. 0.506842 1.178097 2.037156 3.141593 -2.037156 -1.178097 -0.506842 -0. 0.141352 -0.392699 -0.358584"
				}
			},
			{
				"box": {
					"id": "qft_descriptor_unpack",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": [
						"float",
						"float",
						"float"
					],
					"patching_rect": [
						1280.0,
						830.0,
						110.0,
						22.0
					],
					"text": "unpack f f f"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "ir_return_gain",
					"maxclass": "flonum",
					"maximum": 1.0,
					"minimum": 0.0,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						300.0,
						1080.0,
						75.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						944.0,
						714.0,
						75.0,
						22.0
					]
				}
			},
			{
				"box": {
					"id": "ir_return_gain_label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						380.0,
						1082.0,
						95.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						944.0,
						690.0,
						95.0,
						20.0
					],
					"text": "IR return gain"
				}
			},
			{
				"box": {
					"id": "ir_return_gain_default",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						300.0,
						1110.0,
						82.0,
						22.0
					],
					"text": "loadmess 0.5"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "ir_size",
					"maxclass": "flonum",
					"maximum": 1.0,
					"minimum": 0.1,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						490.0,
						1080.0,
						75.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						948.5,
						744.0,
						75.0,
						22.0
					]
				}
			},
			{
				"box": {
					"id": "ir_size_label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						570.0,
						1082.0,
						105.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						943.5,
						770.0,
						105.0,
						20.0
					],
					"text": "IR size / decay"
				}
			},
			{
				"box": {
					"id": "ir_size_default",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						490.0,
						1110.0,
						78.0,
						22.0
					],
					"text": "loadmess 1."
				}
			},
			{
				"box": {
					"id": "ir_size_prepend",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						575.0,
						1110.0,
						95.0,
						22.0
					],
					"text": "prepend irsize"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "ir_scale",
					"maxclass": "flonum",
					"maximum": 8.0,
					"minimum": 1.0,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						680.0,
						1080.0,
						75.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						941.0,
						852.0,
						75.0,
						22.0
					]
				}
			},
			{
				"box": {
					"id": "ir_scale_label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						760.0,
						1082.0,
						100.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						1021.0,
						854.0,
						100.0,
						20.0
					],
					"text": "IR buffer scale"
				}
			},
			{
				"box": {
					"id": "ir_scale_default",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						680.0,
						1110.0,
						78.0,
						22.0
					],
					"text": "loadmess 3."
				}
			},
			{
				"box": {
					"id": "ir_scale_prepend",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						765.0,
						1110.0,
						98.0,
						22.0
					],
					"text": "prepend irscale"
				}
			},
			{
				"box": {
					"id": "difference_buffer",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"float",
						"bang"
					],
					"patching_rect": [
						880.0,
						1110.0,
						310.0,
						22.0
					],
					"text": "buffer~ qmw_v6_difference @samps 1024 @channels 1"
				}
			},
			{
				"box": {
					"id": "difference_wave",
					"maxclass": "newobj",
					"numinlets": 4,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						880.0,
						1140.0,
						175.0,
						22.0
					],
					"text": "2d.wave~ qmw_v6_difference"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "difference_gain",
					"maxclass": "flonum",
					"maximum": 2.0,
					"minimum": 0.0,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						870.0,
						1080.0,
						75.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						949.0,
						884.0,
						75.0,
						22.0
					]
				}
			},
			{
				"box": {
					"id": "difference_gain_label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						950.0,
						1082.0,
						125.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						1029.0,
						886.0,
						125.0,
						20.0
					],
					"text": "IBM-local residual"
				}
			},
			{
				"box": {
					"id": "difference_gain_sig",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1065.0,
						1140.0,
						52.0,
						22.0
					],
					"text": "sig~ 0."
				}
			},
			{
				"box": {
					"id": "difference_mul",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1125.0,
						1140.0,
						42.0,
						22.0
					],
					"text": "*~"
				}
			},
			{
				"box": {
					"id": "comparison_sum",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						700.0,
						1180.0,
						42.0,
						22.0
					],
					"text": "+~"
				}
			},
			{
				"box": {
					"id": "v6_compare",
					"maxclass": "newobj",
					"text": "js qmw_pauli_coherence_v6.js",
					"patching_rect": [
						1200.0,
						900.0,
						220.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 5,
					"outlettype": [
						"",
						"list",
						"list",
						"list",
						"list"
					]
				}
			},
			{
				"box": {
					"id": "v6_local_unpack",
					"maxclass": "newobj",
					"text": "unpack f f f f f f f f f f f f f f f",
					"patching_rect": [
						10.0,
						630.0,
						880.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 15,
					"outlettype": [
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float"
					]
				}
			},
			{
				"box": {
					"id": "v6_ibm_unpack",
					"maxclass": "newobj",
					"text": "unpack f f f f f f f f f f f f f f f",
					"patching_rect": [
						10.0,
						660.0,
						880.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 15,
					"outlettype": [
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float"
					]
				}
			},
			{
				"box": {
					"id": "v6_delta_unpack",
					"maxclass": "newobj",
					"text": "unpack f f f f f f f f f f f f f f f",
					"patching_rect": [
						10.0,
						690.0,
						880.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 15,
					"outlettype": [
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float"
					]
				}
			},
			{
				"box": {
					"id": "v6_rows_label",
					"maxclass": "comment",
					"text": "LOCAL / IBM / IBM-LOCAL: XI YI ZI | IX IY IZ | XX XY XZ | YX YY YZ | ZX ZY ZZ",
					"patching_rect": [
						10.0,
						605.0,
						880.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						10.0,
						625.0,
						880.0,
						20.0
					]
				}
			},
			{
				"box": {
					"id": "v6_local_XI",
					"maxclass": "flonum",
					"patching_rect": [
						10.0,
						650.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						10.0,
						650.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_local_YI",
					"maxclass": "flonum",
					"patching_rect": [
						68.0,
						650.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						68.0,
						650.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_local_ZI",
					"maxclass": "flonum",
					"patching_rect": [
						126.0,
						650.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						126.0,
						650.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_local_IX",
					"maxclass": "flonum",
					"patching_rect": [
						184.0,
						650.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						184.0,
						650.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_local_IY",
					"maxclass": "flonum",
					"patching_rect": [
						242.0,
						650.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						242.0,
						650.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_local_IZ",
					"maxclass": "flonum",
					"patching_rect": [
						300.0,
						650.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						300.0,
						650.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_local_XX",
					"maxclass": "flonum",
					"patching_rect": [
						358.0,
						650.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						358.0,
						650.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_local_XY",
					"maxclass": "flonum",
					"patching_rect": [
						416.0,
						650.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						416.0,
						650.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_local_XZ",
					"maxclass": "flonum",
					"patching_rect": [
						474.0,
						650.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						474.0,
						650.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_local_YX",
					"maxclass": "flonum",
					"patching_rect": [
						532.0,
						650.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						532.0,
						650.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_local_YY",
					"maxclass": "flonum",
					"patching_rect": [
						590.0,
						650.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						590.0,
						650.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_local_YZ",
					"maxclass": "flonum",
					"patching_rect": [
						648.0,
						650.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						648.0,
						650.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_local_ZX",
					"maxclass": "flonum",
					"patching_rect": [
						706.0,
						650.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						706.0,
						650.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_local_ZY",
					"maxclass": "flonum",
					"patching_rect": [
						764.0,
						650.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						764.0,
						650.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_local_ZZ",
					"maxclass": "flonum",
					"patching_rect": [
						822.0,
						650.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						822.0,
						650.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_ibm_XI",
					"maxclass": "flonum",
					"patching_rect": [
						10.0,
						680.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						10.0,
						680.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_ibm_YI",
					"maxclass": "flonum",
					"patching_rect": [
						68.0,
						680.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						68.0,
						680.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_ibm_ZI",
					"maxclass": "flonum",
					"patching_rect": [
						126.0,
						680.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						126.0,
						680.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_ibm_IX",
					"maxclass": "flonum",
					"patching_rect": [
						184.0,
						680.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						184.0,
						680.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_ibm_IY",
					"maxclass": "flonum",
					"patching_rect": [
						242.0,
						680.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						242.0,
						680.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_ibm_IZ",
					"maxclass": "flonum",
					"patching_rect": [
						300.0,
						680.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						300.0,
						680.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_ibm_XX",
					"maxclass": "flonum",
					"patching_rect": [
						358.0,
						680.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						358.0,
						680.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_ibm_XY",
					"maxclass": "flonum",
					"patching_rect": [
						416.0,
						680.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						416.0,
						680.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_ibm_XZ",
					"maxclass": "flonum",
					"patching_rect": [
						474.0,
						680.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						474.0,
						680.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_ibm_YX",
					"maxclass": "flonum",
					"patching_rect": [
						532.0,
						680.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						532.0,
						680.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_ibm_YY",
					"maxclass": "flonum",
					"patching_rect": [
						590.0,
						680.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						590.0,
						680.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_ibm_YZ",
					"maxclass": "flonum",
					"patching_rect": [
						648.0,
						680.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						648.0,
						680.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_ibm_ZX",
					"maxclass": "flonum",
					"patching_rect": [
						706.0,
						680.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						706.0,
						680.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_ibm_ZY",
					"maxclass": "flonum",
					"patching_rect": [
						764.0,
						680.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						764.0,
						680.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_ibm_ZZ",
					"maxclass": "flonum",
					"patching_rect": [
						822.0,
						680.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						822.0,
						680.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_delta_XI",
					"maxclass": "flonum",
					"patching_rect": [
						10.0,
						710.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						10.0,
						710.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_delta_YI",
					"maxclass": "flonum",
					"patching_rect": [
						68.0,
						710.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						68.0,
						710.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_delta_ZI",
					"maxclass": "flonum",
					"patching_rect": [
						126.0,
						710.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						126.0,
						710.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_delta_IX",
					"maxclass": "flonum",
					"patching_rect": [
						184.0,
						710.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						184.0,
						710.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_delta_IY",
					"maxclass": "flonum",
					"patching_rect": [
						242.0,
						710.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						242.0,
						710.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_delta_IZ",
					"maxclass": "flonum",
					"patching_rect": [
						300.0,
						710.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						300.0,
						710.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_delta_XX",
					"maxclass": "flonum",
					"patching_rect": [
						358.0,
						710.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						358.0,
						710.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_delta_XY",
					"maxclass": "flonum",
					"patching_rect": [
						416.0,
						710.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						416.0,
						710.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_delta_XZ",
					"maxclass": "flonum",
					"patching_rect": [
						474.0,
						710.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						474.0,
						710.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_delta_YX",
					"maxclass": "flonum",
					"patching_rect": [
						532.0,
						710.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						532.0,
						710.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_delta_YY",
					"maxclass": "flonum",
					"patching_rect": [
						590.0,
						710.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						590.0,
						710.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_delta_YZ",
					"maxclass": "flonum",
					"patching_rect": [
						648.0,
						710.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						648.0,
						710.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_delta_ZX",
					"maxclass": "flonum",
					"patching_rect": [
						706.0,
						710.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						706.0,
						710.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_delta_ZY",
					"maxclass": "flonum",
					"patching_rect": [
						764.0,
						710.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						764.0,
						710.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_delta_ZZ",
					"maxclass": "flonum",
					"patching_rect": [
						822.0,
						710.0,
						54.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						822.0,
						710.0,
						54.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_coh_buf_local",
					"maxclass": "newobj",
					"text": "buffer~ qmw_v6_coherence_local @samps 256 @channels 1",
					"patching_rect": [
						1200.0,
						940.0,
						300.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"float",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_coh_wave_local",
					"maxclass": "newobj",
					"text": "wave~ qmw_v6_coherence_local",
					"patching_rect": [
						1200.0,
						1060.0,
						190.0,
						22.0
					],
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_coh_buf_ibm",
					"maxclass": "newobj",
					"text": "buffer~ qmw_v6_coherence_ibm @samps 256 @channels 1",
					"patching_rect": [
						1200.0,
						980.0,
						300.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"float",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_coh_wave_ibm",
					"maxclass": "newobj",
					"text": "wave~ qmw_v6_coherence_ibm",
					"patching_rect": [
						1200.0,
						1090.0,
						190.0,
						22.0
					],
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_coh_buf_difference",
					"maxclass": "newobj",
					"text": "buffer~ qmw_v6_coherence_difference @samps 256 @channels 1",
					"patching_rect": [
						1200.0,
						980.0,
						300.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"float",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_coh_wave_difference",
					"maxclass": "newobj",
					"text": "wave~ qmw_v6_coherence_difference",
					"patching_rect": [
						1200.0,
						1090.0,
						190.0,
						22.0
					],
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_coh_local_mul",
					"maxclass": "newobj",
					"text": "*~",
					"patching_rect": [
						1200.0,
						1160.0,
						42.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_coh_ibm_mul",
					"maxclass": "newobj",
					"text": "*~",
					"patching_rect": [
						1250.0,
						1160.0,
						42.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_coh_source_sum",
					"maxclass": "newobj",
					"text": "+~",
					"patching_rect": [
						1300.0,
						1160.0,
						42.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_coh_difference_mul",
					"maxclass": "newobj",
					"text": "*~",
					"patching_rect": [
						1350.0,
						1160.0,
						42.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_coh_mix_sum",
					"maxclass": "newobj",
					"text": "+~",
					"patching_rect": [
						1400.0,
						1160.0,
						42.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_coh_gain",
					"maxclass": "flonum",
					"minimum": 0.0,
					"maximum": 1.0,
					"patching_rect": [
						1080.0,
						1080.0,
						75.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						1080.0,
						1038.0,
						75.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_coh_gain_label",
					"maxclass": "comment",
					"text": "coherence voice",
					"patching_rect": [
						1160.0,
						1082.0,
						110.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						1160.0,
						1040.0,
						110.0,
						20.0
					]
				}
			},
			{
				"box": {
					"id": "v6_coh_gain_default",
					"maxclass": "newobj",
					"text": "loadmess 0.2",
					"patching_rect": [
						1080.0,
						1110.0,
						82.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					]
				}
			},
			{
				"box": {
					"id": "v6_coh_gain_sig",
					"maxclass": "newobj",
					"text": "sig~ 0.",
					"patching_rect": [
						1450.0,
						1160.0,
						52.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_coh_gain_mul",
					"maxclass": "newobj",
					"text": "*~",
					"patching_rect": [
						1510.0,
						1160.0,
						42.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_final_sum",
					"maxclass": "newobj",
					"text": "+~",
					"patching_rect": [
						760.0,
						1180.0,
						42.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_density_line_slice",
					"maxclass": "newobj",
					"text": "zl.slice 2",
					"patching_rect": [
						1200.0,
						1220.0,
						70.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 2,
					"outlettype": [
						"list",
						"list"
					]
				}
			},
			{
				"box": {
					"id": "v6_density_line_unpack",
					"maxclass": "newobj",
					"text": "unpack f f f f f f f f f f f f f f f f f f",
					"patching_rect": [
						1280.0,
						1220.0,
						500.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 18,
					"outlettype": [
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float"
					]
				}
			},
			{
				"box": {
					"id": "v6_density_line_gain",
					"maxclass": "flonum",
					"minimum": 0.0,
					"maximum": 1.0,
					"patching_rect": [
						1275.0,
						1080.0,
						75.0,
						22.0
					],
					"presentation": 1,
					"presentation_rect": [
						1275.0,
						1038.0,
						75.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "v6_density_line_label",
					"maxclass": "comment",
					"text": "density-H lines",
					"patching_rect": [
						1355.0,
						1082.0,
						105.0,
						20.0
					],
					"presentation": 1,
					"presentation_rect": [
						1355.0,
						1040.0,
						105.0,
						20.0
					]
				}
			},
			{
				"box": {
					"id": "v6_density_line_gain_sig",
					"maxclass": "newobj",
					"text": "sig~ 0.",
					"patching_rect": [
						1450.0,
						1220.0,
						52.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_density_line_sum",
					"maxclass": "newobj",
					"text": "+~",
					"patching_rect": [
						1510.0,
						1220.0,
						42.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_density_line_gain_mul",
					"maxclass": "newobj",
					"text": "*~",
					"patching_rect": [
						1560.0,
						1220.0,
						42.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_density_line_final_sum",
					"maxclass": "newobj",
					"text": "+~",
					"patching_rect": [
						820.0,
						1180.0,
						42.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_z_cycle_0",
					"maxclass": "newobj",
					"text": "cycle~",
					"patching_rect": [
						1200.0,
						1260.0,
						55.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_z_amp_0",
					"maxclass": "newobj",
					"text": "*~",
					"patching_rect": [
						1200.0,
						1290.0,
						42.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_z_phase_0",
					"maxclass": "newobj",
					"text": "expr $f1 / 6.283185307",
					"patching_rect": [
						1200.0,
						1360.0,
						120.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					]
				}
			},
			{
				"box": {
					"id": "v6_z_phase_sig_0",
					"maxclass": "newobj",
					"text": "sig~",
					"patching_rect": [
						1200.0,
						1390.0,
						42.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_z_cycle_1",
					"maxclass": "newobj",
					"text": "cycle~",
					"patching_rect": [
						1270.0,
						1260.0,
						55.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_z_amp_1",
					"maxclass": "newobj",
					"text": "*~",
					"patching_rect": [
						1270.0,
						1290.0,
						42.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_z_phase_1",
					"maxclass": "newobj",
					"text": "expr $f1 / 6.283185307",
					"patching_rect": [
						1270.0,
						1360.0,
						120.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					]
				}
			},
			{
				"box": {
					"id": "v6_z_phase_sig_1",
					"maxclass": "newobj",
					"text": "sig~",
					"patching_rect": [
						1270.0,
						1390.0,
						42.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_z_cycle_2",
					"maxclass": "newobj",
					"text": "cycle~",
					"patching_rect": [
						1340.0,
						1260.0,
						55.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_z_amp_2",
					"maxclass": "newobj",
					"text": "*~",
					"patching_rect": [
						1340.0,
						1290.0,
						42.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_z_phase_2",
					"maxclass": "newobj",
					"text": "expr $f1 / 6.283185307",
					"patching_rect": [
						1340.0,
						1360.0,
						120.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					]
				}
			},
			{
				"box": {
					"id": "v6_z_phase_sig_2",
					"maxclass": "newobj",
					"text": "sig~",
					"patching_rect": [
						1340.0,
						1390.0,
						42.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_z_cycle_3",
					"maxclass": "newobj",
					"text": "cycle~",
					"patching_rect": [
						1410.0,
						1260.0,
						55.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_z_amp_3",
					"maxclass": "newobj",
					"text": "*~",
					"patching_rect": [
						1410.0,
						1290.0,
						42.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_z_phase_3",
					"maxclass": "newobj",
					"text": "expr $f1 / 6.283185307",
					"patching_rect": [
						1410.0,
						1360.0,
						120.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					]
				}
			},
			{
				"box": {
					"id": "v6_z_phase_sig_3",
					"maxclass": "newobj",
					"text": "sig~",
					"patching_rect": [
						1410.0,
						1390.0,
						42.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_z_cycle_4",
					"maxclass": "newobj",
					"text": "cycle~",
					"patching_rect": [
						1480.0,
						1260.0,
						55.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_z_amp_4",
					"maxclass": "newobj",
					"text": "*~",
					"patching_rect": [
						1480.0,
						1290.0,
						42.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_z_phase_4",
					"maxclass": "newobj",
					"text": "expr $f1 / 6.283185307",
					"patching_rect": [
						1480.0,
						1360.0,
						120.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					]
				}
			},
			{
				"box": {
					"id": "v6_z_phase_sig_4",
					"maxclass": "newobj",
					"text": "sig~",
					"patching_rect": [
						1480.0,
						1390.0,
						42.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_z_cycle_5",
					"maxclass": "newobj",
					"text": "cycle~",
					"patching_rect": [
						1550.0,
						1260.0,
						55.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_z_amp_5",
					"maxclass": "newobj",
					"text": "*~",
					"patching_rect": [
						1550.0,
						1290.0,
						42.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_z_phase_5",
					"maxclass": "newobj",
					"text": "expr $f1 / 6.283185307",
					"patching_rect": [
						1550.0,
						1360.0,
						120.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					]
				}
			},
			{
				"box": {
					"id": "v6_z_phase_sig_5",
					"maxclass": "newobj",
					"text": "sig~",
					"patching_rect": [
						1550.0,
						1390.0,
						42.0,
						22.0
					],
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_z_sum_1",
					"maxclass": "newobj",
					"text": "+~",
					"patching_rect": [
						1255.0,
						1330.0,
						42.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_z_sum_2",
					"maxclass": "newobj",
					"text": "+~",
					"patching_rect": [
						1310.0,
						1330.0,
						42.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_z_sum_3",
					"maxclass": "newobj",
					"text": "+~",
					"patching_rect": [
						1365.0,
						1330.0,
						42.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_z_sum_4",
					"maxclass": "newobj",
					"text": "+~",
					"patching_rect": [
						1420.0,
						1330.0,
						42.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			},
			{
				"box": {
					"id": "v6_z_sum_5",
					"maxclass": "newobj",
					"text": "+~",
					"patching_rect": [
						1475.0,
						1330.0,
						42.0,
						22.0
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					]
				}
			}
		],
		"lines": [
			{
				"patchline": {
					"destination": [
						"rotation_layer",
						0
					],
					"order": 0,
					"source": [
						"axis_rx",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"theta_qasm",
						0
					],
					"order": 1,
					"source": [
						"axis_rx",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"rotation_layer",
						0
					],
					"order": 0,
					"source": [
						"axis_ry",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"theta_qasm",
						0
					],
					"order": 1,
					"source": [
						"axis_ry",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"rotation_layer",
						0
					],
					"order": 0,
					"source": [
						"axis_rz",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"theta_qasm",
						0
					],
					"order": 1,
					"source": [
						"axis_rz",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_convolver",
						0
					],
					"order": 1,
					"source": [
						"v6_density_line_final_sum",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_mix_sum",
						0
					],
					"order": 0,
					"source": [
						"v6_density_line_final_sum",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"controls_unpack",
						0
					],
					"source": [
						"controls_slice",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"correlation_display",
						0
					],
					"order": 1,
					"source": [
						"controls_unpack",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"entanglement_display",
						0
					],
					"order": 1,
					"source": [
						"controls_unpack",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"entropy_display",
						0
					],
					"source": [
						"controls_unpack",
						3
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"gain_map",
						0
					],
					"order": 0,
					"source": [
						"controls_unpack",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"pitch_map",
						0
					],
					"order": 0,
					"source": [
						"controls_unpack",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"polarization_display",
						0
					],
					"order": 1,
					"source": [
						"controls_unpack",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"scan_map",
						0
					],
					"order": 0,
					"source": [
						"controls_unpack",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"xx",
						0
					],
					"source": [
						"corr_unpack",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"yy",
						0
					],
					"source": [
						"corr_unpack",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"zz",
						0
					],
					"source": [
						"corr_unpack",
						3
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"designer_status",
						0
					],
					"source": [
						"designer",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qac",
						0
					],
					"source": [
						"designer",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"difference_gain_sig",
						0
					],
					"source": [
						"difference_gain",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"difference_mul",
						1
					],
					"source": [
						"difference_gain_sig",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"comparison_sum",
						1
					],
					"source": [
						"difference_mul",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"difference_mul",
						0
					],
					"source": [
						"difference_wave",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"y_depth_mul",
						1
					],
					"source": [
						"entropy_sig",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"phasor",
						0
					],
					"source": [
						"freq",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"dac",
						1
					],
					"order": 0,
					"source": [
						"gain",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"dac",
						0
					],
					"order": 1,
					"source": [
						"gain",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"gain",
						1
					],
					"source": [
						"gain_map",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"gain_map",
						2
					],
					"source": [
						"gain_max",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"gain_max",
						0
					],
					"source": [
						"gain_max_default",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"gain_map",
						1
					],
					"source": [
						"gain_min",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"gain_min",
						0
					],
					"source": [
						"gain_min_default",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_ibm_mul",
						0
					],
					"source": [
						"ir_convolver",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_local_mul",
						0
					],
					"source": [
						"ir_convolver",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_dry_sqrt",
						0
					],
					"source": [
						"ir_dry_inverse",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_dry_mul",
						1
					],
					"source": [
						"ir_dry_sqrt",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_drywet_pack",
						0
					],
					"source": [
						"ir_drywet",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_dry_inverse",
						0
					],
					"order": 1,
					"source": [
						"ir_drywet_line",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_wet_sqrt",
						0
					],
					"order": 0,
					"source": [
						"ir_drywet_line",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_drywet_line",
						0
					],
					"source": [
						"ir_drywet_pack",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_wet_sum",
						1
					],
					"source": [
						"ir_ibm_mul",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_wet_sum",
						0
					],
					"source": [
						"ir_local_mul",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"gain",
						0
					],
					"source": [
						"ir_mix_sum",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_wet_return_trim",
						1
					],
					"source": [
						"ir_return_gain",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_return_gain",
						0
					],
					"source": [
						"ir_return_gain_default",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_scale_prepend",
						0
					],
					"source": [
						"ir_scale",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_scale",
						0
					],
					"source": [
						"ir_scale_default",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"v3_renderer",
						0
					],
					"source": [
						"ir_scale_prepend",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_convolver",
						0
					],
					"source": [
						"ir_set_ibm",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_convolver",
						0
					],
					"source": [
						"ir_set_local",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_size_prepend",
						0
					],
					"source": [
						"ir_size",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_size",
						0
					],
					"source": [
						"ir_size_default",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"v3_renderer",
						0
					],
					"source": [
						"ir_size_prepend",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_wet_return_trim",
						0
					],
					"source": [
						"ir_wet_mul",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_mix_sum",
						1
					],
					"source": [
						"ir_wet_return_trim",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_wet_mul",
						1
					],
					"source": [
						"ir_wet_sqrt",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_wet_mul",
						0
					],
					"source": [
						"ir_wet_sum",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"display",
						0
					],
					"source": [
						"loader",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"status",
						0
					],
					"source": [
						"loader",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"dac",
						1
					],
					"order": 0,
					"source": [
						"local_monitor_gain",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"dac",
						0
					],
					"order": 1,
					"source": [
						"local_monitor_gain",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-5",
						0
					],
					"source": [
						"morph",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"y_depth_mul",
						0
					],
					"source": [
						"obj-5",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"controls_slice",
						0
					],
					"source": [
						"oroute",
						6
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"corr_unpack",
						0
					],
					"order": 1,
					"source": [
						"oroute",
						3
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"loader",
						0
					],
					"source": [
						"oroute",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"pauli_slice",
						0
					],
					"order": 0,
					"source": [
						"oroute",
						4
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"print",
						0
					],
					"source": [
						"oroute",
						12
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_spectrum_renderer",
						2
					],
					"source": [
						"oroute",
						10
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_spectrum_renderer",
						1
					],
					"source": [
						"oroute",
						9
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_spectrum_renderer",
						0
					],
					"source": [
						"oroute",
						8
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_spectrum_renderer",
						0
					],
					"order": 0,
					"source": [
						"oroute",
						3
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"status",
						0
					],
					"source": [
						"oroute",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"status",
						0
					],
					"source": [
						"oroute",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"surface_loader",
						0
					],
					"order": 1,
					"source": [
						"oroute",
						4
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"surface_slice",
						0
					],
					"source": [
						"oroute",
						5
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"v3_renderer",
						0
					],
					"source": [
						"oroute",
						7
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"pauli_display",
						0
					],
					"source": [
						"pauli_slice",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"difference_wave",
						0
					],
					"order": 1,
					"source": [
						"phasor",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_wave_reader",
						0
					],
					"order": 0,
					"source": [
						"phasor",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"two_d",
						0
					],
					"order": 3,
					"source": [
						"phasor",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"v3_ibm_wave",
						0
					],
					"order": 2,
					"source": [
						"phasor",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"v3_local_wave",
						0
					],
					"order": 4,
					"source": [
						"phasor",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"freq",
						0
					],
					"source": [
						"pitch_map",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"rotation_layer",
						0
					],
					"source": [
						"qac",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_active",
						0
					],
					"source": [
						"qft_active_prepend",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_descriptor_unpack",
						0
					],
					"source": [
						"qft_data_route",
						3
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_magnitude_list",
						1
					],
					"source": [
						"qft_data_route",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_phase_list",
						1
					],
					"source": [
						"qft_data_route",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_probability_list",
						1
					],
					"source": [
						"qft_data_route",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_active_prepend",
						0
					],
					"order": 0,
					"source": [
						"qft_default",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_pack",
						0
					],
					"order": 1,
					"source": [
						"qft_default",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_active_prepend",
						0
					],
					"order": 0,
					"source": [
						"qft_iqft",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_pack",
						0
					],
					"order": 1,
					"source": [
						"qft_iqft",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_active_prepend",
						0
					],
					"order": 0,
					"source": [
						"qft_none",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_pack",
						0
					],
					"order": 1,
					"source": [
						"qft_none",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_udp",
						0
					],
					"source": [
						"qft_pack",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_active_prepend",
						0
					],
					"order": 0,
					"source": [
						"qft_qft",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_pack",
						0
					],
					"order": 1,
					"source": [
						"qft_qft",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_data_route",
						0
					],
					"source": [
						"qft_spectrum_renderer",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_spectrogram",
						0
					],
					"source": [
						"qft_spectrum_renderer",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_spectrum_status",
						0
					],
					"source": [
						"qft_spectrum_renderer",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_spectrum_renderer",
						2
					],
					"source": [
						"qft_spectrum_route",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_spectrum_renderer",
						1
					],
					"source": [
						"qft_spectrum_route",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_spectrum_renderer",
						0
					],
					"source": [
						"qft_spectrum_route",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"dac",
						1
					],
					"order": 0,
					"source": [
						"qft_wave_gain",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"dac",
						0
					],
					"order": 1,
					"source": [
						"qft_wave_gain",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_wave_gain",
						0
					],
					"source": [
						"qft_wave_reader",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"render_detail_prepend",
						0
					],
					"source": [
						"render_detail",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"v3_renderer",
						0
					],
					"source": [
						"render_detail_prepend",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"v3_renderer",
						0
					],
					"source": [
						"render_mode_density",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"v3_renderer",
						0
					],
					"source": [
						"render_mode_hybrid",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"v3_renderer",
						0
					],
					"source": [
						"render_mode_ifft",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"v3_renderer",
						0
					],
					"source": [
						"render_mode_spline",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"render_nonlinear_prepend",
						0
					],
					"source": [
						"render_nonlinear",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"v3_renderer",
						0
					],
					"source": [
						"render_nonlinear_prepend",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"render_spectral_prepend",
						0
					],
					"source": [
						"render_spectral",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"v3_renderer",
						0
					],
					"source": [
						"render_spectral_prepend",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"rotation_enable_prepend",
						0
					],
					"source": [
						"rotation_enable",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"rotation_enable",
						0
					],
					"source": [
						"rotation_enable_default",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"rotation_layer",
						0
					],
					"source": [
						"rotation_enable_prepend",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"sender",
						0
					],
					"source": [
						"rotation_layer",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"sendstatus",
						0
					],
					"source": [
						"rotation_layer",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"rotation_target_prepend",
						0
					],
					"source": [
						"rotation_target",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"rotation_layer",
						0
					],
					"source": [
						"rotation_target_prepend",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"rotation_layer",
						0
					],
					"source": [
						"rotation_theta_prepend",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"difference_wave",
						0
					],
					"order": 0,
					"source": [
						"rows",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"two_d",
						0
					],
					"order": 2,
					"source": [
						"rows",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"v3_ibm_wave",
						0
					],
					"order": 1,
					"source": [
						"rows",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"v3_local_wave",
						0
					],
					"order": 3,
					"source": [
						"rows",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"rows",
						0
					],
					"source": [
						"rows_load",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"morph",
						0
					],
					"source": [
						"scan_map",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"sendstatus",
						0
					],
					"source": [
						"sender",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"source_sum",
						1
					],
					"source": [
						"source_ibm_mul",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"source_sum",
						0
					],
					"source": [
						"source_local_mul",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"comparison_sum",
						0
					],
					"source": [
						"source_sum",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"source_xfade_pack",
						0
					],
					"source": [
						"source_xfade",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_local_mul",
						1
					],
					"order": 1,
					"source": [
						"source_xfade_inverse",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"source_local_mul",
						1
					],
					"order": 0,
					"source": [
						"source_xfade_inverse",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_ibm_mul",
						1
					],
					"order": 2,
					"source": [
						"source_xfade_line",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"source_ibm_mul",
						1
					],
					"order": 0,
					"source": [
						"source_xfade_line",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"source_xfade_inverse",
						0
					],
					"order": 1,
					"source": [
						"source_xfade_line",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"source_xfade_line",
						0
					],
					"source": [
						"source_xfade_pack",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"buffer",
						0
					],
					"order": 1,
					"source": [
						"surface_loader",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"rows",
						0
					],
					"order": 0,
					"source": [
						"surface_loader",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"status",
						0
					],
					"source": [
						"surface_loader",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"buffer",
						0
					],
					"source": [
						"surface_replace",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"surface_replace",
						0
					],
					"source": [
						"surface_slice",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"rotation_theta_prepend",
						0
					],
					"order": 0,
					"source": [
						"theta_control",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"theta_qasm",
						0
					],
					"order": 1,
					"source": [
						"theta_control",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"sender",
						0
					],
					"source": [
						"theta_qasm",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"sendstatus",
						0
					],
					"source": [
						"theta_qasm",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"theta_qasm",
						0
					],
					"source": [
						"theta_send",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"oroute",
						0
					],
					"order": 2,
					"source": [
						"udp",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"qft_spectrum_route",
						0
					],
					"order": 0,
					"source": [
						"udp",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"rawprint",
						0
					],
					"order": 1,
					"source": [
						"udp",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"source_ibm_mul",
						0
					],
					"source": [
						"v3_ibm_wave",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ibm_xx",
						0
					],
					"source": [
						"v3_ibm_xyz_unpack",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ibm_yy",
						0
					],
					"source": [
						"v3_ibm_xyz_unpack",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ibm_zz",
						0
					],
					"source": [
						"v3_ibm_xyz_unpack",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"local_monitor_gain",
						0
					],
					"order": 1,
					"source": [
						"v3_local_wave",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"source_local_mul",
						0
					],
					"order": 0,
					"source": [
						"v3_local_wave",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"xx",
						0
					],
					"source": [
						"v3_local_xyz_unpack",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"yy",
						0
					],
					"source": [
						"v3_local_xyz_unpack",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"zz",
						0
					],
					"source": [
						"v3_local_xyz_unpack",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"display",
						0
					],
					"source": [
						"v3_renderer",
						3
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_set_ibm",
						0
					],
					"order": 0,
					"source": [
						"v3_renderer",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"ir_set_local",
						0
					],
					"order": 0,
					"source": [
						"v3_renderer",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"pauli_display",
						0
					],
					"source": [
						"v3_renderer",
						4
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"status",
						0
					],
					"source": [
						"v3_renderer",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"v3_ibm_buffer",
						0
					],
					"order": 1,
					"source": [
						"v3_renderer",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"v3_ibm_xyz_unpack",
						0
					],
					"source": [
						"v3_renderer",
						6
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"v3_local_buffer",
						0
					],
					"order": 1,
					"source": [
						"v3_renderer",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"v3_local_xyz_unpack",
						0
					],
					"source": [
						"v3_renderer",
						5
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"difference_wave",
						1
					],
					"order": 0,
					"source": [
						"y_depth_mul",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"two_d",
						1
					],
					"order": 1,
					"source": [
						"y_depth_mul",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"v3_ibm_wave",
						1
					],
					"order": 2,
					"source": [
						"y_depth_mul",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"v3_local_wave",
						1
					],
					"order": 3,
					"source": [
						"y_depth_mul",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"oroute",
						7
					],
					"destination": [
						"v6_compare",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"oroute",
						11
					],
					"destination": [
						"v6_density_line_slice",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_density_line_slice",
						1
					],
					"destination": [
						"v6_density_line_unpack",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_compare",
						1
					],
					"destination": [
						"v6_local_unpack",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_compare",
						2
					],
					"destination": [
						"v6_ibm_unpack",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_compare",
						3
					],
					"destination": [
						"v6_delta_unpack",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_local_unpack",
						0
					],
					"destination": [
						"v6_local_XI",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_local_unpack",
						1
					],
					"destination": [
						"v6_local_YI",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_local_unpack",
						2
					],
					"destination": [
						"v6_local_ZI",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_local_unpack",
						3
					],
					"destination": [
						"v6_local_IX",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_local_unpack",
						4
					],
					"destination": [
						"v6_local_IY",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_local_unpack",
						5
					],
					"destination": [
						"v6_local_IZ",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_local_unpack",
						6
					],
					"destination": [
						"v6_local_XX",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_local_unpack",
						7
					],
					"destination": [
						"v6_local_XY",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_local_unpack",
						8
					],
					"destination": [
						"v6_local_XZ",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_local_unpack",
						9
					],
					"destination": [
						"v6_local_YX",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_local_unpack",
						10
					],
					"destination": [
						"v6_local_YY",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_local_unpack",
						11
					],
					"destination": [
						"v6_local_YZ",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_local_unpack",
						12
					],
					"destination": [
						"v6_local_ZX",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_local_unpack",
						13
					],
					"destination": [
						"v6_local_ZY",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_local_unpack",
						14
					],
					"destination": [
						"v6_local_ZZ",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_ibm_unpack",
						0
					],
					"destination": [
						"v6_ibm_XI",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_ibm_unpack",
						1
					],
					"destination": [
						"v6_ibm_YI",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_ibm_unpack",
						2
					],
					"destination": [
						"v6_ibm_ZI",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_ibm_unpack",
						3
					],
					"destination": [
						"v6_ibm_IX",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_ibm_unpack",
						4
					],
					"destination": [
						"v6_ibm_IY",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_ibm_unpack",
						5
					],
					"destination": [
						"v6_ibm_IZ",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_ibm_unpack",
						6
					],
					"destination": [
						"v6_ibm_XX",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_ibm_unpack",
						7
					],
					"destination": [
						"v6_ibm_XY",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_ibm_unpack",
						8
					],
					"destination": [
						"v6_ibm_XZ",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_ibm_unpack",
						9
					],
					"destination": [
						"v6_ibm_YX",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_ibm_unpack",
						10
					],
					"destination": [
						"v6_ibm_YY",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_ibm_unpack",
						11
					],
					"destination": [
						"v6_ibm_YZ",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_ibm_unpack",
						12
					],
					"destination": [
						"v6_ibm_ZX",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_ibm_unpack",
						13
					],
					"destination": [
						"v6_ibm_ZY",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_ibm_unpack",
						14
					],
					"destination": [
						"v6_ibm_ZZ",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_delta_unpack",
						0
					],
					"destination": [
						"v6_delta_XI",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_delta_unpack",
						1
					],
					"destination": [
						"v6_delta_YI",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_delta_unpack",
						2
					],
					"destination": [
						"v6_delta_ZI",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_delta_unpack",
						3
					],
					"destination": [
						"v6_delta_IX",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_delta_unpack",
						4
					],
					"destination": [
						"v6_delta_IY",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_delta_unpack",
						5
					],
					"destination": [
						"v6_delta_IZ",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_delta_unpack",
						6
					],
					"destination": [
						"v6_delta_XX",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_delta_unpack",
						7
					],
					"destination": [
						"v6_delta_XY",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_delta_unpack",
						8
					],
					"destination": [
						"v6_delta_XZ",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_delta_unpack",
						9
					],
					"destination": [
						"v6_delta_YX",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_delta_unpack",
						10
					],
					"destination": [
						"v6_delta_YY",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_delta_unpack",
						11
					],
					"destination": [
						"v6_delta_YZ",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_delta_unpack",
						12
					],
					"destination": [
						"v6_delta_ZX",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_delta_unpack",
						13
					],
					"destination": [
						"v6_delta_ZY",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_delta_unpack",
						14
					],
					"destination": [
						"v6_delta_ZZ",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"phasor",
						0
					],
					"destination": [
						"v6_coh_wave_local",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"phasor",
						0
					],
					"destination": [
						"v6_coh_wave_ibm",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"phasor",
						0
					],
					"destination": [
						"v6_coh_wave_difference",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_coh_wave_local",
						0
					],
					"destination": [
						"v6_coh_local_mul",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"source_xfade_inverse",
						0
					],
					"destination": [
						"v6_coh_local_mul",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_coh_wave_ibm",
						0
					],
					"destination": [
						"v6_coh_ibm_mul",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"source_xfade_line",
						0
					],
					"destination": [
						"v6_coh_ibm_mul",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_coh_local_mul",
						0
					],
					"destination": [
						"v6_coh_source_sum",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_coh_ibm_mul",
						0
					],
					"destination": [
						"v6_coh_source_sum",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_coh_wave_difference",
						0
					],
					"destination": [
						"v6_coh_difference_mul",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"difference_gain_sig",
						0
					],
					"destination": [
						"v6_coh_difference_mul",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_coh_source_sum",
						0
					],
					"destination": [
						"v6_coh_mix_sum",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_coh_difference_mul",
						0
					],
					"destination": [
						"v6_coh_mix_sum",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_coh_gain_default",
						0
					],
					"destination": [
						"v6_coh_gain",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_coh_gain",
						0
					],
					"destination": [
						"v6_coh_gain_sig",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_coh_mix_sum",
						0
					],
					"destination": [
						"v6_coh_gain_mul",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_coh_gain_sig",
						0
					],
					"destination": [
						"v6_coh_gain_mul",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"comparison_sum",
						0
					],
					"destination": [
						"v6_final_sum",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_coh_gain_mul",
						0
					],
					"destination": [
						"v6_final_sum",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_density_line_gain",
						0
					],
					"destination": [
						"v6_density_line_gain_sig",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_density_line_unpack",
						0
					],
					"destination": [
						"v6_z_cycle_0",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_density_line_unpack",
						1
					],
					"destination": [
						"v6_z_amp_0",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_density_line_unpack",
						2
					],
					"destination": [
						"v6_z_phase_0",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_phase_0",
						0
					],
					"destination": [
						"v6_z_phase_sig_0",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_phase_sig_0",
						0
					],
					"destination": [
						"v6_z_cycle_0",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_cycle_0",
						0
					],
					"destination": [
						"v6_z_amp_0",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_density_line_unpack",
						3
					],
					"destination": [
						"v6_z_cycle_1",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_density_line_unpack",
						4
					],
					"destination": [
						"v6_z_amp_1",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_density_line_unpack",
						5
					],
					"destination": [
						"v6_z_phase_1",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_phase_1",
						0
					],
					"destination": [
						"v6_z_phase_sig_1",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_phase_sig_1",
						0
					],
					"destination": [
						"v6_z_cycle_1",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_cycle_1",
						0
					],
					"destination": [
						"v6_z_amp_1",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_amp_0",
						0
					],
					"destination": [
						"v6_z_sum_1",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_amp_1",
						0
					],
					"destination": [
						"v6_z_sum_1",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_density_line_unpack",
						6
					],
					"destination": [
						"v6_z_cycle_2",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_density_line_unpack",
						7
					],
					"destination": [
						"v6_z_amp_2",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_density_line_unpack",
						8
					],
					"destination": [
						"v6_z_phase_2",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_phase_2",
						0
					],
					"destination": [
						"v6_z_phase_sig_2",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_phase_sig_2",
						0
					],
					"destination": [
						"v6_z_cycle_2",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_cycle_2",
						0
					],
					"destination": [
						"v6_z_amp_2",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_sum_1",
						0
					],
					"destination": [
						"v6_z_sum_2",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_amp_2",
						0
					],
					"destination": [
						"v6_z_sum_2",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_density_line_unpack",
						9
					],
					"destination": [
						"v6_z_cycle_3",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_density_line_unpack",
						10
					],
					"destination": [
						"v6_z_amp_3",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_density_line_unpack",
						11
					],
					"destination": [
						"v6_z_phase_3",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_phase_3",
						0
					],
					"destination": [
						"v6_z_phase_sig_3",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_phase_sig_3",
						0
					],
					"destination": [
						"v6_z_cycle_3",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_cycle_3",
						0
					],
					"destination": [
						"v6_z_amp_3",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_sum_2",
						0
					],
					"destination": [
						"v6_z_sum_3",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_amp_3",
						0
					],
					"destination": [
						"v6_z_sum_3",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_density_line_unpack",
						12
					],
					"destination": [
						"v6_z_cycle_4",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_density_line_unpack",
						13
					],
					"destination": [
						"v6_z_amp_4",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_density_line_unpack",
						14
					],
					"destination": [
						"v6_z_phase_4",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_phase_4",
						0
					],
					"destination": [
						"v6_z_phase_sig_4",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_phase_sig_4",
						0
					],
					"destination": [
						"v6_z_cycle_4",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_cycle_4",
						0
					],
					"destination": [
						"v6_z_amp_4",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_sum_3",
						0
					],
					"destination": [
						"v6_z_sum_4",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_amp_4",
						0
					],
					"destination": [
						"v6_z_sum_4",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_density_line_unpack",
						15
					],
					"destination": [
						"v6_z_cycle_5",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_density_line_unpack",
						16
					],
					"destination": [
						"v6_z_amp_5",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_density_line_unpack",
						17
					],
					"destination": [
						"v6_z_phase_5",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_phase_5",
						0
					],
					"destination": [
						"v6_z_phase_sig_5",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_phase_sig_5",
						0
					],
					"destination": [
						"v6_z_cycle_5",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_cycle_5",
						0
					],
					"destination": [
						"v6_z_amp_5",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_sum_4",
						0
					],
					"destination": [
						"v6_z_sum_5",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_amp_5",
						0
					],
					"destination": [
						"v6_z_sum_5",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_z_sum_5",
						0
					],
					"destination": [
						"v6_density_line_gain_mul",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_density_line_gain_sig",
						0
					],
					"destination": [
						"v6_density_line_gain_mul",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_final_sum",
						0
					],
					"destination": [
						"v6_density_line_final_sum",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"v6_density_line_gain_mul",
						0
					],
					"destination": [
						"v6_density_line_final_sum",
						1
					]
				}
			}
		],
		"originid": "pat-167",
		"dependency_cache": [
			{
				"name": "multiconvolve~.mxo",
				"type": "iLaX"
			},
			{
				"name": "o.pack.mxo",
				"type": "iLaX"
			},
			{
				"name": "o.route.mxo",
				"type": "iLaX"
			},
			{
				"name": "och.microqiskit.mxo",
				"type": "iLaX"
			},
			{
				"name": "qac_qasm_sender_v1.js",
				"bootpath": "~/QuantumSonification/max",
				"patcherrelativepath": ".",
				"type": "TEXT",
				"implicit": 1
			},
			{
				"name": "qac_wavetable_sender_v1.maxpat",
				"bootpath": "~/QuantumSonification/max",
				"patcherrelativepath": ".",
				"type": "JSON",
				"implicit": 1
			},
			{
				"name": "qmw_compact_state_renderer_v6.js",
				"bootpath": "~/QuantumSonification/max",
				"patcherrelativepath": ".",
				"type": "TEXT",
				"implicit": 1
			},
			{
				"name": "qmw_parameterized_bell_v1.js",
				"bootpath": "~/QuantumSonification/max",
				"patcherrelativepath": ".",
				"type": "TEXT",
				"implicit": 1
			},
			{
				"name": "qmw_pauli_surface_receiver_v1.js",
				"bootpath": "~/QuantumSonification/max",
				"patcherrelativepath": ".",
				"type": "TEXT",
				"implicit": 1
			},
			{
				"name": "qmw_qac_wavetable_designer_v1.js",
				"bootpath": "~/QuantumSonification/max",
				"patcherrelativepath": ".",
				"type": "TEXT",
				"implicit": 1
			},
			{
				"name": "qmw_qasm_rotation_layer_v2.js",
				"bootpath": "~/QuantumSonification/max",
				"patcherrelativepath": ".",
				"type": "TEXT",
				"implicit": 1
			},
			{
				"name": "qmw_qft_spectrum_renderer_v5.js",
				"bootpath": "~/QuantumSonification/max",
				"patcherrelativepath": ".",
				"type": "TEXT",
				"implicit": 1
			},
			{
				"name": "qmw_wavetable_receiver_v4.js",
				"bootpath": "~/QuantumSonification/max",
				"patcherrelativepath": ".",
				"type": "TEXT",
				"implicit": 1
			},
			{
				"name": "qmw_pauli_coherence_v6.js",
				"bootpath": "~/QuantumSonification/max",
				"patcherrelativepath": ".",
				"type": "TEXT",
				"implicit": 1
			}
		],
		"autosave": 0
	}
}
