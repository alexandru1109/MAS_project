import traci
import asyncio
import os

os.environ['LIBGL_ALWAYS_SOFTWARE'] = '1'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
os.environ['SUMO_HOME'] = '/usr/share/sumo' 

from agents.traffic_light_agent import TrafficLightAgent
from agents.sensor_agent import SensorAgent
from agents.city_manager_agent import CityManagerAgent
from agents.ambulance_agent import AmbulanceAgent

async def start_agent(agent):
    await agent.start(auto_register=True)
    return agent

async def main():
    print("Incarc mediul SUMO...")
    sumo_cmd = ["sumo-gui", "-c", "environment/sim.sumocfg", "--max-num-vehicles", "200"]
    traci.start(sumo_cmd)
    
    try:
        traci.route.add("emergency_route", ["left0A0", "A0B0", "B0C0", "C0right0"])
    except Exception as e:
        print(f"Eroare adaugare ruta urgenta: {e}")

    PWD = "mas_traffic_2026_ab!"
    SVR = "localhost"
    
    tl_jids = [f"amab_tl_a0@{SVR}", f"amab_tl_b0@{SVR}", f"amab_tl_c0@{SVR}"]
    
    tl_map = {
        "left0A0": tl_jids[0],
        "A0B0": tl_jids[1],
        "B0C0": tl_jids[2]
    }
    
    print("Initializez Sistemul Multi-Agent...")
    
    agents = []
    
    agents.append(await start_agent(TrafficLightAgent(tl_jids[0], PWD, "A0", tl_jids[1])))
    agents.append(await start_agent(TrafficLightAgent(tl_jids[1], PWD, "B0", tl_jids[2])))
    agents.append(await start_agent(TrafficLightAgent(tl_jids[2], PWD, "C0", None)))
    
    agents.append(await start_agent(SensorAgent(f"amab_sens_a0@{SVR}", PWD, "left0A0", tl_jids[0])))
    agents.append(await start_agent(SensorAgent(f"amab_sens_b0@{SVR}", PWD, "A0B0", tl_jids[1])))
    agents.append(await start_agent(SensorAgent(f"amab_sens_c0@{SVR}", PWD, "B0C0", tl_jids[2])))
    
    agents.append(await start_agent(CityManagerAgent(f"amab_manager@{SVR}", PWD, tl_jids)))

    print("Toate microserviciile de baza au pornit! Simulare activa.")
    
    amb_count = 0
    max_amb = 10
    step = 0
    
    try:
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            
            if step % 150 == 0 and amb_count < max_amb:
                amb_id = f"AMBULANTA_{amb_count+1}"
                try:
                    traci.vehicle.add(vehID=amb_id, routeID="emergency_route", typeID="DEFAULT_VEHTYPE")
                    traci.vehicle.setColor(amb_id, (0, 255, 255, 255)) 
                    traci.vehicle.setShapeClass(amb_id, "emergency")
                    traci.vehicle.setVehicleClass(amb_id, "emergency")
                    traci.vehicle.setParameter(amb_id, "has.bluelight.device", "true")
                    traci.vehicle.setSpeed(amb_id, 30.0)
                    
                    agents.append(await start_agent(AmbulanceAgent(f"amab_amb_{amb_count+1}@{SVR}", PWD, amb_id, tl_map)))
                    amb_count += 1
                except Exception as e:
                    print(f"Eroare injectare ambulanta {amb_id}: {e}")

            step += 1
            await asyncio.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        for a in agents: await a.stop()
        traci.close()

if __name__ == "__main__":
    asyncio.run(main())