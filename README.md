# Traffic Optimization & Emergency Routing MAS

Acest proiect reprezintă un Sistem Multi-Agent (MAS) conceput pentru a optimiza traficul urban și pentru a prioritiza vehiculele de urgență (precum ambulanțele). Este realizat folosind **Python**, biblioteca **SPADE** pentru arhitectura multi-agent, și **Eclipse SUMO** (Simulation of Urban MObility) pentru simularea fizică a traficului.

## Funcționalități principale

- **Limitare și control trafic:** Simularea rulează cu un maxim de 200 de vehicule simultan pentru a preveni supraîncărcarea necontrolată.
- **Semafoare Inteligente:** Fiecare intersecție (`TrafficLightAgent`) își reglează fazele dinamic pe baza numărului de mașini în așteptare raportat de senzori.
- **Management la Nivel de Oraș:** Un `CityManagerAgent` supervizează întreg bulevardul. Dacă traficul depășește un prag, trece în modul `RUSH_HOUR`.
- **Prioritizarea Avansată a Urgențelor (Green Wave):** 
  - Ambulanțele (`AmbulanceAgent`) identifică traseul și cer în avans **culoarea verde (Faza 2)** semafoarelor din imediata apropiere (strada curentă și următoarea).
  - Folosesc funcția nativă a simulatorului SUMO pentru vehicule de urgență, forțând mașinile din față să se dea la o parte formând un culoar de salvare (rescue lane).
  - Agenții ambulanței anulează intențiile de a întoarce în sens ale mașinilor din față pentru a preveni tăierea căii.
  - Pe măsură ce depășesc intersecțiile, trimit semnale de tip `stop` pentru a elibera imediat semafoarele. Dacă ambulanța iese din rețea, agentul se oprește curat (`kill()`) și eliberează ultimele semafoare.
- **Prevenirea Blocajelor (Anti-Deadlock & Anti-Starvation):**
  - **Cooldown Semafoare:** Semafoarele care forțează culoarea verde au un timer de **45 de secunde** de așteptare, asigurându-se că traficul de pe străzile lăturalnice nu rămâne niciodată blocat la infinit.
  - **Timeout Urgențe:** Dacă un semafor este blocat pe "Verde de Urgență" mai mult de **60 de secunde** din cauza pierderii unui pachet sau erorii unei ambulanțe, semaforul aplică un Failsafe Timeout și revine la regim normal, prevenind paralizia totală a orașului.

## Structura Proiectului

- `main.py` - Punctul principal de intrare. Inițializează simularea SUMO, creează toți agenții SPADE și pornește injectarea treptată a ambulanțelor.
- `agents/`
  - `ambulance_agent.py` - Agentul care conduce o ambulanță, cere/eliberează undă verde și forțează eliberarea benzii.
  - `city_manager_agent.py` - Agentul care monitorizează întregul bulevard și ia decizii strategice.
  - `sensor_agent.py` - Agentul care citește numărul de mașini oprite de la senzorii SUMO (via TraCI) și le raportează semaforului.
  - `traffic_light_agent.py` - Agentul care controlează faza semaforului bazat pe senzori, manager și cozi de urgență.
- `environment/`
  - Conține rețeaua SUMO (`avenue.net.xml`), configurația (`sim.sumocfg`) și rutele (`routes.rou.xml`).
- `my_prosody.cfg.lua` - Configurație custom pentru serverul XMPP local Prosody.

## Dependențe

1. **Python 3.10+**
2. **Eclipse SUMO:** Trebuie să fie instalat pe sistem (`sumo`, `sumo-gui`, `sumo-tools`).
3. **Prosody XMPP Server:** Trebuie să instalat (`sudo apt install prosody`).
4. **Pachete Python:** Instalabile prin `pip install -r requirements.txt`
   - `spade`
   - `traci`

## Instrucțiuni de inițializare și rulare

### 1. Instalarea și pornirea serverului XMPP (Prosody)
Sistemul Multi-Agent (SPADE) folosește XMPP pentru a trimite mesaje între agenți. Aveți nevoie de Prosody:

```bash
# Instalare Prosody (dacă nu este instalat pe Ubuntu/Debian)
sudo apt update && sudo apt install prosody -y

# Opriți orice instanță Prosody existentă pe portul 5224 pentru a evita conflictele
fuser -k 5224/tcp || true

# Porniți Prosody în fundal folosind configurația locală din acest proiect
prosody --config ./my_prosody.cfg.lua &
```

### 2. Rularea simulării MAS
După ce serverul XMPP rulează și așteaptă conexiuni, porniți scriptul principal de Python. Acesta va deschide interfața grafică SUMO.

```bash
# Pornire simulare
python3 main.py
```

### 3. Utilizarea Simulatorului (SUMO GUI)
- După rularea comenzii `python3 main.py`, se va deschide fereastra **SUMO-GUI**.
- Apăsați butonul de **Play (▶)** din bara de sus pentru a începe scurgerea timpului simulat.
- Puteți ajusta **Delay-ul (ms)** din bara de sus pentru a încetini sau accelera vizualizarea mașinilor.

### 4. Monitorizarea în consolă
În terminalul de unde ați pornit `main.py` veți vedea logurile detaliate ale sistemului:
- `[MANAGER]` -> Afișează strategia curentă.
- `[AMBULANTA_X]` -> Când ambulanța intră în scenă, cere verde, anulează U-turns și eliberează traseul (`🏁 Ambulanta a iesit din retea`).
- `[amab_tl_x0]` -> Când un semafor trece pe verde forțat (`🚨`), când a fost eliberat (`✅`) sau când declanșează siguranța (`⚠️ TIMEOUT urgenta!`).
