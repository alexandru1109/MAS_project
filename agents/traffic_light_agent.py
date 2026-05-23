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
                    print(f"[{self.agent.tl_id}] 🚨 Am primit cerere de urgenta! Trecem pe VERDE fortat.")
                    self.agent.emergency = True
                    try:
                        traci.trafficlight.setPhase(self.agent.tl_id, 0)
                    except: pass

    class ControlBehaviour(PeriodicBehaviour):
        async def run(self):
            if self.agent.emergency:
                if self.agent.halted_cars == 0:
                    self.agent.emergency = False
                else:
                    try:
                        traci.trafficlight.setPhase(self.agent.tl_id, 0)
                    except: pass
                return

            try:
                current = traci.trafficlight.getPhase(self.agent.tl_id)
                if self.agent.halted_cars > self.agent.threshold and current != 0:
                    print(f"[{self.agent.tl_id}] 🚦 Coada ({self.agent.halted_cars}/{self.agent.threshold}). Deschid semaforul.")
                    traci.trafficlight.setPhase(self.agent.tl_id, 0)
            except: pass

    async def setup(self):
        self.add_behaviour(self.ReceiverBehaviour())
        self.add_behaviour(self.ControlBehaviour(period=0.5))