import ghUtils as ghu
import random
import copy
import sys
import argparse
import os

def GetArgs():
    parser = argparse.ArgumentParser(description='Create one or many random Gloomhaven Mercenaries.')
    parser.add_argument('-mp','--modpath',
                       type=str,
                       help='The path to Gloomhaven Mod directory',
                       required=True)
    parser.add_argument('-nm','--nummercs',
                       type=int,
                       help='The number of Mercenaries to create',
                       required=True)
    parser.add_argument('-jotl','--jawsofthelion',
                       type=bool,
                       action=argparse.BooleanOptionalAction,
                       help='If supplied, will use Jaws of the Lion DLC Mercenaries',
                       required=False)
    parser.add_argument('-am','--amalgam',
                       type=int,
                       nargs='?',
                       const=-1,
                       default=argparse.SUPPRESS,
                       help='If supplied, will use "Amalgam" card mode--create cards from random top & bottom halves. Defaults to making all Mercenaries amalgams; supply a number to only make that many amalgams.',
                       required=False)
    parser.add_argument('-lc','--levelcards',
                       type=int,
                       help='The number of cards available on level up',
                       required=False)
    parser.add_argument('-hs','--handsize',
                       type=int,
                       nargs='+',
                       help='Sets the exact number or range of Mercenary Hand Sizes',
                       required=False)
    parser.add_argument('-pp','--perkpoint',
                       type=int,
                       nargs='+',
                       help='Sets the exact number or range of Mercenary Perk Point unlocks',
                       required=False)
    parser.add_argument('-hp','--hitpoints',
                       type=int,
                       nargs='+',
                       help='Sets the exact number or range of Mercenary starting hitpoints; defaults to 10',
                       required=False)
    parser.add_argument('-hi','--hpincrease',
                       type=float,
                       nargs='+',
                       help='Sets the exact number or range that Mercenary hitpoints increase by on level up. Defaults to 1.5',
                       required=False)
    return parser.parse_args()

