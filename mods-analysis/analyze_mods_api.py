#!/usr/bin/env python3
"""
Analizador de mods de Project Zomboid usando la API de Steam
"""

import urllib.request
import json
import time

# Datos del servidor
WORKSHOP_IDS = "3171167894;3378285185;3396446795;3508537032;3596827035;3394044313;3414697768;3330403100;3423984426;3632610172;3634635950;3659009768;3633882960;3686548791;3725311427;2544353492;3546314080;3780298456;3389605231;3739173520;3749848348;3742599937;3744180656;3461263912;2847184718;3781533687;3768669395;2377867605;2829657632;3784847437;3782777908;3779561845;3550032314;3428369137;3739168410;3639628777;3706786888;3706659540;3577903007;2256623447;3616176188;2142622992;2956146279;3773340822"

MODS_NAMES = "damnlib;StarlitLibrary;MoodleFramework;NeatUI_Framework;ShelterHold_Beehive;Buttstroke;jiggasGreenfireMod;KI5trailers;TrueSmoking;TrueMoozic;TMPK02;TM_PinkFloydDark;TMMMB42.13+;TMCDs;PSR;P4HasBeenRead;Waterpipes;BritasArmorPackB42;TchernoLib;PIP;PAR;PSC;RefreshMinimalDisplayBars;CleanHotBar;ProximityInventory;TrueSleep;TrueWeight;ReducedWoodWeight2x41;50%metalweight;traitsAsSkills;WildernessCalm;LGExtendedPlumbing;MoatsB42;NepWreckWorkingCars;Obvious_Skill_Tapes;BurdSurvivalJournals;BCGToolsTEST;BCGRareWeaponsTEST;VanillaFoodsExpanded;firearms;GaelGunStore_B42;RepairAnyClothes;RainCleansBlood;AutoDrop_B42"

# Project Zomboid App ID en Steam
PZ_APP_ID = "108600"

def fetch_workshop_details(workshop_ids):
    """Obtiene detalles de múltiples items de Workshop usando la API de Steam"""
    url = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
    
    # Preparar datos POST
    data = {
        'itemcount': len(workshop_ids),
    }
    
    for i, wid in enumerate(workshop_ids):
        data[f'publishedfileids[{i}]'] = wid
    
    # Codificar como form data
    post_data = '&'.join([f"{k}={v}" for k, v in data.items()])
    
    try:
        req = urllib.request.Request(
            url,
            data=post_data.encode('utf-8'),
            headers={
                'User-Agent': 'Mozilla/5.0',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        if 'response' in result and 'publishedfiledetails' in result['response']:
            return result['response']['publishedfiledetails']
        else:
            print(f"Error en respuesta API: {result}")
            return None
            
    except Exception as e:
        print(f"Error al consultar API: {e}")
        return None

def main():
    workshop_ids = WORKSHOP_IDS.split(';')
    mod_names = MODS_NAMES.split(';')
    
    print(f"=== ANÁLISIS DE MODS (API Steam) ===")
    print(f"Workshop IDs: {len(workshop_ids)}")
    print(f"Mods declarados: {len(mod_names)}")
    print()
    
    if len(workshop_ids) != len(mod_names):
        print(f"⚠️  ADVERTENCIA: Diferente número de IDs ({len(workshop_ids)}) y nombres ({len(mod_names)})")
        print()
    
    print("Consultando API de Steam Workshop...")
    print()
    
    # Obtener detalles de todos los mods
    details = fetch_workshop_details(workshop_ids)
    
    if not details:
        print("ERROR: No se pudieron obtener los detalles")
        return
    
    print(f"✓ Obtenidos {len(details)} mods")
    print()
    print("=" * 80)
    print("LISTA DE MODS DETECTADOS")
    print("=" * 80)
    print()
    
    mod_info_list = []
    
    for i, detail in enumerate(details, 1):
        title = detail.get('title', 'Sin título')
        wid = detail.get('publishedfileid', workshop_ids[i-1])
        tags = [t.get('tag', '') for t in detail.get('tags', [])]
        
        mod_info_list.append({
            'id': wid,
            'title': title,
            'tags': tags,
            'declared_name': mod_names[i-1] if i-1 < len(mod_names) else 'N/A'
        })
        
        print(f"{i:2d}. [{wid}] {title}")
        if tags:
            print(f"    Tags: {', '.join(tags[:5])}")
        print()
    
    print("=" * 80)
    print("ANÁLISIS DE CORRESPONDENCIA")
    print("=" * 80)
    print()
    
    matches = []
    mismatches = []
    
    for info in mod_info_list:
        declared = info['declared_name']
        actual = info['title']
        wid = info['id']
        
        # Normalizar para comparación
        declared_lower = declared.lower().replace(' ', '').replace('_', '').replace('-', '')
        actual_lower = actual.lower().replace(' ', '').replace('_', '').replace('-', '')
        
        # Verificar correspondencia
        is_match = (
            declared_lower in actual_lower or
            actual_lower in declared_lower or
            declared.lower() in actual.lower() or
            actual.lower() in declared.lower()
        )
        
        if is_match:
            matches.append((wid, declared, actual))
        else:
            mismatches.append((wid, declared, actual))
    
    if matches:
        print(f"✓ CORRESPONDENCIAS CORRECTAS ({len(matches)}):")
        print()
        for wid, declared, actual in matches:
            print(f"  [{wid}] {declared} → {actual}")
        print()
    
    if mismatches:
        print(f"⚠️  POSIBLES DESAJUSTES ({len(mismatches)}):")
        print()
        for wid, declared, actual in mismatches:
            print(f"  [{wid}]")
            print(f"    Declarado: {declared}")
            print(f"    Real:      {actual}")
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
        'mismatches': len(mismatches),
        'match_list': matches,
        'mismatch_list': mismatches
    }
    
    with open('mods_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print()
    print("Reporte completo guardado en: mods_report.json")

if __name__ == '__main__':
    main()
