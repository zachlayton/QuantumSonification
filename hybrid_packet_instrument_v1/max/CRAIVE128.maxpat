{
	"patcher" : 	{
		"fileversion" : 1,
		"appversion" : 		{
			"major" : 8,
			"minor" : 3,
			"revision" : 0,
			"architecture" : "x64",
			"modernui" : 1
		}
,
		"classnamespace" : "box",
		"rect" : [ 58.0, 119.0, 1541.0, 713.0 ],
		"bglocked" : 0,
		"openinpresentation" : 0,
		"default_fontsize" : 12.0,
		"default_fontface" : 0,
		"default_fontname" : "Arial",
		"gridonopen" : 1,
		"gridsize" : [ 15.0, 15.0 ],
		"gridsnaponopen" : 1,
		"objectsnaponopen" : 1,
		"statusbarvisible" : 2,
		"toolbarvisible" : 1,
		"lefttoolbarpinned" : 0,
		"toptoolbarpinned" : 0,
		"righttoolbarpinned" : 0,
		"bottomtoolbarpinned" : 0,
		"toolbars_unpinned_last_save" : 0,
		"tallnewobj" : 0,
		"boxanimatetime" : 200,
		"enablehscroll" : 1,
		"enablevscroll" : 1,
		"devicewidth" : 0.0,
		"description" : "",
		"digest" : "",
		"tags" : "",
		"style" : "",
		"subpatcher_template" : "",
		"assistshowspatchername" : 0,
		"boxes" : [ 			{
				"box" : 				{
					"id" : "obj-7",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 350.0, 250.0, 206.0, 22.0 ],
					"presentation_linecount" : 2,
					"text" : "/speaker/[94-123]/direction/xyz -1 0 0"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-6",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 335.0, 235.0, 199.0, 22.0 ],
					"presentation_linecount" : 2,
					"text" : "/speaker/[62-85]/direction/xyz 0 -1 0"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-5",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 320.0, 220.0, 195.0, 22.0 ],
					"text" : "/speaker/[24-54]/direction/xyz 1 0 0"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-4",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 305.0, 205.0, 189.0, 22.0 ],
					"text" : "/speaker/[1-18]/direction/xyz 0 1 0"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-12",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 594.0, 654.0, 319.0, 20.0 ],
					"text" : "Ceiling Speaker Coordinates - to be considered separately"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-3",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 214.0, 656.0, 365.0, 22.0 ],
					"text" : "-2.3 4 2.67 2.3 4 2.67 -2.3 0 2.67 2.3 0 2.67 -2.3 -4 2.67 2.3 -4 2.67"
				}

			}
, 			{
				"box" : 				{
					"comment" : "",
					"id" : "obj-11",
					"index" : 1,
					"maxclass" : "outlet",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 648.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"comment" : "",
					"id" : "obj-10",
					"index" : 1,
					"maxclass" : "inlet",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"patching_rect" : [ 58.0, 62.0, 24.0, 24.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-9",
					"maxclass" : "button",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 30.0, 62.0, 24.0, 24.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-2",
					"linecount" : 29,
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 735.0, 151.0, 593.0, 409.0 ],
					"text" : "/speakers/xyz 1.526026 -6.014338 -0. 1.24843 -6.014338 -0. 0.970833 -6.014338 -0. 0.693237 -6.014338 -0. 0.41564 -6.014338 -0. 0.138044 -6.014338 -0. -0.139553 -6.014338 -0. -0.417149 -6.014338 -0. -0.694745 -6.014338 -0. -0.972342 -6.014338 -0. -1.249938 -6.014338 -0. -1.527535 -6.014338 -0. -1.805131 -6.014338 -0. -2.082727 -6.014338 -0. -2.360324 -6.014338 -0. -2.63792 -6.014338 -0. -2.915517 -6.014338 -0. -3.193113 -6.014338 -0. -3.778731 -5.963043 -0. -4.283132 -5.757863 -0. -4.693491 -5.3817 -0. -4.95 -4.996987 -0. -5.078204 -4.569529 -0. -5.078204 -4.137796 -0. -5.078204 -3.851989 -0. -5.078204 -3.566181 -0. -5.078204 -3.280374 -0. -5.078204 -2.994566 -0. -5.078204 -2.708759 -0. -5.078204 -2.422951 -0. -5.078204 -2.137144 -0. -5.078204 -1.851336 -0. -5.078204 -1.565529 -0. -5.078204 -1.279722 -0. -5.078204 -0.993914 -0. -5.078204 -0.708107 -0. -5.078204 -0.422299 -0. -5.078204 -0.136492 -0. -5.078204 0.149316 -0. -5.078204 0.435123 -0. -5.078204 0.72093 -0. -5.078204 1.006738 -0. -5.078204 1.292545 -0. -5.078204 1.578353 -0. -5.078204 1.86416 -0. -5.078204 2.15 -0. -5.078204 2.435775 -0. -5.078204 2.721582 -0. -5.078204 3.00739 -0. -5.078204 3.293197 -0. -5.078204 3.579005 -0. -5.078204 3.864812 -0. -5.078204 4.15062 -0. -5.078204 4.466939 -0. -5.001262 4.783258 -0. -4.890122 5.116675 -0. -4.667844 5.3817 -0. -4.437016 5.655273 -0. -4.189091 5.826256 -0. -3.864223 5.954494 -0. -3.505158 5.992965 -0. -3.201662 6.022887 -0. -2.92493 6.022887 -0. -2.648197 6.022887 -0. -2.371464 6.022887 -0. -2.094731 6.022887 -0. -1.817999 6.022887 -0. -1.541266 6.022887 -0. -1.264533 6.022887 -0. -0.9878 6.022887 -0. -0.711067 6.022887 -0. -0.434335 6.022887 -0. -0.157602 6.022887 -0. 0.119131 6.022887 -0. 0.395864 6.022887 -0. 0.672596 6.022887 -0. 0.949329 6.022887 -0. 1.226062 6.022887 -0. 1.502795 6.022887 -0. 1.779527 6.022887 -0. 2.05626 6.022887 -0. 2.332993 6.022887 -0. 2.609725 6.022887 -0. 2.886458 6.022887 -0. 3.163191 6.022887 -0. 3.462412 6.014338 -0. 3.821477 5.954494 -0. 4.103599 5.792059 -0. 4.411369 5.621076 -0. 4.650746 5.37315 -0. 4.847377 5.116675 -0. 4.95 4.808906 -0. 5.044007 4.484037 -0. 5.052557 4.14207 -0. 5.052557 3.856411 -0. 5.052557 3.57075 -0. 5.052557 3.28509 -0. 5.052557 3. -0. 5.052557 2.71377 -0. 5.052557 2.42811 -0. 5.052557 2.14245 -0. 5.052557 1.85679 -0. 5.052557 1.57113 -0. 5.052557 1.28547 -0. 5.052557 0.99981 -0. 5.052557 0.71415 -0. 5.052557 0.42849 -0. 5.052557 0.14283 -0. 5.052557 -0.14283 -0. 5.052557 -0.42849 -0. 5.052557 -0.71415 -0. 5.052557 -0.99981 -0. 5.052557 -1.28547 -0. 5.052557 -1.57113 -0. 5.052557 -1.85679 -0. 5.052557 -2.14245 -0. 5.052557 -2.42811 -0. 5.052557 -2.71377 -0. 5.052557 -3. -0. 5.052557 -3.28509 -0. 5.052557 -3.57075 -0. 5.052557 -3.856411 -0. 5.052557 -4.14207 -0. 5.01 -4.578078 -0. 4.864475 -5.014085 -0. 4.676394 -5.3817 -0. 4.240386 -5.749313 -0. 3.770182 -5.971592 -0., bang"
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "obj-2", 0 ],
					"source" : [ "obj-10", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-11", 0 ],
					"source" : [ "obj-2", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-11", 0 ],
					"source" : [ "obj-4", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-11", 0 ],
					"source" : [ "obj-5", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-11", 0 ],
					"source" : [ "obj-6", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-11", 0 ],
					"source" : [ "obj-7", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-2", 0 ],
					"order" : 0,
					"source" : [ "obj-9", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-4", 0 ],
					"order" : 4,
					"source" : [ "obj-9", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-5", 0 ],
					"order" : 3,
					"source" : [ "obj-9", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-6", 0 ],
					"order" : 2,
					"source" : [ "obj-9", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-7", 0 ],
					"order" : 1,
					"source" : [ "obj-9", 0 ]
				}

			}
 ]
	}

}
