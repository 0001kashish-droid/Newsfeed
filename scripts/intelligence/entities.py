# Copyright (c) 2026 Kashish Bhushan — News Colossal
import re
from typing import Dict, List, Set, Any
from intelligence.sanitizer import is_quarantined_publisher

# =============================================================================
# LEXICONS & TAXONOMIES
# =============================================================================

# 1. COUNTRY_LEXICON
# Mapping lowercase text patterns to ISO 2-letter country codes.
_COUNTRY_MAPPINGS = {
    'US': ['US', 'u.s.', 'usa', 'united states', 'america', 'american', 'americans', 'washington'],
    'UK': ['uk', 'u.k.', 'united kingdom', 'britain', 'british', 'london'],
    'CN': ['china', 'chinese', 'beijing', 'prc'],
    'RU': ['russia', 'russian', 'russians', 'moscow'],
    'UA': ['ukraine', 'ukrainian', 'ukrainians', 'kyiv', 'kiev'],
    'IL': ['israel', 'israeli', 'israelis', 'tel aviv', 'jerusalem'],
    'PS': ['palestine', 'palestinian', 'palestinians', 'gaza', 'west bank', 'hamas'],
    'TW': ['taiwan', 'taiwanese', 'taipei'],
    'IR': ['iran', 'iranian', 'iranians', 'tehran'],
    'KP': ['north korea', 'north korean', 'dprk', 'pyongyang'],
    'KR': ['south korea', 'south korean', 'seoul'],
    'JP': ['japan', 'japanese', 'tokyo'],
    'DE': ['germany', 'german', 'germans', 'berlin'],
    'FR': ['france', 'french', 'paris'],
    'IT': ['italy', 'italian', 'italians', 'rome'],
    'CA': ['canada', 'canadian', 'canadians', 'ottawa'],
    'IN': ['india', 'indian', 'indians', 'new delhi'],
    'BR': ['brazil', 'brazilian', 'brazilians', 'brasilia'],
    'ZA': ['south africa', 'south african', 'pretoria'],
    'AU': ['australia', 'australian', 'australians', 'canberra'],
    'TR': ['turkey', 'turkish', 'turkiye', 'ankara'],
    'SA': ['saudi arabia', 'saudi', 'saudis', 'riyadh'],
    'EG': ['egypt', 'egyptian', 'egyptians', 'cairo'],
    'SY': ['syria', 'syrian', 'syrians', 'damascus'],
    'LB': ['lebanon', 'lebanese', 'beirut'],
    'AF': ['afghanistan', 'afghan', 'afghans', 'kabul', 'taliban'],
    'MM': ['myanmar', 'burma', 'burmese'],
    'MX': ['mexico', 'mexican', 'mexicans', 'mexico city'],
    'AR': ['argentina', 'argentine', 'argentines', 'buenos aires'],
    'ID': ['indonesia', 'indonesian', 'indonesians', 'jakarta'],
    'NG': ['nigeria', 'nigerian', 'nigerians', 'abuja'],
    'KE': ['kenya', 'kenyan', 'kenyans', 'nairobi'],
    'ET': ['ethiopia', 'ethiopian', 'ethiopians', 'addis ababa'],
    'PK': ['pakistan', 'pakistani', 'pakistanis', 'islamabad'],
    'BD': ['bangladesh', 'bangladeshi', 'dhaka'],
    'VN': ['vietnam', 'vietnamese', 'hanoi'],
    'TH': ['thailand', 'thai', 'bangkok'],
    'PH': ['philippines', 'philippine', 'filipino', 'filipinos', 'manila'],
    'MY': ['malaysia', 'malaysian', 'kuala lumpur'],
    'SG': ['singapore', 'singaporean'],
    'NZ': ['new zealand', 'kiwi', 'wellington'],
    'ES': ['spain', 'spanish', 'spaniards', 'madrid'],
    'PL': ['poland', 'polish', 'poles', 'warsaw'],
    'NL': ['netherlands', 'dutch', 'amsterdam', 'the hague'],
    'SE': ['sweden', 'swedish', 'swedes', 'stockholm'],
    'CH': ['switzerland', 'swiss', 'bern', 'geneva'],
    'AT': ['austria', 'austrian', 'vienna'],
    'GR': ['greece', 'greek', 'greeks', 'athens'],
    'PT': ['portugal', 'portuguese', 'lisbon'],
    'IE': ['ireland', 'irish', 'dublin'],
    'BE': ['belgium', 'belgian', 'brussels'],
    'DK': ['denmark', 'danish', 'danes', 'copenhagen'],
    'FI': ['finland', 'finnish', 'finns', 'helsinki'],
    'NO': ['norway', 'norwegian', 'norwegians', 'oslo'],
    'CZ': ['czech republic', 'czechia', 'czech', 'prague'],
    'HU': ['hungary', 'hungarian', 'hungarians', 'budapest'],
    'RO': ['romania', 'romanian', 'bucharest'],
    'BG': ['bulgaria', 'bulgarian', 'sofia'],
    'RS': ['serbia', 'serbian', 'belgrade'],
    'HR': ['croatia', 'croatian', 'zagreb'],
    'CU': ['cuba', 'cuban', 'havana'],
    'VE': ['venezuela', 'venezuelan', 'caracas'],
    'CO': ['colombia', 'colombian', 'bogota'],
    'CL': ['chile', 'chilean', 'santiago'],
    'PE': ['peru', 'peruvian', 'lima'],
    # Regional Groupings
    'EU': ['EU', 'european union', 'europe', 'european'],
    'ASEAN': ['asean', 'southeast asia'],
}

COUNTRY_LEXICON = {}
for code, patterns in _COUNTRY_MAPPINGS.items():
    for pattern in patterns:
        COUNTRY_LEXICON[pattern] = code

