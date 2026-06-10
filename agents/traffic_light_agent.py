import json
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
import traci

class TrafficLightAgent(Agent):
    def __init__(self, jid, password, tl_id, next_jid=None):
        super().__init__(jid, password, port=5224, verify_security=False)
        self.tl_id = tl_id
        self.next_jid = next_jid
        self.halted_cars = 0
        self.threshold = 6
        self.emergency = False
        self.emergency_start_time = 0
        self.last_force_time = 0

    class ReceiverBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1.0)
            if msg:
                data = json.loads(msg.body)
                perf = msg.get_metadata("performative")

                if perf == "inform" and data["type"] == "sensor_data":
                    self.agent.halted_cars = data["halted"]

                elif perf == "propose" and data["type"] == "strategy":
                    self.agent.threshold = 3 if data["mode"] == "rush_hour" else 6

                elif perf == "request" and data["type"] == "emergency":
                    if data.get("action", "start") == "start":
                        print(f"[{self.agent.tl_id}] 🚨 Am primit cerere de urgenta! Trecem pe VERDE fortat.")
                        self.agent.emergency = True
                        try:
                            self.agent.emergency_start_time = traci.simulation.getTime()
                            traci.trafficlight.setPhase(self.agent.tl_id, 2)
                        except: pass
                    elif data.get("action") == "stop":
                        print(f"[{self.agent.tl_id}] ✅ Urgenta a trecut. Revin la program normal.")
                        self.agent.emergency = False

    class ControlBehaviour(PeriodicBehaviour):
        async def run(self):
            try:
                now = traci.simulation.getTime()
            except:
                now = 0

            if self.agent.emergency:
                if now - self.agent.emergency_start_time > 60:
                    print(f"[{self.agent.tl_id}] ⚠️ TIMEOUT urgenta! Opresc verdele fortat dupa 60s.")
                    self.agent.emergency = False
                else:
                    try:
                        traci.trafficlight.setPhase(self.agent.tl_id, 2)
                    except: pass
                    return

            try:
                current = traci.trafficlight.getPhase(self.agent.tl_id)
                if self.agent.halted_cars > self.agent.threshold and current != 2:
                    if now - self.agent.last_force_time > 45: # 45 seconds cooldown
                        print(f"[{self.agent.tl_id}] 🚦 Coada ({self.agent.halted_cars}/{self.agent.threshold}). Deschid semaforul.")
                        traci.trafficlight.setPhase(self.agent.tl_id, 2)
                        self.agent.last_force_time = now
            except: pass

    async def setup(self):
        self.add_behaviour(self.ReceiverBehaviour())
        self.add_behaviour(self.ControlBehaviour(period=0.5))