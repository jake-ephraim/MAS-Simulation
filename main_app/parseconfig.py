import json

LINE_VOLTAGE = 33

MIN_VOLATAGE = 10

state_live_ = "live"

state_broken_ = "broken"

file_loc="./config.json"

with open(file_loc, 'r') as fp:
    _model = json.load(fp)


class MyParser:
    '''
    Parses the config file.
    '''
    _model = _model

    @staticmethod
    def its_B(name:str) -> int|None:
        if len(name) > 1 and name[0] == "B" and name[1:].isnumeric():
            return int(name[1:])
    
    @staticmethod
    def its_SOURCE(name:str) -> int|None:
        if len(name) > 6 and name[:6] == "SOURCE" and name[6:-1].isnumeric():
            return int(name[6:-1])
    
    @staticmethod
    def its_DG(name:str) -> int|None:
        if len(name) > 2 and name[:2] == "DG" and name[2:].isnumeric():
            return int(name[2:])
    
    @staticmethod
    def its_CB(name:str) -> int|None:
        if len(name) > 2 and name[:2] == "CB" and name[2:-1].isnumeric():
            return int(name[2:-1])
    
    @staticmethod
    def _expand_list(x:list) -> list:
        return [i for l in x for i in l]

    @staticmethod
    def _print_model(model):
        if not len(model):
            print("dead end!")
            return
        keys = list(model.keys())
        print(keys)
        for key in keys:
            MyParser._print_model(model[key])
    
    @classmethod
    def print_model(cls):
        '''
        Unrolls and display the model on the console.
        '''
        model = cls._model["SystemModel"]
        MyParser._print_model(model)

    @classmethod
    def _get_neighbors(cls, model:dict, id:str, prev_key:str) -> list:
        if not len(model):
            return
        keys = list(model.keys())
        if id not in keys:
            for key in keys:
                neigbors = cls._get_neighbors(model[key], id, key)
                if neigbors:
                    return neigbors
        else:
            if prev_key:
                return [prev_key] + list(model[id].keys())
            return list(model[id].keys())
        
    @classmethod
    def get_neighbors(cls, id:str) -> list:
        '''
        returns the surrounding neighbors of `id` in the `model`.
        '''
        model = cls._model["SystemModel"]
        return cls._get_neighbors(model, id, None)
    
    @classmethod
    def get_dg_designations(cls, dg):
        return cls._expand_list(cls._model["DGDesignations"][dg])

    @classmethod
    def get_after_dg_designations(cls, dg):
        ret = cls._model["DGDesignations"][dg]
        if len(ret) == 2:
            return ret[1]
        return []

    @classmethod
    def get_b4_dg_designations(cls, dg):
        return cls._model["DGDesignations"][dg][0]


    @classmethod
    def get_my_dg(cls, bus_name):
        if not cls.its_B(bus_name):
            return
        for dg, vals in cls._model["DGDesignations"].items():
            vals = cls._expand_list(vals)
            if bus_name in vals:
                return dg
    
    @classmethod
    def _get_source_bus(cls, model:dict, id:str, s_bus:str=-1) -> str: # zero for source and > 0 for bus number
        if not len(model):
            return
        keys = list(model.keys())
        if id not in keys:

            for key in keys:
                if _s_b:=cls.its_B(key):
                    s_bus = f"B{_s_b}"
                elif _s_b:=cls.its_DG(key):
                    s_bus = f"DG{_s_b}"
                elif _s_b:=cls.its_SOURCE(key):
                    s_bus = f"SOURCE{_s_b}V"
                neigbors = cls._get_source_bus(model[key], id, s_bus)
                if neigbors:
                    return neigbors
            return
        else:
            if s_bus:
                return s_bus #, list(model[id].keys())
    
    @classmethod
    def get_pri_sec_sources(cls, id:str) -> tuple:
        '''
        Get's the primary and secondary power supply bus number.
        '''
        if not cls.its_B(id):
            return
        pmodel, smodel = cls._model["SystemModel"], cls._model["DGModel"]
        p_bus, _pssb_dgs = cls._get_source_bus(pmodel, id), cls._get_source_bus(smodel, id)
        return p_bus, _pssb_dgs
    
    @classmethod
    def _get_all_cb_from_source(cls, model, id, arr=[]) -> list:
        if not len(model):
            return
        keys = list(model.keys())
        if id not in keys:
            for key in keys:
                neigbors = cls._get_all_cb_from_source(model[key], id, arr+[key])
                if neigbors:
                    return neigbors
        else:
            return arr+[id]

    @classmethod
    def get_all_agents_from_source(cls, bus, source=True) -> list:
        if source:
            model = cls._model["SystemModel"]
        else:
            model = cls._model["DGModel"]
        return cls._get_all_cb_from_source(model, bus)
    
    @classmethod
    def i_am_boundary_cb(cls, cb_name) -> None|tuple:
        boundary_cbs:dict = cls._model["BoundaryCBs"]
        if cb_name in boundary_cbs.keys():
            return tuple(*boundary_cbs.values())
    
    @classmethod
    def get_dg_first_cb(cls, dg):
        if cls.its_DG(dg):
            model = tuple(cls._model["DGModel"][dg].keys())[0]
            return model
            # n = cls.get_neighbors(model)
            # for _n in n:
            #     if cls.its_CB(_n):
            #         return _n

    @classmethod
    def _init_dict(cls, model:dict, li:dict):
        #def _get_neighbors(cls, model:dict, id:str, prev_key:str) -> list:
        if not len(model):
            return
        keys = list(model.keys())
        for key in keys:
            if key not in li:
                li[key] = cls.get_r_val(key)
            cls._init_dict(model[key], li)
    
    @classmethod
    def get_r_val(cls, agent):
        if cls.its_CB(agent):
            return state_live_
        elif cls.its_B(agent):
            return str(LINE_VOLTAGE)
        elif cls.its_SOURCE(agent):
            return str(LINE_VOLTAGE)
        elif cls.its_DG(agent):
            return str(0)

    @classmethod
    def init_agent_dict(cls) -> dict:
        dct = {}
        model = cls._model["SystemModel"]
        cls._init_dict(model, dct)
        return dct

if __name__ == "__main__":
    # MyParser.print_model()
    # print(MyParser.get_neighbors('CB1B'))
    # print(MyParser.get_dg_designations('DG1'))
    # print(MyParser.get_pri_sec_sources("B4"))
    # print(MyParser.get_all_agents_from_source("DG2", True))
    # print(MyParser.closest_bus2source(["B5", "B2", "B3", "B4"]))
    # print(MyParser.get_after_dg_designations("DG2"))
    # print(MyParser.i_am_boundary_cb("CB7A"))
    # print(MyParser.get_dg_first_cb("DG1"))
    print(MyParser.init_agent_dict())