COUNTRY_NAMES = {
    'US': 'United States', 'UK': 'United Kingdom', 'CN': 'China', 'RU': 'Russia',
    'UA': 'Ukraine', 'IL': 'Israel', 'PS': 'Palestine', 'TW': 'Taiwan',
    'IR': 'Iran', 'KP': 'North Korea', 'KR': 'South Korea', 'JP': 'Japan',
    'DE': 'Germany', 'FR': 'France', 'IT': 'Italy', 'CA': 'Canada',
    'IN': 'India', 'BR': 'Brazil', 'ZA': 'South Africa', 'AU': 'Australia',
    'TR': 'Turkey', 'SA': 'Saudi Arabia', 'EG': 'Egypt', 'SY': 'Syria', 'LB': 'Lebanon',
    'AF': 'Afghanistan', 'MM': 'Myanmar', 'MX': 'Mexico', 'AR': 'Argentina',
    'ID': 'Indonesia', 'NG': 'Nigeria', 'KE': 'Kenya', 'ET': 'Ethiopia',
    'PK': 'Pakistan', 'BD': 'Bangladesh', 'VN': 'Vietnam', 'TH': 'Thailand',
    'PH': 'Philippines', 'MY': 'Malaysia', 'SG': 'Singapore', 'NZ': 'New Zealand',
    'ES': 'Spain', 'PL': 'Poland', 'NL': 'Netherlands', 'SE': 'Sweden',
    'CH': 'Switzerland', 'AT': 'Austria', 'GR': 'Greece', 'PT': 'Portugal',
    'IE': 'Ireland', 'BE': 'Belgium', 'DK': 'Denmark', 'FI': 'Finland',
    'NO': 'Norway', 'CZ': 'Czech Republic', 'HU': 'Hungary', 'RO': 'Romania',
    'BG': 'Bulgaria', 'RS': 'Serbia', 'HR': 'Croatia', 'CU': 'Cuba',
    'VE': 'Venezuela', 'CO': 'Colombia', 'CL': 'Chile', 'PE': 'Peru',
    'EU': 'European Union', 'ASEAN': 'ASEAN'
}

# 2. LEADER_LEXICON
_LEADER_MAPPINGS = {
    'Donald Trump': ['trump', 'donald trump'],
    'Joe Biden': ['biden', 'joe biden'],
    'Kamala Harris': ['harris', 'kamala', 'kamala harris'],
    'Vladimir Putin': ['putin', 'vladimir putin'],
    'Xi Jinping': ['xi', 'xi jinping', 'jinping'],
    'Narendra Modi': ['modi', 'narendra modi'],
    'Keir Starmer': ['starmer', 'keir starmer'],
    'Rishi Sunak': ['sunak', 'rishi sunak'],
    'Emmanuel Macron': ['macron', 'emmanuel macron'],
    'Olaf Scholz': ['scholz', 'olaf scholz'],
    'Justin Trudeau': ['trudeau', 'justin trudeau'],
    'Fumio Kishida': ['kishida', 'fumio kishida'],
    'Shigeru Ishiba': ['ishiba', 'shigeru ishiba'],
    'Giorgia Meloni': ['meloni', 'giorgia meloni'],
    'Luiz Inácio Lula da Silva': ['lula', 'lula da silva'],
    'Jair Bolsonaro': ['bolsonaro', 'jair bolsonaro'],
    'Cyril Ramaphosa': ['ramaphosa', 'cyril ramaphosa'],
    'Anthony Albanese': ['albanese', 'anthony albanese'],
    'Yoon Suk-yeol': ['yoon', 'yoon suk-yeol'],
    'Kim Jong Un': ['kim jong un', 'kim jong-un'],
    'Lai Ching-te': ['lai', 'lai ching-te', 'william lai'],
    'Ali Khamenei': ['khamenei', 'ayatollah khamenei'],
    'Masoud Pezeshkian': ['pezeshkian', 'masoud pezeshkian'],
    'Benjamin Netanyahu': ['netanyahu', 'benjamin netanyahu'],
    'Mahmoud Abbas': ['abbas', 'mahmoud abbas'],
    'Yahya Sinwar': ['sinwar', 'yahya sinwar'],
    'Volodymyr Zelenskyy': ['zelensky', 'zelenskyy', 'volodymyr zelenskyy', 'volodymyr zelensky'],
    'Recep Tayyip Erdogan': ['erdogan', 'recep tayyip erdogan'],
    'Mohammed bin Salman': ['mbs', 'mohammed bin salman', 'bin salman'],
    'Bashar al-Assad': ['assad', 'bashar al-assad', 'bashar assad'],
    'Viktor Orban': ['orban', 'viktor orban'],
    'Ursula von der Leyen': ['von der leyen', 'ursula von der leyen'],
    'António Guterres': ['guterres', 'antonio guterres'],
    'Mark Rutte': ['rutte', 'mark rutte'],
    'Tedros Adhanom Ghebreyesus': ['tedros', 'tedros adhanom ghebreyesus'],
    'Kristalina Georgieva': ['georgieva', 'kristalina georgieva'],
    'Ajay Banga': ['banga', 'ajay banga'],
    'Elon Musk': ['musk', 'elon musk'],
    'Mark Zuckerberg': ['zuckerberg', 'mark zuckerberg'],
    'Sam Altman': ['altman', 'sam altman'],
    'Sundar Pichai': ['pichai', 'sundar pichai'],
    'Satya Nadella': ['nadella', 'satya nadella'],
    'Tim Cook': ['tim cook'],
    'Jensen Huang': ['jensen huang', 'huang']
}

LEADER_LEXICON = {}
for name, patterns in _LEADER_MAPPINGS.items():
    for pattern in patterns:
        LEADER_LEXICON[pattern] = name

