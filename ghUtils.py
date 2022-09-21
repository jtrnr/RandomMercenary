import random
import ruamel.yaml
import math
import sys
from os import listdir
from os.path import isfile, join, split
import pathlib
import re

# Returns a list of data of all .yml files in a directory
# Except for "LongRest.yml" which pollutes the available card list
def LoadYMLDir(datadir, _yaml):
    data = []
    files = [f for f in listdir(datadir) if isfile(join(datadir, f))]
    for f in files:
        if f == "LongRest.yml":
            continue
        with open("{}/{}".format(datadir, f),"r") as rf:
            data.append(_yaml.load(rf))
    return data

# Returns the data of a single .yml file
def LoadYMLFile(datadir, _yaml):
    with open(datadir,"r") as rf:
        return(_yaml.load(rf))

# Writes a single .yml file
def SaveYML(datadir, dataToSave, _yaml):
    with open(datadir, 'w') as wf:
        out = _yaml.dump(dataToSave, wf)

# Cannot find a way to make ruamel capitalize "null" to "Null" in .yml keys
# Gloomhaven seems to require this for a mod to validate
# Do it manually with regex
def CaseFix(datadir):
    files = [f for f in listdir(datadir) if isfile(join(datadir, f))]
    for f in files:
        with open(datadir +"/"+ f,"r") as rf:
            data = rf.read()
        data = re.sub(r' null:', r' Null:', data)
        with open("{}/{}".format(datadir, f), "w") as wf:
            wf.write(data)

# Helper function for ParseForMedPacks() function
# Checks if nested key exists in element dict
def nestedKeysExists(element, *keys):
    _element = element
    for key in keys:
        try:
            _element = _element[key]
        except KeyError:
            return False
    return True

def findkeys(node, kv):
    if isinstance(node, list):
        for i in node:
            for x in findkeys(i, kv):
               return x
    elif isinstance(node, dict):
        if kv in node:
            return node[kv]
        for j in node.values():
            for x in findkeys(j, kv):
                return x

# Cards that give out Med Packs reference the ID of a Med Pack card directly
# Med Pack cards in turn reference the character ID of the original card owner directly
# Elsewhere in this program we create a regular and large Med Pack card for each random character
# Here we must parse a character's ability list for any card that gives out med packs,
# and update the referenced ID to these created Med Pack cards
# This is done manually by checking for key paths in each ability card object
def ParseForMedPacks(abilitiesList, normalMedPackID, bigMedPackID):
    for abilityLevel in abilitiesList:
        for ability in abilityLevel:
            if nestedKeysExists(ability,'Data','Top','Abilities','TGiveSupplyCard','GiveSupplyCard'):
                if ability['Data']['Top']['Abilities']['TGiveSupplyCard']['GiveSupplyCard'] == 417:
                    ability['Data']['Top']['Abilities']['TGiveSupplyCard']['GiveSupplyCard'] = normalMedPackID
                else:
                    ability['Data']['Top']['Abilities']['TGiveSupplyCard']['GiveSupplyCard'] = bigMedPackID
            if nestedKeysExists(ability,'Data','Top','Abilities','THeal','SubAbilities','THealSubGiveSupplyCard','GiveSupplyCard'):
                if ability['Data']['Top']['Abilities']['THeal']['SubAbilities']['THealSubGiveSupplyCard']['GiveSupplyCard'] == 417:
                    ability['Data']['Top']['Abilities']['THeal']['SubAbilities']['THealSubGiveSupplyCard']['GiveSupplyCard'] = normalMedPackID
                else:
                    ability['Data']['Top']['Abilities']['THeal']['SubAbilities']['THealSubGiveSupplyCard']['GiveSupplyCard'] = bigMedPackID
            if nestedKeysExists(ability,'Data','Bottom','Abilities','TGiveSupplyCard','GiveSupplyCard'):
                if ability['Data']['Bottom']['Abilities']['TGiveSupplyCard']['GiveSupplyCard'] == 417:
                    ability['Data']['Bottom']['Abilities']['TGiveSupplyCard']['GiveSupplyCard'] = normalMedPackID
                else:
                    ability['Data']['Bottom']['Abilities']['TGiveSupplyCard']['GiveSupplyCard'] = bigMedPackID
    return abilitiesList

def ParseForBrokenBotAbilities(ability):
    try:
        if ability['Abilities']['BAlly']['Filter'] == "Companion":
            return True
    except:
        pass
    try: 
        if 'ForgoActionsForCompanion' in ability['Abilities']['BActive']:
            return True
    except:
        pass
    try:
        if 'BDoom' in ability['Abilities']:
            return True
    except:
        pass
    try:
        if 'TransferDooms' in ability['Abilities']['BTransferDooms']:
            return True
    except:
        pass
    try:
        if 'IsDoomed' in ability['Abilities']['BAttackBuff']['ActiveBonus']['Filter']:
            return True
    except:
        pass
    try:
        if 'IsDoomed' in ability['Abilities']['BAttack']['Filter']:
            return True
    except:
        pass
    return False

