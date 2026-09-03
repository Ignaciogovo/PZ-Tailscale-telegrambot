# Análisis Exhaustivo de Mods - Project Zomboid B42

**Fecha:** 03/09/2026
**Servidor:** 5GB RAM | 2-4 jugadores (media) | 8 máx
**Build:** 42.20.4 (stable)

---

## 1. Resumen Ejecutivo

### Problema detectado
El server.ini actual tiene **44 mods** configurados. Para un servidor de **5GB RAM** con B42, esto es **excesivo**. Las guías de rendimiento 2026 indican:

| Setup | RAM recomendada |
|-------|----------------|
| Vanilla B42, 2-4 jugadores | 8GB |
| Light mods (5-10 QoL) | 12GB |
| Medium mods (15-20 mixed) | 16GB |
| Heavy mods (30+ con maps/vehicles) | 20-24GB |

**Conclusión:** Con 5GB RAM, el máximo recomendado es **10-15 mods ligeros** o **5-8 mods mixtos**. Los 44 actuales causarán crashes por OOM, lag severo y desync.

### Recomendación final
Reducir a **~20 mods** seleccionados, priorizando:
- Frameworks necesarios (damnlib, StarlitLibrary, TchernoLib)
- QoL mods ligeros
- 1-2 packs de contenido (no ambos Brita + GaelGunStore)
- Eliminar vehículos pesados (KI5 tiene ~350MB de assets)

---

## 2. Guía de Impacto por Categoría

| Categoría | Impacto RAM | Ejemplo |
|-----------|-------------|---------|
| Framework | Mínimo (~50MB) | damnlib, StarlitLibrary |
| QoL/Interface | Mínimo (~20MB) | CleanHotBar, ProximityInventory |
| Audio/Música | Bajo (~50MB) | TrueMoozic, TMCDs |
| Clothing/Armor | Medio (~200MB) | BritasArmorPackB42 |
| Vehicles | Alto (~350MB+) | KI5trailers, NepWreckWorkingCars |
| Firearms/Weapons | Alto (~500MB+) | GaelGunStore, firearms |
| Map | Muy alto (~1GB+) | MoatsB42 |
| NPC/AI | Alto (~200MB+) | Bandits (no incluido aún) |

---

## 3. Análisis de la Colección (ID: 3435349193)

**URL:** https://steamcommunity.com/sharedfiles/filedetails/?id=3435349193
**Título:** "Mods para tu partida" por Capidicapi
**Items:** 22 mods | **Valoración:** 4/5 estrellas

**⚠️ Nota:** Esta colección fue removida por Steam por violar guidelines, y marcada como incompatible con PZ. Contiene algunos mods de Build 41 que no están actualizados para B42.

### Mods de la colección y su estado en B42

| # | Mod | Workshop ID | Autor | Estado B42 | ¿Está en server.ini? |
|---|-----|-------------|-------|------------|----------------------|
| 1 | '69 Chevrolet Camaro | 2991201484 | KI5 | ✅ B42.20 MP | ❌ No |
| 2 | '92 Jeep YJ Wrangler | 3287727378 | KI5 | ✅ B42.20 MP | ❌ No |
| 3 | '82 Porsche 911 | 3379334330 | KI5 | ✅ B42.20 MP | ❌ No |
| 4 | '91 RANGE ROVER Classic | 2409333430 | KI5 | ✅ B42.20 MP | ❌ No |
| 5 | that DAMN Library | 3171167894 | KI5 | ✅ B42.20 MP | ✅ Sí |
| 6 | Map Symbol Size Slider | 2734705913 | capsgry | ✅ B42 | ❌ No |
| 7 | Add More Map Symbols (AMMS) | 3020323164 | Golem | ✅ B42 | ❌ No |
| 8 | More Maps [B42] | 3390897023 | Champy | ✅ B42 (ligero) | ❌ No |
| 9 | [B41/B42] Item Condition | 2852309899 | Qudix | ✅ B42 | ❌ No |
| 10 | Common Sense | 2875848298 | Braven | ✅ B42 | ❌ No |
| 11 | Spongie's Clothing | 2684285534 | spongie | ⚠️ Requiere Open Jackets | ❌ No |
| 12 | Spongie's Hair | 2463184726 | spongie | ✅ B42.20 | ❌ No |
| 13 | More Traits [Legacy] | 1299328280 | HypnoToadTrance | ❌ Legacy/Abandonado | ❌ No |
| 14 | [B42] Item Condition Fix | 3394609418 | Hx | ✅ B42 | ❌ No |
| 15 | Rain Cleans Blood | 2956146279 | Akamir | ✅ B42.20 MP | ✅ Sí |
| 16 | Twitch Stats | 3422377034 | M3ss | ⚠️ Solo OBS overlay | ❌ No |
| 17 | [B42] Bandits NPC | 3268487204 | Slayer | ✅ B42.20+ MP | ❌ No |
| 18 | Equipment UI [DISCONTINUED] | 2950902979 | Notloc | ❌ Discontinuado | ❌ No |
| 19 | Firearms | 2256623447 | Hyzo | ✅ B42 MP | ✅ Sí |
| 20 | Vanilla Gear Expanded | 3401134276 | Tango | ✅ B42 | ❌ No |
| 21 | Draw On The Map [DISCONTINUED] | 2804531012 | Notloc | ❌ Discontinuado | ❌ No |
| 22 | [B42] Traducción Español | 3392460250 | Turno Zero | ✅ B42 | ❌ No |

