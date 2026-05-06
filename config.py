import os
import logging

logger = logging.getLogger(__name__)

CACHE_TTL_COUNTRY = 6 * 3600
CACHE_TTL_GLOBAL  = 4 * 3600

COUNTRY_NAMES = {
    "ae": "United Arab Emirates", "ar": "Argentina", "at": "Austria",
    "au": "Australia", "be": "Belgium", "bg": "Bulgaria", "br": "Brazil",
    "ca": "Canada", "ch": "Switzerland", "cn": "China", "co": "Colombia",
    "cu": "Cuba", "cz": "Czech Republic", "de": "Germany", "eg": "Egypt",
    "fr": "France", "gb": "United Kingdom", "gr": "Greece", "hk": "Hong Kong",
    "hu": "Hungary", "id": "Indonesia", "ie": "Ireland", "il": "Israel",
    "in": "India", "it": "Italy", "jp": "Japan", "kr": "South Korea",
    "lt": "Lithuania", "lv": "Latvia", "ma": "Morocco", "mx": "Mexico",
    "my": "Malaysia", "ng": "Nigeria", "nl": "Netherlands", "no": "Norway",
    "nz": "New Zealand", "ph": "Philippines", "pl": "Poland", "pt": "Portugal",
    "ro": "Romania", "rs": "Serbia", "ru": "Russia", "sa": "Saudi Arabia",
    "se": "Sweden", "sg": "Singapore", "si": "Slovenia", "sk": "Slovakia",
    "th": "Thailand", "tr": "Turkey", "tw": "Taiwan", "ua": "Ukraine",
    "us": "United States", "ve": "Venezuela", "za": "South Africa",
    "es": "Spain", "pe": "Peru", "cl": "Chile", "ec": "Ecuador",
    "bo": "Bolivia", "py": "Paraguay", "uy": "Uruguay", "pa": "Panama",
    "cr": "Costa Rica", "gt": "Guatemala", "hn": "Honduras", "sv": "El Salvador",
    "ni": "Nicaragua", "do": "Dominican Republic", "pr": "Puerto Rico",
    "ke": "Kenya", "gh": "Ghana", "et": "Ethiopia", "tz": "Tanzania",
    "ug": "Uganda", "dz": "Algeria", "tn": "Tunisia", "ly": "Libya",
    "sd": "Sudan", "cm": "Cameroon", "ci": "Ivory Coast", "sn": "Senegal",
    "zw": "Zimbabwe", "zm": "Zambia", "mz": "Mozambique", "mg": "Madagascar",
    "ao": "Angola", "cd": "Congo", "pk": "Pakistan", "bd": "Bangladesh",
    "lk": "Sri Lanka", "np": "Nepal", "mm": "Myanmar", "vn": "Vietnam",
    "kh": "Cambodia", "la": "Laos", "af": "Afghanistan", "ir": "Iran",
    "iq": "Iraq", "sy": "Syria", "jo": "Jordan", "lb": "Lebanon",
    "om": "Oman", "kw": "Kuwait", "qa": "Qatar", "bh": "Bahrain",
    "ye": "Yemen", "fi": "Finland", "dk": "Denmark", "ee": "Estonia",
    "by": "Belarus", "md": "Moldova", "ge": "Georgia", "am": "Armenia",
    "az": "Azerbaijan", "kz": "Kazakhstan", "uz": "Uzbekistan",
    "al": "Albania", "ba": "Bosnia", "hr": "Croatia", "mk": "North Macedonia",
    "me": "Montenegro", "mt": "Malta", "cy": "Cyprus", "is": "Iceland",
    "lu": "Luxembourg", "li": "Liechtenstein", "mc": "Monaco", "ad": "Andorra",
    "sm": "San Marino", "va": "Vatican", "nk": "North Korea", "so": "Somalia",
    "mr": "Mauritania", "ml": "Mali", "bf": "Burkina Faso", "ne": "Niger",
    "td": "Chad", "cf": "Central African Republic", "rw": "Rwanda",
    "bi": "Burundi", "er": "Eritrea", "dj": "Djibouti",
}

NEWSAPI_COUNTRIES = {
    "ae","ar","at","au","be","bg","br","ca","ch","cn","co","cu","cz",
    "de","eg","fr","gb","gr","hk","hu","id","ie","il","in","it","jp",
    "kr","lt","lv","ma","mx","my","ng","nl","no","nz","ph","pl","pt",
    "ro","rs","ru","sa","se","sg","si","sk","th","tr","tw","ua","us","ve","za"
}

def build_api_keys():
    keys = []
    raw = os.environ.get("NEWS_API_KEY", "")
    for k in raw.split(","):
        k = k.strip()
        if k:
            keys.append({'key': k, 'requests_used': 0, 'rate_limited': False})
    if not keys:
        logger.warning("⚠️ No NEWS_API_KEY encontrada.")
        keys.append({'key': 'PLACEHOLDER', 'requests_used': 0, 'rate_limited': False})
    return keys