def ParseForBrokenTopAbilities(ability):
    popTop = False
    try:
        if ability['Abilities']['TAlly']['Filter'] == "Companion":
            return True
    except:
        pass
    try:
        if 'TPlaySong' in ability['Abilities']:
            return True
    except:
        pass
    try:
        if 'TransferDooms' in ability['Abilities']['TActive']['TAddActiveBonus']:
            return True
    except:
        pass
    try:
        if 'IsDoomed' in ability['Abilities']['TActive']['ActiveBonus']['AuraFilter']:
            return True
    except:
        pass
    try:
        if 'IsDoomed' in ability['Abilities']['TAttack']['ConditionalOverrides']['TAttackCO']['Filter']:
            return True
    except:
        pass
    try:
        if 'IsDoomed' in ability['Abilities']['TAdvantage']['ActiveBonus']['Filter']:
            return True
    except:
        pass
    return False

# Treasure Table YAML has duplicate keys...
# Therefore must treat it with care and not load it via ruamel
# TODO: Trash this and use other functions that do the same thing
def LoadTreasureTable(datadir):
    with open(datadir, "r") as rf:
        data = rf.readlines()
    return data

# Treasure Table YAML has duplicate keys...
# Therefore must treat it with care and not write it via ruamel
# TODO: Trash this and use other functions that do the same thing
def WriteTreasureTable(datadir, data):
    with open(datadir, "w") as wf:
        data = "".join(data)
        wf.write(data)

# Append updated key,value lines to LangUpdate.csv
def MakeLangUpdate(datadir,updateDict):
    with open(datadir, 'a') as wf:
        for key, value in updateDict.items():
            wf.write("\n{},{}".format(key, value))

# Initialize ruamel with necessary parameters
def StartYaml():
    yaml = ruamel.yaml.YAML()
    yaml.default_flow_style = True
    yaml.preserve_quotes = True
    yaml.allow_duplicate_keys = True
    yaml.width = math.inf
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.boolean_representation = ['False', 'True']
    return yaml

# Combine an adjective with a noun to create a Mercenary name
# TODO: More names
def MakeName(space):
    firstName = ["able","achy","acid","acidic","aged","airy","anti","arch","arid","arty","ashy","avid","away","bald","bare","base","blue","bold","bony","boxy","buff","busy","calm","chic","clean","clever","cold","cool","cosy","cozy","curt","cute","cyan","daft","damn","damp","dank","dark","darn","dead","deaf","dear","deep","demi","dense","dim","dire","dirty","dour","down","dozy","drab","dry","dull","dumb","easy","edgy","eery","eggy","epic","even","evil","fair","fake","fast","fawn","fine","firm","flaky","flat","fond","fore","foul","foxy","free","fresh","full","gent","giant","glad","glam","glib","glum","gold","good","gory","gray","grey","grim","grimy","gross","grumpy","hairy","half","hard","hazy","head","high","hind","holy","hot","hued","huge","hurt","icky","idle","iffy","ill","indy","inky","itchy","itty","joky","keen","kind","lacy","lame","last","late","lazy","lean","lewd","limp","limy","lite","loco","lone","long","loud","lush","main","male","manic","mazy","mean","meek","mega","mere","mild","mint","miry","misc","mock","moot","mute","near","neat","needy","neon","nice","nifty","normal","nosy","nude","null","numb","odd","oily","okay","old","olde","only","onyx","oozy","open","over","ower","pale","past","pesky","pink","poky","poly","poor","posh","poxy","prim","puny","pure","racy","rank","rapt","rare","rash","raw","real","rear","regal","rich","rife","ripe","ropy","rosy","ruby","rude","sad","safe","sage","salt","same","sane","scary","sexy","sham","shaved","shut","shy","sick","slim","slimy","slit","slow","smart","smug","snap","snug","soft","sole","solo","sore","sour","spicy","spry","sure","sweet","tall","tame","tan","tart","taut","thin","tidy","tiny","trad","trim","true","tuff","twin","ugly","vain","vast","very","vice","vile","void","wack","warm","wary","wavy","waxy","weak","wet","whole","wide","wild","wily","wiry","wise","zany"]
    endName = ["area","body","guy","dude","life","soul","body","person","entity","toon","knight","priest","cleric","archer","guard","thief","bard","warrior","rogue","shaman","face","zone","part","ninja","mage","spy","sage","witch","seer","boxer","monk","paladin","demon","psion","stalker","scout","hunter","warlock","druid","saint","friend","gal","lady","sir","king","queen","god","part","ogre","oaf","fiend","speck","athlete","thing","oddity","object"]
    if space:
        sp = "_"
    else:
        sp = ""
    return random.choice(firstName).capitalize() + sp + random.choice(endName).capitalize()

# Calls MakeName repeatedly until the requisite number of unique names have been generated
def MakeManyNames(n, spaces):
    nameList = []
    i = 0
    while len(nameList) < n:
        name = MakeName(spaces[i])
        if name not in nameList:
            i += 1
            nameList.append(name)
    return nameList

# Make a short description for the Mercenary. Not relevant to gameplay.
def MakeDescription(charName):
    adj = ["good","bad","mediocre","great","skilled","adept","incompetent","cool","weird","hungry","bashful","noisy","foolish","stealthy","violent","brave","wary","careless","cautious","obnoxious","obedient","tall","nervous","short","heroic","meek","bony","old","fat","thin","orange","red","blue","green","left-handed","right-handed","smart","stupid","rich"]
    return "The {} is {}.".format(charName,random.choice(adj))

