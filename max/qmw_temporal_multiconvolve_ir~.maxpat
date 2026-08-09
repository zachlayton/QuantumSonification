{
	"patcher" : 	{
		"fileversion" : 1,
		"appversion" : 		{
			"major" : 9,
			"minor" : 0,
			"revision" : 5,
			"architecture" : "x64",
			"modernui" : 1
		}
,
		"classnamespace" : "box",
		"rect" : [ 305.0, 148.0, 920.0, 620.0 ],
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"comment" : "IR morph 0..1",
					"id" : "obj-4",
					"index" : 1,
					"maxclass" : "inlet",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 81.0, 35.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"comment" : "",
					"id" : "obj-3",
					"index" : 2,
					"maxclass" : "outlet",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 215.0, 571.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"comment" : "",
					"id" : "obj-2",
					"index" : 1,
					"maxclass" : "outlet",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 95.0, 571.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "in_audio",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ -6.0, 29.0, 25.0, 22.0 ],
					"text" : "in~"
				}

			}
, 			{
				"box" : 				{
					"comment" : "IR morph 0..1",
					"id" : "in_morph",
					"index" : 2,
					"maxclass" : "inlet",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 330.0, 55.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"comment" : "wet gain 0..1",
					"id" : "in_wet",
					"index" : 3,
					"maxclass" : "inlet",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 610.0, 55.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 95.0, 20.0, 430.0, 20.0 ],
					"text" : "QMW temporal click → self-contained quantum IR convolution"
				}

			}
, 			{
				"box" : 				{
					"id" : "buffer_a",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "float", "bang" ],
					"patching_rect" : [ 40.0, 145.0, 298.0, 22.0 ],
					"text" : "buffer~ #0_qtm_ir_A @samps 262144 @channels 2"
				}

			}
, 			{
				"box" : 				{
					"id" : "buffer_b",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "float", "bang" ],
					"patching_rect" : [ 355.0, 145.0, 298.0, 22.0 ],
					"text" : "buffer~ #0_qtm_ir_B @samps 262144 @channels 2"
				}

			}
, 			{
				"box" : 				{
					"id" : "loadbang",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"patching_rect" : [ 690.0, 55.0, 60.0, 22.0 ],
					"text" : "loadbang"
				}

			}
, 			{
				"box" : 				{
					"id" : "read_a",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 40.0, 95.0, 600.0, 22.0 ],
					"text" : "read /Users/zlayton/QuantumSonification/algebraic_surfaces/tanglecube_v1/living/state_000001/modal_ir.wav"
				}

			}
, 			{
				"box" : 				{
					"id" : "read_b",
					"linecount" : 3,
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 388.0, 39.0, 495.0, 49.0 ],
					"text" : "read /Users/zlayton/QuantumSonification/algebraic_surfaces/heart_v1/living/state_000001/ir_surface_laplacian_r000001.wav"
				}

			}
, 			{
				"box" : 				{
					"id" : "ready_a",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "bang", "bang" ],
					"patching_rect" : [ 680.0, 145.0, 45.0, 22.0 ],
					"text" : "t b b"
				}

			}
, 			{
				"box" : 				{
					"id" : "ready_b",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "bang", "bang" ],
					"patching_rect" : [ 740.0, 145.0, 45.0, 22.0 ],
					"text" : "t b b"
				}

			}
, 			{
				"box" : 				{
					"id" : "set_a_l",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 40.0, 225.0, 155.0, 22.0 ],
					"text" : "set 1 1 #0_qtm_ir_A 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "set_a_r",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 205.0, 225.0, 155.0, 22.0 ],
					"text" : "set 1 2 #0_qtm_ir_A 2"
				}

			}
, 			{
				"box" : 				{
					"id" : "set_b_l",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 370.0, 225.0, 155.0, 22.0 ],
					"text" : "set 1 3 #0_qtm_ir_B 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "set_b_r",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 535.0, 225.0, 155.0, 22.0 ],
					"text" : "set 1 4 #0_qtm_ir_B 2"
				}

			}
, 			{
				"box" : 				{
					"id" : "convolver",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 4,
					"outlettype" : [ "signal", "signal", "signal", "signal" ],
					"patching_rect" : [ 40.0, 280.0, 185.0, 22.0 ],
					"text" : "multiconvolve~ 1 4 medium"
				}

			}
, 			{
				"box" : 				{
					"id" : "morph_default",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 330.0, 95.0, 78.0, 22.0 ],
					"text" : "loadmess 0."
				}

			}
, 			{
				"box" : 				{
					"id" : "morph_clip",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 330.0, 280.0, 68.0, 22.0 ],
					"text" : "clip 0. 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "morph_trigger",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "float", "float" ],
					"patching_rect" : [ 330.0, 315.0, 42.0, 22.0 ],
					"text" : "t f f"
				}

			}
, 			{
				"box" : 				{
					"id" : "morph_inverse",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 280.0, 350.0, 43.0, 22.0 ],
					"text" : "!- 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "sqrt_a",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 260.0, 385.0, 92.0, 22.0 ],
					"text" : "expr sqrt($f1)"
				}

			}
, 			{
				"box" : 				{
					"id" : "sqrt_b",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 380.0, 350.0, 92.0, 22.0 ],
					"text" : "expr sqrt($f1)"
				}

			}
