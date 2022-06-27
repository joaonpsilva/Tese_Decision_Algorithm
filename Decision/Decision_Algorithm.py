from Decision.Priority_Object import Priority_Object
from Decision.Decision import Decision
from Battery import Battery

class Decision_Algorithm:
    def __init__(self):
        self.receive_Priority = []
        self.give_Priority = []

    def correct_simul_error(self,context,decisions):
        """House might need more energy than predicted
        On real world this would be handled when it happened but in the
        simulation this needs to be taken care of here"""

        house_cons = [d.energy_amount for d in decisions if d.obj == "Consumption"]
        house_cons = sum(house_cons) if len(house_cons) > 0 else 0
        simulation_Error = context["Real_consumption"] - house_cons
        
        new_decisions = []
        if simulation_Error > 0:    #consumption was actually bigger than expected
            self.receive_Priority = [Priority_Object("Consumption", 4, simulation_Error)]
            self.give_Priority = [Priority_Object("Grid", 4, 999999)]
            new_decisions = self.make_Decisions()
        
        return new_decisions

    
    def analyse(self, context):
        """ this method will construct the priority lists
        and then mek the decisions based on the priorities"""

        self.receive_Priority = []
        self.give_Priority = []

        self.define_receive_Priority(context)
        self.define_give_Priority(context)

        decisions = self.make_Decisions()

        decisions += self.correct_simul_error(context,decisions)

        return decisions

    
    def receive_consumption(self,context):
        raise NotImplementedError
    def receive_EVS(self,context):
        raise NotImplementedError
    def receive_Stationary_Batteries(self,context):
        raise NotImplementedError
    def receive_Grid(self,context):
        raise NotImplementedError
    def give_Production(self,context):
        raise NotImplementedError
    def give_EVs(self,context):
        raise NotImplementedError
    def give_Stationary_Batteries(self,context):
        raise NotImplementedError
    def give_Grid(self,context):
        raise NotImplementedError

    
    def define_receive_Priority(self, context):
        
        #Define CHARGE priority off all elements
        self.receive_consumption(context)
        self.receive_EVS(context)
        self.receive_Stationary_Batteries(context)
        self.receive_Grid(context)
        
        self.receive_Priority.sort(key=lambda x: x.priority, reverse=True)
    

    def define_give_Priority(self, context):

        #Define Discharge priority off all elements
        self.give_Production(context)
        self.give_EVs(context)
        self.give_Stationary_Batteries(context)
        self.give_Grid(context)

        self.give_Priority.sort(key=lambda x: x.priority)
    

    def make_Decisions(self):
        """ make decisions based on the priority lists"""

        self.give_Priority = [obj for obj in self.give_Priority if obj.amount_kw > 0]
        self.receive_Priority = [obj for obj in self.receive_Priority if obj.amount_kw > 0]
        decisions = []

        for obj_receive in self.receive_Priority:
            
            #remove givers that were exausted in previous loop
            self.give_Priority = [obj for obj in self.give_Priority if obj.amount_kw > 0]

            for obj_give in self.give_Priority: #Find who will give energy


                #object cannot give energy to itself
                if obj_receive.object == obj_give.object:
                    continue
                
                #wont happen but make sure stationary batteries dont exange energy
                if isinstance(obj_receive.object, Battery) and isinstance(obj_give.object, Battery):
                    continue
                
                #Compare priorities
                if obj_give.priority <= obj_receive.priority:

                    obj_give_amount_kw_temp = obj_give.amount_kw
                    obj_give.amount_kw -= obj_receive.amount_kw

                    if obj_give.amount_kw >= 0: #can give more, receiver is satisfied
                        decisions.append(Decision(obj_receive.object, "charge", obj_receive.amount_kw))
                        decisions.append(Decision(obj_give.object, "discharge", obj_receive.amount_kw))
                        break
                    else:   #giver doesnt have enough, receiver is not satisfied
                        #CHECK IF CAN DO THIS
                        decisions.append(Decision(obj_receive.object, "charge", obj_give_amount_kw_temp))
                        decisions.append(Decision(obj_give.object, "discharge", obj_give_amount_kw_temp))
                        obj_receive.amount_kw -= obj_give_amount_kw_temp

        return decisions            