# Give the Mercenary a role. Not relevant to gameplay.
def MakeRole():
    roles = ["Accountant","Acrobat","Actor","Actuary","Acupuncturist","Administrator","Aerospace engineer","Air traffic controller","Alchemist","Alderman","Ambassador","Analyst","Anesthetist","Anesthesiologist","Anchorman","Animator","Animal Trainer","Announcer","Antique dealer","Arborist","Archaeologist","Archbishop","Architect","Archivist","Art dealer","Art director","Artist","Assayer","Assessor","Assistant","Astrologer","Astronaut","Astronomer","Astrophysicist","Athlete","Athletic trainer","Attorney","Auctioneer","Author","Automobile racer","Automotive designer","Audiologist","Auditor","Audio Analyser","Babysitter","Bacteriologist","Bailiff","Baker","Balloonist","Bank teller","Banker","Bar keeper","Barber","Bargeman","Barista","Barman","Barrister","Bartender","Bassoonist","Batman","Beautician","Beauty specialist","Beauty therapist","Beekeeper","Bellhop","Biographer","Biologist","Bishop","Blacksmith","Boatman","Bodyguard","Boilermaker","Bookbinder","Bookkeeper","Bookseller","Border patrol","Bounty hunter","Boxer","Blacksmith","Brain surgeon","Brewer","Bricklayer","Broker","Builder","Bureaucrat","Butcher","Butler","Heading text","Cab driver","Cabinetmaker","Caddy","Calligrapher","Cameraman","Captain","Cardinal","Cardiologist","Carpenter","Cartoonist","Cartographer","Cashier","Cellist","Chancellor","Chaplain","Chauffeur","Chess player","Cheesemaker","Chef","Chemist","Compliance Officer","Chief engineer","CEO","CFO","CTO","CIO","Chief of Police","Chimney sweep","Chiropodist","Chiropractor","Choreographer","Cinematographer","Civil servant","Civil engineer","Clarinetist","Cleaner","Clergymen","Clerk","Climatologist","Clockmaker","Clown","Coach","Coachman","Coast guard","Cobbler","Columnist","Comedian","Company secretary","Compasssmith","Composer","Computer programmer","Conductor","Confectioner","Conferencier","Constable","Cooper","Construction foreman","Consul","Consultant","Controller","Cosmetologist","Contractor","Cook","Copywriter","Coroner","Corrector","Correspondent","Cosmetologist","Cosmonaut","Costume designer","Courier","Court jester","Cowboy","Crafter","Crammer","Cryptographer","Cryptozoologist","Curator","Currier","Custodian","Customer","Customs officer","Cyclist","Dancer","Dealer","Delivery man","Dental hygienist","Dentist","Deputy","Dermatologist","Demolitionist","Designer","Detective","Dietician","Dictator","Diplomat","Disc jockey","Dispatcher","Diver","Dock labourer","Doctor","Documentalist","Dog walker","Doorman","Dramatist","Dressmaker","Dressman","Driver","Drug dealer","Drummer","DJ","Ecologist","Editor","Educationalist","Electrician","Escort","Embalmer","Engine-driver","Engine fitter","Engineer","Entertainer","Entrepreneur","Estate agent","Ethnologist","Ethologist","Etymologist","Evangelist","Examiner","Executive","Executor","Exotic dancer","Explorer","Executioner","Factory worker","Falconer","Farmer","Farrier","Fashion designer","Ferryman","Film critic","Film director","Film producer","Financial adviser","Fire marshal","Fire Safety Officer","Firefighter","First mate","Fisherman","Fishmonger","Fishwife","Fitter","Flautist","Flavorist","Fletcher","Flight attendant","Flight instructor","Flight technician","Flight engineer","Floor manager","Florist","Flutist","Food critic","Footballer","Footman","Forester","Fortune teller","Fowler","Funeral director","Game designer","Game show host","Game warden","Gamekeeper","Gangster","Garbage collector","Gardener","Gate-keeper","Gemcutter","Genealogist","General","Geographer","Geologist","Geometrician","Geophysicist","Gigolo","Gladiator","Goldsmith","Gondolier","Gofer","Governess","Government agent","Governor","Grammarian","Graphic artist","Graphic designer","Gravedigger","Greengrocer","Grocer","Guard","Guide","Guitarist","Gunsmith","Hairdresser","Hairstylist","Handyman","Harbourmaster","Harpist","Hatter","Headmaster","Headmistress","Health inspector","Herder","Historian","Hitman","Homeopath","Hornist","Host","Hostess","Hotel manager","Hotelier","House painter","Housekeeper","Housewife","Homeowner","Hunter","Hydraulic engineer","Ice cream man","Illuminator","Illusionist","Illustrator","Image consultant","Imam","Impersonator","Importer","Industrial engineer","Industrialist","Information broker","Inker","Innkeeper","Instructor","Insurer","Intelligence officer","Intercity bus driver","Interior designer","Internist","Interpreter","Interrogator","Inventor","Investment banker","Investment broker","Ironmonger","Ironmaster","Ironworker","Jailer","Janitor","Jeweller","Jockey","Joggler","Joiner","Joker","Journalist","Judge","Juggler","Jurist","Karate master","Kickboxer","Kinesiologist","King","Lab tech","Laborer","Lady-in-waiting","Landlord","Laundress","Lawyer","Leadworker","Leatherer","Leather worker","Lecturer","Legislator","Librarian","Librarianship","Librettist","Lieutenant","Lifeguard","Lighthouse keeper","Lighting technician","Lineman","Linguist","Loan officer","Lobbyist","Locksmith","Logistician","Lumberjack","Lyricist","Magistrate","Magician","Magnate","Maid","Mailman","Make-up artist","Manager","Manicurist","Manservant","Manual therapist","Manufacturer","Marine","Marine biologist","Market gardener","Marketing manager","Marksman","Marshal","Martial artist","Mason","Masseuse","Matador","Mathematician","Matron","Mayor","Mechanic","Mechanical engineer","Mechanician","Mediator","Medic","Medical biller","Mercer","Merchant","Mesmerist","Messenger","Meteorologist","Mid-wife","Milkman","Miller","Miner","Minister","Missionary","Mobile","Mobster","Model","Modeller","Moldmaker","Moneychanger","Moneylender","Monk","Moonlighter","Mortgage broker","Mountaineer","Muralist","Music educator","Music director","Musician","Nanny","Navigator","Négociant","Negotiator","Netmaker","Neurologist","Newscaster","Night auditor","Nightwatchmen","Notary","Novelist","Numerologist","Numismatist","Nun","Nursemaid","Nurse","Nutritionist","Oboist","Obstetrician","Oceanographer","Occupational therapist","Ocularist","Odontologist","Oenologist","Oncologist","Operator","Ophthalmologist","Optician","Optometrist","Oracle","Ordinary seaman","Organizer","Orthodontist","Orthopaedist","Ornithologist","Ostler","Otorhinolaryngologist","Painter","Paleontologist","Paleoseismologist","Paralegal","Paramedic","Park ranger","Parole officer","Party-leader","Pastor","Patent attorney","Patent examiner","Pathologist","Pawnbroker","Peddler","Pediatrician","Percussionist","Perfumer","Personal trainer","Pharmacist","Philanthropist","Philologist","Philosopher","Photographer","Photographer assistant","Physical therapist","Physician","Physician assistant","Physicist","Physiognomist","Physiologist","Physiotherapist","Pianist","Piano tuner","Pilot","Pimp","Pirate","Plasterer","Plumber","Podiatrist","Poet","Poetrist","Poker player","Poll-taker","Police detective","Police inspector","Police officer","Politician","Political scientist","Pool boy","Pope","Porter","Poulterer","Presenter","President","Press officer","Priest","Prime minister","Prince","Princess","Principal","Printer","Prison officer","Private detective","Probation officer","Proctologist","Producer","Product designer","Professor","Professional dominant","Programmer","Project manager","Proofreader","Prosecutor","Prostitute","Psychiatrist","Psychodramatist","Psychologist","Psychotherapist","Public Relations Officer","Public speaker","Publicist","Publisher","Puppeteer","Queen","Consort","Quilter","Rabbi","Radiologist","Radiographer","Race driver","Rat-catcher","Real estate broker","Real estate investor","Real estate developer","Receptionist","Record producer","Referee","Refuse collector","Registrar","Registered nurse","Remedial teacher","Reporter","Researcher","Resource room assisstant","Respiratory therapist","Restaurateur","Retailer","Rockstar","Sailmaker","Sailor","Sales person","Salesmen","Sanitation worker","Sarariman","Saucier","Saxophonist","Sawyer","Scientist","Scout","Screenwriter","Scribe","Sculptor","Seamstress","Second mate","Secret service agent","Secret shopper","Secretary general","Security guard","Senator","Servant","Sexologist","Sexton","Sheepshearer","Sheriff","Sheriff officer","Shepherd","Shoemaker","Shoeshiner","Signalman","Singer","Skydiver","Sleuth","Sniper","Social worker","Socialite","Soda jerk","Software developer","Software engineer","Soil scientist","Soldier","Solicitor","Sommelier","Sonographer","Sound engineer","Sound technicial","Special agent","Speech therapist","Sportsman","Sports commentator","Spy","Stage designer","Statistician","Steersman","Stevedore","Steward","Street artist","Street musician","Stock-breeder","Stockbroker","Street sweeper","Street vendor","Stripper","Structural engineer","Student","Stunt double","Stunt performer","Stuntman","Suicidologist","Surgeon","Superintendent","Supervisor","Surveyor","Swimmer","Switchboard operator","System administrator","Systems analyst","System designer","Tailor","Taikonaut","Tanner","Tax collector","Tax lawyer","Taxidermist","Taxonomist","Tea lady","Teacher","Technical engineer","Technician","Technologist","Technical writer","Telephone operator","Tennis player","Terminator","Test developer","Test pilot","Thatcher","Theatre director","Theologian","Therapist","Thimbler","Tiler","Toolmaker","Trader","Translator","Treasurer","Tuner","Tutor","Typist","Ufologist","Umbrella repairer","Undercover agent","Undertaker","Underwear model","Underwriter","Upholsterer","Urban planner","Urologist","Usher","Valet","Verger","Ventriloquist","Verger","Veterinarian","Vibraphonist","Vicar","Vice president","Victualler","Video editor","Video game developer","Vintner","Violinist","Violist","Voice actor","Waiter","Waste collector","Watchmaker","Weaponsmith","Weatherman","Weaver","Web coder","Web designer","Web developer","Wedding planner","Welder","Wet nurse","Wine connoisseur","Winemaker","Window-dresser","Wireless operator","Wood cutter","Woodcarver","Wrangler","Wrestler","Writer","Xylophonist","Yodeler","Zookeeper","Zoologist"]
    return random.choice(roles)

