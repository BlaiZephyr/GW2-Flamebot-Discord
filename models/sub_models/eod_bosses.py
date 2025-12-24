from models.boss_class import Boss, Stats
from models.log_class import Log
from func import *

################################ MAI TRIN ################################

class AH(Boss):
    
    last    = None
    name    = "MAI TRIN"
    boss_id = 24033
    wing    = "EOD"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        AH.last  = self

    def get_mvp(self):
        # Create MVP prompt
        mvplist = "**LVPs** \n"

        # Check for mechanics
        msg_exposed = self.mvp_ah_exposed()
        msg_bad_dps = self.get_bad_dps()
        msg_green_skip = self.mvp_ah_green()
        msg_bad_boons = self.get_bad_boons('Full Fight')
        msg_general = self.get_mvp_general()

        # Add prompts to flame if mechanics are garbage
        if msg_exposed:
            mvplist = mvplist + msg_exposed + "\n" 

        if msg_bad_dps:
            mvplist = mvplist + msg_bad_dps + "\n" 

        if msg_green_skip:
            mvplist = mvplist + msg_green_skip + "\n" 

        if msg_bad_boons:
            mvplist = mvplist + msg_bad_boons

        if msg_general:
            mvplist = mvplist + msg_general 

        # Return full list
        return  mvplist
    
    def get_lvp(self):
        # Create LVP prompt
        lvplist = "**MVPs** \n"

        # Check for mechanics
        msg_good_dps = self.get_lvp_dps_PMA(14)
        msg_good_cc = self.get_lvp_cc_cleave_PMA()
        msg_good_bdps = self.get_lvp_bdps_PMA(14)

        # Add prompts to praise if mechanics are bussin fr fr
        if msg_good_dps:
            lvplist = lvplist + msg_good_dps + "\n" 

        if msg_good_bdps:
            lvplist = lvplist + msg_good_bdps + "\n" 

        if msg_good_cc:
            lvplist = lvplist + msg_good_cc + "\n" 

        # Return full list
        return lvplist
    
    ################################ MVP ################################
    
    # Flame the people who get exposed a lot
    def mvp_ah_exposed(self):
        i_players = self.get_ah_exposed()
        self.add_mvps(i_players)
        if i_players:
            mvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["AH MVP EXPOSED"].format(mvp_names=mvp_names)
        return
    
    # Flame the people who skipped going into greens
    def mvp_ah_green(self):
        i_players = self.get_ah_no_green()
        self.add_mvps(i_players)
        if i_players:
            mvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["AH MVP GREEN"].format(mvp_names=mvp_names)
        return
    
    ################################ LVP ################################
    

    ################################ CONDITIONS ################################

    # Check if player got exposed a lot
    def got_exposed(self, i_player: int):
        if self.get_mech_value(i_player, "Exposed Applied") > 1:
            return True
        else:
            return False
        
    # Check if player skipped green
    def got_no_green(self, i_player: int):
        if self.get_mech_value(i_player, "Green Debuff") < 1:
            return True
        else:
            return False


    ################################ DATA MECHAS ################################
    
    # Returns all players who got exposed a lot
    def get_ah_exposed(self):
        noobs = []
        for i in self.player_list:
            if self.got_exposed(i):
                noobs.append(i)
        return noobs   

    # Returns all players who didn't do green
    def get_ah_no_green(self):
        die_Grünen = []
        for i in self.player_list:
            if self.got_no_green(i):
                die_Grünen.append(i)
        return die_Grünen       
    
################################ ANKKA ################################

class XJ(Boss):
    
    last    = None
    name    = "ANKKA"
    boss_id = 23957
    wing    = "EOD"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        XJ.last  = self
        
    def get_mvp(self):
        msg_cc = self.get_mvp_cc_total()
        if msg_cc:
            return msg_cc
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
################################ KO ################################

class KO(Boss):
    
    last    = None
    name    = "KO"
    boss_id = 24485
    wing    = "EOD"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        KO.last  = self
        
    def get_mvp(self):
        msg_debil = self.mvp_debil()
        if msg_debil:
            return msg_debil
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
    ################################ LVP ################################
    
    def get_lvp_dps(self):
        i_players, max_dmg, tot_dmg = Stats.get_max_value(self, self.get_dmg_boss)
        lvp_dps_name                = self.players_to_string(i_players)
        dmg_ratio                   = max_dmg / tot_dmg * 100
        dps                         = max_dmg / self.duration_ms
        self.add_lvps(i_players)
        return LANGUES["selected_language"]["LVP DPS"].format(lvp_dps_name=lvp_dps_name, dmg_ratio=dmg_ratio, dps=dps)
    
    ################################ MVP ################################
    
    def mvp_debil(self):
        i_players, max_debil, _ = Stats.get_max_value(self, self.get_max_debil, exclude=[self.is_heal])
        mvp_names               = self.players_to_string(i_players)
        if max_debil > 1:
            self.add_lvps(i_players)
            if len(i_players) == 1:
                return LANGUES["selected_language"]["KO MVP DEBIL S"].format(mvp_names=mvp_names, max_debil=max_debil)
            else:
                return LANGUES["selected_language"]["KO MVP DEBIL P"].format(mvp_names=mvp_names, max_debil=max_debil)
        return
    
    ################################ DATA MECHAS ################################
    
    def get_max_debil(self, i_player: int):
        buffUptimes = self.log.pjcontent["players"][i_player]["buffUptimes"]
        debil_id    = 67972
        states      = None
        for buff in buffUptimes:
            if buff["id"] == debil_id:
                states = buff["states"]
        debil = 0
        if states:
            for state in states:
                if state[1] > debil:
                    debil = state[1]
        return debil
    
    def get_dmg_boss(self, i_player: int):
        return self.log.pjcontent["players"][i_player]["dpsAll"][0]["damage"]
    
################################ HT ################################

class HT(Boss):
    
    last    = None
    name    = "HT"
    boss_id = 24375
    wing    = "EOD"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        HT.last  = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
################################ OLC ################################

class OLC(Boss):
    
    last    = None
    name    = "OLC"
    boss_id = 25413
    wing    = "EOD"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        OLC.last = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
    ################################ LVP ################################
    
    def get_lvp_dps(self):
        i_players, max_dmg, tot_dmg = Stats.get_max_value(self, self.get_dmg_boss)
        lvp_dps_name                = self.players_to_string(i_players)
        dmg_ratio                   = max_dmg / tot_dmg * 100
        dps                         = max_dmg / self.duration_ms
        self.add_lvps(i_players)
        return LANGUES["selected_language"]["LVP DPS"].format(lvp_dps_name=lvp_dps_name, dmg_ratio=dmg_ratio, dps=dps)
    
    ################################ DATA MECHAS ################################
    
    def get_dmg_boss(self, i_player: int):
        return self.log.pjcontent["players"][i_player]["dpsAll"][0]["damage"]
