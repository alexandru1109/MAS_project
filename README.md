# Traffic Optimization & Emergency Routing MAS

Acest proiect reprezintă un Sistem Multi-Agent (MAS) conceput pentru a optimiza traficul urban și pentru a prioritiza vehiculele de urgență (precum ambulanțele). Este realizat folosind **Python**, biblioteca **SPADE** pentru arhitectura multi-agent, și **Eclipse SUMO** (Simulation of Urban MObility) pentru simularea fizică a traficului.

## Funcționalități principale

- **Limitare și control trafic:** Simularea rulează cu un maxim de 200 de vehicule simultan pentru a preveni supraîncărcarea necontrolată. S-au adăugat și fluxuri de **pietoni** (`personFlow`) pe diferite segmente pentru un realism sporit.
- **Semafoare Inteligente:** Fiecare intersecție (`TrafficLightAgent`) își reglează fazele dinamic pe baza numărului de mașini în așteptare raportat de senzori, utilizând o limită variabilă.
- **Management la Nivel de Oraș:** Un `CityManagerAgent` supervizează întreg bulevardul. Dacă traficul cumulat depășește un anumit prag, managerul schimbă strategia tuturor semafoarelor în modul `RUSH_HOUR`, forțându-le să deschidă culoarea verde mai repede.
- **Prioritizarea Ambulanțelor:** Până la **10 ambulanțe** (`AmbulanceAgent`) sunt injectate treptat în sistem. Pe măsură ce ambulanța se apropie de o intersecție, agentul său trimite o cerere de urgență (preemțiune) direct către agentul semaforului respectiv. Semaforul trece imediat pe **VERDE** până când ambulanța depășește intersecția.
- **Comunicație XMPP:** Toți agenții (semafoare, senzori, manager, ambulanțe) comunică între ei prin intermediul unui server XMPP (ex. **Prosody** instalat local).

## Structura Proiectului

- `main.py` - Punctul principal de intrare. Inițializează simularea SUMO (limitând vehiculele cu flag-ul `--max-num-vehicles`), creează toți agenții SPADE și pornește injectarea treptată a ambulanțelor.
- `agents/`
  - `ambulance_agent.py` - Agentul care conduce o ambulanță și cere undă verde.
  - `city_manager_agent.py` - Agentul care monitorizează întregul bulevard și ia decizii strategice.
  - `sensor_agent.py` - Agentul care citește numărul de mașini oprite de la senzorii SUMO (via TraCI) și le raportează semaforului.
  - `traffic_light_agent.py` - Agentul care controlează efectiv faza semaforului (via TraCI) bazat pe senzori, manager și urgențe.
- `environment/`
  - Conține rețeaua SUMO (`.net.xml`), configurația (`sim.sumocfg`) și rutele (`routes.rou.xml`). Aici sunt definite vehiculele normale și pietonii.
- `my_prosody.cfg.lua` - Configurație custom pentru serverul XMPP local Prosody, necesară rulării agenților.

## Dependențe

1. **Python 3.10+**
2. **Eclipse SUMO:** Trebuie să fie instalat pe sistem (pachetul `sumo` / `sumo-gui` și `sumo-tools`).
3. **Prosody XMPP Server:** Trebuie să fie instalat pe sistem (`sudo apt install prosody`).
4. **Pachete Python:** (se pot instala via `pip install -r requirements.txt` sau direct):
   - `spade`
   - `traci`

## Instrucțiuni de rulare

1. **Pornirea serverului XMPP (Prosody):**
   Proiectul utilizează un server XMPP local pentru comunicare. Puteți rula Prosody cu configurația personalizată din proiect:
   ```bash
   # Opriți orice instanță existentă pe portul 5224 (dacă este cazul)
   fuser -k 5224/tcp || true
   # Porniți Prosody cu fișierul de configurare generat local
   prosody --config ./my_prosody.cfg.lua &
   ```

2. **Rularea simulării MAS:**
   Odată ce serverul XMPP rulează, porniți scriptul principal. Acesta va deschide interfața SUMO (dacă `sumo-gui` este activat) sau va rula in modul headless.
   ```bash
   python3 main.py
   ```

3. **Observații:**
   În timpul rulării, veți observa în consolă mesaje logate de Manager referitoare la strategia curentă (`NORMAL` / `RUSH_HOUR`), precum și mesaje 🚨 de urgență atunci când ambulanțele cer prioritate intersecțiilor (semafoarelor).