# Copyright (c) 2026 Kashish Bhushan — News Colossal
import re
from typing import Dict, List, Set, Any

# =============================================================================
# LEXICONS & TAXONOMIES
# =============================================================================

# 1. COUNTRY_LEXICON
# Mapping lowercase text patterns to ISO 2-letter country codes.
_COUNTRY_MAPPINGS = {
    'US': ['us', 'u.s.', 'usa', 'united states', 'america', 'american', 'americans', 'washington'],
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
    'EU': ['eu', 'european union', 'europe', 'european'],
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
    'TR': 'Turkey', 'SA': 'Saudi Arabia', 'EG': 'Egypt', 'SY': 'Syria',
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
    'UN': ['un', 'u.n.', 'united nations'],
    'NATO': ['nato', 'north atlantic treaty organization'],
    'WHO': ['who', 'w.h.o.', 'world health organization'],
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
    'Wall Street': ['wall street'],
    'Reuters': ['reuters'],
    'AP': ['ap', 'associated press'],
    'BBC': ['bbc']
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
    escaped = [re.escape(k) for k in keys]
    pattern = r'\b(' + '|'.join(escaped) + r')\b'
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
    matches = regex.findall(text)
    seen = set()
    results = []
    
    for match in matches:
        match_lower = match.lower()
        key = lexicon.get(match_lower)
        if not key:
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

def extract_entities(title: str, description: str = '') -> dict:
    """Extract all entities from title and description text.
    
    Returns:
        {
            'countries': [{'code': 'US', 'name': 'United States'}, ...],
            'leaders': [{'name': 'Donald Trump', 'matched': 'trump'}, ...],
            'organizations': [{'name': 'NATO', 'matched': 'nato'}, ...],
            'companies': [{'name': 'Apple', 'matched': 'apple'}, ...],
            'actions': ['conflict', 'diplomacy'],  # action categories detected
            'domains': ['geopolitics', 'economics'],  # intellectual domains
            'entity_count': 5,  # total unique entities
            'entity_density': 0.42  # entities per word
        }
    """
    text = f"{title} {description}".strip()
    if not text:
        return {
            'countries': [], 'leaders': [], 'organizations': [], 'companies': [],
            'actions': [], 'domains': [], 'entity_count': 0, 'entity_density': 0.0
        }
        
    countries = _extract(text, _RE_COUNTRY, COUNTRY_LEXICON, COUNTRY_NAMES, 'country')
    leaders = _extract(text, _RE_LEADER, LEADER_LEXICON, type_name='leader')
    orgs = _extract(text, _RE_ORG, ORGANIZATION_LEXICON, type_name='organization')
    companies = _extract(text, _RE_COMPANY, COMPANY_LEXICON, type_name='company')
    
    actions = extract_action_categories(text)
    domains = extract_domains(text)
    
    entity_count = len(countries) + len(leaders) + len(orgs) + len(companies)
    
    # Calculate density (entities per word)
    words = len(re.findall(r'\b\w+\b', text))
    entity_density = round(entity_count / words, 4) if words > 0 else 0.0
    
    return {
        'countries': countries,
        'leaders': leaders,
        'organizations': orgs,
        'companies': companies,
        'actions': actions,
        'domains': domains,
        'entity_count': entity_count,
        'entity_density': entity_density
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
