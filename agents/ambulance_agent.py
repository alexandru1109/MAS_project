import json
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
import traci

class AmbulanceAgent(Agent):
    def __init__(self, jid, password, veh_id, tl_map):
        super().__init__(jid, password, port=5224, verify_security=False)
        self.veh_id = veh_id
        self.tl_map = tl_map
        self.cleared_edges = set()
        self.requested_tls = set()

    class DriveBehaviour(PeriodicBehaviour):
        async def run(self):
            try:
                if self.agent.veh_id in traci.vehicle.getIDList():
                    current_edge = traci.vehicle.getRoadID(self.agent.veh_id)
                    
                    try:
                        amb_pos = traci.vehicle.getLanePosition(self.agent.veh_id)
                        amb_route = traci.vehicle.getRoute(self.agent.veh_id)
                        amb_route_idx = traci.vehicle.getRouteIndex(self.agent.veh_id)
                        
                        # Request green only for the immediate proximity
                        active_edges = [current_edge]
                        if amb_route_idx + 1 < len(amb_route):
                            active_edges.append(amb_route[amb_route_idx + 1])
                        
                        for edge in active_edges:
                            if edge in self.agent.tl_map and edge not in self.agent.requested_tls:
                                target_tl = self.agent.tl_map[edge]
                                print(f"[{self.agent.veh_id}] 🚑 Cer verde in avans pentru {edge} de la {target_tl.split('@')[0]}!")
                                msg = Message(to=target_tl)
                                msg.set_metadata("performative", "request")
                                msg.body = json.dumps({"type": "emergency", "action": "start"})
                                await self.send(msg)
                                self.agent.requested_tls.add(edge)

                        # Check for edges we have passed
                        for edge in list(self.agent.requested_tls):
                            if edge not in active_edges:
                                target_tl = self.agent.tl_map[edge]
                                print(f"[{self.agent.veh_id}] 🚑 Am trecut de {edge}, eliberez semaforul {target_tl.split('@')[0]}!")
                                msg = Message(to=target_tl)
                                msg.set_metadata("performative", "request")
                                msg.body = json.dumps({"type": "emergency", "action": "stop"})
                                await self.send(msg)
                                self.agent.requested_tls.remove(edge)
                                self.agent.cleared_edges.add(edge)
                        
                        # Force vehicles on the same edge to yield priority
                        vehicles_on_edge = traci.edge.getLastStepVehicleIDs(current_edge)
                        for v in vehicles_on_edge:
                            if v != self.agent.veh_id:
                                v_pos = traci.vehicle.getLanePosition(v)
                                if v_pos > amb_pos: 
                                    v_route = traci.vehicle.getRoute(v)
                                    v_idx = traci.vehicle.getRouteIndex(v)
                                    if v_idx + 1 < len(v_route):
                                        next_edge = v_route[v_idx + 1]
                                        
                                        is_uturn = False
                                        if current_edge == "left0A0" and next_edge == "A0left0": is_uturn = True
                                        elif current_edge == "A0B0" and next_edge == "B0A0": is_uturn = True
                                        elif current_edge == "B0C0" and next_edge == "C0B0": is_uturn = True
                                        
                                        if is_uturn:
                                            new_route = amb_route[amb_route_idx:]
                                            traci.vehicle.setRoute(v, new_route)
                                            print(f"[{self.agent.veh_id}] 🚓 Am anulat intoarcerea in sens pentru {v}. Eliberam banda!")
                                            
                                    # Lăsăm SUMO să gestioneze nativ schimbarea benzilor pentru vehiculele de urgență (rescue lane).
                                    # Am eliminat forțarea încetinirii (slowDown) deoarece bloca ambulanța în spatele lor.

                    except Exception as e:
                        print(f"[{self.agent.veh_id}] Inner Exception: {e}")
                else:
                    if self.agent.requested_tls:
                        print(f"[{self.agent.veh_id}] 🏁 Ambulanta a iesit din retea. Eliberez ultimele semafoare: {self.agent.requested_tls}")
                        for edge in list(self.agent.requested_tls):
                            target_tl = self.agent.tl_map[edge]
                            msg = Message(to=target_tl)
                            msg.set_metadata("performative", "request")
                            msg.body = json.dumps({"type": "emergency", "action": "stop"})
                            await self.send(msg)
                            self.agent.requested_tls.remove(edge)
                        self.kill()
                    
            except Exception as e:
                print(f"[{self.agent.veh_id}] Outer Exception: {e}")

    async def setup(self):
        self.add_behaviour(self.DriveBehaviour(period=0.5))