# Give the Mercenary some Strengths. Not relevant to gameplay.
def MakeStrengths():
    attrs = ["abiding","acceding","accelerating","accepting","accomplishing","achieving","acquiring","activating","adapting","adding","addressing","administering","admiring","admitting","adopting","affording","agreeing","alerting","alighting","allowing","altering","amusing","analyzing","annoying","answering","apologizing","appearing","applauding","appointing","appraising","appreciating","approving","arbitrating","arguing","arising","arranging","arresting","arriving","ascertaining","asking","assessing","assisting","assuring","attaching","attacking","attaining","attempting","attending","avoiding","baking","balancing","banging","banning","barring","bathing","bating","battling","bearing","beating","becoming","begging","beginning","beholding","being","belonging","besetting","betting","biding","binding","biting","bleaching","bleeding","blessing","blinking","blotting","blowing","blushing","boasting","boiling","bombing","booking","borrowing","bouncing","bowing","boxing","braking","breaking","breathing","breeding","broadcasting","bruising","brushing","budgeting","building","bumping","burning","bursting","busting","buying","buzzing","calculating","calling","camping","caring","carrying","carving","casting","cataloging","catching","causing","challenging","changing","charging","chasing","cheating","checking","cheering","chewing","choking","choosing","chopping","claiming","clarifying","classifying","cleaning","clearing","clinging","clipping","clothing","coaching","coiling","collecting","coloring","combing","coming","commanding","communicating","comparing","competing","compiling","complaining","completing","computing","conceiving","concentrating","conducting","confessing","confronting","confusing","connecting","conserving","considering","consisting","consolidating","constructing","containing","contracting","controlling","converting","coordinating","copying","correcting","correlating","costing","coughing","counseling","covering","cracking","crashing","crawling","creating","creeping","critiquing","crossing","crushing","crying","curing","curling","curving","cutting","cycling","damaging","damming","dealing","decaying","deceiving","deciding","decorating","defining","delaying","delegating","delighting","delivering","depending","describing","deserting","deserving","designing","detailing","detecting","determining","developing","devising","diagnosing","digging","directing","disagreeing","disappearing","disapproving","discovering","disliking","dispensing","displaying","disproving","dissecting","distributing","diverting","dividing","diving","doing","doubling","doubting","drafting","dragging","draining","dramatizing","drawing","dreaming","dressing","drinking","dripping","driving","dropping","drying","earning","eating","editing","educating","eliminating","embarrassing","employing","enacting","encouraging","ending","enduring","enforcing","engineering","enhancing","enjoying","ensuring","entering","entertaining","establishing","estimating","evaluating","examining","exceeding","exciting","excusing","executing","exercising","exhibiting","existing","expanding","expecting","experimenting","explaining","exploding","expressing","extending","extracting","facilitating","facing","fading","fancying","faxing","fearing","feeding","fencing","fetching","fighting","filling","filming","finalizing","financing","finding","firing","fitting","fixing","flapping","flecting","fleeing","flinging","floating","flowing","flying","folding","following","fooling","forbidding","forcing","forecasting","foregoing","foreseeing","forgetting","forgiving","forming","formulating","forsaking","framing","freezing","frightening","frying","gazing","generating","getting","giving","glowing","glueing","going","governing","grabbing","graduating","grating","greasing","greeting","grinding","grinning","groaning","growing","guaranteeing","guarding","guessing","guiding","hammering","handling","handwriting","hanging","happening","harassing","harming","haunting","heading","heaping","hearing","heating","helping","hiding","hitting","holding","hooking","hoping","hugging","hunting","hurrying","hurting","hypothesizing","identifying","ignoring","imagining","implementing","impressing","improving","improvising","including","increasing","inducing","informing","initiating","injecting","innovating","inputing","inspecting","installing","instituting","instructing","insuring","integrating","intending","interesting","interlaying","interrupting","inventing","inventorying","investigating","irritating","jailing","jamming","joking","judging","juggling","jumping","keeping","killing","kissing","kneeling","knitting","knocking","knotting","knowing","landing","lasting","launching","laying","leading","leaning","learning","leaving","lecturing","lending","letting","leveling","licensing","licking","lifting","lightening","lighting","liking","living","loading","locking","logging","longing","looking","losing","loving","lying","maintaining","making","manipulating","manning","manufacturing","mapping","marching","marketing","marrying","matching","mating","mattering","meaning","measuring","meddling","mediating","meeting","melting","memorizing","mending","milking","mining","misleading","missing","mistaking","misunderstanding","moaning","modifying","monitoring","mooring","motivating","moving","muddling","mugging","multiplying","murdering","nailing","naming","navigating","needing","negotiating","nesting","nodding","nominating","normalizing","noticing","noting","numbering","obeying","objecting","observing","occurring","offending","offering","officiating","operating","ordering","organizing","orienteering","originating","overcoming","overdoing","overdrawing","overflowing","overhearing","overthrowing","owing","owning","packing","paddling","painting","parking","participating","parting","passing","pasting","patting","pecking","pedaling","peeling","perceiving","performing","permitting","phoning","photographing","piloting","pinching","pining","pinpointing","planing","planting","pleading","plugging","poking","polishing","possessing","pouring","praising","praying","preaching","preceding","predicting","preferring","preparing","prescribing","presenting","presetting","presiding","pressing","pretending","preventing","pricking","processing","procuring","producing","professing","programming","progressing","projecting","promising","promoting","proofreading","proposing","protecting","providing","proving","publicizing","pumping","punching","puncturing","purchasing","putting","questioning","queueing","quitting","racing","radiating","raising","ranking","rating","reaching","reading","realigning","realizing","reasoning","receiving","recognizing","reconciling","recording","recruiting","reducing","referring","reflecting","regulating","reigning","reinforcing","rejecting","rejoicing","relating","relaxing","releasing","relying","remaining","remembering","reminding","removing","rendering","reorganizing","repairing","repeating","replacing","replying","representing","requesting","rescuing","researching","resolving","responding","restoring","restructuring","retiring","retrieving","returning","reviewing","revising","rhyming","riding","ringing","rinsing","rising","risking","rocking","rolling","rotting","rubbing","ruining","running","sacking","satisfying","sawing","saying","scaring","scattering","scheduling","scolding","scorching","scraping","scratching","screwing","scribbling","scrubbing","sealing","searching","securing","seeing","seeking","selecting","selling","sending","sensing","separating","servicing","serving","setting","settling","sewing","shading","shaking","shaping","sharing","shearing","sheltering","shining","shivering","shocking","shoeing","shooting","shopping","showing","shrinking","shrugging","shutting","sighing","signaling","signing","simplifying","singing","sinking","sipping","siting","sketching","skiing","skipping","slapping","slaying","sleeping","sliding","slinging","slipping","slitting","smashing","smelling","smiling","smiting","smoking","sneaking","sneezing","sniffing","snoring","snowing","soaking","solving","soothing","soothsaying","sorting","sowing","sparking","sparkling","speaking","speeding","spelling","spending","spilling","spinning","spiting","splitting","spoiling","spotting","spraying","spreading","springing","sprouting","squashing","squeaking","squealing","squeezing","staining","stamping","standing","staring","starting","stealing","sticking","stimulating","stinging","stinking","stirring","stitching","stoping","storing","strapping","streamlining","strengthening","striking","striping","striving","structuring","subtracting","sucking","suffering","suggesting","summarizing","supplying","supposing","surprising","surrounding","suspending","sweating","swelling","swimming","swinging","symbolizing","systemizing","tabulating","taking","taming","taping","targeting","tasting","teaching","teasing","telephoning","telling","tempting","testing","thanking","thriving","thrusting","tickling","timing","tipping","tiring","touching","touring","towing","tracing","trading","training","transforming","transporting","trapping","treating","tricking","trotting","troubleshooting","trusting","trying","tugging","tutoring","twisting","tying","typing","undergoing","understanding","undressing","unfastening","unifying","unpacking","untidying","updating","upgrading","upholding","using","utilizing","verbalizing","vexing","visiting","wailing","waiting","walking","wandering","wanting","washing","watering","wearing","weighing","welcoming","wending","wetting","whispering","winding","winking","wiping","wishing","withstanding","wobbling","working","worrying","wrapping","wrecking","wrestling","wriggling","wringing","writing","yelling","zooming"]
    strs = random.sample(attrs,2)
    return '\"- <indent=%15>Great at {}</indent>\n- <indent=%15>A master of {}</indent>\"'.format(strs[0],strs[1])

