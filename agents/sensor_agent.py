import json
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
import traci

class SensorAgent(Agent):
    def __init__(self, jid, password, edge_id, tl_jid):
        super().__init__(jid, password, port=5224, verify_security=False)
        self.edge_id = edge_id
        self.tl_jid = tl_jid

    class SenseBehaviour(PeriodicBehaviour):
        async def run(self):
            try:
                halted = traci.edge.getLastStepHaltingNumber(self.agent.edge_id)
                msg = Message(to=self.agent.tl_jid)
                msg.set_metadata("performative", "inform")
                msg.body = json.dumps({"type": "sensor_data", "halted": halted})
                await self.send(msg)
            except:
                pass

    async def setup(self):
        self.add_behaviour(self.SenseBehaviour(period=0.5))