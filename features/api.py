"""
api.py — Integração com a API do Banco Mundial (ONU)
Busca dados reais de países com bandeiras corretas
"""

import urllib.request
import json
from typing import List, Dict, Optional

# ── BANDEIRAS por código ISO2 ─────────────────────────────────────────────────
FLAGS: Dict[str, str] = {
    "US":"🇺🇸","BR":"🇧🇷","CN":"🇨🇳","DE":"🇩🇪","IN":"🇮🇳","JP":"🇯🇵",
    "GB":"🇬🇧","FR":"🇫🇷","IT":"🇮🇹","CA":"🇨🇦","KR":"🇰🇷","RU":"🇷🇺",
    "AU":"🇦🇺","ES":"🇪🇸","MX":"🇲🇽","ID":"🇮🇩","NL":"🇳🇱","SA":"🇸🇦",
    "TR":"🇹🇷","CH":"🇨🇭","AR":"🇦🇷","SE":"🇸🇪","PL":"🇵🇱","BE":"🇧🇪",
    "NO":"🇳🇴","TH":"🇹🇭","AT":"🇦🇹","NG":"🇳🇬","UA":"🇺🇦","AE":"🇦🇪",
    "IL":"🇮🇱","ZA":"🇿🇦","MY":"🇲🇾","PH":"🇵🇭","BD":"🇧🇩","DK":"🇩🇰",
    "SG":"🇸🇬","CL":"🇨🇱","FI":"🇫🇮","CO":"🇨🇴","PK":"🇵🇰","RO":"🇷🇴",
    "CZ":"🇨🇿","HU":"🇭🇺","VN":"🇻🇳","PT":"🇵🇹","GR":"🇬🇷","NZ":"🇳🇿",
    "PE":"🇵🇪","EG":"🇪🇬","QA":"🇶🇦","KW":"🇰🇼","ET":"🇪🇹","MA":"🇲🇦",
    "GH":"🇬🇭","IQ":"🇮🇶","KZ":"🇰🇿","OM":"🇴🇲","DO":"🇩🇴","TZ":"🇹🇿",
    "EC":"🇪🇨","GT":"🇬🇹","UZ":"🇺🇿","BY":"🇧🇾","MM":"🇲🇲","KE":"🇰🇪",
    "AZ":"🇦🇿","TN":"🇹🇳","HR":"🇭🇷","LT":"🇱🇹","SK":"🇸🇰","RS":"🇷🇸",
    "LV":"🇱🇻","SI":"🇸🇮","BG":"🇧🇬","EE":"🇪🇪","JO":"🇯🇴","LK":"🇱🇰",
    "PY":"🇵🇾","UY":"🇺🇾","CR":"🇨🇷","PA":"🇵🇦","BO":"🇧🇴","CU":"🇨🇺",
    "NP":"🇳🇵","KH":"🇰🇭","MZ":"🇲🇿","ZM":"🇿🇲","SN":"🇸🇳","CI":"🇨🇮",
    "CM":"🇨🇲","MG":"🇲🇬","AO":"🇦🇴","ZW":"🇿🇼","RW":"🇷🇼","ML":"🇲🇱",
    "BJ":"🇧🇯","TD":"🇹🇩","SO":"🇸🇴","SD":"🇸🇩","UG":"🇺🇬","MK":"🇲🇰",
    "BH":"🇧🇭","LB":"🇱🇧","CY":"🇨🇾","MT":"🇲🇹","LU":"🇱🇺","IS":"🇮🇸","IE":"🇮🇪","CD":"🇨🇩","HK":"🇭🇰","TW":"🇹🇼",
    "AF":"🇦🇫","YE":"🇾🇪","SY":"🇸🇾","LY":"🇱🇾","DZ":"🇩🇿","IR":"🇮🇷",
    "VE":"🇻🇪","MN":"🇲🇳","PG":"🇵🇬","FJ":"🇫🇯","MU":"🇲🇺","NA":"🇳🇦",
}

