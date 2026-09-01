#!/usr/bin/env python3
"""
Analizador de mods de Project Zomboid
Verifica correspondencia entre Workshop IDs y nombres de mods
"""

import urllib.request
import re
import time
import json
from html.parser import HTMLParser

# Datos del servidor
WORKSHOP_IDS = "3171167894;3378285185;3396446795;3508537032;3596827035;3394044313;3414697768;3330403100;3423984426;3632610172;3634635950;3659009768;3633882960;3686548791;3725311427;2544353492;3546314080;3780298456;3389605231;3739173520;3749848348;3742599937;3744180656;3461263912;2847184718;3781533687;3768669395;2377867605;2829657632;3784847437;3782777908;3779561845;3550032314;3428369137;3739168410;3639628777;3706786888;3706659540;3577903007;2256623447;3616176188;2142622992;2956146279;3773340822"

MODS_NAMES = "damnlib;StarlitLibrary;MoodleFramework;NeatUI_Framework;ShelterHold_Beehive;Buttstroke;jiggasGreenfireMod;KI5trailers;TrueSmoking;TrueMoozic;TMPK02;TM_PinkFloydDark;TMMMB42.13+;TMCDs;PSR;P4HasBeenRead;Waterpipes;BritasArmorPackB42;TchernoLib;PIP;PAR;PSC;RefreshMinimalDisplayBars;CleanHotBar;ProximityInventory;TrueSleep;TrueWeight;ReducedWoodWeight2x41;50%metalweight;traitsAsSkills;WildernessCalm;LGExtendedPlumbing;MoatsB42;NepWreckWorkingCars;Obvious_Skill_Tapes;BurdSurvivalJournals;BCGToolsTEST;BCGRareWeaponsTEST;VanillaFoodsExpanded;firearms;GaelGunStore_B42;RepairAnyClothes;RainCleansBlood;AutoDrop_B42"

class SteamWorkshopParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.in_workshop_title = False
        self.title = ""
        self.description = ""
        self.in_description = False
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'div' and 'workshopItemTitle' in attrs_dict.get('class', ''):
            self.in_workshop_title = True
        if tag == 'title':
            self.in_title = True
            
    def handle_data(self, data):
        if self.in_workshop_title:
            self.title = data.strip()
            self.in_workshop_title = False
        if self.in_title:
            self.title = data.strip()
            self.in_title = False
            
    def handle_endtag(self, tag):
        if tag == 'div':
            self.in_workshop_title = False
        if tag == 'title':
            self.in_title = False

def fetch_mod_info(workshop_id):
    """Obtiene información de un mod de Steam Workshop"""
    url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}"
    
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
        
        # Extraer título del mod
        title_match = re.search(r'<div class="workshopItemTitle"[^>]*>([^<]+)</div>', html)
        if not title_match:
            title_match = re.search(r'<title>([^<]+)</title>', html)
        
        title = title_match.group(1).strip() if title_match else "Desconocido"
        
        # Limpiar título (quitar "Steam Workshop::" si existe)
        title = title.replace("Steam Workshop::", "").strip()
        
        # Buscar descripción/tags
        tags = []
        tag_matches = re.findall(r'<a class="app_tag"[^>]*>([^<]+)</a>', html)
        tags = [t.strip() for t in tag_matches]
        
        return {
            'id': workshop_id,
            'title': title,
            'tags': tags,
            'url': url
        }
    except Exception as e:
        return {
            'id': workshop_id,
            'title': f"ERROR: {str(e)}",
            'tags': [],
            'url': url
        }

def main():
    workshop_ids = WORKSHOP_IDS.split(';')
    mod_names = MODS_NAMES.split(';')
    
    print(f"=== ANÁLISIS DE MODS ===")
    print(f"Workshop IDs: {len(workshop_ids)}")
    print(f"Mods declarados: {len(mod_names)}")
    print()
    
    if len(workshop_ids) != len(mod_names):
        print(f"⚠️  ADVERTENCIA: Diferente número de IDs ({len(workshop_ids)}) y nombres ({len(mod_names)})")
        print()
    
    print("Obteniendo información de Steam Workshop...")
    print()
    
    mod_info_list = []
    for i, wid in enumerate(workshop_ids, 1):
        print(f"[{i}/{len(workshop_ids)}] Consultando ID {wid}...", end=" ")
        info = fetch_mod_info(wid)
        mod_info_list.append(info)
        print(f"✓ {info['title'][:50]}")
        time.sleep(0.5)  # Rate limiting
    
    print()
    print("=" * 80)
    print("REPORTE DE CORRESPONDENCIA")
    print("=" * 80)
    print()
    
    # Crear mapeo
    mismatches = []
    matches = []
    
    for i, (wid, declared_name) in enumerate(zip(workshop_ids, mod_names)):
        actual_title = mod_info_list[i]['title']
        
        # Normalizar para comparación
        declared_lower = declared_name.lower().replace(' ', '').replace('_', '')
        actual_lower = actual_title.lower().replace(' ', '').replace('_', '')
        
        # Verificar si hay correspondencia razonable
        is_match = (
            declared_lower in actual_lower or
            actual_lower in declared_lower or
            declared_name.lower() in actual_title.lower() or
            actual_title.lower() in declared_name.lower()
        )
        
        if is_match:
            matches.append((wid, declared_name, actual_title))
        else:
            mismatches.append((wid, declared_name, actual_title))
    
    if matches:
        print(f"✓ MODS CORRECTOS ({len(matches)}):")
        print()
        for wid, declared, actual in matches:
            print(f"  ID {wid}: {declared} → {actual}")
        print()
    
    if mismatches:
        print(f"⚠️  POSIBLES DESAJUSTES ({len(mismatches)}):")
        print()
        for wid, declared, actual in mismatches:
            print(f"  ID {wid}:")
            print(f"    Declarado: {declared}")
            print(f"    Real:      {actual}")
            print()
    
    print("=" * 80)
    print("LISTA COMPLETA DE MODS")
    print("=" * 80)
    print()
    
    for i, info in enumerate(mod_info_list, 1):
        print(f"{i:2d}. [{info['id']}] {info['title']}")
    
    print()
    print("=" * 80)
    print("RESUMEN")
    print("=" * 80)
    print(f"Total Workshop IDs: {len(workshop_ids)}")
    print(f"Total Mods declarados: {len(mod_names)}")
    print(f"Correspondencias correctas: {len(matches)}")
    print(f"Posibles desajustes: {len(mismatches)}")
    
    # Guardar reporte JSON
    report = {
        'workshop_ids': workshop_ids,
        'mod_names': mod_names,
        'mod_details': mod_info_list,
        'matches': len(matches),
        'mismatches': len(mismatches)
    }
    
    with open('mods_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print()
    print("Reporte completo guardado en: mods_report.json")

if __name__ == '__main__':
    main()