# Give the Mercenary some Weaknesses. Not relevant to gameplay.
def MakeWeaks():
    attrs = ["abiding","acceding","accelerating","accepting","accomplishing","achieving","acquiring","activating","adapting","adding","addressing","administering","admiring","admitting","adopting","affording","agreeing","alerting","alighting","allowing","altering","amusing","analyzing","annoying","answering","apologizing","appearing","applauding","appointing","appraising","appreciating","approving","arbitrating","arguing","arising","arranging","arresting","arriving","ascertaining","asking","assessing","assisting","assuring","attaching","attacking","attaining","attempting","attending","avoiding","baking","balancing","banging","banning","barring","bathing","bating","battling","bearing","beating","becoming","begging","beginning","beholding","being","belonging","besetting","betting","biding","binding","biting","bleaching","bleeding","blessing","blinking","blotting","blowing","blushing","boasting","boiling","bombing","booking","borrowing","bouncing","bowing","boxing","braking","breaking","breathing","breeding","broadcasting","bruising","brushing","budgeting","building","bumping","burning","bursting","busting","buying","buzzing","calculating","calling","camping","caring","carrying","carving","casting","cataloging","catching","causing","challenging","changing","charging","chasing","cheating","checking","cheering","chewing","choking","choosing","chopping","claiming","clarifying","classifying","cleaning","clearing","clinging","clipping","clothing","coaching","coiling","collecting","coloring","combing","coming","commanding","communicating","comparing","competing","compiling","complaining","completing","computing","conceiving","concentrating","conducting","confessing","confronting","confusing","connecting","conserving","considering","consisting","consolidating","constructing","containing","contracting","controlling","converting","coordinating","copying","correcting","correlating","costing","coughing","counseling","covering","cracking","crashing","crawling","creating","creeping","critiquing","crossing","crushing","crying","curing","curling","curving","cutting","cycling","damaging","damming","dealing","decaying","deceiving","deciding","decorating","defining","delaying","delegating","delighting","delivering","depending","describing","deserting","deserving","designing","detailing","detecting","determining","developing","devising","diagnosing","digging","directing","disagreeing","disappearing","disapproving","discovering","disliking","dispensing","displaying","disproving","dissecting","distributing","diverting","dividing","diving","doing","doubling","doubting","drafting","dragging","draining","dramatizing","drawing","dreaming","dressing","drinking","dripping","driving","dropping","drying","earning","eating","editing","educating","eliminating","embarrassing","employing","enacting","encouraging","ending","enduring","enforcing","engineering","enhancing","enjoying","ensuring","entering","entertaining","establishing","estimating","evaluating","examining","exceeding","exciting","excusing","executing","exercising","exhibiting","existing","expanding","expecting","experimenting","explaining","exploding","expressing","extending","extracting","facilitating","facing","fading","fancying","faxing","fearing","feeding","fencing","fetching","fighting","filling","filming","finalizing","financing","finding","firing","fitting","fixing","flapping","flecting","fleeing","flinging","floating","flowing","flying","folding","following","fooling","forbidding","forcing","forecasting","foregoing","foreseeing","forgetting","forgiving","forming","formulating","forsaking","framing","freezing","frightening","frying","gazing","generating","getting","giving","glowing","glueing","going","governing","grabbing","graduating","grating","greasing","greeting","grinding","grinning","groaning","growing","guaranteeing","guarding","guessing","guiding","hammering","handling","handwriting","hanging","happening","harassing","harming","haunting","heading","heaping","hearing","heating","helping","hiding","hitting","holding","hooking","hoping","hugging","hunting","hurrying","hurting","hypothesizing","identifying","ignoring","imagining","implementing","impressing","improving","improvising","including","increasing","inducing","informing","initiating","injecting","innovating","inputing","inspecting","installing","instituting","instructing","insuring","integrating","intending","interesting","interlaying","interrupting","inventing","inventorying","investigating","irritating","jailing","jamming","joking","judging","juggling","jumping","keeping","killing","kissing","kneeling","knitting","knocking","knotting","knowing","landing","lasting","launching","laying","leading","leaning","learning","leaving","lecturing","lending","letting","leveling","licensing","licking","lifting","lightening","lighting","liking","living","loading","locking","logging","longing","looking","losing","loving","lying","maintaining","making","manipulating","manning","manufacturing","mapping","marching","marketing","marrying","matching","mating","mattering","meaning","measuring","meddling","mediating","meeting","melting","memorizing","mending","milking","mining","misleading","missing","mistaking","misunderstanding","moaning","modifying","monitoring","mooring","motivating","moving","muddling","mugging","multiplying","murdering","nailing","naming","navigating","needing","negotiating","nesting","nodding","nominating","normalizing","noticing","noting","numbering","obeying","objecting","observing","occurring","offending","offering","officiating","operating","ordering","organizing","orienteering","originating","overcoming","overdoing","overdrawing","overflowing","overhearing","overthrowing","owing","owning","packing","paddling","painting","parking","participating","parting","passing","pasting","patting","pecking","pedaling","peeling","perceiving","performing","permitting","phoning","photographing","piloting","pinching","pining","pinpointing","planing","planting","pleading","plugging","poking","polishing","possessing","pouring","praising","praying","preaching","preceding","predicting","preferring","preparing","prescribing","presenting","presetting","presiding","pressing","pretending","preventing","pricking","processing","procuring","producing","professing","programming","progressing","projecting","promising","promoting","proofreading","proposing","protecting","providing","proving","publicizing","pumping","punching","puncturing","purchasing","putting","questioning","queueing","quitting","racing","radiating","raising","ranking","rating","reaching","reading","realigning","realizing","reasoning","receiving","recognizing","reconciling","recording","recruiting","reducing","referring","reflecting","regulating","reigning","reinforcing","rejecting","rejoicing","relating","relaxing","releasing","relying","remaining","remembering","reminding","removing","rendering","reorganizing","repairing","repeating","replacing","replying","representing","requesting","rescuing","researching","resolving","responding","restoring","restructuring","retiring","retrieving","returning","reviewing","revising","rhyming","riding","ringing","rinsing","rising","risking","rocking","rolling","rotting","rubbing","ruining","running","sacking","satisfying","sawing","saying","scaring","scattering","scheduling","scolding","scorching","scraping","scratching","screwing","scribbling","scrubbing","sealing","searching","securing","seeing","seeking","selecting","selling","sending","sensing","separating","servicing","serving","setting","settling","sewing","shading","shaking","shaping","sharing","shearing","sheltering","shining","shivering","shocking","shoeing","shooting","shopping","showing","shrinking","shrugging","shutting","sighing","signaling","signing","simplifying","singing","sinking","sipping","siting","sketching","skiing","skipping","slapping","slaying","sleeping","sliding","slinging","slipping","slitting","smashing","smelling","smiling","smiting","smoking","sneaking","sneezing","sniffing","snoring","snowing","soaking","solving","soothing","soothsaying","sorting","sowing","sparking","sparkling","speaking","speeding","spelling","spending","spilling","spinning","spiting","splitting","spoiling","spotting","spraying","spreading","springing","sprouting","squashing","squeaking","squealing","squeezing","staining","stamping","standing","staring","starting","stealing","sticking","stimulating","stinging","stinking","stirring","stitching","stoping","storing","strapping","streamlining","strengthening","striking","striping","striving","structuring","subtracting","sucking","suffering","suggesting","summarizing","supplying","supposing","surprising","surrounding","suspending","sweating","swelling","swimming","swinging","symbolizing","systemizing","tabulating","taking","taming","taping","targeting","tasting","teaching","teasing","telephoning","telling","tempting","testing","thanking","thriving","thrusting","tickling","timing","tipping","tiring","touching","touring","towing","tracing","trading","training","transforming","transporting","trapping","treating","tricking","trotting","troubleshooting","trusting","trying","tugging","tutoring","twisting","tying","typing","undergoing","understanding","undressing","unfastening","unifying","unpacking","untidying","updating","upgrading","upholding","using","utilizing","verbalizing","vexing","visiting","wailing","waiting","walking","wandering","wanting","washing","watering","wearing","weighing","welcoming","wending","wetting","whispering","winding","winking","wiping","wishing","withstanding","wobbling","working","worrying","wrapping","wrecking","wrestling","wriggling","wringing","writing","yelling","zooming"]
    weaks = random.sample(attrs,2)
    return  '\"- <indent=%15>Terrible at {}</indent>\n- <indent=%15>Not great at {}</indent>\"'.format(weaks[0],weaks[1])

