import uiScriptLocale
import app
if app.ENABLE_GUILDRENEWAL_SYSTEM:
    SMALL_VALUE_FILE = "d:/ymir work/ui/public/Parameter_Slot_01.sub"
    LARGE_VALUE_FILE = "d:/ymir work/ui/public/Parameter_Slot_03.sub"
    XLARGE_VALUE_FILE = "d:/ymir work/ui/public/Parameter_Slot_04.sub"

    window = {
	    "name" : "InputDialog",

	    "x" : 0,
	    "y" : 0,

	    "style" : ("movable", "float",),

	    "width" : 230,
	    "height" : 250,

	    "children" :
	    (
		    {
			    "name" : "Board",
			    "type" : "board_with_titlebar",

			    "x" : 0,
			    "y" : 0,

			    "width" : 230,
			    "height" : 250,

			    "title" : uiScriptLocale.GUILD_WAR_ACCEPT,

			    "children" :
			    (
				    ## 상대길드
				    {
					    "name" : "InputName", "type" : "text", "x" : 23, "y" : 40, "text" : uiScriptLocale.GUILD_WAR_ENEMY,
					    "children" :
					    (
						    {
							    "name" : "InputSlot", "type" : "image", "x" : 64, "y" : -3, "width" : 130, "height" : 18, "image" : XLARGE_VALUE_FILE,
							    "children" :
							    (
								    {"name":"InputValue","type":"text","text":"","x":0,"y":0, "all_align":"center"},
							    ),
						    },
					    ),
				    },
				    ## 전투 방식
				    {
					    "name" : "WarType", "type" : "text", "x" : 23, "y" : 73, "text" : uiScriptLocale.GUILD_WAR_BATTLE_TYPE,
					    "children" :
					    (
						    {
							    "name" : "WarTypeSlot", "type" : "image", "x" : 64, "y" : -3, "width" : 130, "height" : 18, "image" : XLARGE_VALUE_FILE,
							    "children" :
							    (
								    {"name":"WarTypeName","type":"text","text":"","x":0,"y":0, "all_align":"center"},
							    ),
						    },
					    ),
				    },
				    ## 선승제
				    {
					    "name" : "WarWinType", "type" : "text", "x" : 23, "y" : 105, "text" : uiScriptLocale.GUILD_WAR_WIN,
					    "children" :
					    (
						    {
							    "name" : "WarWinTypeSlot", "type" : "image", "x" : 64, "y" : -3, "width" : 130, "height" : 18, "image" : XLARGE_VALUE_FILE,
							    "children" :
							    (
								    {"name":"WarWinTypeName","type":"text","text":"","x":0,"y":0, "all_align":"center"},
							    ),
						    },
					    ),
				    },
				    ## 획득 점수
				    {
					    "name" : "WarScore", "type" : "text", "x" : 23, "y" : 140, "text" : uiScriptLocale.GUILD_WAR_GAINSCORE,
					    "children" :
					    (
						    {
							    "name" : "WarScoreSlot", "type" : "image", "x" : 64, "y" : -3, "width" : 130, "height" : 18, "image" : XLARGE_VALUE_FILE,
							    "children" :
							    (
								    {"name":"WarScoreName","type":"text","text":"","x":0,"y":0, "all_align":"center"},
							    ),
						    },
					    ),
				    },
				    ## 경기 시간
				    {
					    "name" : "WarTime", "type" : "text", "x" : 23, "y" : 175, "text" : uiScriptLocale.GUILD_WAR_GAMETIME,
					    "children" :
					    (
						    {
							    "name" : "WarTimeSlot", "type" : "image", "x" : 64, "y" : -3, "width" : 130, "height" : 18, "image" : XLARGE_VALUE_FILE,
							    "children" :
							    (
								    {"name":"WarTimeName","type":"text","text":"","x":0,"y":0, "all_align":"center"},
							    ),
						    },
					    ),
				    },
    				
				    ### 참가 인원
				    #{
					    #"name" : "WarMemberType", "type" : "text", "x" : 23, "y" : 210, "text" : uiScriptLocale.GUILD_WAR_JOINMEMBER,
					    #"children" :
					    #(
						    #{
							    #"name" : "WarMemberSlot", "type" : "image", "x" : 64, "y" : -3, "width" : 130, "height" : 18, "image" : XLARGE_VALUE_FILE,
							    #"children" :
							    #(
								    #{"name":"WarMemberName","type":"text","text":"","x":0,"y":0, "all_align":"center"},
							    #),
						    #},
					    #),
				    #},
    				
				    ## 확인 취소 버튼
				    {
					    "name" : "AcceptButton",
					    "type" : "button",

					    "x" : - 61 - 5 + 30,
					    "y" : 210,
					    "horizontal_align" : "center",

					    "text" : uiScriptLocale.OK,

					    "default_image" : "d:/ymir work/ui/public/middle_button_01.sub",
					    "over_image" : "d:/ymir work/ui/public/middle_button_02.sub",
					    "down_image" : "d:/ymir work/ui/public/middle_button_03.sub",
				    },
				    {
					    "name" : "CancelButton",
					    "type" : "button",

					    "x" : 5 + 30,
					    "y" : 210,
					    "horizontal_align" : "center",

					    "text" : uiScriptLocale.CANCEL,

					    "default_image" : "d:/ymir work/ui/public/middle_button_01.sub",
					    "over_image" : "d:/ymir work/ui/public/middle_button_02.sub",
					    "down_image" : "d:/ymir work/ui/public/middle_button_03.sub",
				    },
			    ),
		    },
	    ),
    }

