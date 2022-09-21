
## Gloomhaven Mercenary Randomizer

**Overview**
Creates an arbitrary number of random mercenaries in the form of modded YAML files that can be imported into Gloomhaven Digital as a mod.
This repository does not contain any actual Gloomhaven Digital data files.
In order to use the scripts in this repository, you must already own a copy of Gloomhaven Digital.

**Spoiler Alert:**
- The scripts in this repository access all available Gloomhaven and Jaws of the Lion mercenaries and their respective cards on the user's local machine.
- Using these scripts to create a random mercenary will definitely spoil mercenaries and cards that are unlocked later in the game.
- These scripts do not create any item, storyline, or scenario spoilers.
- The documentation for these scripts is occasionally vague for the purpose of avoiding spoilers.
- Due to the nature of these scripts and Gloomhaven data files in general, certain lines of code in this repository contain mercenary and card spoilers.
## Preparing the Environment

**Building the Cache**

This repository does not contain any Gloomhaven data files.
To use it, you must first export the YML data files from Gloomhaven.
To do this, start Gloomhaven. From the main menu select: `Extras -> Modding -> Export YML`
Keep note of the path the YML files are exported to.

A cache must then be created using `buildCache.py`:
`python buildCache.py -ep PATH_TO_GLOOMHAVEN_YML_EXPORT`
If Jaws of the Lion is installed, instead run:
`python buildCache.py -ep PATH_TO_GLOOMHAVEN_YML_EXPORT -jotl`

This creates a directory called "cache" in the same folder the script is running in.
This cache directory contains a sanitized copy of all relevant Gloomhaven data files.
Sanitized in that the original files contain quirks that make them incompatible with YML parsing libraries.
The cache only needs to be built once.

**Preparing a Mod**

Next, a Gloomhaven mod directory must be created. This is the folder where the game stores and looks for mods.
The location of the Gloomhaven mod directory will be different depending on the local environment. It can be changed from inside Gloomhaven.
To do this, start Gloomhaven. From the main menu select:
`Extras -> Modding -> Manage Mods -> Change Mod Directory`

Finally, a Gloomhaven mod must be created. This is where the actual modded files will be written. Many randomized mercenaries can be created in a single mod, but subsequent batches of random mercenaries must be created in separate mods.
To do this, start Gloomhaven. From the main menu select:
`Extras -> Modding -> Manage Mods -> Create New Mod`
Keep a note of the path to the mod directory and the specific mod.
## Creating Random Mercenaries

**Basic Usage**
`python randomMerc.py -mp PATH_TO_GLOOMHAVEN_MOD -nm NUM_MERCS`

Example:
`python randomMerc.py -mp C:\GloomhavenMods\Random -nm 4`
This will create 4 new mercenaries and all of their ability cards at `C:\GloomhavenMods\Random\ModdedYML`
This also appends description and other written information to the LangUpdate.csv file at `C:\GloomhavenMods\Random\LangUpdates\LangUpdate.csv`

To play with the random mercenaries, a custom ruleset must be created in Gloomhaven.
To do this, start Gloomhaven. From the main menu select:
`Extras -> Modding -> Custom Rulesets`
Create a new ruleset. Select the mod you created. Compile the ruleset. Then select Play and start a new campaign.

**Optional Arguments**
`python randomMerc.py -mp MOD_PATH -nm NUM_MERCS -jotl -hs NUM_CARDS -pp NUM_PERKS -hp NUM_HP -hi NUM_INCREASE -lc NUM_CARDS -am NUM_AMALGAMS`
-  `-jotl` || `--jawsofthelion`
	- Supplying this flag will put Jaws of the Lion mercenaries and ability cards into the card and character model pools.
		-  `python randomMerc.py -mp C:\GloomhavenMods\Random -nm 4 -jotl`
-  `-hs NUM_CARDS` || `--handsize NUM_CARDS`
	- Sets a fixed hand size or range of hand sizes to apply to created mercenaries.
	- If not supplied, all mercenary hand sizes will be 12 by default.
	-  `NUM_CARDS` is exactly one or two integers representing either the fixed hand size or min and max (inclusive) hand sizes.
		-  `python randomMerc.py -mp C:\GloomhavenMods\Random -nm 4 -hs 11`
		-  `python randomMerc.py -mp C:\GloomhavenMods\Random -nm 4 -hs 8 14`
-  `-pp NUM_PERKS` || `--perkpoint NUM_PERKS`
	- Sets a fixed number or range of perk unlocks to apply to created mercenaries.
	- If not supplied, all mercenaries will have 11 perk unlocks by default.
	-  `NUM_PERKS` is exactly one or two integers representing either the fixed number or min and max (inclusive) range of perk unlocks.
		-  `python randomMerc.py -mp C:\GloomhavenMods\Random -nm 4 -pp 11`
		-  `python randomMerc.py -mp C:\GloomhavenMods\Random -nm 4 -pp 8 14`
-  `-hp NUM_HP` || `--hitpoints NUM_HP`
	- Sets a fixed number or range of starting hitpoints to apply to created mercenaries.
	- If not supplied, all mercenaries will start with 10 hitpoints.
	-  `NUM_HP` is exactly one or two integers representing either the fixed hitpoints or min and max (inclusive) range of hitpoints.
		-  `python randomMerc.py -mp C:\GloomhavenMods\Random -nm 4 -hp 15`
		-  `python randomMerc.py -mp C:\GloomhavenMods\Random -nm 4 -hp 6 13`