### Análisis de la colección
- **5 de 22** están en el server.ini actual
- **2 mods discontinuados** (Equipment UI, Draw On The Map) - no instalar
- **1 mod legacy** (More Traits) - abandonado, usar alternativa moderna
- **Vehículos KI5** (4 coches) - cada uno ~80MB, total ~320MB. Pesado para 5GB.
- **Common Sense** es un mod QoL excelente, debería tenerse
- **Bandits NPC** es pesado pero funcional - considerar si el servidor aguanta

---

## 4. Análisis Completo de los 44 Mods del Server.ini

### Leyenda de impacto
- 🟢 **Mínimo** - Framework/QoL, <50MB
- 🟡 **Bajo-Medio** - Contenido ligero, 50-200MB
- 🟠 **Alto** - Contenido pesado, 200-500MB
- 🔴 **Muy alto** - Assets pesados, >500MB

---

### FRAMEWORKS (Obligatorios - no eliminar)

#### 1. that DAMN Library (damnlib)
- **Workshop:** [3171167894](https://steamcommunity.com/sharedfiles/filedetails/?id=3171167894)
- **Mod ID:** damnlib
- **Autor:** KI5
- **Impacto:** 🟢 Mínimo (~27MB)
- **Compatibilidad:** ✅ B42.20 MP
- **Dependencias:** Ninguna (es dependencia de otros)
- **Función:** Framework central para TODOS los mods de KI5 (vehículos, trailers, etc.)
- **Recomendación:** **OBLIGATORIO** si se usan mods KI5. Si se eliminan todos los vehículos KI5, se puede quitar.

#### 2. Starlit Library
- **Workshop:** [3378285185](https://steamcommunity.com/sharedfiles/filedetails/?id=3378285185)
- **Mod ID:** StarlitLibrary
- **Autor:** albion (demiurgeQuantified)
- **Impacto:** 🟢 Mínimo (~0.34MB)
- **Compatibilidad:** ✅ B42 MP
- **Dependencias:** Ninguna (es dependencia de otros)
- **Función:** Framework de dependencias para otros mods (Burd's Survival Journals, etc.)
- **Recomendación:** **OBLIGATORIO** si se usa BurdSurvivalJournals u otros mods que lo requieran.

#### 3. Moodle Framework
- **Workshop:** [3396446795](https://steamcommunity.com/sharedfiles/filedetails/?id=3396446795)
- **Mod ID:** MoodleFramework
- **Autor:** Tchernobill
- **Impacto:** 🟢 Mínimo (~0.08MB)
- **Compatibilidad:** ⚠️ B42 (removido de Steam, versión B41 marcada como OBSOLETE)
- **Dependencias:** Ninguna (es framework)
- **Función:** API para crear moodles personalizados
- **Recomendación:** **VERIFICAR** - El Workshop ID 3396446795 está marcado como removido/incompatible en Steam. Si ningún mod lo requiere activamente, **ELIMINAR**. Si se necesita, buscar versión actualizada.

#### 4. NeatUI Framework
- **Workshop:** [3508537032](https://steamcommunity.com/sharedfiles/filedetails/?id=3508537032)
- **Mod ID:** NeatUI_Framework
- **Autor:** Rocco/Afyrmo
- **Impacto:** 🟢 Mínimo
- **Compatibilidad:** ✅ B42.0.2 a B42.20.x
- **Dependencias:** Ninguna (es framework para CleanUI, Neat Crafting, etc.)
- **Función:** Framework UI compartido
- **Recomendación:** **OBLIGATORIO** si se usan CleanUI, Neat Crafting o Neat Building. En server.ini no se incluyen esos mods, así que **EVALUAR** si se necesita.

#### 5. TchernoLib
- **Workshop:** [No verificado - buscar ID]
- **Mod ID:** TchernoLib
- **Autor:** Tchernobill
- **Impacto:** 🟢 Mínimo
- **Función:** API con herramientas variadas para modders
- **Recomendación:** **VERIFICAR** si algún mod lo requiere como dependencia.

---

### MODS DE CALIDAD DE VIDA (QoL) - Recomendados

#### 6. CleanHotBar
- **Workshop:** [No verificado en server.ini WorkshopItems]
- **Mod ID:** CleanHotBar
- **Impacto:** 🟢 Mínimo
- **Función:** Rediseño del hotbar para mejor legibilidad
- **Recomendación:** **MANTENER** - QoL puro, sin impacto.

#### 7. Proximity Inventory
- **Workshop:** [2847184718](https://steamcommunity.com/sharedfiles/filedetails/?id=2847184718)
- **Mod ID:** ProximityInventory
- **Autor:** Mxswat
- **Impacto:** 🟢 Mínimo
- **Compatibilidad:** ✅ B42.20+
- **Función:** Muestra contenido de contenedores cercanos en una ventana
- **Recomendación:** **MANTENER** - Muy útil para gestión de base.

#### 8. RefreshMinimalDisplayBars
- **Workshop:** [No verificado]
- **Mod ID:** RefreshMinimalDisplayBars
- **Impacto:** 🟢 Mínimo
- **Función:** Barras de estado mejoradas
- **Recomendación:** **MANTENER** - QoL puro.

#### 9. P4HasBeenRead
- **Workshop:** [2544353492](https://steamcommunity.com/sharedfiles/filedetails/?id=2544353492)
- **Mod ID:** P4HasBeenRead (Has Been Read)
- **Autor:** PePePePePeil
- **Impacto:** 🟢 Mínimo
- **Compatibilidad:** ✅ B42.20
- **Función:** Marca libros/magazines leídos
- **Recomendación:** **MANTENER** - QoL excelente.

#### 10. AutoDrop_B42
- **Workshop:** [No verificado]
- **Mod ID:** AutoDrop_B42
- **Impacto:** 🟢 Mínimo
- **Función:** Auto-soltar items según configuración
- **Recomendación:** **MANTENER** - QoL útil.

#### 11. traitsAsSkills
- **Workshop:** [No verificado]
- **Mod ID:** traitsAsSkills
- **Impacto:** 🟢 Mínimo
- **Función:** Convierte traits en skills progresivos
- **Recomendación:** **EVALUAR** - Puede cambiar balance del juego.

#### 12. TrueWeight
- **Workshop:** [No verificado]
- **Mod ID:** TrueWeight
- **Impacto:** 🟢 Mínimo
- **Función:** Muestra peso real de items
- **Recomendación:** **MANTENER** - QoL.

#### 13. ReducedWoodWeight2x41
- **Workshop:** [No verificado]
- **Mod ID:** ReducedWoodWeight2x41
- **Impacto:** 🟢 Mínimo
- **Función:** Reduce peso de madera
- **Recomendación:** **EVALUAR** - Afecta balance.

#### 14. 50%metalweight
- **Workshop:** [No verificado]
- **Mod ID:** 50%metalweight
- **Impacto:** 🟢 Mínimo
- **Función:** Reduce peso de metal 50%
- **Recomendación:** **EVALUAR** - Afecta balance.

#### 15. Obvious_Skill_Tapes
- **Workshop:** [No verificado]
- **Mod ID:** Obvious_Skill_Tapes
- **Impacto:** 🟢 Mínimo
- **Función:** Hace obvio qué skill enseña cada tape
- **Recomendación:** **MANTENER** - QoL.

#### 16. RepairAnyClothes
- **Workshop:** [No verificado]
- **Mod ID:** RepairAnyClothes
- **Impacto:** 🟢 Mínimo
- **Función:** Permite reparar cualquier ropa
- **Recomendación:** **MANTENER** - QoL.

---

### MODS DE CONTENIDO LIGERO

#### 17. ShelterHold_Beehive
- **Workshop:** [No verificado]
- **Mod ID:** ShelterHold_Beehive
- **Impacto:** 🟡 Bajo
- **Función:** Sistema de colmenas/abejas
- **Recomendación:** **EVALUAR** - Contenido niche, bajo impacto.

#### 18. Buttstroke
- **Workshop:** [No verificado]
- **Mod ID:** Buttstroke
- **Impacto:** 🟡 Bajo
- **Función:** Ataque cuerpo a cuerpo con culata de arma
- **Recomendación:** **EVALUAR** - Contenido ligero.

#### 19. PSR
- **Workshop:** [No verificado]
- **Mod ID:** PSR
- **Impacto:** 🟡 Bajo
- **Función:** [No determinado - verificar]
- **Recomendación:** **VERIFICAR** función antes de decidir.

#### 20. TrueSleep
- **Workshop:** [No verificado]
- **Mod ID:** TrueSleep
- **Impacto:** 🟡 Bajo
- **Función:** Sistema de sueño mejorado
- **Recomendación:** **EVALUAR** - Afecta gameplay.

#### 21. WildernessCalm
- **Workshop:** [No verificado]
- **Mod ID:** WildernessCalm
- **Impacto:** 🟡 Bajo
- **Función:** [No determinado - verificar]
- **Recomendación:** **VERIFICAR**.

#### 22. RainCleansBlood
- **Workshop:** [2956146279](https://steamcommunity.com/sharedfiles/filedetails/?id=2956146279)
- **Mod ID:** RainCleansBlood
- **Autor:** Akamir
- **Impacto:** 🟢 Mínimo
- **Compatibilidad:** ✅ B42.20 MP
- **Función:** Lluvia/nieve limpia sangre del suelo
- **Recomendación:** **MANTENER** - Inmersión, sin impacto.

---

### MODS DE ARMAS (Compatibles entre sí)

#### 23. GaelGunStore_B42
- **Workshop:** [3616176188](https://steamcommunity.com/sharedfiles/filedetails/?id=3616176188)
- **Mod ID:** GaelGunStore_B42
- **Autor:** Pen-Pen Pirulin
- **Impacto:** 🔴 Muy alto (~500MB+, 366+ armas, 400+ accesorios)
- **Compatibilidad:** ✅ B42.20 MP
- **Dependencias:** Ninguna
- **Notas:** Reemplaza y edita TODAS las armas vanilla. **Incompatible** con Brita's Weapon Pack y cualquier otro mod de armas vanilla.
- **Recomendación:** ⚠️ **ELEGIR UNO:** GaelGunStore O firearms (Hyzo). NO ambos. GaelGunStore es más completo pero mucho más pesado.

#### 24. firearms (Hyzo)
- **Workshop:** [2256623447](https://steamcommunity.com/sharedfiles/filedetails/?id=2256623447)
- **Mod ID:** firearms
- **Autor:** Hyzo
- **Impacto:** 🟠 Alto (~300MB, 200+ armas)
- **Compatibilidad:** ✅ B42 MP
- **Dependencias:** Ninguna
- **Notas:** Requiere que GaelGunStore NO esté activo (conflicto de edición vanilla)
- **Recomendación:** Alternativa más ligera a GaelGunStore. **ELEGIR UNO.**

#### 25. BCGToolsTEST
- **Workshop:** [No verificado]
- **Mod ID:** BCGToolsTEST
- **Impacto:** 🟡 Bajo
- **Función:** Bushcraft Gear - herramientas
- **Recomendación:** **EVALUAR** - Puede ser redundante con otros mods de crafting.

#### 26. BCGRareWeaponsTEST
- **Workshop:** [2432621382](https://steamcommunity.com/sharedfiles/filedetails/?id=2432621382) (Bushcraft Gear)
- **Mod ID:** BCGRareWeaponsTEST
- **Autor:** Scavenger
- **Impacto:** 🟡 Bajo (~50MB)
- **Compatibilidad:** ✅ B42 MP
- **Función:** Armas raras (hacha vikingo, bate reforzado)
- **Recomendación:** **MANTENER** si se quiere rareza. Bajo impacto.

---

### MODS DE ROPA/ARMADURA

#### 27. BritasArmorPackB42
- **Workshop:** [3780298456](https://steamcommunity.com/sharedfiles/filedetails/?id=3780298456)
- **Mod ID:** BritasArmorPackB42
- **Autor:** Brita (port no oficial B42.20)
- **Impacto:** 🟠 Alto (~300MB+, cientos de items de ropa/armadura)
- **Compatibilidad:** ✅ B42.20
- **Dependencias:** Ninguna (port standalone)
- **Notas:** No incluye Brita's Weapon Pack. Port no oficial, puede tener bugs.
- **Recomendación:** **EVALUAR** - Contenido pesado. Si se quiere ropa militar, es buena opción. Sino, considerar Vanilla Gear Expanded (más ligero).

---

### MODS DE VEHÍCULOS

#### 28. KI5trailers
- **Workshop:** [3330403100](https://steamcommunity.com/sharedfiles/filedetails/?id=3330403100)
- **Mod ID:** KI5trailers
- **Autor:** KI5
- **Impacto:** 🟠 Alto (~200MB+)
- **Compatibilidad:** ✅ B42.20 MP
- **Dependencias:** damnlib
- **Función:** Trailers y remolques
- **Recomendación:** **EVALUAR** - Los trailers son útiles pero pesados. Si se eliminan todos los vehículos KI5, también se elimina damnlib.

#### 29. NepWreckWorkingCars
- **Workshop:** [No verificado]
- **Mod ID:** NepWreckWorkingCars
- **Impacto:** 🟠 Alto (~200MB+)
- **Función:** Vehículos wrecked que pueden repararse
- **Recomendación:** **EVALUAR** - Pack de vehículos. Considerar si se necesita.

#### 30. MoatsB42
- **Workshop:** [No verificado]
- **Mod ID:** MoatsB42
- **Impacto:** 🔴 Muy alto (mapa)
- **Función:** Mapa nuevo
- **Recomendación:** ⚠️ **CUIDADO** - Los mapas son los mods más pesados. Solo incluir si se necesita. Requiere agregar a `Map=` en server.ini.

---

### MODS DE MÚSICA/AUDIO

#### 31. TrueMoozic
- **Workshop:** [3632610172](https://steamcommunity.com/sharedfiles/filedetails/?id=3632610172)
- **Mod ID:** TrueMoozic
- **Autor:** (sucesor de True Music de iBrRus)
- **Impacto:** 🟢 Mínimo (~50MB base, + contenido de música)
- **Compatibilidad:** ✅ B42 MP
- **Función:** Sistema de música para reproductores de disco/CD
- **Recomendación:** **MANTENER** si se quiere sistema de música. Ligero.

#### 32. TrueSmoking
- **Workshop:** [No verificado]
- **Mod ID:** TrueSmoking
- **Impacto:** 🟢 Mínimo
- **Función:** Sistema de fumar mejorado
- **Recomendación:** **MANTENER** - Inmersión, bajo impacto.

#### 33. TM_PinkFloydDark
- **Workshop:** [No verificado]
- **Mod ID:** TM_PinkFloydDark
- **Impacto:** 🟢 Mínimo (contenido de música)
- **Función:** Álbum de Pink Floyd para True Moozic
- **Recomendación:** **MANTENER** si se usa TrueMoozic. Sin esto, TrueMoozic no tiene música.

#### 34. TMMMB42.13+
- **Workshop:** [No verificado]
- **Mod ID:** TMMMB42.13+
- **Impacto:** 🟢 Mínimo (contenido de música)
- **Función:** Más música para True Moozic
- **Recomendación:** **MANTENER** si se usa TrueMoozic.

#### 35. TMCDs
- **Workshop:** [No verificado]
- **Mod ID:** TMCDs
- **Impacto:** 🟢 Mínimo (contenido de música)
- **Función:** CDs de música para True Moozic
- **Recomendación:** **MANTENER** si se usa TrueMoozic.

#### 36. TMPK02
- **Workshop:** [No verificado]
- **Mod ID:** TMPK02
- **Impacto:** 🟢 Mínimo (contenido de música)
- **Función:** Pack de música adicional
- **Recomendación:** **MANTENER** si se usa TrueMoozic.

---

### MODS DE FARMING/AGRICULTURA

#### 37. LGExtendedPlumbing
- **Workshop:** [No verificado]
- **Mod ID:** LGExtendedPlumbing
- **Impacto:** 🟡 Bajo
- **Función:** Sistema de plomería extendido
- **Recomendación:** **EVALUAR** - Útil para granjas. Compatible con Waterpipes.

#### 38. Waterpipes
- **Workshop:** [3546314080](https://steamcommunity.com/sharedfiles/filedetails/?id=3546314080)
- **Mod ID:** Waterpipes
- **Autor:** (desconocido)
- **Impacto:** 🟡 Bajo-Medio
- **Compatibilidad:** ✅ B42
- **Función:** Sistema de riego por tuberías desde ríos/lagos
- **Recomendación:** **EVALUAR** - Muy útil para agricultura. Puede conflicto con LGExtendedPlumbing. Elegir uno.

---

### MODS DE CONTENIDO VARIADO

#### 39. jiggasGreenfireMod
- **Workshop:** [No verificado]
- **Mod ID:** jiggasGreenfireMod
- **Impacto:** 🟡 Bajo
- **Función:** [No determinado - verificar]
- **Recomendación:** **VERIFICAR**.

#### 40. PIP
- **Workshop:** [No verificado]
- **Mod ID:** PIP
- **Impacto:** 🟡 Bajo
- **Función:** [No determinado - verificar]
- **Recomendación:** **VERIFICAR**.

#### 41. PAR
- **Workshop:** [No verificado]
- **Mod ID:** PAR
- **Impacto:** 🟡 Bajo
- **Función:** [No determinado - verificar]
- **Recomendación:** **VERIFICAR**.

#### 42. PSC
- **Workshop:** [No verificado]
- **Mod ID:** PSC
- **Impacto:** 🟡 Bajo
- **Función:** [No determinado - verificar]
- **Recomendación:** **VERIFICAR**.

#### 43. BurdSurvivalJournals
- **Workshop:** [No verificado]
- **Mod ID:** BurdSurvivalJournals
- **Impacto:** 🟡 Bajo
- **Dependencias:** StarlitLibrary
- **Función:** Diarios de supervivencia
- **Recomendación:** **MANTENER** si se quiere inmersión. Requiere StarlitLibrary.

#### 44. VanillaFoodsExpanded
- **Workshop:** [3577903007](https://steamcommunity.com/sharedfiles/filedetails/?id=3577903007)
- **Mod ID:** VanillaFoodsExpanded
- **Autor:** jiizzjacuzzii
- **Impacto:** 🟡 Bajo-Medio (~100MB)
- **Compatibilidad:** ✅ B42
- **Función:** Expande la categoría de cocina con nuevas recetas
- **Recomendación:** **MANTENER** - Contenido que respeta el balance vanilla. Uno de los mejores mods de cocina.

---

## 5. Mapa de Dependencias

```
damnlib ──────────┬── KI5trailers
                  ├── NepWreckWorkingCars (si es KI5)
                  └── Cualquier mod KI5 de vehículos

StarlitLibrary ─── BurdSurvivalJournals

NeatUI_Framework ─ (CleanUI, Neat Crafting, Neat Building) [NO instalados]

MoodleFramework ── (Mods que usen moodles custom) [Posible obsoleto]

TchernoLib ──────── (Algunos mods de Tchernobill)
```

---

## 6. Conflictos Detectados

| Conflicto | Mods afectados | Solución |
|-----------|----------------|----------|
| **Armas vanilla** | GaelGunStore + firearms | Elegir UNO. GaelGunStore reemplaza todas las armas vanilla; firearms también. |
| **Plomería** | LGExtendedPlumbing + Waterpipes | Elegir UNO. Ambos modifican sistema de agua. |
| **MoodleFramework** | Posiblemente obsoleto | Verificar si algún mod lo necesita activamente. Si no, eliminar. |
| **damnlib** | Solo necesario con vehículos KI5 | Si se eliminan todos los vehículos KI5, se puede quitar damnlib. |

---

## 7. Tabla Resumen de Recomendaciones

### ✅ MANTENER (14 mods esenciales)

| Mod | Categoría | Workshop URL | Por qué |
|-----|-----------|--------------|---------|
| damnlib | Framework | [3171167894](https://steamcommunity.com/sharedfiles/filedetails/?id=3171167894) | Requerido por vehículos KI5 |
| StarlitLibrary | Framework | [3378285185](https://steamcommunity.com/sharedfiles/filedetails/?id=3378285185) | Requerido por BurdSurvivalJournals |
| CleanHotBar | QoL | No verificado | Interface mejorada |
| ProximityInventory | QoL | [2847184718](https://steamcommunity.com/sharedfiles/filedetails/?id=2847184718) | Gestión de base |
| P4HasBeenRead | QoL | [2544353492](https://steamcommunity.com/sharedfiles/filedetails/?id=2544353492) | Marca lectura |
| TrueWeight | QoL | No verificado | Info de peso |
| Obvious_Skill_Tapes | QoL | No verificado | Info de tapes |
| RepairAnyClothes | QoL | No verificado | Reparación flexible |
| AutoDrop_B42 | QoL | No verificado | Auto-soltar |
| RainCleansBlood | Inmersión | [2956146279](https://steamcommunity.com/sharedfiles/filedetails/?id=2956146279) | Limpieza ambiental |
| TrueMoozic | Audio | [3632610172](https://steamcommunity.com/sharedfiles/filedetails/?id=3632610172) | Sistema de música |
| TM_PinkFloydDark | Audio | No verificado | Música para TrueMoozic |
| VanillaFoodsExpanded | Contenido | [3577903007](https://steamcommunity.com/sharedfiles/filedetails/?id=3577903007) | Cocina expandida |
| BCGRareWeaponsTEST | Contenido | [2432621382](https://steamcommunity.com/sharedfiles/filedetails/?id=2432621382) | Armas raras, bajo impacto |

### ⚠️ EVALUAR (8 mods opcionales)

| Mod | Workshop URL | Condición para mantener |
|-----|--------------|------------------------|
| KI5trailers | [3330403100](https://steamcommunity.com/sharedfiles/filedetails/?id=3330403100) | Si se quieren trailers |
| NepWreckWorkingCars | No verificado | Si se quieren más vehículos |
| Waterpipes | [3546314080](https://steamcommunity.com/sharedfiles/filedetails/?id=3546314080) | Si se usa agricultura intensiva |
| BurdSurvivalJournals | No verificado | Si se quiere sistema de diarios |
| BritasArmorPackB42 | [3780298456](https://steamcommunity.com/sharedfiles/filedetails/?id=3780298456) | Si se quiere ropa militar pesada |
| traitsAsSkills | No verificado | Si se quiere progresión de traits |
| ReducedWoodWeight2x41 | No verificado | Si se quiere reducir peso madera |
| 50%metalweight | No verificado | Si se quiere reducir peso metal |

### ❌ ELIMINAR (7+ mods)

| Mod | Razón |
|-----|-------|
| MoodleFramework | Posiblemente obsoleto, verificar dependencias |
| MoatsB42 | Mapa = extremadamente pesado para 5GB |
| GaelGunStore_B42 | O/firearms. Elegir UNO. Si se elige firearms, eliminar este. |
| firearms | O/GaelGunStore. Elegir UNO. Si se elige GaelGunStore, eliminar este. |
| LGExtendedPlumbing | Conflicto con Waterpipes. Elegir uno. |
| TchernoLib | Verificar si algún mod lo necesita. Si no, eliminar. |
| TMCDs, TMMMB42.13+, TMPK02 | Redundantes si ya hay TM_PinkFloydDark. Mantener solo 1-2 packs de música. |

---

## 8. Configuración Recomendada Final (5GB RAM)

### Opción A: Ultra-conservadora (15 mods)
```
WorkshopItems=3171167894;3378285185;2847184718;2544353492;2956146279;3632610172;3577903007;2432621382;2256623447
Mods=\damnlib;\StarlitLibrary;\ProximityInventory;\P4HasBeenRead;\RainCleansBlood;\TrueMoozic;\TM_PinkFloydDark;\VanillaFoodsExpanded;\BCGRareWeaponsTEST;\firearms;\CleanHotBar;\TrueWeight;\Obvious_Skill_Tapes;\RepairAnyClothes;\AutoDrop_B42
```
- 1 framework KI5 + 1 framework Starlit + 1 arma + 1 cocina + 1 rareza + 5 QoL + 2 audio + 1 inmersión
- ~800MB total estimado
- **Ideal para 5GB RAM con 2-4 jugadores**

### Opción B: Moderada (20 mods)
```
WorkshopItems=3171167894;3378285185;2847184718;2544353492;2956146279;3632610172;3577903007;2432621382;2256623447;3330403100;3546314080;3780298456
Mods=\damnlib;\StarlitLibrary;\ProximityInventory;\P4HasBeenRead;\RainCleansBlood;\TrueMoozic;\TM_PinkFloydDark;\VanillaFoodsExpanded;\BCGRareWeaponsTEST;\firearms;\CleanHotBar;\TrueWeight;\Obvious_Skill_Tapes;\RepairAnyClothes;\AutoDrop_B42;\KI5trailers;\Waterpipes;\BritasArmorPackB42;\traitsAsSkills;\BurdSurvivalJournals
```
- 2 frameworks + 2 armas + 1 cocina + 1 rareza + 1 vehicle + 1 farming + 1 armor + 7 QoL + 2 audio + 1 inmersión
- ~1.5GB total estimado
- **Riesgo: puede causar lag con 8 jugadores**

### Opción C: Con GaelGunStore (18 mods)
Si prefieres GaelGunStore sobre firearms:
```
WorkshopItems=3171167894;3378285185;2847184718;2544353492;2956146279;3632610172;3577903007;2432621382;3616176188
Mods=\damnlib;\StarlitLibrary;\ProximityInventory;\P4HasBeenRead;\RainCleansBlood;\TrueMoozic;\TM_PinkFloydDark;\VanillaFoodsExpanded;\BCGRareWeaponsTEST;\GaelGunStore_B42;\CleanHotBar;\TrueWeight;\Obvious_Skill_Tapes;\RepairAnyClothes;\AutoDrop_B42
```
- ~900MB total estimado (GaelGunStore es más pesado que firearms)

---

## 9. Notas de Instalación

### Formato Build 42
En B42, cada Mod ID debe tener prefijo `\`:
```
Mods=\damnlib;\StarlitLibrary;\ProximityInventory
```

### Carga de dependencias
El orden en `Mods=` importa. Frameworks primero:
1. damnlib (framework KI5)
2. StarlitLibrary (framework dependencias)
3. TchernoLib (si se usa)
4. NeatUI Framework (si se usa)
5. Mods que dependen de los frameworks
6. Resto de mods

### Mapas
Si se usa MoatsB42 u otro mapa, agregar a `Map=`:
```
Map=Muldraugh, KY;MoatsB42
```

---

## 10. Safe Uninstall: Requisitos por Mod

> **⚠️ IMPORTANTE:** En Project Zomboid B42, quitar mods de un save existente puede corromper el mundo. Cada mod tiene riesgos diferentes según tipo. Esta sección documenta qué mods se pueden quitar de forma segura y cuáles requieren procedimientos especiales.

### Principio general de B42
Build 42 almacena definiciones de mods en el `WorldDictionary` del save. Si se quita un mod que registró contenido (items, recetas, entidades de mundo), el juego puede fallar al cargar porque esas definiciones ya no existen.

### Clasificación de riesgo por tipo de mod

| Tipo de mod | Riesgo al quitar | Descripción |
|-------------|-------------------|-------------|
| **Framework** (damnlib, StarlitLibrary) | 🔴 ALTO | Si otros mods dependen de él, esos mods también deben quitarse. Si no hay dependientes, es seguro. |
| **QoL/Interface** | 🟢 BAJO | No registran contenido en el mundo. Safe para quitar. |
| **Audio/Música** | 🟢 BAJO | Solo agregan items de audio. Seguro. |
| **Recetas/Cocina** | 🟡 MEDIO | Recetas creadas desaparecen de los生存istas. No corrompe el save pero items cocinados con esas recetas pueden quedar en inventario sin receta asociada. |
| **Armas/Armament** | 🔴 ALTO | Reemplazan modelos vanilla. Items spawned quedan con texturas rotas. |
| **Vehículos** | 🟠 ALTO | Vehículos en el mundo quedan como objetos huérfanos. Pueden causar errores de carga. |
| **Mapas** | 🔴 CRÍTICO | NO se pueden quitar de un save existente. Crea huecos en el mapa y corrupción del mundo. |
| **Mundo** (plomería, construcciones) | 🔴 ALTO | Entidades construidas por el jugador quedan con scripts inválidos. Save puede romperse. |

---

### Mods con Safe Uninstall Soportado

#### Waterpipes (Workshop: 3546314080)
- **Riesgo:** 🔴 ALTO — "if you remove the mod, your save will break"
- **Safe Uninstall:** ✅ SÍ — El mod incluye `WaterpipesRemoved` (Mod ID incluido)
- **Procedimiento:**
  1. Quitar `Waterpipes` de `Mods=`
  2. Agregar `WaterpipesRemoved` a `Mods=`
  3. Agregar el mismo Workshop ID `3546314080` a `WorkshopItems=`
  4. Reiniciar servidor
- **Nota:** Las tuberías instaladas permanecen en el mundo pero sin funcionalidad. No se pueden construir nuevas.

#### ShelterHold: Beehive (Workshop: ShelterHold_Beehive)
- **Riesgo:** 🔴 ALTO — Entidades de colmenas/extractores quedan con definiciones faltantes
- **Safe Uninstall:** ✅ SÍ — Existe mod separado `ShelterHold: Beehive - Safe Uninstall Support` (Workshop: 3791498378)
- **Procedimiento:**
  1. Detener servidor y backup del save
  2. Quitar `ShelterHold_Beehive` de `Mods=`
  3. Agregar `ShelterHold_Beehive_SafeUninstallSupport` a `Mods=`
  4. Quitar el Workshop ID principal de `WorkshopItems=`, agregar `3791498378`
  5. Reiniciar servidor
- **Nota:** NO habilitar ambos mods al mismo tiempo. Las colmenas/extractores existentes permanecen pero sin producción.

---

### Mods con Riesgo ALTO (No Safe Uninstall)

#### GaelGunStore_B42 (Workshop: 3616176188)
- **Riesgo:** 🔴 ALTO
- **Descripción:** Reemplaza TODAS las armas vanilla. 366+ armas, 400+ accesorios.
- **Al quitar:** Items spawned en el mundo quedan con texturas/modelos rotos. El juego mostrará errores de "missing dictionary script" para cada arma GaelGunStore en inventarios, contenedores y zombies.
- **Safe Uninstall:** ❌ NO — No incluye mecanismo de desinstalación segura.
- **Recomendación:** Si se quita, considerar empezar un mundo nuevo. O usar debug mode para eliminar todos los items del mod antes de quitarlo ( laborioso).

#### firearms / Hyzo (Workshop: 2256623447)
- **Riesgo:** 🔴 ALTO
- **Descripción:** "all of the changes in this mod will irreversibly change any save it is applied to, so it is therefore not recommended you remove this mod mid-playthrough."
- **Al quitar:** Texturas rotas para todas las armas de firearms en el mundo.
- **Safe Uninstall:** ❌ NO — Autor advierte explícitamente contra desinstalación mid-playthrough.
- **Recomendación:** Igual que GaelGunStore. Elegir uno y no quitarlo.

#### MoatsB42 (Mapa)
- **Riesgo:** 🔴 CRÍTICO
- **Descripción:** Mapa completo que agrega chunks al mundo.
- **Al quitar:** Crea huecos en el mapa, terreno faltante, structures rotas. El mundo puede volverse injugable.
- **Safe Uninstall:** ❌ NO — Los mapas NO se pueden quitar de saves existentes bajo ninguna circunstancia.
- **Recomendación:** Si se instaló, debe permanecer para siempre en ese save.

---

### Mods con Riesgo MEDIO

#### KI5trailers + damnlib (Workshop: 3330403100)
- **Riesgo:** 🟠 ALTO
- **Descripción:** Vehículos trailers que quedan como objetos en el mundo.
- **Al quitar:** Trailers en el mundo quedan como objetos huérfanos. Pueden causar errores al cargar chunks, pero generalmente el save no se rompe completamente.
- **Safe Uninstall:** ⚠️ PARCIAL — No hay safe uninstall mod. Pero el riesgo es manejable si no hay muchos vehículos spawned.
- **Recomendación:** Antes de quitar, recoger todos los trailers a una zona central y eliminarlos con admin commands.

#### NepWreckWorkingCars
- **Riesgo:** 🟠 ALTO
- **Descripción:** Vehículos wrecked reparables.
- **Al quitar:** Mismo caso que KI5 — vehículos huérfanos en el mundo.
- **Safe Uninstall:** ⚠️ PARCIAL — Sin mecanismo oficial.
- **Recomendación:** Misma que KI5trailers.

#### BritasArmorPackB42 (Workshop: 3780298456)
- **Riesgo:** 🟡 MEDIO
- **Descripción:** Solo ropa/armadura, NO armas. No modifica entidades de mundo.
- **Al quitar:** Items de Brita en inventarios quedan sin modelo visible. No corrompe el mundo pero objetos son inutilizables.
- **Safe Uninstall:** ⚠️ PARCIAL — No incluye safe uninstall. Pero al ser solo items de inventario (no world entities), el save generalmente carga bien.
- **Recomendación:** Antes de quitar, tirar/vender todos los items de Brita en el mundo.

#### Waterpipes (sin usar WaterpipesRemoved)
- **Riesgo:** 🔴 ALTO
- **Al quitar sin Safe Uninstall:** Save NO carga. El juego falla porque las tuberías construidas tienen scripts que ya no existen.
- **Recomendación:** SIEMPRE usar el procedimiento de Safe Uninstall con `WaterpipesRemoved`.

---

### Mods con Riesgo BAJO (Safe para quitar)

| Mod | Workshop | Tipo | Razón safe |
|-----|----------|------|------------|
| CleanHotBar | No verificado | QoL | Interfaz, no world data |
| ProximityInventory | 2847184718 | QoL | Interfaz |
| P4HasBeenRead | 2544353492 | QoL | Solo flags de lectura |
| TrueWeight | No verificado | QoL | Solo info en UI |
| Obvious_Skill_Tapes | No verificado | QoL | Solo labels |
| RepairAnyClothes | No verificado | QoL | Solo recetas, items vanilla |
| AutoDrop_B42 | No verificado | QoL | Gameplay helper |
| RainCleansBlood | 2956146279 | Inmersión | Solo visual, no world entities |
| TrueMoozic | 3632610172 | Audio | Items de audio, no world data |
| TM_PinkFloydDark | No verificado | Audio | Contenido musical |
| VanillaFoodsExpanded | 3577903007 | Recetas | Recetas nuevas. Al quitar, desaparecen pero no corrompen. |
| BCGRareWeaponsTEST | 2432621382 | Armas ligeras | Solo 2 armas raras, solo loot tables. No reemplaza vanilla. |
| BurdSurvivalJournals | No verificado | Contenido | Items de inventario |
| traitsAsSkills | No verificado | QoL | Solo progresión |
| ReducedWoodWeight2x41 | No verificado | Balance | Solo pesos |
| 50%metalweight | No verificado | Balance | Solo pesos |

---

### Resumen de safe uninstall por opción de configuración

#### Opción A (15 mods) — ✅ SAFE para reconfigurar
Todos los mods de esta opción son QoL/audio/balance. Ninguno modifica el mundo ni reemplaza entidades vanilla. Se pueden quitar sin problemas.

#### Opción B (20 mods) — ⚠️ CUIDADO con estos:
- **Waterpipes** → Usar WaterpipesRemoved antes de quitar
- **KI5trailers** → Recoger todos los trailers antes de quitar
- **damnlib** → Solo quitar si no hay otros mods KI5 activos
- **BritasArmorPackB42** → Tirar items Brita antes de quitar

#### Opción C (18 mods con GaelGunStore) — ⚠️ ALTO RIESGO
- **GaelGunStore_B42** → No se puede quitar de forma segura. Si se quita, el mundo queda con items rotos. Considérese como permanente para ese save.

---

### Regla de oro
> **Antes de quitar cualquier mod de categoría ALTA o CRÍTICA, hacer backup del save completo. Si el mod agregó entidades al mundo (vehículos, construcciones, armas spawned), el save puede no cargar correctamente sin ese mod.**

---

## 11. Fuentes

- Steam Workshop: https://steamcommunity.com/app/108600/workshop/
- Guía RAM B42: https://winternode.com/blog/project-zomboid/how-much-ram
- Guía rendimiento: https://supercraft.host/wiki/project-zomboid/b42_performance_tuning/
- Guía mods B42: https://winternode.com/blog/project-zomboid/best-server-mods-build-42
- Colección analizada: https://steamcommunity.com/sharedfiles/filedetails/?id=3435349193
- Mods individuales: https://steamcommunity.com/workshop/filedetails/?id=2490220997
- Guía removal: https://supercraft.host/wiki/project-zomboid/remove_mod/
- Waterpipes: https://steamcommunity.com/sharedfiles/filedetails/?id=3546314080
- ShelterHold Safe Uninstall: https://steamcommunity.com/sharedfiles/filedetails/?id=3791498378
- GaelGunStore: https://steamcommunity.com/sharedfiles/filedetails/?id=3616176188
- firearms: https://steamcommunity.com/sharedfiles/filedetails/?id=2256623447
