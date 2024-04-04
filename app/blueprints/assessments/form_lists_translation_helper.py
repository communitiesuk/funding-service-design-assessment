import json
import os
from pprint import pprint

from app.blueprints.shared.filters import (
    remove_dashes_underscores_capitalize_keep_uppercase,
)

# This dictionary was dynamically generated based on the script defined on this module. If you want to regenerate
# this dictionary, you will need to rerun the script. This may need to be rerun every single time a new round is
# added that has both English and Welsh.
_LIST_TRANSLATIONS_GENERATED = {
    "Adeilad swyddfa bost": "Post office building",
    "Adnewyddu lesddaliad": "Renovate a leasehold",
    "Adnewyddu rhydd-ddaliad": "Renovate a freehold",
    "Amgueddfa": "Museum",
    "Ar werth neu wedi'i restru ar gyfer gwaredu": "for-sale-or-listed-for-disposal",
    "Arall": "Other",
    "Balchder cymunedol a chanfyddiadau o'r ardal leol fel lle i fyw ynddo": "community-pride",
    "Benthycwyr eraill": "Other Lenders",
    "Buddsoddwyr cymunedol": "Social Investors",
    "CIC": "CIC",
    "CIO": "CIO",
    "CLG": "CLG",
    "COOP": "COOP",
    "Cael effaith gadarnhaol ar iechyd corfforol ac iechyd meddwl, a lleihau unigrwydd ac ynysigrwydd": "delivering-positive",  # noqa
    "Cam cynnar": "Early stage",
    "Cam hwyr": "Late stage",
    "Camddeall neu wanllyd": "Neglect or dereliction",
    "Canlyniadau economaidd lleol, fel cyflogaeth a chyfleoedd i wirfoddoli, a  chyflogadwyedd a sgiliau": "local-economic",  # noqa
    "Canolfan gymunedol": "Community centre",
    "Cau": "Closure",
    "Closure": "Closure",
    "Codi arian yn eich cymuned": "Fundraising in your community",
    "Cwmni buddiannau cymunedol": "community-interest-company",
    "Cwmni buddiannau cymunedol (CIC)": "CIC",
    "Cwmni cydweithredol, fel cymdeithas budd cymunedol": "COOP",
    "Cwmni cyfyngedig drwy warant": "company-limited",
    "Cydweithrediaeth (er enghraifft, cymdeithas budd cymunedol)": "co-operative",
    "Cyfleuster chwaraeon neu hamdden": "Sporting or leisure facility",
    "Cyfleuster hamdden neu chwaraeon": "sporting",
    "Cyfranddaliadau cymunedol": "Community shares",
    "Cyfranogi mewn bywyd cymunedol, y celfyddydau a diwylliant, neu chwaraeon": "participation",
    "Cyfreithiol": "Legal",
    "Cyllidwyr y Loteri Genedlaethol": "National lottery funders",
    "Cymorth llywodraethu": "Governance support",
    "Cynghorau plwyf, tref a chymuned": "parish-town-community-councils",
    "Cyngor plwyf, tref neu gymuned": "PTC",
    "Cyrff cyhoeddus": "Public bodies",
    "Ddim yn gorfforedig eto": "not-yet-incorporated",
    "Ddim yn gwybod pwy yw'r perchennog": "Do not know who owner is",
    "Ddim yn siŵr": "Not sure",
    "Eich adnoddau ariannol eich hun": "Your own financial resources",
    "Eisoes wedi'i llogi gan eich sefydliad": "already-leased-by-organisation",
    "Eisoes wedi'i sicrhau": "Already secured",
    "Eisoes yn eiddo i'w sefydliad": "already-owned-by-organisation",
    "Elusennau neu ymddiriedolaethau": "Charities or trusts",
    "Esgeulustod neu gyflwr adfeiliedig": "Neglect or dereliction",
    "Gostyngiad ar rydd-ddaliad/lesddaliad": "Discount on freehold/leasehold",
    "Gweinyddiaethau datganoledig": "Devolved administrations",
    "Gwerth annyoneddol na thâl fel y mae'r model busnes presennol": "unprofitable-under-current-business-model",
    "Gwerthu": "Sale",
    "Heb ddechrau eto": "Not yet started",
    "Heb gysylltu ag unrhyw gyllidwyr eto": "Not yet approached any funders",
    "House": "House",
    "Listed for disposal": "Listed for disposal",
    "Lleoliad cerddoriaeth": "Music venue",
    "Llogi'r eiddo": "lease-the-asset",
    "Model busnes cyfredol anghynaliadwy": "Unsustainable current business model",
    "Model busnes presennol na ellir ei gynnal": "Unsustainable current business "
    "model",
    "Nac oes": "No",
    "Nac ydy, nid yw'n perthyn i awdurdod cyhoeddus": "No, it does not belong to "
    "a public authority",
    "Neglect or dereliction": "Neglect or dereliction",
    "Nid wyf am i neb gysylltu â mi": "No, I do not wish to be contacted",
    "Nid yw'r defnydd yn y dyfodol wedi'i sicrhau": "future-use-not-secured",
    "Nid yw'r perchenogaeth gyfredol yn ddichonadwy": "current-ownership-not-tenable",
    "No": "No",
    "Oes": "Yes",
    "Oriel": "Gallery",
    "Other": "Other",
    "PTC": "PTC",
    "Parc": "Park",
    "Part of a Community Asset Transfer": "Part of a Community Asset Transfer",
    "Penderfyniad i gau neu les yn dod i ben": "Closure or end of lease",
    "Porthladd ymddiriedolaeth": "trust-port",
    "Prynu lesddaliad": "Buy a leasehold",
    "Prynu rhydd-ddaliad": "Buy a freehold",
    "Prynu'r eiddo": "buy-the-asset",
    "Rhagolwg ariannol": "Financial forecasting",
    "Rhan o Trosglwyddiad Ased Cymunedol": "Part of a Community Asset Transfer",
    "Rhan o broses trosglwyddo asedau cymunedol": "Part of a community asset "
    "transfer",
    "Rhoi gwasanaethau proffesiynol": "Donation of professional services",
    "Rhoi nwyddau": "Donation of goods",
    "Rwy'n cytuno y gellir cysylltu â mi os wyf yn gymwys": "Yes, I agree to be "
    "contacted if "
    "eligible",
    "SCIO": "SCIO",
    "Sale": "Sale",
    "Sefydliad corfforedig elusennol": "Charitable incorporated organisation",
    "Sefydliad corfforedig elusennol (CIO)": "CIO",
    "Sefydliad corfforedig elusennol yn yr Alban": "scottish-charitable",
    "Sefydliad corfforedig elusennol yr Alban (SCIO)": "SCIO",
    "Sinema": "Cinema",
    "Siop": "Shop",
    "Tafarn": "Pub",
    "Tai": "Housing",
    "Technegol": "Technical",
    "Theatr": "Theatre",
    "Trafodaethau ar gam cynnar": "Early stage negotiations",
    "Trafodaethau ar gam datblygedig": "Advanced stage negotiations",
    "Tŷ'r Cwmnïau": "Companies House",
    "Unsustainable current business model": "Unsustainable current business model",
    "Wedi cysylltu â rhai cyllidwyr ond heb sicrhau cyllid eto": "Approached some "
    "funders but not "
    "yet secured",
    "Wedi cysylltu â'r holl gyllidwyr ond heb sicrhau cyllid eto": "Approached "
    "all funders "
    "but not yet "
    "secured",
    "Wedi sicrhau rhywfaint o arian cyfatebol": "Secured some match funding",
    "Wedi sicrhau'r holl arian cyfatebol": "Secured all match funding",
    "Wedi'i restru i'w waredu": "Listed for disposal",
    "Wedî'i restru ar gyfer gwaredu": "Listed for disposal",
    "Werthiant": "Sale",
    "Ydy, cyngor tref, plwyf neu gymuned": "Yes, a town, parish or community "
    "council",
    "Ydy, math arall o awdurdod cyhoeddus": "Yes, another type of public " "authority",
    "Yes": "Yes",
    "Ymddiriedaeth gymdeithasol, cydlyniant ac ymdeimlad o berthyn": "social-trust",
    "Yn gwybod pwy yw'r perchennog ond heb gysylltu": "Know who owner is but have "
    "not approached",
    "Ysgrifennu cynllun busnes": "Writing a business plan",
    "already-leased-by-organisation": "already-leased-by-organisation",
    "already-owned-by-organisation": "already-owned-by-organisation",
    "buy-the-asset": "buy-the-asset",
    "cadarnhaf": "confirm",
    "cinema": "cinema",
    "community-centre": "community-centre",
    "community-pride": "community-pride",
    "confirm": "confirm",
    "current-ownership-not-tenable": "current-ownership-not-tenable",
    "delivering-positive": "delivering-positive",
    "fight-climate-change": "fight-climate-change",
    "for-sale-or-listed-for-disposal": "for-sale-or-listed-for-disposal",
    "future-use-not-secured": "future-use-not-secured",
    "gallery": "gallery",
    "improve-local-skills": "improve-local-skills",
    "lease-the-asset": "lease-the-asset",
    "local-economic": "local-economic",
    "museum": "museum",
    "music-venue": "music-venue",
    "net-zero": "net-zero",
    "no": "no",
    "none": "Not sure",
    "one": "one",
    "other": "other",
    "park": "park",
    "participation": "participation",
    "post-office": "post-office",
    "pub": "pub",
    "regeneration": "regeneration",
    "shop": "shop",
    "social-trust": "social-trust",
    "sporting": "sporting",
    "support-local-community": "support-local-community",
    "theatre": "theatre",
    "two": "two",
    "unprofitable-under-current-business-model": "unprofitable-under-current-business-model",
    "yes": "yes",
}