, 			{
				"box" : 				{
					"id" : "sig_a",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 280.0, 420.0, 35.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"id" : "sig_b",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 400.0, 385.0, 35.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"id" : "a_l_gain",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 40.0, 455.0, 35.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"id" : "a_r_gain",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 90.0, 455.0, 35.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"id" : "b_l_gain",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 145.0, 455.0, 35.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"id" : "b_r_gain",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 195.0, 455.0, 35.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"id" : "sum_l",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 60.0, 495.0, 35.0, 22.0 ],
					"text" : "+~"
				}

			}
, 			{
				"box" : 				{
					"id" : "sum_r",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 165.0, 495.0, 35.0, 22.0 ],
					"text" : "+~"
				}

			}
, 			{
				"box" : 				{
					"id" : "wet_default",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 610.0, 95.0, 92.0, 22.0 ],
					"text" : "loadmess 0.35"
				}

			}
, 			{
				"box" : 				{
					"id" : "wet_clip",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 610.0, 280.0, 68.0, 22.0 ],
					"text" : "clip 0. 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "wet_pack",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 610.0, 315.0, 75.0, 22.0 ],
					"text" : "pack 0. 30"
				}

			}
, 			{
				"box" : 				{
					"id" : "wet_line",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 610.0, 350.0, 40.0, 22.0 ],
					"text" : "line~"
				}

			}
, 			{
				"box" : 				{
					"id" : "wet_l",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 60.0, 535.0, 35.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"id" : "wet_r",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 165.0, 535.0, 35.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"id" : "out_l",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 60.0, 575.0, 32.0, 22.0 ],
					"text" : "out~"
				}

			}
, 			{
				"box" : 				{
					"id" : "out_r",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 165.0, 575.0, 32.0, 22.0 ],
					"text" : "out~"
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "sum_l", 0 ],
					"source" : [ "a_l_gain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sum_r", 0 ],
					"source" : [ "a_r_gain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sum_l", 1 ],
					"source" : [ "b_l_gain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sum_r", 1 ],
					"source" : [ "b_r_gain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ready_a", 0 ],
					"source" : [ "buffer_a", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ready_b", 0 ],
					"source" : [ "buffer_b", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "a_l_gain", 0 ],
					"source" : [ "convolver", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "a_r_gain", 0 ],
					"source" : [ "convolver", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "b_l_gain", 0 ],
					"source" : [ "convolver", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "b_r_gain", 0 ],
					"source" : [ "convolver", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "convolver", 0 ],
					"source" : [ "in_audio", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "morph_clip", 0 ],
					"source" : [ "in_morph", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "wet_clip", 0 ],
					"source" : [ "in_wet", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "read_a", 0 ],
					"order" : 1,
					"source" : [ "loadbang", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "read_b", 0 ],
					"order" : 0,
					"source" : [ "loadbang", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "morph_trigger", 0 ],
					"source" : [ "morph_clip", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "morph_clip", 0 ],
					"source" : [ "morph_default", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sqrt_a", 0 ],
					"source" : [ "morph_inverse", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "morph_inverse", 0 ],
					"source" : [ "morph_trigger", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sqrt_b", 0 ],
					"source" : [ "morph_trigger", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "convolver", 0 ],
					"source" : [ "obj-4", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "buffer_a", 0 ],
					"source" : [ "read_a", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "buffer_b", 0 ],
					"source" : [ "read_b", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "set_a_l", 0 ],
					"source" : [ "ready_a", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "set_a_r", 0 ],
					"source" : [ "ready_a", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "set_b_l", 0 ],
					"source" : [ "ready_b", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "set_b_r", 0 ],
					"source" : [ "ready_b", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "convolver", 0 ],
					"source" : [ "set_a_l", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "convolver", 0 ],
					"source" : [ "set_a_r", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "convolver", 0 ],
					"source" : [ "set_b_l", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "convolver", 0 ],
					"source" : [ "set_b_r", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "a_l_gain", 1 ],
					"order" : 1,
					"source" : [ "sig_a", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "a_r_gain", 1 ],
					"order" : 0,
					"source" : [ "sig_a", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "b_l_gain", 1 ],
					"order" : 1,
					"source" : [ "sig_b", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "b_r_gain", 1 ],
					"order" : 0,
					"source" : [ "sig_b", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sig_a", 0 ],
					"source" : [ "sqrt_a", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sig_b", 0 ],
					"source" : [ "sqrt_b", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "wet_l", 0 ],
					"source" : [ "sum_l", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "wet_r", 0 ],
					"source" : [ "sum_r", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "wet_pack", 0 ],
					"source" : [ "wet_clip", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "wet_clip", 0 ],
					"source" : [ "wet_default", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-2", 0 ],
					"order" : 0,
					"source" : [ "wet_l", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "out_l", 0 ],
					"order" : 1,
					"source" : [ "wet_l", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "wet_l", 1 ],
					"order" : 1,
					"source" : [ "wet_line", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "wet_r", 1 ],
					"order" : 0,
					"source" : [ "wet_line", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "wet_line", 0 ],
					"source" : [ "wet_pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-3", 0 ],
					"order" : 0,
					"source" : [ "wet_r", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "out_r", 0 ],
					"order" : 1,
					"source" : [ "wet_r", 0 ]
				}

			}
 ],
		"originid" : "pat-1526"
	}

}