# Conjunto de ISO2 que são PAÍSES reais (exclui agregados do Banco Mundial)
# Agregados conhecidos: OE, XC, XD, XE, XJ, XL, XM, XN, XO, XP, XQ, XT,
# XU, XY, ZB, ZF, ZG, ZH, ZI, ZJ, ZQ, ZT, ZG, 1A, S1, S2, S3, S4
# A forma mais confiável: manter whitelist de ISO2 reais
REAL_COUNTRIES = set(FLAGS.keys())

# ── CAMPOS disponíveis ────────────────────────────────────────────────────────
FIELDS: Dict[str, Dict] = {
    "gdp": {
        "label":     "Banco Mundial — PIB (US$ bilhões)",
        "short":     "PIB (US$ bilhões)",
        "indicator": "NY.GDP.MKTP.CD",
        "format":    lambda v: f"US$ {v/1e9:.1f}B",
    },
    "lifeExp": {
        "label":     "Banco Mundial — Expectativa de Vida",
        "short":     "Expectativa de Vida (anos)",
        "indicator": "SP.DYN.LE00.IN",
        "format":    lambda v: f"{v:.1f} anos",
    },
    "population": {
        "label":     "Banco Mundial — População",
        "short":     "População (milhões)",
        "indicator": "SP.POP.TOTL",
        "format":    lambda v: f"{v/1e6:.1f} M",
    },
    "gdpPerCapita": {
        "label":     "Banco Mundial — PIB per Capita",
        "short":     "PIB per Capita (US$)",
        "indicator": "NY.GDP.PCAP.CD",
        "format":    lambda v: f"US$ {v:,.0f}",
    },
}

_cache: Dict[str, List] = {}