# Gloomhaven yaml files contain duplicate keys sometimes.
# This is not compatible with any known python yaml parser
# If such a parser exists, this function is unnecessary
# For the time being, it is necessary
# 
# Manually parses all files in the given directory
# If a duplicate key is found, replaces it with a unique placeholder to be reverted later
# Also caches the files for repeated character generation
def ParseForDuplicateKeysAndCacheDir(datadir,parents):
    files = [f for f in listdir(datadir) if isfile(join(datadir, f))]
    for f in files:
        if f == "LongRest.yml":
            continue
        with open("{}/{}".format(datadir,f),"r") as rf:
            lines = rf.readlines()
            lines = [line.rstrip() for line in lines]
        for i in range(len(lines)-1):
            ispaces = len(lines[i]) - len(lines[i].lstrip(' '))
            ikey = lines[i].lstrip(' ').partition(":")[0]
            if ispaces == 0 or ikey[0] == '-':
                continue
            for j in range(i+1,len(lines)):
                jspaces = len(lines[j]) - len(lines[j].lstrip(' '))
                jkey = lines[j].lstrip(' ').partition(":")[0]
                if jspaces < ispaces or jspaces == 0:
                    break
                if jspaces == ispaces:
                    if ikey == jkey:
                        lines[j] = lines[j].replace(ikey,"DuplicateKey_{}_{:02d}".format(ikey,j))
        MakeCacheFromLines(lines,f,parents)