# 3. ORGANIZATION_LEXICON & COMPANY_LEXICON
_ORG_MAPPINGS = {
    'UN': ['UN', 'u.n.', 'united nations'],
    'NATO': ['nato', 'north atlantic treaty organization'],
    'WHO': ['WHO', 'w.h.o.', 'world health organization'],
    'IMF': ['imf', 'i.m.f.', 'international monetary fund'],
    'World Bank': ['world bank'],
    'WTO': ['wto', 'w.t.o.', 'world trade organization'],
    'OPEC': ['opec'],
    'ICC': ['icc', 'i.c.c.', 'international criminal court'],
    'BRICS': ['brics'],
    'G7': ['g7', 'g-7', 'group of seven'],
    'G20': ['g20', 'g-20', 'group of twenty'],
    'African Union': ['african union', 'au'],
    'Supreme Court': ['supreme court', 'scotus'],
    'Pentagon': ['pentagon', 'department of defense', 'dod'],
    'Congress': ['congress', 'senate', 'house of representatives'],
    'Parliament': ['parliament'],
    'European Commission': ['european commission', 'ec'],
    'Kremlin': ['kremlin'],
    'White House': ['white house'],
    'CIA': ['cia', 'c.i.a.', 'central intelligence agency'],
    'FBI': ['fbi', 'f.b.i.', 'federal bureau of investigation'],
    'NSA': ['nsa', 'n.s.a.', 'national security agency'],
    'MI6': ['mi6', 'm.i.6'],
    'Mossad': ['mossad'],
    'NASA': ['nasa'],
    'ISRO': ['isro'],
    'ESA': ['esa', 'european space agency'],
    'Federal Reserve': ['federal reserve', 'the fed'],
    'ECB': ['ecb', 'european central bank'],
    'Bank of England': ['bank of england', 'boe'],
    'SEC': ['sec', 'securities and exchange commission'],
    'Wall Street': ['wall street']
}

ORGANIZATION_LEXICON = {}
for name, patterns in _ORG_MAPPINGS.items():
    for pattern in patterns:
        ORGANIZATION_LEXICON[pattern] = name

_COMPANY_MAPPINGS = {
    'Apple': ['apple'],
    'Google': ['google', 'alphabet'],
    'Microsoft': ['microsoft'],
    'Amazon': ['amazon'],
    'Meta': ['meta', 'facebook', 'instagram', 'whatsapp'],
    'Nvidia': ['nvidia'],
    'OpenAI': ['openai'],
    'Anthropic': ['anthropic'],
    'Tesla': ['tesla'],
    'Samsung': ['samsung'],
    'TSMC': ['tsmc', 'taiwan semiconductor'],
    'Huawei': ['huawei'],
    'SpaceX': ['spacex']
}

COMPANY_LEXICON = {}
for name, patterns in _COMPANY_MAPPINGS.items():
    for pattern in patterns:
        COMPANY_LEXICON[pattern] = name

# 4. ACTION_LEXICON
ACTION_CATEGORIES = {
    'conflict': ['attack', 'bomb', 'strike', 'invade', 'missile', 'war', 'assault', 'siege', 'shell', 'drone strike', 'airstrike'],
    'diplomacy': ['negotiate', 'summit', 'treaty', 'ceasefire', 'peace', 'talks', 'agreement', 'deal', 'accord', 'pact'],
    'legislation': ['pass', 'ban', 'regulate', 'law', 'bill', 'act', 'legislation', 'vote', 'approve', 'ratify', 'veto', 'repeal'],
    'economy': ['inflation', 'recession', 'gdp', 'trade', 'tariff', 'sanction', 'market', 'stocks', 'crash', 'surge', 'rally', 'interest rate'],
    'crisis': ['earthquake', 'flood', 'hurricane', 'wildfire', 'pandemic', 'outbreak', 'famine', 'collapse', 'disaster', 'emergency'],
    'justice': ['arrest', 'indict', 'convict', 'sentence', 'trial', 'verdict', 'corruption', 'fraud', 'scandal', 'investigation', 'probe'],
    'technology': ['launch', 'release', 'breakthrough', 'ai', 'quantum', 'chip', 'semiconductor', 'patent', 'innovation'],
    'election': ['election', 'vote', 'poll', 'ballot', 'campaign', 'candidate', 'primary', 'referendum', 'runoff'],
}
ACTION_LEXICON = {}
for category, verbs in ACTION_CATEGORIES.items():
    for verb in verbs:
        ACTION_LEXICON[verb] = category

# 5. DOMAIN_TAXONOMY
DOMAIN_TAXONOMY = {
    'geopolitics': ['war', 'military', 'defense', 'nuclear', 'nato', 'sanctions', 'territory', 'sovereignty', 'alliance', 'conflict', 'ceasefire', 'troops'],
    'economics': ['gdp', 'inflation', 'recession', 'trade', 'tariff', 'market', 'stocks', 'bonds', 'currency', 'fiscal', 'monetary', 'debt', 'deficit'],
    'technology': ['ai', 'artificial intelligence', 'quantum', 'semiconductor', 'chip', 'software', 'algorithm', 'data', 'cyber', 'blockchain', 'robot'],
    'climate': ['climate', 'emissions', 'carbon', 'renewable', 'solar', 'wind', 'fossil', 'temperature', 'arctic', 'sea level', 'deforestation'],
    'health': ['pandemic', 'vaccine', 'disease', 'cancer', 'virus', 'outbreak', 'hospital', 'mental health', 'drug', 'treatment', 'clinical'],
    'rights': ['human rights', 'protest', 'freedom', 'censorship', 'democracy', 'authoritarian', 'refugee', 'migrant', 'discrimination', 'equality'],
    'science': ['space', 'nasa', 'planet', 'genome', 'physics', 'discovery', 'research', 'study', 'experiment', 'species'],
    'governance': ['legislation', 'regulation', 'policy', 'reform', 'constitution', 'court', 'ruling', 'amendment', 'executive order'],
}
DOMAIN_LEXICON = {}
for domain, keywords in DOMAIN_TAXONOMY.items():
    for kw in keywords:
        DOMAIN_LEXICON[kw] = domain


# =============================================================================
# COMPILED REGEX ENGINES
# =============================================================================