# ── FALLBACK completo com dados reais ─────────────────────────────────────────
FALLBACK: Dict[str, List] = {
    "gdp": [
        {"id":"US","name":"United States","val":26900000000000},
        {"id":"CN","name":"China","val":17700000000000},
        {"id":"DE","name":"Germany","val":4500000000000},
        {"id":"JP","name":"Japan","val":4200000000000},
        {"id":"IN","name":"India","val":3730000000000},
        {"id":"GB","name":"United Kingdom","val":3100000000000},
        {"id":"FR","name":"France","val":2920000000000},
        {"id":"IT","name":"Italy","val":2130000000000},
        {"id":"CA","name":"Canada","val":2100000000000},
        {"id":"BR","name":"Brazil","val":1920000000000},
        {"id":"RU","name":"Russia","val":1800000000000},
        {"id":"KR","name":"South Korea","val":1700000000000},
        {"id":"AU","name":"Australia","val":1700000000000},
        {"id":"ES","name":"Spain","val":1580000000000},
        {"id":"MX","name":"Mexico","val":1322000000000},
        {"id":"ID","name":"Indonesia","val":1319000000000},
        {"id":"SA","name":"Saudi Arabia","val":1069000000000},
        {"id":"NL","name":"Netherlands","val":1008000000000},
        {"id":"TR","name":"Turkey","val":906000000000},
        {"id":"CH","name":"Switzerland","val":807000000000},
        {"id":"PL","name":"Poland","val":688000000000},
        {"id":"AR","name":"Argentina","val":632000000000},
        {"id":"SE","name":"Sweden","val":584000000000},
        {"id":"BE","name":"Belgium","val":579000000000},
        {"id":"NO","name":"Norway","val":546000000000},
        {"id":"TH","name":"Thailand","val":495000000000},
        {"id":"NG","name":"Nigeria","val":477000000000},
        {"id":"AT","name":"Austria","val":476000000000},
        {"id":"SG","name":"Singapore","val":424000000000},
        {"id":"AE","name":"United Arab Emirates","val":415000000000},
        {"id":"VN","name":"Vietnam","val":409000000000},
        {"id":"MY","name":"Malaysia","val":407000000000},
        {"id":"PH","name":"Philippines","val":404000000000},
        {"id":"DK","name":"Denmark","val":395000000000},
        {"id":"EG","name":"Egypt","val":387000000000},
        {"id":"IL","name":"Israel","val":387000000000},
        {"id":"ZA","name":"South Africa","val":373000000000},
        {"id":"CO","name":"Colombia","val":314000000000},
        {"id":"RO","name":"Romania","val":300000000000},
        {"id":"CZ","name":"Czech Republic","val":295000000000},
        {"id":"NZ","name":"New Zealand","val":247000000000},
        {"id":"QA","name":"Qatar","val":236000000000},
        {"id":"PE","name":"Peru","val":242000000000},
        {"id":"FI","name":"Finland","val":299000000000},
        {"id":"CL","name":"Chile","val":301000000000},
        {"id":"PT","name":"Portugal","val":255000000000},
        {"id":"GR","name":"Greece","val":218000000000},
        {"id":"HU","name":"Hungary","val":185000000000},
        {"id":"MA","name":"Morocco","val":130000000000},
        {"id":"ET","name":"Ethiopia","val":126000000000},
    ],
    "population": [
        {"id":"IN","name":"India","val":1428627663},
        {"id":"CN","name":"China","val":1410710000},
        {"id":"US","name":"United States","val":335893238},
        {"id":"ID","name":"Indonesia","val":277534122},
        {"id":"PK","name":"Pakistan","val":231402117},
        {"id":"BR","name":"Brazil","val":215313498},
        {"id":"NG","name":"Nigeria","val":218541212},
        {"id":"BD","name":"Bangladesh","val":169356251},
        {"id":"RU","name":"Russia","val":144444359},
        {"id":"ET","name":"Ethiopia","val":126527060},
        {"id":"MX","name":"Mexico","val":127575529},
        {"id":"JP","name":"Japan","val":125124989},
        {"id":"PH","name":"Philippines","val":115559009},
        {"id":"EG","name":"Egypt","val":105914499},
        {"id":"CD","name":"DR Congo","val":99010212},
        {"id":"VN","name":"Vietnam","val":97468029},
        {"id":"IR","name":"Iran","val":87923432},
        {"id":"TR","name":"Turkey","val":85341241},
        {"id":"DE","name":"Germany","val":83200000},
        {"id":"TH","name":"Thailand","val":71801279},
        {"id":"GB","name":"United Kingdom","val":67736802},
        {"id":"FR","name":"France","val":68042591},
        {"id":"TZ","name":"Tanzania","val":63298550},
        {"id":"ZA","name":"South Africa","val":60414495},
        {"id":"MM","name":"Myanmar","val":54409794},
        {"id":"KE","name":"Kenya","val":54027487},
        {"id":"KR","name":"South Korea","val":51744876},
        {"id":"CO","name":"Colombia","val":51874024},
        {"id":"ES","name":"Spain","val":47426632},
        {"id":"UG","name":"Uganda","val":47958776},
        {"id":"AR","name":"Argentina","val":45773884},
        {"id":"DZ","name":"Algeria","val":44177969},
        {"id":"SD","name":"Sudan","val":46874204},
        {"id":"IQ","name":"Iraq","val":41995948},
        {"id":"UA","name":"Ukraine","val":43531422},
        {"id":"CA","name":"Canada","val":38781292},
        {"id":"MA","name":"Morocco","val":37457971},
        {"id":"SA","name":"Saudi Arabia","val":36947025},
        {"id":"UZ","name":"Uzbekistan","val":35264000},
        {"id":"PE","name":"Peru","val":33359418},
        {"id":"AF","name":"Afghanistan","val":42239854},
        {"id":"MY","name":"Malaysia","val":33573874},
        {"id":"AO","name":"Angola","val":36684202},
        {"id":"MZ","name":"Mozambique","val":33089461},
        {"id":"GH","name":"Ghana","val":33107044},
        {"id":"YE","name":"Yemen","val":33696614},
        {"id":"NP","name":"Nepal","val":30034989},
        {"id":"AU","name":"Australia","val":26439111},
        {"id":"CM","name":"Cameroon","val":27914536},
        {"id":"CI","name":"Côte d'Ivoire","val":27478249},
    ],
    "lifeExp": [
        {"id":"HK","name":"Hong Kong","val":85.5},
        {"id":"JP","name":"Japan","val":84.3},
        {"id":"CH","name":"Switzerland","val":83.4},
        {"id":"KR","name":"South Korea","val":83.6},
        {"id":"SG","name":"Singapore","val":83.5},
        {"id":"AU","name":"Australia","val":83.2},
        {"id":"IS","name":"Iceland","val":83.1},
        {"id":"ES","name":"Spain","val":83.3},
        {"id":"IT","name":"Italy","val":83.0},
        {"id":"SE","name":"Sweden","val":82.8},
        {"id":"IL","name":"Israel","val":82.9},
        {"id":"NO","name":"Norway","val":82.9},
        {"id":"LU","name":"Luxembourg","val":82.2},
        {"id":"FR","name":"France","val":82.3},
        {"id":"NZ","name":"New Zealand","val":82.5},
        {"id":"FI","name":"Finland","val":82.0},
        {"id":"DE","name":"Germany","val":81.3},
        {"id":"GB","name":"United Kingdom","val":81.3},
        {"id":"BE","name":"Belgium","val":81.4},
        {"id":"AT","name":"Austria","val":81.6},
        {"id":"NL","name":"Netherlands","val":81.7},
        {"id":"CA","name":"Canada","val":82.0},
        {"id":"DK","name":"Denmark","val":81.3},
        {"id":"PT","name":"Portugal","val":81.4},
        {"id":"GR","name":"Greece","val":81.0},
        {"id":"MT","name":"Malta","val":83.0},
        {"id":"CY","name":"Cyprus","val":81.0},
        {"id":"SI","name":"Slovenia","val":81.3},
        {"id":"CZ","name":"Czech Republic","val":78.5},
        {"id":"US","name":"United States","val":76.4},
        {"id":"CN","name":"China","val":78.2},
        {"id":"CL","name":"Chile","val":80.5},
        {"id":"AR","name":"Argentina","val":76.4},
        {"id":"VN","name":"Vietnam","val":73.6},
        {"id":"BR","name":"Brazil","val":74.0},
        {"id":"TH","name":"Thailand","val":77.2},
        {"id":"MX","name":"Mexico","val":75.1},
        {"id":"RU","name":"Russia","val":72.8},
        {"id":"IN","name":"India","val":67.2},
        {"id":"BD","name":"Bangladesh","val":72.4},
        {"id":"PK","name":"Pakistan","val":67.1},
        {"id":"EG","name":"Egypt","val":70.2},
        {"id":"NG","name":"Nigeria","val":53.4},
        {"id":"ET","name":"Ethiopia","val":65.5},
        {"id":"ZA","name":"South Africa","val":63.9},
        {"id":"ID","name":"Indonesia","val":67.6},
        {"id":"PH","name":"Philippines","val":71.1},
        {"id":"TR","name":"Turkey","val":77.5},
        {"id":"SA","name":"Saudi Arabia","val":76.5},
        {"id":"IR","name":"Iran","val":73.9},
    ],
    "gdpPerCapita": [
        {"id":"LU","name":"Luxembourg","val":133590},
        {"id":"SG","name":"Singapore","val":84734},
        {"id":"CH","name":"Switzerland","val":93520},
        {"id":"NO","name":"Norway","val":101103},
        {"id":"US","name":"United States","val":80034},
        {"id":"IS","name":"Iceland","val":78834},
        {"id":"DK","name":"Denmark","val":68008},
        {"id":"AU","name":"Australia","val":65099},
        {"id":"NL","name":"Netherlands","val":62153},
        {"id":"AT","name":"Austria","val":56801},
        {"id":"FI","name":"Finland","val":55328},
        {"id":"SE","name":"Sweden","val":55840},
        {"id":"BE","name":"Belgium","val":52085},
        {"id":"CA","name":"Canada","val":55522},
        {"id":"DE","name":"Germany","val":54114},
        {"id":"GB","name":"United Kingdom","val":46125},
        {"id":"NZ","name":"New Zealand","val":46010},
        {"id":"FR","name":"France","val":43658},
        {"id":"IE","name":"Ireland","val":100172},
        {"id":"IL","name":"Israel","val":54930},
        {"id":"JP","name":"Japan","val":33834},
        {"id":"KR","name":"South Korea","val":33147},
        {"id":"IT","name":"Italy","val":36812},
        {"id":"ES","name":"Spain","val":33090},
        {"id":"QA","name":"Qatar","val":83891},
        {"id":"AE","name":"United Arab Emirates","val":49000},
        {"id":"SA","name":"Saudi Arabia","val":28932},
        {"id":"PT","name":"Portugal","val":25676},
        {"id":"CZ","name":"Czech Republic","val":27700},
        {"id":"GR","name":"Greece","val":20384},
        {"id":"PL","name":"Poland","val":18180},
        {"id":"HU","name":"Hungary","val":18891},
        {"id":"RU","name":"Russia","val":12575},
        {"id":"MX","name":"Mexico","val":10388},
        {"id":"MY","name":"Malaysia","val":12364},
        {"id":"TR","name":"Turkey","val":10674},
        {"id":"AR","name":"Argentina","val":13797},
        {"id":"ZA","name":"South Africa","val":6194},
        {"id":"CN","name":"China","val":12541},
        {"id":"BR","name":"Brazil","val":8917},
        {"id":"TH","name":"Thailand","val":6908},
        {"id":"CO","name":"Colombia","val":6105},
        {"id":"PE","name":"Peru","val":7126},
        {"id":"EG","name":"Egypt","val":3643},
        {"id":"ID","name":"Indonesia","val":4788},
        {"id":"IN","name":"India","val":2612},
        {"id":"PH","name":"Philippines","val":3516},
        {"id":"VN","name":"Vietnam","val":4163},
        {"id":"PK","name":"Pakistan","val":1505},
        {"id":"BD","name":"Bangladesh","val":2688},
    ],
}


