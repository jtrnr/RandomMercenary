import ghUtils as ghu
import argparse
import shutil

def GetArgs():
    parser = argparse.ArgumentParser(description='Builds a cache of relevant Gloomhaven data files. Applies some necessary fixes to out-of-spec YAML files. Run this first before the mercenary randomizer.')
    parser.add_argument('-ep','--exportpath',
                       type=str,
                       help='the path to Gloomhaven ModdingExport folder',
                       required=True)
    parser.add_argument('-jotl','--jawsofthelion',
                       type=bool,
                       action=argparse.BooleanOptionalAction,
                       help='If supplied, will use Jaws of the Lion DLC Mercenaries',
                       required=False)
    return parser.parse_args()

if __name__ == "__main__":
    args = GetArgs()

    exPath = args.exportpath
    jaws = args.jawsofthelion
    ghu.ParseForDuplicateKeysAndCacheDir("{}/Global/AbilityCard".format(exPath),["Global","AbilityCard"])
    ghu.ParseForDuplicateKeysAndCacheDir("{}/Global/AttackModifier".format(exPath),["Global","AttackModifier"])
    ghu.ParseForDuplicateKeysAndCacheDir("{}/Global/Character".format(exPath),["Global","Character"])
    ghu.ParseForDuplicateKeysAndCacheDir("{}/Global/Perk".format(exPath),["Global","Perk"])
    if jaws:
        ghu.ParseForDuplicateKeysAndCacheDir("{}/DLC_JOTL/Global/AbilityCard".format(exPath),["DLC_JOTL","Global","AbilityCard"])
        ghu.ParseForDuplicateKeysAndCacheDir("{}/DLC_JOTL/Global/AttackModifier".format(exPath),["DLC_JOTL","Global","AttackModifier"])
        ghu.ParseForDuplicateKeysAndCacheDir("{}/DLC_JOTL/Global/Character".format(exPath),["DLC_JOTL","Global","Character"])
        ghu.ParseForDuplicateKeysAndCacheDir("{}/DLC_JOTL/Global/Perk".format(exPath),["DLC_JOTL","Global","Perk"])
    
    shutil.copy("{}/Campaign/TreasureTable/StartingTreasureTable.yml".format(exPath),"cache")