-  `-hi NUM_INCREASE` || `--hpincrease NUM_INCREASE`
	- Sets a fixed number or range of numbers that define mercenary health tables (hitpoints at levels greater than 1).
	- If not supplied, all mercenaries gain 1.5 hitpoints (rounded up) per level.
	-  `NUM_INCREASE` is exactly one or two floats representing either the fixed hitpoints increase amount or min and max range of hitpoints increase.
		-  `python randomMerc.py -mp C:\GloomhavenMods\Random -nm 4 -hi 1.85`
		-  `python randomMerc.py -mp C:\GloomhavenMods\Random -nm 4 -hi 1.25 3.14`
-  `-lc NUM_CARDS` || `--levelcards NUM_CARDS`
	- The number of new cards available to choose from when leveling up.
	- If not supplied, all mercenaries will have two new cards to choose from when leveling up (same as regular Gloomhaven).
	-  `NUM_CARDS` is the number of cards to make available to choose from.
		-  `python randomMerc.py -mp C:\GloomhavenMods\Random -nm 4 -lc 5`
-  `-am NUM_AMALGAMS` || `--amalgam NUM_AMALGAMS`
	- Supplying this flag will set "Amalgam" mode for the first `NUM_AMALGAMS` created mercenaries.
	- Created ability cards will be "amalgams" of random top and bottom cards from the appropriate level bracket, with random initiatives.
		- For example, a card might be the top half of a Brute card and the bottom half of a Cragheart card.
	- If not supplied, all mercenaries will have random card pools of actual existing Gloomhaven cards.
	-  `NUM_AMALGAMS` is an optional integer representing the number of "amalgam" mercenaries to create. If `-am` is present but `NUM_AMALGAMS` is not supplied, all created mercenaries will be "amalgams".
		-  `python randomMerc.py -mp C:\GloomhavenMods\Random -nm 4 -am`
		-  `python randomMerc.py -mp C:\GloomhavenMods\Random -nm 4 -am 2`

## Further Reading
**What is randomized**
- Mercenary Models
	- Chosen from the currently available mercenary models.
- Mercenary Class Names
	- Chosen from a limited list of adjectives and nouns.
	- "Amalgam" mercenaries have an underscore in their name; normal random mercenaries do not.
		- For example, `Slim_Dude` is an amalgam, `GrossMage` is a normal random mercenary.
- Hand Sizes
	- Default behavior is to use a hand size of 10 for all mercenaries.
	- Optionally can create Hand Sizes in a user-specified number or range (see Optional Argument `-hs`).
- Card Pools
	- Available cards at each level are chosen by picking random cards of that level from all Gloomhaven mercenaries.
	- Optionally can use "amalgam" mode to create card pools from random top and bottom halves of cards (see Optional Argument `-am`).
- Starting Hitpoints
	- Default behavior is to give each Mercenary 10 hitpoints at level 1.
	- Optionally can give each Mercenary a user-specified number or range of starting hitpoints (see Optional Argument `-hp`).
- Health Tables
	- Default behavior is for each Mercenary to gain 1.5 hitpoints per level.
	- Optionally can give each Mercenary a user-specified number or range of hitpoint increases (see Optional Argument `-hs`).
- Random Perk Point unlocks
	- Default behavior is to give each Mercenary 11 random Perk Point unlocks.
	- Optionally can give each Mercenary a user-specified number or range of Perk Point unlocks (see Optional Argument `-pp`).

**Currently unsupported features**
- Custom mercenary models
	- Gloomhaven itself does not officially support this feature; out of scope.
- "True Random" Card Pools
	- Each card is completely new, generated on the spot using known Gloomhaven card "morphemes" or a machine learning approach; implementation TBD.
- Random Enemies
	- Enemy ability cards can in theory be shuffled as well; implementation TBD.
- Random Scenarios
	- Either shuffle the Scenarios themselves or create novel scenarios using a direct algorithm or machine learning approach; implementation TBD.

**Known issues and fixes**
- Music Note's special signature cards don't seem to work. The card gets played correctly, but the effect does not apply.
	- Patch: Replace all offending card halves with a random known-good card half from that card's level bracket; remove from pool entirely in Amalgam mode.
	- Notes: It is probably possible to make them work correctly; actual fix TBD.
- Two Minis' special signature cards have no effect. This is expected, but is undesirable.
	- Patch: Replace all offending card halves with a random known-good card half from that card's level bracket; remove from pool entirely in Amalgam mode.
	- Notes: These cards probably function as intended IF the random mercenary is made to function like Two Minis (a certain start of scenario effect unique to that mercenary).
- Angry Face's special signature cards are slightly broken. They apply correctly at first, but if cancelled they apply to the mercenary that played the card rather than being discarded.
	- Patch: Replace all offending card halves with a random known-good card half from that card's level bracket; remove from pool entirely in Amalgam mode.
- Some animations are broken in game. This is likely a result of telling the game to play special mercenary-specific animations on different mercenary models.
	- Notes: The broken animations appear to fail gracefully, in that they do not lead to crashes or errors. This may not be universally true.