else:
    window = {
	    "name" : "InputDialog",

	    "x" : 0,
	    "y" : 0,

	    "style" : ("movable", "float",),

	    "width" : 230,
	    "height" : 130,

	    "children" :
	    (
		    {
			    "name" : "Board",
			    "type" : "board_with_titlebar",

			    "x" : 0,
			    "y" : 0,

			    "width" : 230,
			    "height" : 130,

			    "title" : uiScriptLocale.GUILD_WAR_ACCEPT,

			    "children" :
			    (
				    ## Input Slot
				    {
					    "name" : "InputName",
					    "type" : "text",

					    "x" : 15,
					    "y" : 40,

					    "text" : uiScriptLocale.GUILD_WAR_ENEMY,
				    },
				    {
					    "name" : "InputSlot",
					    "type" : "slotbar",

					    "x" : 80,
					    "y" : 37,
					    "width" : 130,
					    "height" : 18,

					    "children" :
					    (
						    {
							    "name" : "InputValue",
							    "type" : "text",

							    "x" : 3,
							    "y" : 3,

							    "width" : 90,
							    "height" : 18,

						    },
					    ),
				    },
				    ## Input Slot
				    {
					    "name" : "GameType", "x" : 15, "y" : 65, "width" : 65+45*4, "height" : 20,
    					
					    "children" :
					    (
						    {"name" : "GameTypeLabel", "type" : "text", "x" : 0, "y" : 3, "text" : uiScriptLocale.GUILD_WAR_BATTLE_TYPE,},
						    {
							    "name" : "NormalButton",
							    "type" : "radio_button",

							    "x" : 65,
							    "y" : 0,

							    "text" : uiScriptLocale.GUILD_WAR_NORMAL,							

							    "default_image" : "d:/ymir work/ui/public/small_button_01.sub",
							    "over_image" : "d:/ymir work/ui/public/small_button_02.sub",
							    "down_image" : "d:/ymir work/ui/public/small_button_03.sub",
						    },
						    {
							    "name" : "WarpButton",
							    "type" : "radio_button",

							    "x" : 65+45*1,
							    "y" : 0,

							    "text" : uiScriptLocale.GUILD_WAR_WARP,
    							
							    "default_image" : "d:/ymir work/ui/public/small_button_01.sub",
							    "over_image" : "d:/ymir work/ui/public/small_button_02.sub",
							    "down_image" : "d:/ymir work/ui/public/small_button_03.sub",
						    },
						    {
							    "name" : "CTFButton",
							    "type" : "radio_button",

							    "x" : 65+45*2,
							    "y" : 0,

							    "text" : uiScriptLocale.GUILD_WAR_CTF,
    							
							    "default_image" : "d:/ymir work/ui/public/small_button_01.sub",
							    "over_image" : "d:/ymir work/ui/public/small_button_02.sub",
							    "down_image" : "d:/ymir work/ui/public/small_button_03.sub",
						    },
					    ),
				    },
				    ## Button
				    {
					    "name" : "AcceptButton",
					    "type" : "button",

					    "x" : - 61 - 5 + 30,
					    "y" : 95,
					    "horizontal_align" : "center",

					    "text" : uiScriptLocale.OK,

					    "default_image" : "d:/ymir work/ui/public/middle_button_01.sub",
					    "over_image" : "d:/ymir work/ui/public/middle_button_02.sub",
					    "down_image" : "d:/ymir work/ui/public/middle_button_03.sub",
				    },
				    {
					    "name" : "CancelButton",
					    "type" : "button",

					    "x" : 5 + 30,
					    "y" : 95,
					    "horizontal_align" : "center",

					    "text" : uiScriptLocale.CANCEL,

					    "default_image" : "d:/ymir work/ui/public/middle_button_01.sub",
					    "over_image" : "d:/ymir work/ui/public/middle_button_02.sub",
					    "down_image" : "d:/ymir work/ui/public/middle_button_03.sub",
				    },
			    ),
		    },
	    ),
    }
