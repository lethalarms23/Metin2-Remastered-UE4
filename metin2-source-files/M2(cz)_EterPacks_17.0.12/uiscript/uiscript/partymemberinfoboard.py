import uiScriptLocale
import app

ROOT = "d:/ymir work/ui/public/"

if app.ENABLE_PARTY_LEADER_RENEWAL:
	window = {
		"name" : "PartyMemeberInfoBoard",

		"x" : 0,
		"y" : 0,

		"width" : 106,
		"height" : 36,

		"children" :
		(

			{
				"name" : "StateButton",
				"type" : "button",

				"x" : 0,
				"y" : 0,

				"default_image" : "d:/ymir work/ui/game/windows/party_state_normal_01.sub",
				"over_image" : "d:/ymir work/ui/game/windows/party_state_normal_02.sub",
				"down_image" : "d:/ymir work/ui/game/windows/party_state_normal_03.sub",
			},

			{
				"name" : "NameSlot",
				"type" : "bar",
				"style" : ("not_pick",),

				"x" : 22,
				"y" : 0,
				"width" : 84,
				"height" : 17,
				"color" : 0x99000000,

				"children" :
				(
					{
						"name" : "NamePrint",
						"type" : "text",

						"x" : 3,
						"y" : 2,

						"text" : uiScriptLocale.PARTY_MEMBER_INFO_NAME,
					},
				),
			},

			{
				"name" : "Gauge",
				"type" : "gauge",
				"style" : ("not_pick",),

				"x" : 22,
				"y" : 17,
				"width" : 84,
				"color" : "red",
			},
			## 경험치 보너스
			{
				"name" : "ExperienceImage",
				"type" : "image",

				"x" : 22,
				"y" : 24,

				"image" : "d:/ymir work/ui/game/windows/party_affect_experience.sub",
			},
			## 어태커 보너스
			{
				"name" : "AttackerImage",
				"type" : "image",

				"x" : 34,
				"y" : 24,

				"image" : "d:/ymir work/ui/game/windows/party_affect_attackgrade.sub",
			},
			## 버서커 보너스
			{
				"name" : "TimeBonusImage",
				"type" : "image",

				"x" : 46,
				"y" : 24,

				"image" : "d:/ymir work/ui/game/windows/party_affect_timebonus.sub",
			},
			## 탱커 보너스
			{
				"name" : "DefenderImage",
				"type" : "image",

				"x" : 58,
				"y" : 24,

				"image" : "d:/ymir work/ui/game/windows/party_affect_defencegrade.sub",
			},
			## 버퍼 보너스
			{
				"name" : "BufferImage",
				"type" : "image",

				"x" : 70,
				"y" : 24,

				"image" : "d:/ymir work/ui/game/windows/party_affect_bufferbonus.sub",
			},
			## 스킬마스터 보너스
			{
				"name" : "SkillMasterImage",
				"type" : "image",

				"x" : 82,
				"y" : 24,

				"image" : "d:/ymir work/ui/game/windows/party_affect_skillmasterbonus.sub",
			},
			## 디팬더 보너스
			{
				"name" : "RegenBonus",
				"type" : "image",

				"x" : 94,
				"y" : 24,

				"image" : "d:/ymir work/ui/game/windows/party_affect_regenbonus.sub",
			},
			
			{
				"name" : "IncreaseArea150",
				"type" : "image",

				"x" : 82,
				"y" : 24,

				"image" : "d:/ymir work/ui/game/windows/party_affect_increasearea_150.sub",
			},
			{
				"name" : "IncreaseArea200",
				"type" : "image",

				"x" : 94,
				"y" : 24,

				"image" : "d:/ymir work/ui/game/windows/party_affect_increasearea_200.sub",
			},

		),
	}
else:
	window = {
		"name" : "PartyMemeberInfoBoard",

		"x" : 0,
		"y" : 0,

		"width" : 106,
		"height" : 36,

		"children" :
		(

			{
				"name" : "StateButton",
				"type" : "button",

				"x" : 0,
				"y" : 0,

				"default_image" : "d:/ymir work/ui/game/windows/party_state_normal_01.sub",
				"over_image" : "d:/ymir work/ui/game/windows/party_state_normal_02.sub",
				"down_image" : "d:/ymir work/ui/game/windows/party_state_normal_03.sub",
			},

			{
				"name" : "NameSlot",
				"type" : "bar",
				"style" : ("not_pick",),

				"x" : 22,
				"y" : 0,
				"width" : 84,
				"height" : 17,
				"color" : 0x99000000,

				"children" :
				(
					{
						"name" : "NamePrint",
						"type" : "text",

						"x" : 3,
						"y" : 2,

						"text" : uiScriptLocale.PARTY_MEMBER_INFO_NAME,
					},
				),
			},

			{
				"name" : "Gauge",
				"type" : "gauge",
				"style" : ("not_pick",),

				"x" : 22,
				"y" : 17,
				"width" : 84,
				"color" : "red",
			},

			{
				"name" : "ExperienceImage",
				"type" : "image",

				"x" : 22,
				"y" : 24,

				"image" : "d:/ymir work/ui/game/windows/party_affect_experience.sub",
			},
			{
				"name" : "AttackerImage",
				"type" : "image",

				"x" : 34,
				"y" : 24,

				"image" : "d:/ymir work/ui/game/windows/party_affect_attackgrade.sub",
			},
			{
				"name" : "DefenderImage",
				"type" : "image",

				"x" : 46,
				"y" : 24,

				"image" : "d:/ymir work/ui/game/windows/party_affect_defencegrade.sub",
			},
			{
				"name" : "BufferImage",
				"type" : "image",

				"x" : 34,
				"y" : 24,

				"image" : "d:/ymir work/ui/game/windows/party_affect_attackgrade.sub",
			},
			{
				"name" : "SkillMasterImage",
				"type" : "image",

				"x" : 46,
				"y" : 24,

				"image" : "d:/ymir work/ui/game/windows/party_affect_attackgrade.sub",
			},
			{
				"name" : "TimeBonusImage",
				"type" : "image",

				"x" : 58,
				"y" : 24,

				"image" : "d:/ymir work/ui/game/windows/party_affect_timebonus.sub",
			},
			{
				"name" : "RegenBonus",
				"type" : "image",

				"x" : 70,
				"y" : 24,

				"image" : "d:/ymir work/ui/game/windows/party_affect_regenbonus.sub",
			},
			{
				"name" : "IncreaseArea150",
				"type" : "image",

				"x" : 82,
				"y" : 24,

				"image" : "d:/ymir work/ui/game/windows/party_affect_increasearea_150.sub",
			},
			{
				"name" : "IncreaseArea200",
				"type" : "image",

				"x" : 94,
				"y" : 24,

				"image" : "d:/ymir work/ui/game/windows/party_affect_increasearea_200.sub",
			},

		),
	}