# Single file duplicate key replacer
def ParseForDuplicateKeysAndCacheFile(file,parents):
    path, fname = split(file)
    with open(file,"r") as rf:
        lines = rf.readlines()
        lines = [line.rstrip() for line in lines]
    for i in range(len(lines)-1):
        ispaces = len(lines[i]) - len(lines[i].lstrip(' '))
        ikey = lines[i].lstrip(' ').partition(":")[0]
        if ispaces == 0 or ikey[0] == '-':
            continue
        for j in range(i+1,len(lines)):
            jspaces = len(lines[j]) - len(lines[j].lstrip(' '))
            jkey = lines[j].lstrip(' ').partition(":")[0]
            if jspaces < ispaces or jspaces == 0:
                break
            if jspaces == ispaces:
                if ikey == jkey:
                    lines[j] = lines[j].replace(ikey,"DuplicateKey_{}_{:02d}".format(ikey,j))
    MakeCacheFromLines(lines,fname,parents)

# Takes a list of lines and re-saves it in a cache directory
def MakeCacheFromLines(data,filename,parents):
    path = "cache/"
    for parent in parents:
        path = path + parent + "/"
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    with open('{}{}'.format(path, filename), 'w') as wf:
        for line in data:
            wf.write(f"{line}\n")

# Reverses the duplicate key replacer function
# This is run as a final step in the random mercenary creator on all generated yaml files
def ReconstructDuplicateKeysDir(datadir):
    files = [f for f in listdir(datadir) if isfile(join(datadir, f))]
    for f in files:
        with open("{}/{}".format(datadir,f),"r") as rf:
            lines = rf.readlines()
            lines = [line.rstrip() for line in lines]
        for i in range(len(lines)):
            p = re.compile(r'DuplicateKey_(.*)_\d{1,}')
            lines[i] = p.sub(r'\1',lines[i])
        with open("{}/{}".format(datadir,f),"w") as wf:
            for line in lines:
                wf.write(f"{line}\n")

# Single file version of the duplicate key reconstructor function
def ReconstructDuplicateKeysFile(file):
    path, fname = split(file)
    with open(file,"r") as rf:
        lines = rf.readlines()
        lines = [line.rstrip() for line in lines]
    for i in range(len(lines)):
        p = re.compile(r'DuplicateKey_(.*)_\d{1,}')
        lines[i] = p.sub(r'\1',lines[i])
    with open(file,"w") as wf:
        for line in lines:
            wf.write(f"{line}\n")