def _build_regex(lexicon: Dict[str, Any]) -> re.Pattern:
    # Sort by length descending to match longest phrases first
    keys = sorted(lexicon.keys(), key=len, reverse=True)
    parts = []
    for k in keys:
        esc = re.escape(k)
        start_b = r'\b' if k[0].isalnum() else r'(?<!\w)'
        end_b = r'\b' if k[-1].isalnum() else r'(?!\w)'
        parts.append(f"{start_b}{esc}{end_b}")
    pattern = '|'.join(parts)
    return re.compile(pattern, re.IGNORECASE)

_RE_COUNTRY = _build_regex(COUNTRY_LEXICON)
_RE_LEADER = _build_regex(LEADER_LEXICON)
_RE_ORG = _build_regex(ORGANIZATION_LEXICON)
_RE_COMPANY = _build_regex(COMPANY_LEXICON)
_RE_ACTION = _build_regex(ACTION_LEXICON)
_RE_DOMAIN = _build_regex(DOMAIN_LEXICON)


# =============================================================================
# EXTRACTION FUNCTIONS
# =============================================================================

def _extract(text: str, regex: re.Pattern, lexicon: Dict[str, str], name_map: Dict[str, str] = None, type_name: str = None) -> List[Dict[str, str]]:
    seen = set()
    results = []
    
    for match in regex.finditer(text):
        raw_token = match.group(0)
        match_lower = raw_token.lower()
        key = lexicon.get(raw_token) or lexicon.get(match_lower)
        if not key:
            continue
            
        # Acronym & pronoun collision guard for organizations and countries (e.g. WHO, US, UN, EU)
        if type_name in ('country', 'organization', 'company'):
            if match_lower in ('who', 'us', 'un', 'eu'):
                # Must be exact uppercase in source text (WHO, not 'who'; US, not 'us')
                if not raw_token.isupper() or raw_token not in ('WHO', 'US', 'UN', 'EU'):
                    continue
            elif len(raw_token) <= 3 and '.' not in raw_token and key in ('US', 'WHO', 'UN', 'EU', 'UK', 'IMF', 'WTO', 'ICC', 'G7', 'G20', 'AU', 'CIA', 'FBI', 'NSA', 'SEC', 'ECB', 'ESA'):
                if not raw_token.isupper():
                    continue

        if key not in seen:
            seen.add(key)
            if type_name == 'country':
                results.append({'code': key, 'name': name_map[key]})
            elif type_name == 'leader':
                results.append({'name': key, 'matched': match_lower})
            elif type_name in ('organization', 'company'):
                results.append({'name': key, 'matched': match_lower})
                
    return results


