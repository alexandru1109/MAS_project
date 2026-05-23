import json
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
import traci

class CityManagerAgent(Agent):
    def __init__(self, jid, password, tl_jids):
        super().__init__(jid, password, port=5224, verify_security=False)
        self.tl_jids = tl_jids

    class StrategyBehaviour(PeriodicBehaviour):
        async def run(self):
            try:
                total_halted = sum([traci.edge.getLastStepHaltingNumber(e) for e in ["left0A0", "A0B0", "B0C0"]])
                
                strategy = "normal"
                if total_halted > 15:
                    strategy = "rush_hour"

                print(f"[MANAGER] Trafic total bulevard: {total_halted}. Strategie: {strategy.upper()}")
                
                for jid in self.agent.tl_jids:
                    msg = Message(to=jid)
                    msg.set_metadata("performative", "propose")
                    msg.body = json.dumps({"type": "strategy", "mode": strategy})
                    await self.send(msg)
            except:
                pass

    async def setup(self):
        self.add_behaviour(self.StrategyBehaviour(period=5.0))