def _fetch_world_bank(indicator: str, per_page: int = 300) -> Optional[List]:
    cache_key = f"{indicator}_{per_page}"
    if cache_key in _cache:
        return _cache[cache_key]

    url = (
        f"https://api.worldbank.org/v2/country/all/indicator/{indicator}"
        f"?format=json&mrv=1&per_page={per_page}&source=2"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SortEngine/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
            records = data[1] if isinstance(data, list) and len(data) > 1 else []
            _cache[cache_key] = records
            return records
    except Exception as e:
        print(f"[API] Erro ao buscar {indicator}: {e} — usando fallback")
        return None


def get_data(field_key: str, sample_size: int = 20) -> List[Dict]:
    """Retorna lista de países reais com bandeiras corretas."""
    field = FIELDS.get(field_key)
    if not field:
        raise ValueError(f"Campo desconhecido: {field_key}")

    raw = _fetch_world_bank(field["indicator"])

    if raw:
        # Filtra APENAS países reais (ISO2 que estão no nosso mapa de bandeiras)
        valid = [
            d for d in raw
            if d.get("value") is not None
            and d.get("country", {}).get("id", "") in REAL_COUNTRIES
        ]
        valid.sort(key=lambda d: d["value"], reverse=True)
        items = []
        for d in valid[:sample_size]:
            cid = d["country"]["id"]
            val = d["value"]
            items.append({
                "id":    cid,
                "name":  d["country"]["value"],
                "val":   val,
                "flag":  FLAGS[cid],
                "label": field["format"](val),
            })
        if items:
            return items

    # Fallback por campo
    fallback_data = FALLBACK.get(field_key, FALLBACK["gdp"])
    fmt = field["format"]
    data = sorted(fallback_data, key=lambda x: x["val"], reverse=True)[:sample_size]
    return [
        {**d, "flag": FLAGS.get(d["id"], "🌍"), "label": fmt(d["val"])}
        for d in data
    ]


def list_fields() -> List[Dict]:
    return [{"key": k, "label": v["label"]} for k, v in FIELDS.items()]