class SyntacticActorGrammar:
    """
    Pure Python standard library rule-based syntactic actor extraction automaton (R2, R6).
    Extracts 5W1H Active Agents, Impacted Populations, Collective Factions,
    and Sovereign Regional Stakeholders without external NLP packages.
    """

    # 8 Canonical Collective Factions (Taxonomy & Lexicon)
    COLLECTIVE_FACTIONS = [
        (
            "Insurgent / Rebel Factions",
            re.compile(
                r'\b(?:tigray\s+rebel\s+groups?|rebel\s+groups?|rebels?|insurgents?|militias?|'
                r'guerrillas?|junta|separatists?|paramilitaries?|paramilitary|fighters?|'
                r'tplf|rapid\s+support\s+forces|rsf|houthis?|hamas|hezbollah|taliban|'
                r'wagner(?:\s+group)?|m23|sdf|pkk)\b',
                re.IGNORECASE
            )
        ),
        (
            "Military Command / Armed Forces",
            re.compile(
                r'\b(?:military\s+command|military|army|armed\s+forces|navy|air\s+force|'
                r'defense\s+forces?|troops?|soldiers?|commandos?|generals?|commanders?|'
                r'pentagon|idf|pla|guardsmen)\b',
                re.IGNORECASE
            )
        ),
        (
            "Civic Activists / Protesters",
            re.compile(
                r'\b(?:civic\s+activists?|protesters?|demonstrators?|activists?|strikers?|'
                r'dissidents?|marchers?|union\s+workers?|trade\s+unions?|tenant\s+unions?|'
                r'civic\s+groups?|advocates?|reformers?)\b',
                re.IGNORECASE
            )
        ),
        (
            "Civilians & Impacted Communities",
            re.compile(
                r'\b(?:civilians?|residents?|citizens?|villagers?|refugees?|'
                r'displaced\s+families?|displaced\s+persons?|hostages?|detainees?|casualties?|'
                r'survivors?|migrants?|asylum\s+seekers?|bystanders?|passengers?|'
                r'boys?\s+as\s+young\s+as\s+\d+|children|families|pensioners?)\b',
                re.IGNORECASE
            )
        ),
        (
            "Regulatory & State Authorities",
            re.compile(
                r'\b(?:regulators?|watchdogs?|commissions?|ministry|parliament|'
                r'congress|senate|officials?|central\s+bank|monetary\s+authority|'
                r'sec|ftc|epa|fda|faa|fcc|ecb)\b',
                re.IGNORECASE
            )
        ),
        (
            "Judicial & Investigative Bodies",
            re.compile(
                r'\b(?:supreme\s+court|courts?|judges?|prosecutors?|grand\s+jury|'
                r'magistrates?|tribunal|investigators?|police|detectives?|'
                r'special\s+counsel|cbi|fbi)\b',
                re.IGNORECASE
            )
        ),
        (
            "Diplomatic Envoys",
            re.compile(
                r'\b(?:diplomats?|envoys?|negotiators?|mediators?|ambassadors?|'
                r'peacekeepers?|delegations?|un\s+envoys?)\b',
                re.IGNORECASE
            )
        ),
        (
            "Scientific & Research Teams",
            re.compile(
                r'\b(?:scientists?|researchers?|engineers?|physicists?|biologists?|'
                r'astronomers?|archaeologists?|lab\s+workers?|technicians?|analysts?)\b',
                re.IGNORECASE
            )
        )
    ]

    # Verb Anchor Lexicon across major headline action categories
    _VERB_PATTERNS = [
        # Conflict / Kinetic
        r'\b(targets?|targeted|targeting|attacks?|attacked|attacking|bombs?|bombed|bombing|strikes?|struck|striking|'
        r'invades?|invaded|invading|kills?|killed|killing|recruits?|recruited|recruiting|'
        r'seizes?|seized|seizing|shells?|shelled|shelling|fires?|fired|firing|shoots?|shot|shooting|'
        r'(?:launch|launches)|launched|launching|intercepts?|intercepted|intercepting|advances?|advanced|advancing|'
        r'retreats?|retreated|retreating)\b',
        # Regulatory / Legal / Judicial
        r'\b(interviews?|interviewed|interviewing|indicts?|indicted|indicting|arrests?|arrested|arresting|sues?|sued|suing|'
        r'probes?|probed|probing|investigates?|investigated|investigating|bans?|banned|banning|'
        r'blocks?|blocked|blocking|fines?|fined|fining|rules?|ruled|ruling|sentences?|sentenced|sentencing|'
        r'(?:pass|passes)|passed|passing|rejects?|rejected|rejecting|(?:veto|vetoes)|vetoed|vetoing|files?|filed|filing)\b',
        # Diplomatic / Strategic
        r'\b(opens?|opened|opening|signs?|signed|signing|agrees?|agreed|agreeing|warns?|warned|warning|'
        r'urges?|urged|urging|demands?|demanded|demanding|meets?|met|meeting|hosts?|hosted|hosting|'
        r'seeks?|sought|seeking|vows?|vowed|vowing|pledges?|pledged|pledging|'
        r'(?:backs\b|backed\b|backing\b|back\b(?!\s+(?:to|on|in|at|from)\b))|'
        r'resumes?|resumed|resuming|renews?|renewed|renewing|convenes?|convened|convening|concludes?|concluded|concluding|'
        r'(?:march|marches)|marched|marching)\b',
        # Economic / Corporate / Tech
        r'\b(buys?|bought|buying|sells?|sold|selling|hikes?|hiked|hiking|cuts?|cut|cutting|'
        r'raises?|raised|raising|slumps?|slumped|slumping|surges?|surged|surging|imposes?|imposed|imposing|'
        r'weighs?|weighed|weighing|explores?|explored|exploring|'
        r'introduces?|introduced|introducing|unveils?|unveiled|unveiling|reveals?|revealed|revealing|'
        r'announces?|announced|announcing|releases?|released|releasing)\b',
        # Scientific / Research / Discovery
        r'\b(discovers?|discovered|discovering|develops?|developed|developing|creates?|created|creating|'
        r'(?:identify|identifies)|identified|identifying|tests?|tested|testing|builds?|built|building)\b',
        # Humanitarian / Status / Life Events / Escalation
        r'\b(faces?|faced|facing|dies?|died|dying|succumbs?|succumbed|succumbing|survives?|survived|surviving|'
        r'wins?|won|winning|loses?|lost|losing|resigns?|resigned|resigning|'
        r'deepens?|deepened|deepening|worsens?|worsened|worsening|escalates?|escalated|escalating)\b'
    ]
    _RE_VERBS = re.compile('|'.join(_VERB_PATTERNS), re.IGNORECASE)

    # Clause segmentation conjunctions (guarding idioms like "as young as", "as old as")
    _RE_CLAUSE_SPLIT = re.compile(
        r'\s+(?:as\s+(?!young\s+as|old\s+as|well\s+as|many\s+as|much\s+as)|while|after|amid|before|when|because|where)\s+',
        re.IGNORECASE
    )
    
    # Prepositions for noun phrase boundary
    _RE_PREPOSITIONS = re.compile(r'\s+(?:in|on|at|to|for|from|with|by|against|over|into|under)\s+', re.IGNORECASE)

    # Editorial quotes and adverbs to strip from subject/object
    _RE_QUOTES = re.compile(r"^[\s'\"‘“’”\(\)\[\]]+|[\s'\"‘“’”\(\)\[\]]+$")
    _RE_ADVERBS = re.compile(r'\b(?:forcibly|allegedly|reportedly|secretly|officially|closely|still|now|again|sharply|heavily)\s*', re.IGNORECASE)

    # Non-agent abstract event nouns that should trigger sovereign stakeholder resolution
    ABSTRACT_EVENT_WORDS = frozenset({
        'talks', 'summit', 'summits', 'meeting', 'meetings', 'conference', 'conferences',
        'deal', 'deals', 'agreement', 'agreements', 'pact', 'pacts', 'treaty', 'treaties',
        'investigation', 'investigations', 'probe', 'probes', 'report', 'reports',
        'study', 'studies', 'crisis', 'crises', 'earthquake', 'earthquakes', 'flood', 'floods',
        'inflation', 'war', 'wars', 'conflict', 'conflicts', 'price', 'prices',
        'stock', 'stocks', 'market', 'markets', 'trade', 'trades', 'economy', 'economies',
        'dispute', 'disputes', 'trial', 'trials', 'hearing', 'hearings', 'row', 'rows',
        'scandal', 'scandals', 'crash', 'crashes', 'surge', 'surges', 'rally', 'rallies',
        'slump', 'slumps', 'effort', 'efforts', 'plan', 'plans', 'proposal', 'proposals',
        'measure', 'measures', 'bill', 'bills', 'law', 'laws', 'election', 'elections',
        'vote', 'votes', 'poll', 'polls', 'ballot', 'ballots', 'visit', 'visits',
        'trip', 'trips', 'talk', 'indicator', 'indicators', 'rate', 'rates',
        'yield', 'yields', 'outlook', 'forecast', 'forecasts', 'trend', 'trends',
        'roundup', 'release', 'releases'
    })

    @classmethod
    def _is_valid_syntactic_subject(cls, s: str) -> bool:
        """
        Validates whether a candidate string forms a concise, valid syntactic subject noun phrase.
        Constrains length to <= 5 words and disallows questions, clauses, and conversational openers.
        """
        if not s or not isinstance(s, str):
            return False
        clean = s.strip()
        words = clean.split()
        if not (1 <= len(words) <= 5):
            return False
        if len(clean) < 2:
            return False
        if any(ch in clean for ch in ('?', '!', ';', ':', '"', '“', '”', '‘', '’')):
            return False
        if clean.endswith(('?', '!', '.', ',')):
            return False

        trailing_invalid = {'to', 'is', 'are', 'was', 'were', 'the', 'a', 'an', 'in', 'on', 'at', 'for', 'from', 'with', 'by', 'and', 'or', 'as'}
        if words[-1].lower().strip("',\"") in trailing_invalid:
            return False

        first_word = words[0].lower().strip("',\"")
        if first_word in (
            'what', 'when', 'where', 'why', 'how', 'who', 'which', 'can', 'could', 'should', 'would',
            'is', 'are', 'was', 'were', 'looking', 'we', 'here', 'every', 'come', 'there', 'let', 'lets',
            'it', 'its', 'they', 'you', 'i'
        ):
            return False

        clean_lower = clean.lower()
        if any(frag in clean_lower for frag in ('there is', 'there are', 'there was', 'there were', 'all the way', 'every day', 'every week', 'as far as')):
            return False
        return True

    @classmethod
    def _extract_faction_noun_phrase(cls, text: str, matched_text: str) -> str:
        """
        Extracts a concise noun phrase (1 to 4 words) around a collective faction match,
        including any preceding proper noun or title modifier (e.g. 'Houthi fighters', 'Special counsel').
        """
        if not text or not matched_text:
            return matched_text
        pat = re.compile(
            r'\b((?:[A-Z0-9][a-zA-Z0-9\'-]+\s+){0,2}' + re.escape(matched_text) +
            r'(?:\s+(?:fighters|rebels|forces|groups?|unions?|command|council|court|officials?))?)\b',
            re.IGNORECASE
        )
        m = pat.search(text)
        if m:
            candidate = m.group(1).strip()
            if 1 <= len(candidate.split()) <= 4 and cls._is_valid_syntactic_subject(candidate):
                return candidate
        return matched_text

    @classmethod
    def extract_syntactic_frame(cls, title: str) -> Dict[str, str]:
        """
        Parses title into syntactic frame: subject, verb, object.
        Uses clause segmentation, verb anchor detection, and NP boundary analysis.
        """
        if not title:
            return {"subject": "", "verb": "", "object": ""}

        text = title.strip()
        
        # 0. Clean non-restrictive relative clauses enclosed in commas (e.g. ", who won an Oscar,")
        working_text = re.sub(r',\s*(?:who|which|that)\b[^,]+,', '', text)
        # Clean trailing attribution clauses (e.g. ", court told", ", police say")
        working_text = re.sub(r',\s*(?:court told|police say|officials say|sources say)\s*$', '', working_text, flags=re.IGNORECASE)
        
        # 1. Segment primary clause by punctuation (: — – | ;)
        # If initial segment starts with quote or has no verb while second segment has a verb, use second segment
        segments = [p.strip() for p in re.split(r'[:—–|;]', working_text) if p.strip()]
        primary_clause = segments[0] if segments else working_text
        if len(segments) > 1 and (re.match(r"^['\"‘“]", segments[0]) or not cls._RE_VERBS.search(segments[0])):
            if cls._RE_VERBS.search(segments[1]):
                primary_clause = segments[1]
        
        # 2. Check subordinate clauses
        sub_clauses = cls._RE_CLAUSE_SPLIT.split(primary_clause)
        working_clause = primary_clause
        if len(sub_clauses) > 1:
            if cls._RE_VERBS.search(sub_clauses[0]):
                working_clause = sub_clauses[0].strip()

        # 3. Detect verb anchor
        m_verb = cls._RE_VERBS.search(working_clause)
        if not m_verb:
            m_verb = cls._RE_VERBS.search(text)
            if not m_verb:
                subj = cls._RE_QUOTES.sub('', primary_clause).strip()
                subj = re.sub(r'^(?:the|a|an)\s+', '', subj, flags=re.IGNORECASE).strip()
                subj = re.sub(r'\s+(?:to|is|are|was|were)\s*$', '', subj, flags=re.IGNORECASE).strip()
                if is_quarantined_publisher(subj) or subj in ('Editorial Bureau', 'Syndicated Bureau'):
                    subj = ""
                return {"subject": subj, "verb": "", "object": ""}
            working_clause = text

        verb = m_verb.group(0).strip()
        verb_start = m_verb.start()
        verb_end = m_verb.end()

        # 4. Extract subject
        pre_verb = working_clause[:verb_start].strip()
        subj = cls._RE_QUOTES.sub('', pre_verb).strip()
        subj = cls._RE_ADVERBS.sub('', subj).strip()
        subj = cls._RE_QUOTES.sub('', subj).strip()
        subj = re.sub(r'^(?:the|a|an)\s+', '', subj, flags=re.IGNORECASE).strip()
        subj = re.sub(r'\s+(?:to|is|are|was|were)\s*$', '', subj, flags=re.IGNORECASE).strip()

        # 5. Extract object
        post_verb = working_clause[verb_end:].strip()
        post_verb = cls._RE_QUOTES.sub('', post_verb).strip()

        m_idiom = re.match(r'(?:boys?|girls?|children|men|women|people)\s+as\s+young\s+as\s+\d+', post_verb, re.IGNORECASE)
        if m_idiom:
            obj = m_idiom.group(0).strip()
        else:
            prep_parts = cls._RE_PREPOSITIONS.split(post_verb)
            obj = prep_parts[0].strip() if prep_parts else post_verb

        obj = cls._RE_QUOTES.sub('', obj).strip()
        obj = re.sub(r'^(?:the|a|an)\s+', '', obj, flags=re.IGNORECASE).strip()
        obj = re.sub(r'^(?:in|on|at|to|for|from|with|by|against|over|into|under)\s+', '', obj, flags=re.IGNORECASE).strip()

        # Zero publisher leakage
        if is_quarantined_publisher(subj) or subj in ('Editorial Bureau', 'Syndicated Bureau'):
            subj = ""
        if is_quarantined_publisher(obj) or obj in ('Editorial Bureau', 'Syndicated Bureau'):
            obj = ""

        return {
            "subject": subj,
            "verb": verb,
            "object": obj
        }

    @classmethod
    def extract_collective_factions(cls, text: str) -> List[Dict[str, str]]:
        """
        Detects collective non-state factions from text across 8 canonical categories.
        """
        factions = []
        seen = set()
        for category, pattern in cls.COLLECTIVE_FACTIONS:
            for match in pattern.finditer(text):
                matched_text = match.group(0).strip()
                norm = matched_text.lower()
                if norm not in seen and not is_quarantined_publisher(matched_text):
                    seen.add(norm)
                    factions.append({
                        "category": category,
                        "matched_text": matched_text,
                        "canonical_label": f"{category} ({matched_text})"
                    })
        return factions

    @classmethod
    def extract_actors(cls, title: str, description: str = '', entities: dict = None, region: str = '') -> Dict[str, Any]:
        """
        Extracts 5W1H Primary Actors conforming to Requirement R2 specification:
        - active_agent
        - active_agent_type: 'leader' | 'collective_faction' | 'sovereign_stakeholder' | 'syntactic_subject' | None
        - impacted_population
        - impacted_type: 'impacted_community' | 'state_body' | None
        - collective_factions
        - leaders
        - sovereign_stakeholders
        - syntactic_frame: {subject, verb, object}
        """
        if entities is None:
            entities = {}

        clean_title = re.sub(r',\s*(?:court told|police say|officials say|sources say)\s*$', '', title, flags=re.IGNORECASE)

        # 1. Syntactic Frame
        frame = cls.extract_syntactic_frame(clean_title)

        # 2. Collective Factions
        factions = cls.extract_collective_factions(clean_title)
        if not factions and description:
            factions = cls.extract_collective_factions(description)

        # 3. Leaders
        leaders = [
            l['name'] for l in entities.get('leaders', [])
            if not is_quarantined_publisher(l.get('name', ''))
        ]

        # 4. Sovereign Stakeholders
        countries = entities.get('countries', [])
        sovereign_stakeholders = []
        if countries:
            sovereign_stakeholders = [c['name'] for c in countries]
        elif region and region not in ('Global', '', 'null', None):
            sovereign_stakeholders = [f"{region} Regional Stakeholders"]

        # 5. Impacted Population & Type
        impacted_population = None
        impacted_type = None

        # Check collective factions for Civilians & Impacted Communities
        for f in factions:
            if f['category'] == "Civilians & Impacted Communities":
                impacted_population = f['matched_text']
                impacted_type = "impacted_community"
                break

        # Check syntactic object if not found from factions
        if not impacted_population and frame['object']:
            obj_lower = frame['object'].lower()
            if any(w in obj_lower for w in ('civilian', 'resident', 'citizen', 'boy', 'girl', 'child', 'refugee', 'hostage', 'victim', 'family', 'people', 'migrant', 'pensioner', 'passenger', 'detainee', 'casualty', 'survivor')):
                impacted_population = frame['object']
                impacted_type = "impacted_community"
            elif any(w in obj_lower for w in ('court', 'ministry', 'parliament', 'commission', 'state', 'police', 'hospital', 'board')):
                impacted_population = frame['object']
                impacted_type = "state_body"

        # 6. Active Agent & Active Agent Type
        active_agent = None
        active_agent_type = None

        # Priority 1: Verified World Leader
        if leaders:
            active_agent = leaders[0]
            active_agent_type = "leader"
        else:
            subj = frame['subject']
            subj_lower = subj.lower()
            is_abstract_event = any(w in cls.ABSTRACT_EVENT_WORDS for w in subj_lower.split())

            # Priority 2: Collective Faction
            agent_faction = None
            title_factions = cls.extract_collective_factions(clean_title)

            # Check if subject NP itself matches any non-civilian faction
            if subj and cls._is_valid_syntactic_subject(subj):
                for f in factions:
                    if f['category'] != "Civilians & Impacted Communities":
                        if f['matched_text'].lower() in subj_lower:
                            # Keep full compound subject if it forms a clean NP
                            if frame.get('verb'):
                                agent_faction = subj
                                break
                            else:
                                if len(subj.split()) <= 3 and (subj_lower.endswith(f['matched_text'].lower()) or subj_lower == f['matched_text'].lower()):
                                    agent_faction = subj
                                else:
                                    agent_faction = cls._extract_faction_noun_phrase(subj, f['matched_text'])
                                break

            # If no subject faction, but title has a non-civilian faction and subject is not an abstract event
            if not agent_faction and title_factions and not is_abstract_event:
                for f in title_factions:
                    if f['category'] != "Civilians & Impacted Communities":
                        agent_faction = cls._extract_faction_noun_phrase(clean_title, f['matched_text'])
                        break

            if agent_faction:
                active_agent = agent_faction
                active_agent_type = "collective_faction"
            elif subj and cls._is_valid_syntactic_subject(subj) and not is_abstract_event and not is_quarantined_publisher(subj):
                # Priority 3: Syntactic Subject
                active_agent = subj
                active_agent_type = "syntactic_subject"
            elif sovereign_stakeholders:
                # Priority 4: Sovereign Regional Stakeholder
                if countries:
                    active_agent = f"{countries[0]['name']} Sovereign Authorities"
                else:
                    active_agent = sovereign_stakeholders[0]
                active_agent_type = "sovereign_stakeholder"
            elif factions:
                for f in factions:
                    if f['category'] != "Civilians & Impacted Communities":
                        candidate = f['matched_text']
                        if cls._is_valid_syntactic_subject(candidate):
                            active_agent = candidate
                            active_agent_type = "collective_faction"
                            break
            else:
                active_agent = None
                active_agent_type = None

        # 7. Strict Fallback Constraint: Sentence-Length Subjects, Punctuation Guard, and Trailing Invalid Words
        if active_agent:
            agent_words = str(active_agent).split()
            trailing_invalid = {'to', 'is', 'are', 'was', 'were', 'the', 'a', 'an', 'in', 'on', 'at', 'for', 'from', 'with', 'by', 'and', 'or', 'as'}
            if (len(agent_words) > 5 or 
                str(active_agent).endswith('?') or 
                any(ch in str(active_agent) for ch in ('?', '!', ';')) or
                agent_words[-1].lower().strip("',\"") in trailing_invalid or
                not cls._is_valid_syntactic_subject(str(active_agent))):
                if sovereign_stakeholders:
                    if countries:
                        active_agent = f"{countries[0]['name']} Sovereign Authorities"
                    else:
                        active_agent = sovereign_stakeholders[0]
                    active_agent_type = "sovereign_stakeholder"
                else:
                    active_agent = None
                    active_agent_type = None

        # 8. Strict Negative Invariant: Zero Editorial Bureau / Wire Names
        if active_agent in ('Editorial Bureau', 'Syndicated Bureau') or is_quarantined_publisher(str(active_agent)):
            active_agent = None
            active_agent_type = None
        if impacted_population in ('Editorial Bureau', 'Syndicated Bureau') or is_quarantined_publisher(str(impacted_population)):
            impacted_population = None
            impacted_type = None

        return {
            "active_agent": active_agent,
            "active_agent_type": active_agent_type,
            "impacted_population": impacted_population,
            "impacted_type": impacted_type,
            "collective_factions": factions,
            "leaders": leaders,
            "sovereign_stakeholders": sovereign_stakeholders,
            "syntactic_frame": frame
        }