if __name__ == "__main__":

    if not os.path.exists("cache"):
        sys.exit("You must run buildCache.py before the mercenary randomizer.")

    args = GetArgs()

    modDir = args.modpath
    numCharacters = args.nummercs
    jaws = args.jawsofthelion
    amalgam = args.amalgam
    ths = args.handsize
    tpp = args.perkpoint
    levelCards = args.levelcards
    startHP = args.hitpoints
    hpIncrease = args.hpincrease

    if startHP:
        if type(startHP) is list:
            if len(startHP) == 2:
                startHPMin = startHP[0]
                startHPMax = startHP[1]
            elif len(startHP) == 1:
                startHPMin = startHP[0]
                startHPMax = startHP[0]
            else:
                sys.exit("If supplied, Starting HP must be exactly one or two ints: '-hp 11' or '-hp 6 12' for example")
    else:
        startHPMin = 10
        startHPMax = 10

    if hpIncrease:
        if type(hpIncrease) is list:
            if len(hpIncrease) == 2:
                HPIncreaseMin = startHP[0]
                HPIncreaseMax = startHP[1]
            elif len(hpIncrease) == 1:
                HPIncreaseMin = startHP[0]
                HPIncreaseMax = startHP[0]
            else:
                sys.exit("If supplied, HP Increase must be exactly one or two floats: '-hi 2.5' or '-hp 0.5 2.7' for example")
    else:
        HPIncreaseMin = 1.5
        HPIncreaseMax = 1.5

    if ths:
        if type(ths) is list:
            if len(ths) == 2:
                handSizeMin = min(ths)
                handSizeMax = max(ths)
            elif len(ths) == 1:
                handSizeMin = ths[0]
                handSizeMax = ths[0]
            else:
                sys.exit("Hand Size must be exactly one or two ints: '-hs 10' or '-hs 8 12' for example")
    else:
        handSizeMin = 10
        handSizeMax = 10

    if tpp:
        if type(tpp) is list:
            if len(tpp) == 2:
                perkMin = min(tpp)
                perkMax = max(tpp)
            elif len(tpp) == 1:
                perkMin = tpp[0]
                perkMax = tpp[0]
            else:
                sys.exit("Perk Point Unlocks must be exactly one or two ints: '-pp 10' or '-pp 8 12' for example")
    else:
        perkMin = 11
        perkMax = 11

    if not levelCards:
        levelCards = 2

    if amalgam:
        if amalgam >= numCharacters or amalgam < 0:
            amalgam = numCharacters

    amalgamating = []

    for i in range(numCharacters):
        if i < amalgam:
            amalgamating.append(True)
        else:
            amalgamating.append(False)

    charNames = ghu.MakeManyNames(numCharacters, amalgamating)

    yaml = ghu.StartYaml()

    treasureTable = ghu.LoadTreasureTable("cache/StartingTreasureTable.yml")
    classes = ghu.LoadYMLDir("cache/Global/Character", yaml)
    abilities = ghu.LoadYMLDir("cache/Global/AbilityCard", yaml)
    allPerks = ghu.LoadYMLDir("cache/Global/Perk", yaml)
    if jaws:
        jawsClasses = ghu.LoadYMLDir("cache/DLC_JoTL/Global/Character", yaml)
        jawsAbilities = ghu.LoadYMLDir("cache/DLC_JoTL/Global/AbilityCard", yaml)
        jawsPerks = ghu.LoadYMLDir("cache/DLC_JoTL/Global/Perk", yaml)
        jawsAttackMods = ghu.LoadYMLDir("cache/DLC_JoTL/Global/AttackModifier", yaml)
        for amod in jawsAttackMods:
            ghu.SaveYML("{}/ModdedYML/{}.yml".format(modDir, amod['Name']), amod, yaml)
        classes = classes + jawsClasses
        abilities = abilities + jawsAbilities
        allPerks = allPerks + jawsPerks

    abilitiesByLevel = [[] for x in range(10)]
    abilityTopsByLevel = [[] for x in range(10)]
    abilityBottomsByLevel = [[] for x in range(10)]
    abilityTopLayoutByLevel = [[] for x in range(10)]
    abilityBottomLayoutByLevel = [[] for x in range(10)]
    abilityTopDiscardByLevel = [[] for x in range(10)]
    abilityBottomDiscardByLevel = [[] for x in range(10)]
    abiIDMax = 0

    initiativeWeights = [1, 1, 1, 1, 4, 5, 3, 5, 8, 9, 12, 8, 10, 9, 8, 9, 8, 6, 12, 11, 9, 9, 11, 5, 8, 12, 11, 8, 12, 4, 11, 8, 7, 6, 11, 6, 8, 8, 5, 9, 8, 4, 7, 8, 2, 9, 7, 7, 2, 4, 8, 7, 4, 4, 4, 6, 7, 2, 4, 3, 10, 11, 2, 6, 4, 6, 7, 5, 3, 3, 6, 5, 5, 5, 7, 4, 7, 6, 5, 4, 8, 4, 4, 7, 9, 8, 4, 5, 6, 6, 9, 2, 2, 4, 4, 2, 2, 4, 0]

    for ability in abilities:
        if ability['Name'] == '$ABILITY_CARD_LargeMedicalPack$':
            largeMedPack = ability
            continue
        if ability['Name'] == '$ABILITY_CARD_MedicalPack$':
            normalMedPack = ability
            continue
        if ability['Level'] == 'X':
            abilitiesByLevel[0].append(ability)
            abilityTopsByLevel[0].append(ability['Data']['Top'])
            abilityBottomsByLevel[0].append(ability['Data']['Bottom'])
            abilityTopLayoutByLevel[0].append(ability['Layout']['Top'])
            abilityBottomLayoutByLevel[0].append(ability['Layout']['Bottom'])
            abilityTopDiscardByLevel[0].append(ability['Discard'][0])
            abilityBottomDiscardByLevel[0].append(ability['Discard'][1])
        else:
            ablvl = int(ability['Level'])
            abilitiesByLevel[ablvl].append(ability)
            abilityTopsByLevel[ablvl].append(ability['Data']['Top'])
            abilityBottomsByLevel[ablvl].append(ability['Data']['Bottom'])
            abilityTopLayoutByLevel[ablvl].append(ability['Layout']['Top'])
            abilityBottomLayoutByLevel[ablvl].append(ability['Layout']['Bottom'])
            abilityTopDiscardByLevel[ablvl].append(ability['Discard'][0])
            abilityBottomDiscardByLevel[ablvl].append(ability['Discard'][1])
        if int(ability['ID']) > abiIDMax:
            abiIDMax = 1 + int(ability['ID'])

    langDict = {}

    allPerksID = copy.deepcopy(allPerks)
    
    for i in range(0,len(allPerksID)):
        allPerksID[i]['tempID'] = i

    for characterIndex in range(numCharacters):
        curAmalgam = amalgamating[characterIndex]

        newCharName = charNames[characterIndex]
        print("Creating character named {}".format(newCharName))

        treasureTable.insert(12,"  UnlockCharacter: {}ID\n".format(newCharName))
        
        newChar = random.choice(classes)

        if newChar['ID'] == 'BeastTyrantID':
            newChar.pop('CompanionSummonData')

        healthTable = []
        shp = random.randint(startHPMin,startHPMax)
        hpInc = random.uniform(HPIncreaseMin,HPIncreaseMax)
        for i in range(0,9):
            healthTable.append(round(shp + hpInc * i))
        
        handSize = random.randint(handSizeMin, handSizeMax)
        perkSize = random.randint(perkMin, perkMax)

        newChar['ID'] = newCharName + "ID"
        newChar['LocKey'] = "$" + newCharName + "$"
        newChar['Role'] = "$" + newCharName + "_ROLE$"
        newChar['Description'] = "$" + newCharName + "_DESCRIPTION$"
        newChar['Strengths'] = "$" + newCharName + "_STRENGTHS$"
        newChar['Weaknesses'] = "$" + newCharName + "_WEAKNESSES$"
        newChar['Adventure_Description'] = "$" + newCharName + "_ADVENTURE_DESCRIPTION$"
        newChar['HealthTable'] = healthTable
        newChar['NumberAbilityCardsInBattle'] = handSize

        r = lambda: random.randint(0,255)
        newChar.insert(6,'Colour','%02X%02X%02X' % (r(),r(),r()))

        langDict[newCharName] = newCharName
        desc = ghu.MakeDescription(newCharName)
        langDict[newCharName + "_ROLE"]=ghu.MakeRole()
        langDict[newCharName + "_DESCRIPTION"]=desc
        langDict[newCharName + "_STRENGTHS"]=ghu.MakeStrengths()
        langDict[newCharName + "_WEAKNESSES"]=ghu.MakeWeaks()
        langDict[newCharName + "_ADVENTURE_DESCRIPTION"]=desc

        # Create Perks
        charPerks = copy.deepcopy(allPerks)
        charPerksID = copy.deepcopy(allPerksID)

        for i in range(0,len(charPerks)):
            charPerks[i]['ID'] = newCharName
            charPerks[i]['Name'] = "PERK_{}_".format(newCharName)
            charPerks[i]['Description'] = "PERK_{}_".format(newCharName)
            charPerks[i]['CharacterID'] = "{}ID".format(newCharName)
            charPerksID[i]['ID'] = newCharName
            charPerksID[i]['Name'] = "PERK_{}_".format(newCharName)
            charPerksID[i]['Description'] = "PERK_{}_".format(newCharName)
            charPerksID[i]['CharacterID'] = "{}ID".format(newCharName)
        
        uniqueCharPerks = []

        for index, value in enumerate(charPerks):
            if value not in charPerks[index + 1:]:
                value['tempID'] = charPerksID[index]['tempID']
                uniqueCharPerks.append(value)

        createdCharPerks = random.sample(uniqueCharPerks,perkSize)

        for i in range(0,len(createdCharPerks)):
            tid = createdCharPerks[i]['tempID']
            createdCharPerks[i]['ID'] = "{}{:02d}".format(newCharName,i+1)
            createdCharPerks[i]['Name'] = allPerksID[tid]['Name']
            createdCharPerks[i]['Description'] = allPerksID[tid]['Description']
            createdCharPerks[i].pop('tempID')
            ghu.SaveYML("{}/ModdedYML/Perk_{}_{:02d}.yml".format(modDir,newCharName,i+1), createdCharPerks[i], yaml)

        characterAbilities = [[] for x in range(10)]

        for i in range(0,len(abilitiesByLevel)):
            if i == 0:
                characterAbilities[i] = random.sample(abilitiesByLevel[i], 3)
            elif i == 1:
                characterAbilities[i] = random.sample(abilitiesByLevel[i], handSize)
            else:
                characterAbilities[i] = random.sample(abilitiesByLevel[i], levelCards)

        if curAmalgam:
            for i in range(0, len(characterAbilities)):
                randTops = random.sample(range(len(abilityTopsByLevel[i])), len(characterAbilities[i]))
                randBots = random.sample(range(len(abilityBottomsByLevel[i])), len(characterAbilities[i]))
                for j in range(0, len(characterAbilities[i])):
                    characterAbilities[i][j]['Data']['Top'] = abilityTopsByLevel[i][randTops[j]]
                    characterAbilities[i][j]['Layout']['Top'] = abilityTopLayoutByLevel[i][randTops[j]]
                    characterAbilities[i][j]['Data']['Bottom'] = abilityBottomsByLevel[i][randBots[j]]
                    characterAbilities[i][j]['Layout']['Bottom'] = abilityBottomLayoutByLevel[i][randBots[j]]
                    characterAbilities[i][j]['Discard'][0] = abilityTopDiscardByLevel[i][randTops[j]]
                    characterAbilities[i][j]['Discard'][1] = abilityBottomDiscardByLevel[i][randBots[j]]
                    characterAbilities[i][j]['Initiative'] = random.choices(range(1,100),weights=initiativeWeights,k=1)[0]

        abiIDMax += 1
        normalMedID = abiIDMax
        normalMedPack['ID'] = abiIDMax
        normalMedPack['Character'] = newCharName + "ID"
        abiIDMax += 7
        largeMedID = abiIDMax
        largeMedPack['ID'] = abiIDMax
        largeMedPack['Character'] = newCharName + "ID"
        abiIDMax += 4
        characterAbilities[0].append(normalMedPack)
        characterAbilities[0].append(largeMedPack)

        characterAbilities = ghu.ParseForMedPacks(characterAbilities, normalMedID, largeMedID)

        newAbilityTops = copy.deepcopy(abilityTopsByLevel)
        newAbilityBottoms = copy.deepcopy(abilityBottomsByLevel)
        newLayoutTops = copy.deepcopy(abilityTopLayoutByLevel)
        newLayoutBottoms = copy.deepcopy(abilityBottomLayoutByLevel)
        newDiscardTops = copy.deepcopy(abilityTopDiscardByLevel)
        newDiscardBottoms = copy.deepcopy(abilityBottomDiscardByLevel)

        # Weed out Command and Song cards
        # Remove their halves from the list of good halves
        for i in range(0,len(abilityTopsByLevel)-1):
            for j in range(0, len(abilityTopsByLevel[i])-1):
                if ghu.ParseForBrokenTopAbilities(abilityTopsByLevel[i][j]):
                    newAbilityTops[i].pop(j)
                    newLayoutTops[i].pop(j)
                    newDiscardTops[i].pop(j)
        for i in range(0,len(abilityBottomsByLevel)-1):
            for j in range(0,len(abilityBottomsByLevel[i])-1):
                if ghu.ParseForBrokenBotAbilities(abilityBottomsByLevel[i][j]):
                    newAbilityBottoms[i].pop(j)
                    newLayoutBottoms[i].pop(j)
                    newDiscardBottoms[i].pop(j)
        # Loop through all of new character's abilities
        # 
        for i in range(0,len(characterAbilities)):
            for j in range(0,len(characterAbilities[i])):
                if ghu.ParseForBrokenTopAbilities(characterAbilities[i][j]['Data']['Top']):
                    newIndx = random.choice(range(len(newAbilityTops[i])))
                    characterAbilities[i][j]['Data']['Top'] = newAbilityTops[i][newIndx]
                    characterAbilities[i][j]['Layout']['Top'] = newLayoutTops[i][newIndx]
                    characterAbilities[i][j]['Discard'][0] = newDiscardTops[i][newIndx]
                if ghu.ParseForBrokenBotAbilities(characterAbilities[i][j]['Data']['Bottom']):
                    newIndx = random.choice(range(len(newAbilityBottoms[i])))
                    characterAbilities[i][j]['Data']['Bottom'] = newAbilityBottoms[i][newIndx]
                    characterAbilities[i][j]['Layout']['Bottom'] = newLayoutBottoms[i][newIndx]
                    characterAbilities[i][j]['Discard'][1] = newDiscardBottoms[i][newIndx]
                characterAbilities[i][j]['Character'] = newCharName + "ID"
                if characterAbilities[i][j]['Name'] != "$ABILITY_CARD_LargeMedicalPack$" and characterAbilities[i][j]['Name'] != "$ABILITY_CARD_MedicalPack$":
                    abiIDMax += 1
                    characterAbilities[i][j]['ID'] = abiIDMax
                fname = "{}_{}_{}".format(characterAbilities[i][j]['ID'], newCharName, characterAbilities[i][j]['Name'][14:-1])
                ghu.SaveYML("{}/ModdedYML/{}.yml".format(modDir, fname), characterAbilities[i][j], yaml)
                ghu.SaveYML("{}/ModdedYML/{}.yml".format(modDir, newCharName), newChar, yaml)
    ghu.WriteTreasureTable("{}/ModdedYML/StartingTreasureTable.yml".format(modDir),treasureTable)
    ghu.CaseFix("{}/ModdedYML/".format(modDir))
    ghu.ReconstructDuplicateKeysDir("{}/ModdedYML".format(modDir))
    ghu.MakeLangUpdate("{}/LangUpdates/LangUpdate.csv".format(modDir),langDict)
    print("Finished creating {} character(s)".format(numCharacters))