_LIST_TRANSLATIONS = {
    **_LIST_TRANSLATIONS_GENERATED,
    "none": "None of these",  # See PR 338 on GitHub.
}


def map_form_json_list_value(value: str):
    if mapping := _LIST_TRANSLATIONS.get(value.strip()):
        return remove_dashes_underscores_capitalize_keep_uppercase(mapping)
    return value


# Below this section of the file are internal functions used for the script when you execute this module. If you
# execute this module, it will print out a dictionary dynamically from all the existing form JSONs of a mapping from
# Welsh to English for all the checkbox/radio item lists embedded inside the form JSONs.
def __gather_lists(directory, language_code):
    all_lists = {}
    for filename in os.listdir(directory):
        if not filename.endswith(".json"):
            continue
        with open(os.path.join(directory, filename), "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data.get("lists", []):
                name = item.get("name").strip()
                all_lists.setdefault(name, {"EN": [], "CY": []})[language_code].extend(
                    [
                        {"value": item.get("value").strip()}
                        for item in item.get("items", [])
                    ]
                )
    return all_lists


def __combine_rounds(rounds):
    round_lists = {}
    for r in rounds:
        for lang_code, sub_dir in [("EN", "en"), ("CY", "cy")]:
            path = os.path.join(r, sub_dir)
            lists = __gather_lists(path, lang_code)
            for name, items in lists.items():
                round_lists.setdefault(name, {"EN": [], "CY": []})[lang_code].extend(
                    items[lang_code]
                )
    return round_lists


def __extract_translations(round_lists):
    translation_dict, duplicates = {}, set()
    for content in round_lists.values():
        for welsh, english in zip(content["CY"], content["EN"]):
            welsh_value, english_value = (
                welsh["value"].strip(),
                english["value"].strip(),
            )
            if (
                welsh_value in translation_dict
                and translation_dict[welsh_value] != english_value
            ):
                duplicates.add(welsh_value)
            translation_dict[welsh_value] = english_value
    return translation_dict, duplicates


# This script is used to dynamically crawl all the form jsons of existing rounds that have both English and Welsh.
# Take the English form and take the Welsh form and create a dictionary of a mapping of the Welsh to English for all
# the list items inside the forms. The list items represent checkbox/radio values. Therefore, we use this mapping that
# is generated to translate things in assessment as it's only an English service.
if __name__ == "__main__":
    # relative path to this current module, will need update if this file is moved
    root_dir = "../../../../digital-form-builder/fsd_config/form_jsons"

    rounds = []
    for dirpath, dirnames, _ in os.walk(root_dir):
        print(dirpath)
        lower_dirnames = [d.lower() for d in dirnames]
        if "en" in lower_dirnames and "cy" in lower_dirnames:
            rounds.append(dirpath)

    round_lists = __combine_rounds(rounds)
    translation_dict, duplicates = __extract_translations(round_lists)
    if duplicates:
        print("Duplicates found:", duplicates)
    pprint(translation_dict)