def extract_entities(title: str, description: str = '', region: str = '') -> dict:
    """Extract all entities and syntactic 5W1H primary actors from title and description.
    
    Returns:
        {
            'countries': [{'code': 'US', 'name': 'United States'}, ...],
            'leaders': [{'name': 'Donald Trump', 'matched': 'trump'}, ...],
            'organizations': [{'name': 'NATO', 'matched': 'nato'}, ...],
            'companies': [{'name': 'Apple', 'matched': 'apple'}, ...],
            'actions': ['conflict', 'diplomacy'],
            'domains': ['geopolitics', 'economics'],
            'entity_count': 5,
            'entity_density': 0.42,
            'primary_actors': {
                'active_agent': '...',
                'active_agent_type': '...',
                'impacted_population': '...',
                'impacted_type': '...',
                'collective_factions': [...],
                'leaders': [...],
                'sovereign_stakeholders': [...],
                'syntactic_frame': {...}
            }
        }
    """
    text = f"{title} {description}".strip()
    if not text:
        empty_actors = SyntacticActorGrammar.extract_actors("", "", {}, region)
        return {
            'countries': [], 'leaders': [], 'organizations': [], 'companies': [],
            'actions': [], 'domains': [], 'entity_count': 0, 'entity_density': 0.0,
            'primary_actors': empty_actors
        }
        
    countries = _extract(text, _RE_COUNTRY, COUNTRY_LEXICON, COUNTRY_NAMES, 'country')
    leaders = [l for l in _extract(text, _RE_LEADER, LEADER_LEXICON, type_name='leader') if not is_quarantined_publisher(l.get('name', ''))]
    orgs = [o for o in _extract(text, _RE_ORG, ORGANIZATION_LEXICON, type_name='organization') if not is_quarantined_publisher(o.get('name', ''))]
    companies = [c for c in _extract(text, _RE_COMPANY, COMPANY_LEXICON, type_name='company') if not is_quarantined_publisher(c.get('name', ''))]

    actions = extract_action_categories(text)
    domains = extract_domains(text)
    
    entity_count = len(countries) + len(leaders) + len(orgs) + len(companies)
    
    words = len(re.findall(r'\b\w+\b', text))
    entity_density = round(entity_count / words, 4) if words > 0 else 0.0
    
    entities_dict = {
        'countries': countries,
        'leaders': leaders,
        'organizations': orgs,
        'companies': companies,
        'actions': actions,
        'domains': domains
    }
    
    primary_actors = SyntacticActorGrammar.extract_actors(title, description, entities_dict, region)
    
    return {
        'countries': countries,
        'leaders': leaders,
        'organizations': orgs,
        'companies': companies,
        'actions': actions,
        'domains': domains,
        'entity_count': entity_count,
        'entity_density': entity_density,
        'primary_actors': primary_actors
    }

def extract_action_categories(title: str) -> list:
    """Detect action categories present in the title."""
    matches = _RE_ACTION.findall(title)
    categories = set()
    for match in matches:
        match_lower = match.lower()
        if match_lower in ACTION_LEXICON:
            categories.add(ACTION_LEXICON[match_lower])
    return sorted(list(categories))

def extract_domains(title: str, description: str = '') -> list:
    """Detect intellectual domains the article belongs to."""
    text = f"{title} {description}"
    matches = _RE_DOMAIN.findall(text)
    domains = set()
    for match in matches:
        match_lower = match.lower()
        if match_lower in DOMAIN_LEXICON:
            domains.add(DOMAIN_LEXICON[match_lower])
    return sorted(list(domains))

def compute_entity_signature(entities: dict) -> str:
    """Create a compact string fingerprint from entities for dedup comparison.
    E.g., 'CN+US:Trump+Xi:NATO' — sorted deterministically."""
    
    c_codes = sorted([c['code'] for c in entities.get('countries', [])])
    l_names = sorted([l['name'].split()[-1] for l in entities.get('leaders', [])])  # Use last names for brevity
    o_names = sorted([o['name'] for o in entities.get('organizations', [])] + 
                     [c['name'] for c in entities.get('companies', [])])
    
    parts = []
    if c_codes:
        parts.append('+'.join(c_codes))
    if l_names:
        parts.append('+'.join(l_names))
    if o_names:
        parts.append('+'.join(o_names))
        
    return ':'.join(parts)
