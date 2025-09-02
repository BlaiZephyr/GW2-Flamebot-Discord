from models.boss_class import Boss, Stats
from models.log_class import Log
from func import *
import numpy as np

################################ VG ################################

class VG(Boss):
    
    last    = None
    name    = "VG"
    wing    = 1
    boss_id = 15438
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        VG.last  = self
        
    def get_mvp(self):
        # Create MVP prompt
        mvplist = "**MVPs** \n"
        
        # Check for mechanics
        msg_bleu= self.mvp_bleu()
        msg_bad_boons = self.get_bad_boons('Full Fight')
        msg_general = self.get_mvp_general()
        
        # Add prompts to flame if mechanics are garbage
        if msg_bleu:
            mvplist = mvplist + msg_bleu + "\n" 
            
        if msg_bad_boons:
            mvplist = mvplist + msg_bad_boons

        if msg_general:
            mvplist = mvplist + msg_general 
            
        # Return full prompt
        return mvplist

    
    def get_lvp(self):
        # Create LVP prompt
        lvplist = "\n**LVPs** \n"
        
        # Check for mechanics
        msg_good_dps = self.get_lvp_dps_PMA()
        msg_red = self.lvp_vg_red()
        msg_good_bdps = self.get_lvp_bdps_PMA()
        msg_general = self.get_lvp_general('Full Fight')
        
        # Add prompts to praise if mechanics are bussin fr fr
        if msg_good_dps:
            lvplist = lvplist + msg_good_dps + "\n" 

        if msg_good_bdps:
            lvplist = lvplist + msg_good_bdps + "\n" 
            
        if msg_red:
            lvplist = lvplist + msg_red + "\n" 

        if msg_general:
            lvplist = lvplist + msg_general
            
        # Return full prompt
        return lvplist

    def get_dps_ranking(self):
        return self._get_dps_contrib([self.is_support, self.is_condi])
        
    ################################ MVP ################################   
    
    # Old code, flames if people got ported by blue. Yes, I am aware he called it "BLEU". No, I am not changing it.
    def mvp_bleu(self):
        i_players, max_bleu, _ = Stats.get_max_value(self, self.get_bleu)
        mvp_names              = self.players_to_string(i_players)
        if max_bleu < 3:
            return self.get_bad_dps(extra_exclude=[self.is_condi])
        if max_bleu > 1:
            self.add_mvps(i_players)
            nb_players = len(i_players)
            if nb_players == 1:
                return LANGUES["selected_language"]["VG MVP BLEU S"].format(mvp_names=mvp_names, max_bleu=max_bleu)
            if nb_players > 1:
                return LANGUES["selected_language"]["VG MVP BLEU P"].format(mvp_names=mvp_names, nb_players=nb_players, max_bleu=max_bleu)
        return
    
    ################################ LVP ################################
    
    # Praises people who go to red guardian
    def lvp_vg_red(self):
        i_players = self.get_vg_red()
        self.add_lvps(i_players)
        if i_players:
            lvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["LVP VG RED"].format(lvp_names=lvp_names)
        return

    ################################ CONDITIONS ###############################
    
    # Checks if player attuned to red twice
    def got_vg_red(self, i_player: int):
        return self.get_mech_value(i_player, "Red Attuned") > 1
    
    ################################ DATA MECHAS ################################
    
    # Old code, checks if person got tp'ed by blue
    def get_bleu(self, i_player: int):
        bleu_split = self.get_mech_value(i_player, "Green Guard TP")
        bleu_boss  = self.get_mech_value(i_player, "Boss TP")
        return bleu_boss + bleu_split
        
    # Collects all players who went to red
    def get_vg_red(self):
        condigamer = []
        for i in self.player_list:
            if self.got_vg_red(i):
                condigamer.append(i)
        return condigamer

################################ GORS ################################

class GORS(Boss):
    
    last    = None
    name    = "GORSEVAL"
    wing    = 1
    boss_id = 15429
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp  = self.get_mvp()
        self.lvp  = self.get_lvp()
        GORS.last = self
        
    def get_mvp(self):
        # Create MVP prompt
        mvplist = "**MVPs** \n"
        
        # Check for mechanics
        msg_egg = self.mvp_egg()
        msg_dmg_split = self.mvp_dmg_split()
        msg_bad_dps = self.get_bad_dps()
        msg_slam = self.mvp_gorse_slam()
        msg_bad_boons = self.get_bad_boons('Full Fight')
        msg_general = self.get_mvp_general()
        
        # Add prompts to flame if mechanics are garbage
        if msg_egg:
            mvplist = mvplist + msg_egg + "\n" 
            
        if msg_dmg_split:
            mvplist = mvplist + msg_dmg_split + "\n" 
            
        if msg_bad_dps:
            mvplist = mvplist + msg_bad_dps + "\n" 
            
        if msg_slam:
            mvplist = mvplist + msg_slam + "\n" 
            
        if msg_bad_boons:
            mvplist = mvplist + msg_bad_boons

        if msg_general:
            mvplist = mvplist + msg_general 
            
        # Return full prompt
        return mvplist
    
    def get_lvp(self):
        # Create LVP prompt
        lvplist = "\n**LVPs** \n"
        
        # Check for mechanics
        msg_good_dps = self.get_lvp_dps_PMA(9)
        msg_good_bdps = self.get_lvp_bdps_PMA()
        msg_general = self.get_lvp_general('Full Fight')
        
        # Add prompts to praise if mechanics are bussin fr fr
        if msg_good_dps:
            lvplist = lvplist + msg_good_dps + "\n" 

        if msg_good_bdps:
            lvplist = lvplist + msg_good_bdps + "\n" 

        if msg_general:
            lvplist = lvplist + msg_general
            
        # Return full prompt
        return lvplist
        
    ################################ MVP ################################
    
    # Old code, flames people for low split phase dps
    def mvp_dmg_split(self):
        i_players, min_dmg, total_dmg = Stats.get_min_value(self, self.get_dmg_split, exclude=[self.is_support])
        dps_total_dmg                 = Stats.get_tot_value(self, self.get_dmg_split, exclude=[self.is_support])
        if min_dmg/dps_total_dmg < 1/6*0.75:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            dmg_ratio = min_dmg / total_dmg * 100
            return LANGUES["selected_language"]["GORS MVP SPLIT"].format(mvp_names=mvp_names, min_dmg=min_dmg, dmg_ratio=dmg_ratio)
    
    # Old code, flames egged people
    def mvp_egg(self):
        i_players = self.get_egged()
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            if len(i_players) == 1:
                return LANGUES["selected_language"]["GORS MVP EGG S"].format(mvp_names=mvp_names)
            if len(i_players) > 1:
                return LANGUES["selected_language"]["GORS MVP EGG P"].format(mvp_names=mvp_names)
        return 
        
    # Flame the supports for not block/stabing gorse  slam
    def mvp_gorse_slam(self):
        # Find victims
        victims = self.get_gorse_slam()
        # Get supports out of victimlist
        i_players = []
        for i in victims:
            if not self.is_support(i):
                i_players.append(i)
        # Return if no one got hatecrimed
        if not i_players:
            return
        # Return if less than 3 people get stunned (they were probably AFK in narnia)
        if len(i_players) < 3:
            return
        # Check victim subgroups
        victim_in_sub1 = False
        victim_in_sub2 = False
        
        Group_No = self.log.pjcontent['players'][2]['group']
        
        for i in i_players:
            if self.log.pjcontent['players'][i]['group'] == Group_No:
                victim_in_sub1 = True
            else:
                victim_in_sub2 = True 
        # Find supports
        supports_sub1 = []
        supports_sub2 = []
        supports_all = []
        for i in self.player_list:
            if self.is_support(i):
                supports_all.append(i)
                if self.log.pjcontent['players'][i]['group'] == Group_No:
                    supports_sub1.append(i)
                else:
                    supports_sub2.append(i)
        # Blame the correct supports based on subgroup
        param = victim_in_sub1 + 2*victim_in_sub2
        match param:
            case 1:
                supports = supports_sub1
            case 2:
                supports = supports_sub2
            case 3:
                supports = supports_all
        # Return necessary flame
        if i_players:
            self.add_mvps(supports)
            mvp_names = self.players_to_string(supports)
            self.add_lvps(i_players)
            cucks = self.players_to_string(i_players)
            return LANGUES["selected_language"]["MVP GORS SLAM"].format(mvp_names=mvp_names, cucked_players=cucks)
        return
    
    ################################ LVP ################################
    
    # Old code, praises good split dps
    def lvp_dmg_split(self):
        i_players, max_dmg, total_dmg = Stats.get_max_value(self, self.get_dmg_split)
        lvp_names                     = self.players_to_string(i_players)
        dmg_ratio                     = max_dmg / total_dmg * 100
        self.add_lvps(i_players)
        return LANGUES["selected_language"]["GORS LVP SPLIT"].format(lvp_names=lvp_names, max_dmg=max_dmg, dmg_ratio=dmg_ratio)

    ################################ CONDITIONS ###############################
    
    # Old code, returns if egged
    def got_egged(self, i_player: int):
        return self.get_mech_value(i_player, "Egged") > 0
        
    # Checks if player got slammed without stab
    def got_gorse_slam(self, i_player: int):
        return self.get_mech_value(i_player, "Slam") > 0
    
    ################################ DATA MECHAS ################################
     
    # Old code, returns damage in split phases
    def get_dmg_split(self, i_player: int):
        dmg_split   = 0
        for i in range(len(self.log.jcontent['phases'])):
            if self.log.jcontent['phases'][i]['name'] == 'Split 1':
                dmg_split_1 = self.log.jcontent['phases'][i]['dpsStatsTargets'][i_player]
            if self.log.jcontent['phases'][i]['name'] == 'Split 2':
                dmg_split_2 = self.log.jcontent['phases'][i]['dpsStatsTargets'][i_player]
        for add_split1, add_split2 in zip(dmg_split_1,dmg_split_2):
            dmg_split += add_split1[0] + add_split2[0]
        return dmg_split
    
    # Old code, collects all players that got egged
    def get_egged(self):
        egged = []
        for i in self.player_list:
            if self.got_egged(i):
                egged.append(i)
        return egged
        
    # Collects all players who got slammed
    def get_gorse_slam(self):
        slamjam = []
        for i in self.player_list:
            if self.got_gorse_slam(i):
                slamjam.append(i)
        return slamjam
    
################################ SABETHA ################################

class SABETHA(Boss):
    
    last    = None
    name    = "SABETHA"
    wing    = 1
    boss_id = 15375
    
    pos_sab             = [376.7,364.4]
    pos_canon1          = [346.9,706.7]
    pos_canon2          = [35.9,336.8]
    pos_canon3          = [403.3,36.0]
    pos_canon4          = [713.9,403.1] 
    canon_detect_radius = 45
    scaler              = 9.34179 
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp     = self.get_mvp()
        self.lvp     = self.get_lvp()
        SABETHA.last = self               
        
    def get_mvp(self):
        # Create MVP prompt
        mvplist = "**MVPs** \n"
        
        # Check for mechanics
        msg_terrorists = self.mvp_terrorists()
        msg_dmg_split = self.mvp_dmg_split()
        msg_bad_dps = self.get_bad_dps(extra_exclude=[self.is_cannon])
        msg_flamewall = self.mvp_sab_flamewall()
        msg_bad_boons = self.get_bad_boons('Full Fight')
        msg_general = self.get_mvp_general()
        
        # Add prompts to flame if mechanics are garbage
        if msg_terrorists:
            mvplist = mvplist + msg_terrorists + "\n" 
            
        if msg_dmg_split:
            mvplist = mvplist + msg_dmg_split + "\n" 
            
        if msg_bad_dps:
            mvplist = mvplist + msg_bad_dps + "\n" 
            
        if msg_flamewall:
            mvplist = mvplist + msg_flamewall + "\n" 
            
        if msg_bad_boons:
            mvplist = mvplist + msg_bad_boons

        if msg_general:
            mvplist = mvplist + msg_general 
            
        # Return full prompt
        return mvplist
    
    def get_lvp(self):
        # Create LVP prompt
        lvplist = "\n**LVPs** \n"
        
        # Check for mechanics
        msg_good_dps = self.get_lvp_dps_PMA(4)
        msg_cannon = self.lvp_sab_cannon()
        msg_good_bdps = self.get_lvp_bdps_PMA()
        msg_general = self.get_lvp_general('Full Fight')
        
        # Add prompts to praise if mechanics are bussin fr fr
        if msg_good_dps:
            lvplist = lvplist + msg_good_dps + "\n" 
            
        if msg_cannon:
            lvplist = lvplist + msg_cannon + "\n" 

        if msg_good_bdps:
            lvplist = lvplist + msg_good_bdps + "\n" 

        if msg_general:
            lvplist = lvplist + msg_general + "\n" 
            
        # Return full prompt
        return lvplist
    
    def get_dps_ranking(self):
        return self._get_dps_contrib([self.is_support, self.is_cannon])

    ################################ MVP ################################
    
    # Old code, flames if low dps on split
    def mvp_dmg_split(self):
        i_players, min_dmg, total_dmg = Stats.get_min_value(self, self.get_dmg_split, exclude=[self.is_support,self.is_cannon])
        dps_total_dmg                 = Stats.get_tot_value(self, self.get_dmg_split, exclude=[self.is_support])
        if min_dmg/dps_total_dmg < 1/6*0.75:
            self.add_mvps(i_players) 
            dmg_ratio = min_dmg / total_dmg * 100
            mvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["SABETHA MVP SPLIT"].format(mvp_names=mvp_names, dmg_ratio=dmg_ratio)
        return
    
    # Old code, flames if bombed squad
    def mvp_terrorists(self):
        i_players = self.get_terrorists()
        self.add_mvps(i_players)
        if i_players:
            mvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["SABETHA MVP BOMB"].format(mvp_names=mvp_names)
        return
        
    # Flame players who got hit by flamewall (if they weren't downed I guess)
    def mvp_sab_flamewall(self):
        i_players = self.get_sab_flamewall()
        self.add_mvps(i_players)
        if i_players:
            mvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["MVP SABETHA FLAMEWALL"].format(mvp_names=mvp_names)
        return
    
    ################################ LVP ################################
    
    # Old code, praises good split dps
    def lvp_dmg_split(self):
        i_players, max_dmg, total_dmg = Stats.get_max_value(self, self.get_dmg_split)
        lvp_names                     = self.players_to_string(i_players)
        dmg_ratio                     = max_dmg / total_dmg * 100
        self.add_lvps(i_players)
        return LANGUES["selected_language"]["SABETHA LVP SPLIT"].format(lvp_names=lvp_names, dmg_ratio=dmg_ratio)
        
    # Praises if person did cannons
    def lvp_sab_cannon(self):
        i_players = self.get_sab_cannon()
        self.add_lvps(i_players)
        if i_players:
            lvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["LVP SABETHA CANNON"].format(lvp_names=lvp_names)
        return

    ################################ CONDITIONS ###############################
    
    # Old code, checks if person did cannon
    def is_cannon(self, i_player: int, n: int=0):
        pos_player = self.get_player_pos(i_player)
        match n:
            case 0: 
                canon_pos = [SABETHA.pos_canon1, SABETHA.pos_canon2, SABETHA.pos_canon3, SABETHA.pos_canon4]
            case 1:
                canon_pos = [SABETHA.pos_canon1]
            case 2:
                canon_pos = [SABETHA.pos_canon2]
            case 3:
                canon_pos = [SABETHA.pos_canon3]
            case 4:
                canon_pos = [SABETHA.pos_canon4]
            case _:
                canon_pos = []
        for pos in pos_player:
            for canon in canon_pos:
                if get_dist(pos, canon) <= SABETHA.canon_detect_radius:
                    return True
        return False
    
    # Old code, checks if person bombed squad
    def is_terrorist(self, i_player: int):
        bomb_history = self.get_player_mech_history(i_player, ["Timed Bomb"])
        if bomb_history:
            poses   = self.get_player_pos(i_player)
            players = self.player_list
            for bomb in bomb_history:
                bomb_time  = bomb['time'] + 3000
                time_index = time_to_index(bomb_time, self.time_base)
                try:
                    bomb_pos = poses[time_index]
                except:
                    continue
                bombed_players = 0
                for i in players:
                    if i == i_player or self.is_dead(i):
                        continue
                    i_pos = self.get_player_pos(i)[time_index]
                    if get_dist(bomb_pos, i_pos)*SABETHA.scaler <= 270:
                        bombed_players += 1
                if bombed_players > 1:
                    return True
        return False
    
    ################################ DATA MECHAS ################################
    
    # Old code, returns damage on adds
    def get_dmg_split(self,i_player: int):
        dmg_kernan   = self.log.jcontent['phases'][2]['dpsStatsTargets'][i_player][0][0]
        dmg_mornifle = self.log.jcontent['phases'][5]['dpsStatsTargets'][i_player][0][0]
        dmg_karde    = self.log.jcontent['phases'][7]['dpsStatsTargets'][i_player][0][0]
        return dmg_kernan + dmg_mornifle + dmg_karde 
    
    # Old code, collects all players who bombed the squad
    def get_terrorists(self):
        terrotists = []
        for i in self.player_list:
            if self.is_terrorist(i):
                terrotists.append(i)
        return terrotists 
        
    # Collects all cannon people
    def get_sab_cannon(self):
        cannoneers = []
        for i in self.player_list:
            if self.is_cannon(i):
                cannoneers.append(i)
        return cannoneers
        
    # Collects all flamewalled people
    def get_sab_flamewall(self):
        cannoneers = []
        for i in self.player_list:
            if self.is_dead_instant(i):
                cannoneers.append(i)
        return cannoneers

################################ SLOTH ################################

class SLOTH(Boss):
    
    last    = None
    name    = "SLOTH"
    wing    = 2
    boss_id = 16123
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp   = self.get_mvp()
        self.lvp   = self.get_lvp()
        SLOTH.last = self
        
    def get_mvp(self):
        # Create MVP prompt
        mvplist = "**MVPs** \n"
        
        # Check for mechanics
        msg_tantrum = self.mvp_tantrum()
        msg_cc = self.mvp_cc_sloth()
        msg_bad_dps = self.get_bad_dps(extra_exclude=[self.is_shroom])
        msg_bad_boons = self.get_bad_boons('Full Fight', exclude=[self.is_shroom])
        msg_general = self.get_mvp_general()
        
        # Add prompts to flame if mechanics are garbage
        if msg_tantrum:
            mvplist = mvplist + msg_tantrum + "\n" 
            
        if msg_cc:
            mvplist = mvplist + msg_cc + "\n" 
            
        if msg_bad_dps:
            mvplist = mvplist + msg_bad_dps + "\n" 
            
        if msg_bad_boons:
            mvplist = mvplist + msg_bad_boons

        if msg_general:
            mvplist = mvplist + msg_general 
            
        # Return full prompt
        return mvplist
  
        
    def get_lvp(self):
        # Create LVP prompt
        lvplist = "\n**LVPs** \n"
        
        # Check for mechanics
        msg_good_cc = self.get_lvp_cc_boss_PMA()
        msg_shroom = self.lvp_sloth_shroom()
        msg_Kev = self.lvp_sloth_Kev()
        msg_good_dps = self.get_lvp_dps_PMA()
        msg_good_bdps = self.get_lvp_bdps_PMA()
        msg_general = self.get_lvp_general('Full Fight', exclude=[self.is_shroom])
        
        # Add prompts to praise if mechanics are bussin fr fr
        if msg_good_cc:
            lvplist = lvplist + msg_good_cc + "\n" 

        if msg_good_dps:
            lvplist = lvplist + msg_good_dps + "\n" 

        if msg_good_bdps:
            lvplist = lvplist + msg_good_bdps + "\n" 
            
        if msg_shroom:
            lvplist = lvplist + msg_shroom + "\n" 
            
        if msg_Kev:
            lvplist = lvplist + msg_Kev + "\n" 

        if msg_general:
            lvplist = lvplist + msg_general
            
        # Return full prompt
        return lvplist
        
    def get_dps_ranking(self):
        return self._get_dps_contrib([self.is_support, self.is_shroom])

    ################################ MVP ################################
    
    # Old code, flames bad cc at sloth
    def mvp_cc_sloth(self):
        i_players, min_cc, total_cc = Stats.get_min_value(self, self.get_cc_boss, exclude=[self.is_shroom])  
        if min_cc < 800:
            self.add_mvps(i_players)
            cc_ratio  = min_cc / total_cc * 100
            mvp_names = self.players_to_string(i_players)
            if min_cc == 0:
                if len(i_players) > 1:
                    return LANGUES["selected_language"]["SLOTH MVP 0 CC P"].format(mvp_names=mvp_names)
                return LANGUES["selected_language"]["SLOTH MVP 0 CC S"].format(mvp_names=mvp_names)
            if len(i_players) > 1:
                return LANGUES["selected_language"]["SLOTH MVP CC P"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
            return LANGUES["selected_language"]["SLOTH MVP CC S"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
    
    # Old code, flames if you afk in tantrum
    def mvp_tantrum(self):
        i_players, max_tantrum, _ = Stats.get_max_value(self, self.get_tantrum)
        if max_tantrum > 1:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            if len(i_players) > 1:
                return LANGUES["selected_language"]["SLOTH MVP TANTRUM P"].format(mvp_names=mvp_names, max_tantrum=max_tantrum)
            return LANGUES["selected_language"]["SLOTH MVP TANTRUM S"].format(mvp_names=mvp_names, max_tantrum=max_tantrum)
    
    ################################ LVP ################################
    
    # Praises people who ate the shrooms
    def lvp_sloth_shroom(self):
        i_players = self.get_sloth_shroom()
        lvp_names = self.players_to_string(i_players)
        self.add_lvps(i_players)
        if i_players:
            return LANGUES["selected_language"]["LVP SLOTH SHROOM"].format(lvp_names=lvp_names) 
        return 
        
    # Praises Kev sacrifice
    def lvp_sloth_Kev(self):
        # Case for if Kev ate shroom and died
        if self.is_Kev_shroom_dead():
            for i in self.player_list:
                kev = []
                if self.log.pjcontent['players'][i]['account'] == 'Scapegoat.4783':
                    kev.append(i)
                    lvp_names = self.players_to_string(kev)
                    self.add_lvps(kev)
            return LANGUES["selected_language"]["LVP SLOTH KEV"].format(lvp_names=lvp_names) 
            
        # Case for if Kev ate shroom and survived
        if self.is_Kev_shroom_alive():
            for i in self.player_list:
                kev = []
                if self.log.pjcontent['players'][i]['account'] == 'Scapegoat.4783':
                    kev.append(i)
                    lvp_names = self.players_to_string(kev)
                    self.add_lvps(kev)
            return LANGUES["selected_language"]["LVP SLOTH KEV ALIVE"].format(lvp_names=lvp_names) 
            
        return 

    ################################ CONDITIONS ###############################
    
    # Old code, Checks if player is shroom
    def is_shroom(self, i_player: int):
        rota = self.get_player_rotation(i_player)
        for skill in rota:
            if skill['id'] == 34408:
                return True
        return False
        
    # Checks for if turned to slubling
    def is_slub(self, i_player: int):
        return self.get_mech_value(i_player, "Slub Transform") > 0
        
    # Checks if Kev ate shroom and was killed    
    def is_Kev_shroom_dead(self):
        for i in self.player_list:
            if self.is_slub(i): 
                if self.log.pjcontent['players'][i]['account'] == 'Scapegoat.4783':
                    # Check if Kev was defeated in the fight
                    dead = 0
                    for j in range(len(self.log.pjcontent['players'][i]['defenses'])):
                        if self.log.pjcontent['players'][i]['defenses'][j]['deadCount'] > 0:
                            dead = dead + 1
                    if dead > 0:
                        return True
        return False
        
    # Checks if Kev ate shroom and survived
    def is_Kev_shroom_alive(self):
        for i in self.player_list:
            if self.is_slub(i): 
                if self.log.pjcontent['players'][i]['account'] == 'Scapegoat.4783':
                    # Check if Kev was defeated in the fight
                    dead = 0
                    for j in range(len(self.log.pjcontent['players'][i]['defenses'])):
                        if self.log.pjcontent['players'][i]['defenses'][j]['deadCount'] > 0:
                            dead = dead + 1
                    if dead < 1:
                        return True
        return False
    
    ################################ DATA MECHAS ################################
    
    # Old code, returns amount of tantrums hit
    def get_tantrum(self, i_player: int):
        return self.get_mech_value(i_player, "Tantrum")
        
    # Collects all players that ate shroom (except Kev)
    def get_sloth_shroom(self):
        shroomie = []
        for i in self.player_list:
            if self.is_shroom(i) and not self.log.pjcontent['players'][i]['account'] == 'Scapegoat.4783':
                shroomie.append(i)
        return shroomie
    
    

################################ MATTHIAS ################################

class MATTHIAS(Boss):
    
    last    = None
    name    = "MATTHIAS"
    wing    = 2
    boss_id = 16115
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp      = self.get_mvp()
        self.lvp      = self.get_lvp()
        MATTHIAS.last = self
        
    def get_mvp(self):
        # Create MVP prompt
        mvplist = "**MVPs** \n"
        
        # Check for mechanics
        msg_bad_cc = self.mvp_cc_matthias()
        msg_tornado = self.mvp_matthias_tornado() 
        msg_spirit = self.mvp_matthias_spirit()
        msg_bad_boons = self.get_bad_boons('Full Fight')
        msg_general = self.get_mvp_general()
        
        # Add prompts to flame if mechanics are garbage
        if msg_bad_cc:
            mvplist = mvplist + msg_bad_cc + "\n" 
            
        if msg_tornado:
            mvplist = mvplist + msg_tornado + "\n" 
            
        if msg_spirit:
            mvplist = mvplist + msg_spirit + "\n" 
            
        if msg_bad_boons:
            mvplist = mvplist + msg_bad_boons

        if msg_general:
            mvplist = mvplist + msg_general 
            
        # Return full prompt
        return mvplist
        
    def get_lvp(self):
        # Create LVP prompt
        lvplist = "\n**LVPs** \n"
        
        # Check for mechanics
        msg_good_cc = self.lvp_cc_matthias()
        msg_sacrifice = self.lvp_matthias_sacrifice()
        msg_good_dps = self.get_lvp_dps_PMA()
        msg_good_bdps = self.get_lvp_bdps_PMA()
        msg_general = self.get_lvp_general('Full Fight')
        
        # Add prompts to praise if mechanics are bussin fr fr
        if msg_good_cc:
            lvplist = lvplist + msg_good_cc + "\n" 
            
        if msg_sacrifice:
            lvplist = lvplist + msg_sacrifice + "\n" 

        if msg_good_dps:
            lvplist = lvplist + msg_good_dps + "\n" 

        if msg_good_bdps:
            lvplist = lvplist + msg_good_bdps + "\n" 

        if msg_general:
            lvplist = lvplist + msg_general + "\n" 
           
        # Return full prompt
        return lvplist
    
    # Old code
    def get_dps_ranking(self):
        return self._get_dps_contrib([self.is_support, self.is_sac])

    ################################ MVP ################################
    
    # Old code, flames bad cc
    def mvp_cc_matthias(self):
        i_players, min_cc, total_cc = Stats.get_min_value(self, self.get_cc_total, exclude=[self.is_sac])
        cc_ratio                    = min_cc / total_cc * 100
        mvp_names                   = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if min_cc == 0:
            return LANGUES["selected_language"]["MATTHIAS MVP 0 CC"].format(mvp_names=mvp_names)
        else:
            return LANGUES["selected_language"]["MATTHIAS MVP CC"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
            
    # Flames players who trigger too many red orbs
    def mvp_matthias_tornado(self):
        i_players = self.get_matthias_tornado()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if i_players:
            return LANGUES["selected_language"]["MVP MATTHIAS TORNADO"].format(mvp_names=mvp_names) 
        return 
        
    # Flames players who trigger too many red orbs
    def mvp_matthias_spirit(self):
        i_players = self.get_matthias_spirit()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if i_players:
            return LANGUES["selected_language"]["MVP MATTHIAS SPIRIT"].format(mvp_names=mvp_names) 
        return 
        
    ################################ LVP ################################
    
    # Old code, praises good cc
    def lvp_cc_matthias(self):
        i_players, max_cc, total_cc = Stats.get_max_value(self, self.get_cc_total)       
        cc_ratio                    = max_cc / total_cc * 100
        lvp_names                   = self.players_to_string(i_players)
        self.add_lvps(i_players)
        return LANGUES["selected_language"]["MATTHIAS LVP CC"].format(lvp_names=lvp_names, max_cc=max_cc, cc_ratio=cc_ratio)
        
    # Praises people as pity who got sacrificed several times
    def lvp_matthias_sacrifice(self):
        i_players = self.get_matthias_sacrifice()
        lvp_names = self.players_to_string(i_players)
        self.add_lvps(i_players)
        if i_players:
            return LANGUES["selected_language"]["LVP MATTHIAS SACRIFICE"].format(lvp_names=lvp_names) 
        return 
    
    ################################ CONDITIONS ###############################
    
    # Old code, checks if sacrificed
    def is_sac(self, i_player: int):
        return self.get_nb_sac(i_player) > 0
        
    # Old code, checks if got tornadoed
    def got_matthias_tornado(self, i_player: int):
        return self.get_mech_value(i_player, "Tornado") > 2
        
    # Old code, checks if got went into spirit
    def got_matthias_spirit(self, i_player: int):
        return self.get_mech_value(i_player, "Spirit hit") > 1
    
    ################################ DATA MECHAS ################################    
    
    # Old code, checks if sacrificed
    def get_nb_sac(self, i_player: int):
        return self.get_mech_value(i_player, "Sacrifice")
    
    # Collects all players that got into tornado
    def get_matthias_tornado(self):
        tornado = []
        for i in self.player_list:
            if self.got_matthias_tornado(i):
                tornado.append(i)
        return tornado
        
    # Collects all players that got into Spirit
    def get_matthias_spirit(self):
        spirit = []
        for i in self.player_list:
            if self.got_matthias_spirit(i):
                spirit.append(i)
        return spirit
        
    # Collects all players that got sac'ed many times
    def get_matthias_sacrifice(self):
        sac = []
        for i in self.player_list:
            if self.get_nb_sac(i) > 1:
                sac.append(i)
        return sac

################################ ESCORT ################################

class ESCORT(Boss):
    
    last    = None
    name    = "ESCORT"
    wing    = 3
    boss_id = 16253
    
    towers  = [
               [387,129.1],
               [304.1,115.7],
               [187.1,118.8],
               [226.1,252.3],
               [80.3,255.5]
              ]
    tower_radius = 19
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp    = self.get_mvp()
        self.lvp    = self.get_lvp()
        ESCORT.last = self 
        
    def get_mvp(self):
        # Create MVP prompt
        mvplist = "**MVPs** \n"
        
        # Check for mechanics
        msg_mine = self.mvp_mine()
        
        # Add prompts to flame if mechanics are garbage
        if msg_mine:
            mvplist = mvplist + msg_mine + "\n" 
            
        # Return full prompt
        return mvplist
       
    def get_lvp(self):
        # Create LVP prompt
        lvplist = "\n**LVPs** \n"

        # Check for mechanics
        msg_tower = self.lvp_tower()
        
        # Add prompts to praise if mechanics are bussin fr fr
        if msg_tower:
            lvplist = lvplist + msg_tower + "\n" 

        # Return full prompt
        return lvplist

    
    ################################ MVP ################################
    
    def mvp_mine(self):
        i_players = self.get_mined_players()
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            if len(i_players) == 1:
                return LANGUES["selected_language"]["ESCORT MVP MINE S"].format(mvp_names=mvp_names)
            else:
                return LANGUES["selected_language"]["ESCORT MVP MINE P"].format(mvp_names=mvp_names)
        return
    
    ################################ LVP ################################
    
    def lvp_glenna(self):
        i_players, max_call, _ = Stats.get_max_value(self, self.get_glenna_call)
        lvp_names              = self.players_to_string(i_players)
        self.add_lvps(i_players)
        return LANGUES["selected_language"]["ESCORT LVP GLENNA"].format(lvp_names=lvp_names, max_call=max_call)
    
    def lvp_tower(self):
        towers    = self.get_towers()
        lvp_names = self.players_to_string(towers)
        for i in self.player_list:
            for n in range(1,6):
                if self.is_tower_n(i,n) and not self.is_tower(i):
                    return
        self.add_lvps(towers)
        if len(towers) == 1:
            return LANGUES["selected_language"]["ESCORT LVP TOWER S"].format(lvp_names=lvp_names)
        return LANGUES["selected_language"]["ESCORT LVP TOWER P"].format(lvp_names=lvp_names)
    
    ################################ CONDITIONS ################################
    
    def got_mined(self, i_player: int):
        return self.get_mech_value(i_player, "Mine Detonation Hit") > 0
    
    def is_tower_n(self, i_player: int, n: int):
        poses = self.get_player_pos(i_player)
        tower = ESCORT.towers[n-1]
        for pos in poses:
            if get_dist(pos, tower) < ESCORT.tower_radius:
                return True
        return False
    
    def is_tower(self, i_player: int):
        for n in range(1,6):
            if not self.is_tower_n(i_player, n):
                return False
        return True

    ################################ DATA MECHAS ################################
    
    def get_mined_players(self):
        p = []
        for i in self.player_list:
            if self.got_mined(i):
                p.append(i)
        return p
            
    def get_glenna_call(self, i_player: int):
        return self.get_mech_value(i_player, "Over Here! Cast")
    
    def get_towers(self):
        towers = []
        for i in self.player_list:
            if self.is_tower(i):
                towers.append(i)
        return towers

################################ KC ################################

class KC(Boss):
    
    last    = None
    name    = "KC"
    wing    = 3
    boss_id = 16235
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        KC.last  = self  
        
    def get_mvp(self):
        # Create MVP prompt
        mvplist = "**MVPs** \n"
        
        # Check for mechanics
        msg_orb = self.mvp_orb_kc()
        msg_bad_dps = self.get_bad_dps() 
        msg_pizza = self.mvp_kc_pizza()
        msg_bad_boons = self.get_bad_boons('Full Fight')
        msg_general = self.get_mvp_general()
        
        # Add prompts to flame if mechanics are garbage
        if msg_orb:
            mvplist = mvplist + msg_orb + "\n" 
            
        if msg_bad_dps:
            mvplist = mvplist + msg_bad_dps + "\n" 
            
        if msg_pizza:
            mvplist = mvplist + msg_pizza + "\n" 
            
        if msg_bad_boons:
            mvplist = mvplist + msg_bad_boons

        if msg_general:
            mvplist = mvplist + msg_general 
            
        # Return full prompt
        return mvplist

    
    def get_lvp(self):
        # Create LVP prompt
        lvplist = "\n**LVPs** \n"
        
        # Check for mechanics
        msg_good_orb = self.lvp_orb_kc()
        msg_good_dps = self.get_lvp_dps_PMA()
        msg_good_bdps = self.get_lvp_bdps_PMA()
        msg_general = self.get_lvp_general('Full Fight')
        
        # Add prompts to praise if mechanics are bussin fr fr
        if msg_good_orb:
            lvplist = lvplist + msg_good_orb + "\n" 

        if msg_good_dps:
            lvplist = lvplist + msg_good_dps + "\n" 

        if msg_good_bdps:
            lvplist = lvplist + msg_good_bdps + "\n" 

        if msg_general:
            lvplist = lvplist + msg_general + "\n" 
           
        # Return full prompt
        return lvplist
        
    ################################ MVP ################################
    
    # Old code, flames for collecting low amount of orbs
    def mvp_orb_kc(self):
        i_players, min_orb, _ = Stats.get_min_value(self, self.get_good_orb)
        mvp_names             = self.players_to_string(i_players)
        if min_orb < 6:
            self.add_mvps(i_players)
            if min_orb < 0:
                return LANGUES["selected_language"]["KC MVP BAD ORBS"].format(mvp_names=mvp_names, min_orb=-min_orb)
            if min_orb == 0:
                return LANGUES["selected_language"]["KC MVP 0 ORB"].format(mvp_names=mvp_names)
            else:
                return LANGUES["selected_language"]["KC MVP ORB"].format(mvp_names=mvp_names, min_orb=min_orb)
                
    # Flame people who take (1.2 * squad average) pizza hits
    def mvp_kc_pizza(self, extra_exclude: list[classmethod]=[]):
        total_pizza = 0
        i_players = []
        for i in self.player_list:
            total_pizza = total_pizza + self.got_kc_pizza(i)
        
        for i in self.player_list:
            if self.got_kc_pizza(i) > 1.2 * (total_pizza/len(self.player_list)):
                i_players.append(i)

        if i_players:
            self.add_mvps(i_players)  
            mvp_names  = self.players_to_string(i_players)
            return LANGUES["selected_language"]["MVP KC PIZZA"].format(mvp_names=mvp_names)
        return

            
    ################################ LVP ################################
    
    # Old code, praises for highest collected orb 
    def lvp_orb_kc(self):
        i_players, max_orb, _ = Stats.get_max_value(self, self.get_good_orb)
        lvp_names             = self.players_to_string(i_players)
        self.add_lvps(i_players)
        return LANGUES["selected_language"]["KC LVP ORB"].format(lvp_names=lvp_names, max_orb=max_orb)
    
    ################################ CONDITIONS ################################
    
    # Returns amount of pizza attack hits
    def got_kc_pizza(self, i_player: int):
        return self.get_mech_value(i_player, 'Phantasmal Blades')
    
    ################################ DATA MECHAS ################################
    
    # Old code, returns collected orbs
    def get_good_orb(self, i_player: int):
        good_red_orbs   = self.get_mech_value(i_player, 'Good Red Orb')
        good_white_orbs = self.get_mech_value(i_player, 'Good White Orb')
        bad_red_orbs    = self.get_mech_value(i_player, 'Bad Red Orb')
        bad_white_orbs  = self.get_mech_value(i_player, 'Bad White Orb')
        return good_red_orbs + good_white_orbs - bad_red_orbs - bad_white_orbs

################################ XERA ################################

class XERA(Boss):
    
    last       = None
    name       = "XERA"
    wing       = 3
    boss_id    = 16246
    real_phase = "Phase 1"
    
    debut         = [497.1,86.4]
    l1            = [663.0,314.9]
    l2            = [532.5,557.4]
    fin           = [268.3,586.4]
    r1            = [208.2,103.4]
    r2            = [87.0,346.8]
    centre        = [366.4,323.4]
    debut_radius  = 85
    centre_radius = 140

    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp  = self.get_mvp()
        self.lvp  = self.get_lvp()
        XERA.last = self 
        
        
    def get_mvp(self):
        # Create MVP prompt
        mvplist = "**MVPs** \n"
        
        # Check for mechanics
        msg_fdp = self.mvp_fdp_xera()
        msg_glide = self.mvp_glide()
        msg_bad_cc = self.get_mvp_cc_boss()
        msg_red_orb = self.mvp_xera_red_orb()
        msg_bad_boons = self.get_bad_boons('Main Fight')
        msg_ribbon = self.mvp_xera_ribbon()
        msg_general = self.get_mvp_general()
        
        # Add prompts to flame if mechanics are garbage
        if msg_fdp:
            mvplist = mvplist + msg_fdp + "\n" 
            
        if msg_glide:
            mvplist = mvplist + msg_glide + "\n" 
            
        if msg_bad_cc:
            mvplist = mvplist + msg_bad_cc + "\n" 
            
        if msg_red_orb:
            mvplist = mvplist + msg_red_orb + "\n" 
            
        if msg_ribbon:
            mvplist = mvplist + msg_ribbon + "\n" 
            
        if msg_bad_boons:
            mvplist = mvplist + msg_bad_boons

        if msg_general:
            mvplist = mvplist + msg_general 
            
        # Return full prompt
        return mvplist

    
    def get_lvp(self):
        # Create LVP prompt
        lvplist = "\n**LVPs** \n"
        
        # Check for mechanics
        msg_minijeu = self.lvp_minijeu()
        msg_good_cc = self.get_lvp_cc_boss_PMA()
        msg_button = self.lvp_xera_buttons()
        msg_general = self.get_lvp_general('Main Fight')
        
        # Add prompts to praise if mechanics are bussin fr fr
        if msg_minijeu:
            lvplist = lvplist + msg_minijeu + "\n" 
            
        if msg_good_cc:
            lvplist = lvplist + msg_good_cc + "\n" 
            
        if msg_button:
            lvplist = lvplist + msg_button + "\n" 

        if msg_general:
            lvplist = lvplist + msg_general + "\n" 

        # Return full prompt
        return lvplist

    
    # Old code, idk (?)
    def get_dps_ranking(self):
        return self._get_dps_contrib([self.is_support])

    ################################ MVP ################################
    
    # Old code, flames people who skip minigame by taking the portal
    def mvp_fdp_xera(self):
        i_fdp     = self.get_fdp()
        fdp_names = self.players_to_string(i_fdp)
        self.add_mvps(i_fdp)
        if len(i_fdp) == 1:
            return LANGUES["selected_language"]["XERA MVP SKIP S"].format(fdp_names=fdp_names)
        if len(i_fdp) > 1:
            return LANGUES["selected_language"]["XERA MVP SKIP P"].format(fdp_names=fdp_names)
        return
    
    # Old code, flames people who fail to glide
    def mvp_glide(self):
        i_glide     = self.get_gliding_death()
        glide_names = self.players_to_string(i_glide)
        self.add_mvps(i_glide)
        if len(i_glide) == 1:
            return LANGUES["selected_language"]["XERA MVP GLIDE S"].format(glide_names=glide_names)
        if len(i_glide) > 1:
            return LANGUES["selected_language"]["XERA MVP GLIDE P"].format(glide_names=glide_names)
        return
        
    # Flames players who trigger too many red orbs
    def mvp_xera_red_orb(self):
        i_players = self.get_xera_red_orb()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if i_players:
            return LANGUES["selected_language"]["MVP XERA RED ORB"].format(mvp_names=mvp_names) 
        return 
        
    # Flames players who are too impatient in split phase
    def mvp_xera_ribbon(self):
        i_players = self.get_xera_ribbon()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if i_players:
            return LANGUES["selected_language"]["MVP XERA RIBBON"].format(mvp_names=mvp_names) 
        return 
    
    ################################ LVP ################################
    
    # Old code, praises people who got ported twice
    def lvp_minijeu(self):
        i_players, max_minijeu, _ = Stats.get_max_value(self, self.get_tp_back, exclude=[self.is_fdp])  
        lvp_names                 = self.players_to_string(i_players)
        self.add_lvps(i_players)
        if max_minijeu == 2:
            return LANGUES["selected_language"]["XERA LVP MINI-JEU"].format(lvp_names=lvp_names)
        return
        
    # Praises the people who do buttons a lot
    def lvp_xera_buttons(self):
        i_players = self.get_xera_buttons()
        lvp_names = self.players_to_string(i_players)
        self.add_lvps(i_players)
        if i_players:
            return LANGUES["selected_language"]["LVP XERA BUTTONS"].format(lvp_names=lvp_names) 
        return 
    
    ################################ CONDITIONS ################################
    
    # Old code, checks if person skipped minigame
    def is_fdp(self, i_player: int):
        return i_player in self.get_fdp()
        
    # Returns if player triggered red orb multiple times
    def got_xera_red_orb(self, i_player: int):
        return self.get_mech_value(i_player, 'Red Orb') > 1
        
    # Returns if player did buttons in main phase
    def got_xera_buttons(self, i_player: int):
        buttons = self.get_mech_value(i_player, 'Button 1', "Phase 2")
        buttons = buttons + self.get_mech_value(i_player, 'Button 2', "Phase 2")
        buttons = buttons + self.get_mech_value(i_player, 'Button 3', "Phase 2")
        return buttons > 3
        
    # Returns if player got hit by ribbon several times
    def got_xera_ribbon(self, i_player: int):
        for j in range(len(self.log.pjcontent['players'][i_player]['totalDamageTaken'])):
            for k in range(len(self.log.pjcontent['players'][i_player]['totalDamageTaken'][j])):
                if self.log.pjcontent['players'][i_player]['totalDamageTaken'][j][k]['id'] == 34883:
                    if self.log.pjcontent['players'][i_player]['totalDamageTaken'][j][k]['totalDamage'] > 17000:
                        return True
        return False
    
    ################################ DATA MECHAS ################################
    
    # Old code, checks for TP to minigame
    def get_tp_out(self, i_player: int):
        return self.get_mech_value(i_player, 'TP')
    
    # Old code, checks for TP back from minigame at the end
    def get_tp_back(self, i_player: int):
        return self.get_mech_value(i_player, 'TP back')
    
    # Old code, Collects players who skipped minigame
    def get_fdp(self): # fdp = skip mini jeu XERA
        mecha_data = self.log.pjcontent['mechanics']
        tp_data    = None
        for e in mecha_data:
            if e['name'] == "TP Out":
                tp_data = e['mechanicsData']
                break
        fdp     = []
        delta   = 6000
        i_delta = time_to_index(delta, self.time_base)
        for e in tp_data:
            tp_time     = e['time']
            
            player_name = e['actor']
            i_player    = self.get_player_id(player_name)
            tp_time    += 2000  # 1s de delais pour etre sur
            i_time      = time_to_index(tp_time, self.time_base)
            pos_player  = self.get_player_pos(i_player, i_time, i_time + i_delta)
            for p in pos_player:
                if get_dist(p, XERA.centre) <= XERA.centre_radius:
                    fdp.append(i_player)
                    break
        return fdp
    
    # Old code, collects players who died during gliding
    def get_gliding_death(self):
        dead = []
        glide_phase = self.get_phase_id("Gliding")
        if glide_phase != 0:
            for i in self.player_list:
                if self.log.pjcontent['players'][i]['defenses'][glide_phase]['deadCount'] > 0:
                    dead.append(i)
        return dead   

    # Collect all players who trigger red orb a lot
    def get_xera_red_orb(self):
        afk = []
        for i in self.player_list:
            if self.got_xera_red_orb(i):
                afk.append(i)
        return afk
        
    # Collect all players who do buttons
    def get_xera_buttons(self):
        gamers = []
        for i in self.player_list:
            if self.got_xera_buttons(i):
                gamers.append(i)
        return gamers
        
    # Collect all players who got hit by ribbons in split phase several times
    def get_xera_ribbon(self):
        impatient = []
        for i in self.player_list:
            if self.got_xera_ribbon(i):
                impatient.append(i)
        return impatient

################################ CAIRN ################################

class CAIRN(Boss):
    
    last    = None
    name    = "CAIRN"
    wing    = 4
    boss_id = 17194
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp   = self.get_mvp()
        self.lvp   = self.get_lvp()
        CAIRN.last = self
        
    def get_mvp(self):
        # Create MVP prompt
        mvplist = "**MVPs** \n"
        
        # Check for mechanics
        msg_tp = self.mvp_tp()
        msg_bad_dps = self.get_bad_dps()
        msg_bad_boons = self.get_bad_boons('Full Fight')
        msg_general = self.get_mvp_general()
        
        # Add prompts to flame if mechanics are garbage
        if msg_tp:
            mvplist = mvplist + msg_tp + "\n" 
            
        if msg_bad_dps:
            mvplist = mvplist + msg_bad_dps + "\n" 
            
        if msg_bad_boons:
            mvplist = mvplist + msg_bad_boons
            
        if msg_general:
            mvplist = mvplist + msg_general 

        # Return full prompt
        return mvplist

    
    def get_lvp(self):
        # Create LVP prompt
        lvplist = "\n**LVPs** \n"
        
        # Check for mechanics
        msg_good_dps = self.get_lvp_dps_PMA() 
        msg_covid = self.lvp_cairn_covid()
        msg_good_bdps = self.get_lvp_bdps_PMA()
        msg_general = self.get_lvp_general('Full Fight')
        
        # Add prompts to praise if mechanics are bussin fr fr
        if msg_good_dps:
            lvplist = lvplist + msg_good_dps + "\n" 

        if msg_good_bdps:
            lvplist = lvplist + msg_good_bdps + "\n" 
            
        if msg_covid:
            lvplist = lvplist + msg_covid + "\n" 

        if msg_general:
            lvplist = lvplist + msg_general + "\n" 

        # Return full prompt
        return lvplist
      
    ################################ MVP ################################
    
    # Old code, flames people that tp a lot
    def mvp_tp(self):
        i_players, max_tp, _ = Stats.get_max_value(self, self.get_tp)
        mvp_names            = self.players_to_string(i_players)
        if max_tp > 2:
            self.add_mvps(i_players)
            if len(i_players) == 1:
                return LANGUES["selected_language"]["CAIRN MVP TP S"].format(mvp_names=mvp_names, max_tp=max_tp)
            if len(i_players) > 1:
                return LANGUES["selected_language"]["CAIRN MVP TP P"].format(mvp_names=mvp_names, max_tp=max_tp)
        return
    
    ################################ LVP ################################
    
    # Praises the people who got covid twice
    def lvp_cairn_covid(self):
        i_players = self.get_cairn_covid()
        lvp_names = self.players_to_string(i_players)
        self.add_lvps(i_players)
        if i_players:
            return LANGUES["selected_language"]["LVP CAIRN COVID"].format(lvp_names=lvp_names) 
        return 
    
    ################################ CONDITIONS ################################
    
    # Returns if player got covid multiple times
    def got_cairn_covid(self, i_player: int):
        return self.get_mech_value(i_player, 'Shared Agony') > 1
    
    ################################ DATA MECHAS ################################

    # Old code, returns number of player tp
    def get_tp(self, i_player: int):
        return self.get_mech_value(i_player, 'Orange TP')
        
    # Collect all players who got covid multiple times
    def get_cairn_covid(self):
        covid = []
        for i in self.player_list:
            if self.got_cairn_covid(i):
                covid.append(i)
        return covid

################################ MO ################################

class MO(Boss):
    
    last    = None
    name    = "MO"
    wing    = 4
    boss_id = 17172
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        MO.last  = self
        
    def get_mvp(self):
        # Create MVP prompt
        mvplist = "**MVPs** \n"
        
        # Check for mechanics
        msg_pic = self.mvp_pic()
        msg_bad_dps = self.get_bad_dps()
        msg_bad_boons = self.get_bad_boons('Full Fight')
        msg_general = self.get_mvp_general()
        
        # Add prompts to flame if mechanics are garbage
        if msg_pic:
            mvplist = mvplist + msg_pic + "\n" 
            
        if msg_bad_dps:
            mvplist = mvplist + msg_bad_dps + "\n" 
            
        if msg_bad_boons:
            mvplist = mvplist + msg_bad_boons

        if msg_general:
            mvplist = mvplist + msg_general 
            
        # Return full prompt
        return mvplist

    
    def get_lvp(self):
        # Create LVP prompt
        lvplist = "\n**LVPs** \n"
        
        # Check for mechanics
        msg_good_dps = self.get_lvp_dps_PMA() 
        msg_good_cleave = self.lvp_mo_cleave()
        msg_good_bdps = self.get_lvp_bdps_PMA()
        msg_general = self.get_lvp_general('Full Fight')
        
        # Add prompts to praise if mechanics are bussin fr fr
        if msg_good_dps:
            lvplist = lvplist + msg_good_dps + "\n" 

        if msg_good_bdps:
            lvplist = lvplist + msg_good_bdps + "\n" 
            
        if msg_good_cleave:
            lvplist = lvplist + msg_good_cleave + "\n" 

        if msg_general:
            lvplist = lvplist + msg_general

        # Return full prompt
        return lvplist
        
    ################################ MVP ################################
    
    # Old code, flames if impaled
    def mvp_pic(self):
        i_players = self.get_piced()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if len(i_players) == 1:
            return LANGUES["selected_language"]["MO MVP PICS S"].format(mvp_names=mvp_names) 
        if len(i_players) > 1:
            return LANGUES["selected_language"]["MO MVP PICS P"].format(mvp_names=mvp_names)
        return
    
    ################################ LVP ################################
    
    # Praises the person that took at least 6 fixations
    def lvp_mo_cleave(self):
        i_players = []
        for i in self.player_list:
            if self.is_heal(i):
                continue
            boss_total = self.log.pjcontent['players'][i]['dpsTargets'][0][self.real_phase_id]['damage']
            
            cleave_total = self.log.pjcontent['players'][i]['dpsAll'][0]['damage']
            
            if cleave_total / boss_total > 1.10:
                i_players.append(i)
        if len(i_players) > 0:
            self.add_lvps(i_players)
            lvp_names = self.players_to_string(i_players)   
            return LANGUES["selected_language"]["LVP MO CLEAVE"].format(lvp_names=lvp_names)
        return
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################
    
    # Old code, returns if player died instantly
    def get_piced(self):
        piced = []
        for i in self.player_list:
            if self.is_dead_instant(i):
                piced.append(i)
        return piced

################################ SAMAROG ################################

class SAMAROG(Boss):
    
    last    = None
    name    = "SAMAROG"
    wing    = 4
    boss_id = 17188
    
    top_left_corn  = [278.0,645.2]
    top_right_corn = [667.6,660.7]
    bot_left_corn  = [299.4,58.6]
    bot_right_corn = [690.7,73.6]
    scaler         = 5.4621
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp     = self.get_mvp()
        self.lvp     = self.get_lvp()
        SAMAROG.last = self
        
        
    def get_mvp(self):
        # Create MVP prompt
        mvplist = "**MVPs** \n"
        
        # Check for mechanics
        msg_impaled = self.mvp_impaled()
        msg_bisou = self.mvp_traitors()
        msg_bad_cc = self.get_mvp_cc_boss(extra_exclude=[self.is_fix])
        msg_outside = self.mvp_samarog_outside()
        #msg_stunned = self.mvp_samarog_stunned()
        msg_bad_boons = self.get_bad_boons('Full Fight')
        msg_general = self.get_mvp_general()
        
        # Add prompts to flame if mechanics are garbage
        if msg_impaled:
            mvplist = mvplist + msg_impaled + "\n" 
            
        if msg_bisou:
            mvplist = mvplist + msg_bisou + "\n" 
            
        if msg_bad_cc:
            mvplist = mvplist + msg_bad_cc + "\n" 
            
        if msg_outside:
            mvplist = mvplist + msg_outside + "\n" 
            
        #if msg_stunned:
        #    mvplist = mvplist + msg_stunned + "\n" 
            
        if msg_bad_boons:
            mvplist = mvplist + msg_bad_boons

        if msg_general:
            mvplist = mvplist + msg_general 
            
        # Return full prompt
        return mvplist

    
    def get_lvp(self):        
        # Create LVP prompt
        lvplist = "\n**LVPs** \n"
        
        # Check for mechanics
        msg_good_cc = self.get_lvp_cc_boss_PMA()
        msg_tanking = self.lvp_samarog_tank()
        msg_good_dps = self.get_lvp_dps_PMA()
        msg_good_bdps = self.get_lvp_bdps_PMA()
        msg_general = self.get_lvp_general('Full Fight')
        
        # Add prompts to praise if mechanics are bussin fr fr
        if msg_good_cc:
            lvplist = lvplist + msg_good_cc + "\n" 
            
        if msg_tanking:
            lvplist = lvplist + msg_tanking + "\n" 

        if msg_good_dps:
            lvplist = lvplist + msg_good_dps + "\n" 

        if msg_good_bdps:
            lvplist = lvplist + msg_good_bdps + "\n" 

        if msg_general:
            lvplist = lvplist + msg_general + "\n" 

        # Return full prompt
        return lvplist
    
    ################################ MVP ################################ 
    
    # Old code, flames players who get impaled
    def mvp_impaled(self):
        i_players = self.get_impaled()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if len(i_players) == 1:
            return LANGUES["selected_language"]["SAMAROG MVP IMPALED S"].format(mvp_names=mvp_names) 
        if len(i_players) > 1:
            return LANGUES["selected_language"]["SAMAROG MVP IMPALED P"].format(mvp_names=mvp_names)
        return 
    
    # Old code, flames players who don't do friendship mechanic
    def mvp_traitors(self):
        i_trait, i_vict = self.get_traitors()
        trait_names     = self.players_to_string(i_trait)
        vict_names      = self.players_to_string(i_vict)
        self.add_mvps(i_trait)
        if len(i_trait) == 1:
            return LANGUES["selected_language"]["SAMAROG MVP BISOU S"].format(trait_names=trait_names, vict_names=vict_names)
        if len(i_trait) > 1:
            return LANGUES["selected_language"]["SAMAROG MVP BISOU P"].format(trait_names=trait_names, vict_names=vict_names)
        return  
        
    # Flames players who step outside the arena too much
    def mvp_samarog_outside(self):
        i_players = self.get_samarog_outside()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if i_players:
            return LANGUES["selected_language"]["MVP SAMAROG OUTSIDE"].format(mvp_names=mvp_names) 
        return 
        
    # Flame the supports for not block/stabing guldhem
    def mvp_samarog_stunned(self):
        # Find victims
        victims = self.get_samarog_stunned()
        # Get supports out of victimlist
        i_players = []
        for i in victims:
            if not self.is_support(i):
                i_players.append(i)
        # Return if no one got hatecrimed
        if not i_players:
            return
        # Return if less than 3 people get stunned (they were probably AFK in narnia)
        if len(i_players) < 3:
            return
        # Check victim subgroups
        victim_in_sub1 = False
        victim_in_sub2 = False
        
        Group_No = self.log.pjcontent['players'][2]['group']
        
        for i in i_players:
            if self.log.pjcontent['players'][i]['group'] == Group_No:
                victim_in_sub1 = True
            else:
                victim_in_sub2 = True 
        # Find supports
        supports_sub1 = []
        supports_sub2 = []
        supports_all = []
        for i in self.player_list:
            if self.is_support(i):
                supports_all.append(i)
                if self.log.pjcontent['players'][i]['group'] == Group_No:
                    supports_sub1.append(i)
                else:
                    supports_sub2.append(i)
        # Blame the correct supports based on subgroup
        param = victim_in_sub1 + 2*victim_in_sub2
        match param:
            case 1:
                supports = supports_sub1
            case 2:
                supports = supports_sub2
            case 3:
                supports = supports_all
        # Return necessary flame
        if i_players:
            self.add_mvps(supports)
            mvp_names = self.players_to_string(supports)
            self.add_lvps(i_players)
            cucks = self.players_to_string(i_players)
            return LANGUES["selected_language"]["MVP SAMAROG GULDHEM"].format(mvp_names=mvp_names, cucked_players=cucks)
        return
    
    ################################ LVP ################################ 
    
    # Praises the person that took at least 6 fixations
    def lvp_samarog_tank(self):
        i_players = self.get_samarog_tank()
        lvp_names = self.players_to_string(i_players)
        self.add_lvps(i_players)
        if i_players:
            return LANGUES["selected_language"]["LVP SAMAROG TANK"].format(lvp_names=lvp_names) 
        return 
    
    ################################ CONDITIONS ################################
    
    # Old code, checks if player got yeeted outside
    def got_impaled(self, i_player: int):
        if self.is_dead_instant(i_player):
            mech_history = self.get_player_mech_history(i_player)
            for mech in mech_history:
                if mech['name'] == "DC":
                    mech_history.remove(mech)
            if len(mech_history) > 1:
                if (mech_history[-2]['name'] == "Swp" or mech_history[-2]['name'] == "Schk.Wv") and mech_history[-1]['name'] == "Dead":
                    return True
        return False
    
    # Old code, if person took tank a lot
    def is_fix(self, i_player: int):
        return self.get_mech_value(i_player, "Fixate: Samarog") >= 3
    
    # Checks if person stood outside a lot
    def got_samarog_outside(self, i_player: int):
        return self.get_mech_value(i_player, "Spear Wall") > 1
        
    # Checks if person got stunned by guldhem
    def got_samarog_stunned(self, i_player: int):
        return self.get_mech_value(i_player, "Guldhem's Stun") > 0
        
    # Checks if person got more than 5 cc phases
    def got_samarog_tank(self, i_player: int):
        return self.get_mech_value(i_player, "Brutalized") > 5
    
    ################################ DATA MECHAS ################################
    
    # Old code, collects all players that got yeeted
    def get_impaled(self):
        i_players = []
        for i in self.player_list:
            if self.got_impaled(i):
                  i_players.append(i)
        return i_players
    
    # Old code, collects all players who didn't do friendship mechanic
    def get_traitors(self):
        traitors, victims = [], []
        big_greens        = self.get_mechanic_history("Big Green")
        small_greens      = self.get_mechanic_history("Small Green")
        failed_greens     = self.get_mechanic_history("Failed Green")
        last_fail_time    = None
        if failed_greens:
            for fail_green in failed_greens:
                if fail_green['time'] == last_fail_time:
                    continue
                last_fail_time = fail_green['time']
                fail_actor     = fail_green['actor']
                fail_time      = fail_green['time']
                for small, big in zip(small_greens, big_greens):
                    small_actor = small['actor']
                    big_actor   = big['actor']
                    green_time  = small['time']
                    if fail_actor in [big_actor, small_actor] and np.abs(fail_time - green_time) < 7000:
                        victims.append(self.get_player_id(big_actor))
                        traitors.append(self.get_player_id(small_actor))
        return traitors, victims 
    
    # Collect players who stepped outside the arena
    def get_samarog_outside(self):
        wanderer = []
        for i in self.player_list:
            if self.got_samarog_outside(i):
                  wanderer.append(i)
        return wanderer
        
    # Collect players who got stunned by Guldhem
    def get_samarog_stunned(self):
        rotation_ruined = []
        for i in self.player_list:
            if self.got_samarog_stunned(i):
                  rotation_ruined.append(i)
        return rotation_ruined
        
    # Collects players with more than 5 cc phases
    def get_samarog_tank(self):
        tank = []
        for i in self.player_list:
            if self.got_samarog_tank(i):
                  tank.append(i)
        return tank

################################ DEIMOS ################################

class DEIMOS(Boss):
    
    last       = None
    name       = "DEIMOS"
    wing       = 4
    boss_id    = 17154
    real_phase = "100% - 10%"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp    = self.get_mvp()
        self.lvp    = self.get_lvp()
        DEIMOS.last = self
        
    def get_mvp(self):        
        # Create MVP prompt
        mvplist = "**MVPs** \n"
        
        # Check for mechanics
        msg_black = self.mvp_black()
        msg_pizza = self.mvp_pizza()
        msg_no_port = self.mvp_deimos_no_port()
        msg_bad_boons = self.get_bad_boons('Main Fight', exclude=[self.is_kiter])
        msg_general = self.get_mvp_general()
        
        # Add prompts to flame if mechanics are garbage
        if msg_black:
            mvplist = mvplist + msg_black + "\n" 
            
        if msg_pizza:
            mvplist = mvplist + msg_pizza + "\n" 
            
        if msg_no_port:
            mvplist = mvplist + msg_no_port + "\n" 
            
        if msg_bad_boons:
            mvplist = mvplist + msg_bad_boons

        if msg_general:
            mvplist = mvplist + msg_general 
            
        # Return full prompt
        return mvplist
    
    def get_lvp(self):
        # Create LVP prompt
        lvplist = "\n**LVPs** \n"
        
        # Check for mechanics
        msg_tears = self.lvp_tears()
        msg_kiter = self.lvp_deimos_kiter()
        msg_general = self.get_lvp_general('Main Fight', exclude=[self.is_kiter])
        
        # Add prompts to praise if mechanics are bussin fr fr
        if msg_tears:
            lvplist = lvplist + msg_tears + "\n" 
            
        if msg_kiter:
            lvplist = lvplist + msg_kiter + "\n" 

        if msg_general:
            lvplist = lvplist + msg_general + "\n" 

        # Return full prompt
        return lvplist

    def get_dps_ranking(self):
        return self._get_dps_contrib([self.is_support, self.is_sac])

    ################################ MVP ################################
    
    # Old code, flames players who stepped in black
    def mvp_black(self):
        i_players, max_black, _ = Stats.get_max_value(self, self.get_black_trigger)
        mvp_names               = self.players_to_string(i_players)
        nb_players              = len(i_players)
        self.add_mvps(i_players)
        if nb_players == 1:
            return LANGUES["selected_language"]["DEIMOS MVP BLACK S"].format(mvp_names=mvp_names, max_black=max_black)
        if nb_players > 1:
            return LANGUES["selected_language"]["DEIMOS MVP BLACK P"].format(mvp_names=mvp_names, nb_players=nb_players, max_black=max_black)
        return
    
    # Old code, flames players who got pizza'd out of arena
    def mvp_pizza(self):
        i_players = self.get_pizzaed()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if i_players:
            return LANGUES["selected_language"]["DEIMOS MVP PIZZA"].format(mvp_names=mvp_names)
        return
    
    # Flames people who don't take greens
    def mvp_deimos_no_port(self):
        i_players = self.get_deimos_no_port()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if i_players:
            return LANGUES["selected_language"]["MVP DEIMOS GREEDER"].format(mvp_names=mvp_names)
        return
    
    ################################ LVP ################################ 
    
    # Old code, praises people that collect max tears if more than 3
    def lvp_tears(self):
        i_players, max_tears, _ = Stats.get_max_value(self, self.get_tears)
        lvp_names               = self.players_to_string(i_players)
        if i_players and max_tears > 2:
            self.add_lvps(i_players)
            return LANGUES["selected_language"]["DEIMOS LVP TEARS"].format(lvp_names=lvp_names, max_tears=max_tears)
        return
    
    # Praises for kiting
    def lvp_deimos_kiter(self):
        i_players = self.is_kiter()
        lvp_names = self.players_to_string([i_players])
        self.add_lvps([i_players])
        return LANGUES["selected_language"]["DEIMOS LVP KITER"].format(lvp_names=lvp_names)
    
    ################################ CONDITIONS ################################
    
    # Old code, checks if you got pizza'd to death
    def got_pizzaed(self, i_player: int):
        if self.is_dead_instant(i_player):
            mech_history = self.get_player_mech_history(i_player)
            for mech in mech_history:
                if mech['name'] == "DC":
                    mech_history.remove(mech)
            if mech_history[-2]['name'] == "Pizza" and mech_history[-1]['name'] == "Dead":
                return True
        return False
    
    # Old code, checks if person got the green
    def is_sac(self, i_player: int):
        greens = self.get_mechanic_history('Chosen (Green)')
        if not greens:
            return False
        return greens[-1]['actor'] == self.get_player_name(i_player)
        
    # Checks if player didn't go down with green except kiter & tank
    def got_deimos_no_port(self, i_player: int):
        if self.get_mech_value(i_player, "Teleport", "Main Fight") < 4:
            # don't hatecrime tank
            if self.is_tank(i_player):
                return False
            # don't hatecrime kiter
            if i_player == self.is_kiter():
                return False
            return True
        return False
        
    # Returns kiter
    def is_kiter(self):
        kiter = -1
        max_soulfeast = 0
        # For every player, check how many times they get hit by Soul Feast, keep the player with the highest number
        for i in self.player_list:
            counter = 0
            for j in range(len(self.log.pjcontent['players'][i]['totalDamageTaken'])):
                for k in range(len(self.log.pjcontent['players'][i]['totalDamageTaken'][j])):
                    if self.log.pjcontent['players'][i]['totalDamageTaken'][j][k]['id'] == 37805:
                        counter = counter + 1
            if counter > max_soulfeast:
                kiter = i
                max_soulfeast = counter
        return kiter

    ################################ DATA MECHAS ################################

    # Old code, returns number of black steps
    def get_black_trigger(self, i_player: int):
        return self.get_mech_value(i_player, "Black Oil Trigger")
 
    # Old code, returns number of tears
    def get_tears(self, i_player: int):
        return self.get_mech_value(i_player, "Tear")
    
    # Old code, collects all players who got pizza'd to death
    def get_pizzaed(self):
        pizzaed = []
        for i in self.player_list:
            if self.got_pizzaed(i):
                pizzaed.append(i)
        return pizzaed
        
    # Collects all players who didn't take green to greed
    def get_deimos_no_port(self):
        greeder = []
        for i in self.player_list:
            if self.got_deimos_no_port(i):
                greeder.append(i)
        return greeder

################################ SH ################################

class SH(Boss):
    
    last    = None
    name    = "SH"
    wing    = 5
    boss_id = 19767
    
    center_arena = [375,375]
    radius1      = 345.5
    radius2      = 304.2
    radius3      = 256.2
    radius4      = 208.5
    radius5      = 163
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        SH.last  = self

    def get_mvp(self):
        # Create MVP prompt
        mvplist = "**MVPs** \n"
        
        # Check for mechanics
        msg_wall = self.mvp_wall()
        msg_fall = self.mvp_fall()
        msg_bad_cc = self.get_mvp_cc_boss()
        msg_orange = self.mvp_desmina_orange()
        msg_corrupted = self.mvp_desmina_corrupted()
        msg_bad_boons = self.get_bad_boons('Full Fight')
        msg_general = self.get_mvp_general()
        
        # Add prompts to flame if mechanics are garbage
        if msg_bad_cc:
            mvplist = mvplist + msg_bad_cc + "\n" 
            
        if msg_wall:
            mvplist = mvplist + msg_wall + "\n" 
            
        if msg_fall:
            mvplist = mvplist + msg_fall + "\n" 
            
        if msg_orange:
            mvplist = mvplist + msg_orange + "\n" 
            
        if msg_corrupted:
            mvplist = mvplist + msg_corrupted + "\n" 
            
        if msg_bad_boons:
            mvplist = mvplist + msg_bad_boons

        if msg_general:
            mvplist = mvplist + msg_general 
        
        # Return full prompt
        return mvplist
    
    def get_lvp(self):        
        # Create LVP prompt
        lvplist = "\n**LVPs** \n"
        
        # Check for mechanics
        msg_good_cc = self.get_lvp_cc_boss_PMA()
        msg_good_dps = self.get_lvp_dps_PMA()
        msg_good_bdps = self.get_lvp_bdps_PMA()
        msg_general = self.get_lvp_general('Full Fight')
        
        # Add prompts to praise if mechanics are bussin fr fr
        if msg_good_cc:
            lvplist = lvplist + msg_good_cc + "\n" 

        if msg_good_dps:
            lvplist = lvplist + msg_good_dps + "\n" 

        if msg_good_bdps:
            lvplist = lvplist + msg_good_bdps + "\n" 

        if msg_general:
            lvplist = lvplist + msg_general + "\n" 

        # Return full prompt
        return lvplist
        
    ################################ MVP ################################
    
    # Old code, flames if you get hit by wall
    def mvp_wall(self):
        i_players = self.get_walled_players()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if i_players:
            return LANGUES["selected_language"]["SH MVP WALL"].format(mvp_names=mvp_names)
        return
    
    # Old code, flames if you fall off the platform
    def mvp_fall(self):
        i_players = self.get_fallen_players()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if i_players:
            return LANGUES["selected_language"]["SH MVP FALL"].format(mvp_names=mvp_names)
        return
        
    # Flames all people who keep getting hit by orange aoes
    def mvp_desmina_orange(self):
        i_players = self.get_desmina_orange()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if i_players:
            return LANGUES["selected_language"]["MVP SH ORANGE"].format(mvp_names=mvp_names)
        return
        
    # Flames all people who keep getting hit by orange aoes
    def mvp_desmina_corrupted(self):
        i_players = self.get_desmina_corrupted()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if i_players:
            return LANGUES["selected_language"]["MVP SH CORRUPT"].format(mvp_names=mvp_names)
        return
    
    ################################ LVP ################################
    
    
    
    ################################ CONDITIONS ################################
    
    # Old code, checks if player hit wall
    def took_wall(self, i_player: int):
        if self.is_dead_instant(i_player) and not self.has_fallen(i_player):
            return True
        return False
    
    # Old code, checks if player fell off platform
    def has_fallen(self, i_player: int):
        if self.is_dead_instant(i_player):
            last_pos         = self.get_player_pos(i_player)[-1]
            death_time       = self.get_player_death_timer(i_player)
            fell_at_begin    = get_dist(SH.center_arena, last_pos) > SH.radius2
            fell_to_radius23 = death_time > self.bosshp_to_time(90)+2500 and death_time < self.bosshp_to_time(66)+2500 and get_dist(SH.center_arena, last_pos) > SH.radius3
            fell_to_radius34 = death_time > self.bosshp_to_time(66)+2500 and death_time < self.bosshp_to_time(33)+2500 and get_dist(SH.center_arena, last_pos) > SH.radius4
            fell_to_radius45 = death_time > self.bosshp_to_time(33)+2500 and get_dist(SH.center_arena, last_pos) > SH.radius5
            if fell_at_begin or fell_to_radius23 or fell_to_radius34 or (self.cm and fell_to_radius45):
                return True
        return False
        
    # Check if player stands in oranges
    def got_desmina_orange(self, i_player: int):
        oranges = self.get_mech_value(i_player, "Inner Donut")
        oranges = oranges + self.get_mech_value(i_player, "Outer Donut")
        oranges = oranges + self.get_mech_value(i_player, "8 Slices")     
        oranges = oranges + self.get_mech_value(i_player, "4 Slices 1")  
        oranges = oranges + self.get_mech_value(i_player, "4 Slices 2")          
        return oranges > 5
        
    # Check if player gets corrupted
    def got_desmina_corrupted(self, i_player: int):
        corrupted = self.get_mech_value(i_player, "Scythe")
        corrupted = corrupted + self.get_mech_value(i_player, "Golem Aoe")
        return corrupted > 1
    
    ################################ DATA MECHAS ################################

    # Old code, collect all players that got hit by wall
    def get_walled_players(self):
        walled = []
        for i in self.player_list:
            if self.took_wall(i):
                walled.append(i)
        return walled
    
    # Old code, collect all players that fell down the platform
    def get_fallen_players(self):
        fallen = []
        for i in self.player_list:
            if self.has_fallen(i):
                fallen.append(i)
        return fallen
        
    # Collect all people that get hit by orange aoes
    def get_desmina_orange(self):
        oopsies = []
        for i in self.player_list:
            if self.got_desmina_orange(i):
                oopsies.append(i)
        return oopsies
        
    # Collect all people that get corrupted a lot
    def get_desmina_corrupted(self):
        politicians = []
        for i in self.player_list:
            if self.got_desmina_corrupted(i):
                politicians.append(i)
        return politicians

################################ DHUUM ################################

class DHUUM(Boss):
    
    last       = None
    name       = "DHUUM"
    wing       = 5
    boss_id    = 19450
    real_phase = "Dhuum Fight"
    
    def __init__(self, log: Log):    
        super().__init__(log)
        self.mvp   = self.get_mvp()
        self.lvp   = self.get_lvp()
        DHUUM.last = self
        
    def get_mvp(self):
        # Create MVP prompt
        mvplist = "**MVPs** \n"
        
        # Check for mechanics
        msg_cracks = self.mvp_cracks()
        msg_bad_dps = self.get_bad_dps(extra_exclude=[self.is_green])
        msg_sucked = self.mvp_dhuum_suck()
        msg_shackle = self.mvp_dhuum_shackle()
        msg_bad_boons = self.get_bad_boons('Main Fight', exclude=[self.is_green])
        msg_general = self.get_mvp_general()
        
         # Add prompts to flame if mechanics are garbage
        if msg_bad_dps:
            mvplist = mvplist + msg_bad_dps + "\n" 
            
        if msg_cracks:
            mvplist = mvplist + msg_cracks + "\n" 
            
        if msg_sucked:
            mvplist = mvplist + msg_sucked + "\n" 
            
        if msg_shackle:
            mvplist = mvplist + msg_shackle + "\n" 
            
        if msg_bad_boons:
            mvplist = mvplist + msg_bad_boons

        if msg_general:
            mvplist = mvplist + msg_general 
            
        # Return full prompt
        return mvplist
    
    def get_lvp(self):
        # Create LVP prompt
        lvplist = "\n**LVPs** \n"
        
        # Check for mechanics
        msg_good_dps = self.get_lvp_dps_PMA()
        msg_pity_bomb = self.lvp_dhuum_bomb_pity()
        msg_good_bdps = self.get_lvp_bdps_PMA()
        msg_general = self.get_lvp_general('Main Fight', exclude=[self.is_green])
        
        # Add prompts to praise if mechanics are bussin fr fr
        if msg_good_dps:
            lvplist = lvplist + msg_good_dps + "\n" 

        if msg_good_bdps:
            lvplist = lvplist + msg_good_bdps + "\n" 
            
        if msg_pity_bomb:
            lvplist = lvplist + msg_pity_bomb + "\n" 

        if msg_general:
            lvplist = lvplist + msg_general + "\n" 
            
        # Return full prompt
        return lvplist

    def get_dps_ranking(self):
        return self._get_dps_contrib([self.is_support, self.is_green])
   
    ################################ MVP ################################
    
    # Old code, flames people that step on cracks
    def mvp_cracks(self):
        i_players, max_cracks, _ = Stats.get_max_value(self, self.get_cracks)
        mvp_names                = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if len(i_players) == 1:
            return LANGUES["selected_language"]["DHUUM MVP CRACKS S"].format(mvp_names=mvp_names, max_cracks=max_cracks)
        if len(i_players) > 1:
            return LANGUES["selected_language"]["DHUUM MVP CRACKS P"].format(mvp_names=mvp_names, max_cracks=max_cracks)
        return

    # Flame the people that go in the middle during suck without invuln
    def mvp_dhuum_suck(self):
        i_players = self.get_dhuum_suck()
        # Return necessary flame
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["MVP DHUUM SUCC"].format(mvp_names=mvp_names)
        return
        
    # Flame the people that AFK with shackle
    def mvp_dhuum_shackle(self):
        i_players = self.get_dhuum_shackle()
        # Return necessary flame
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["MVP DHUUM SHACKLE"].format(mvp_names=mvp_names)
        return
        
    ################################ LVP ################################
    
    # Praise the people that got a lot of bombs
    def lvp_dhuum_bomb_pity(self):
        i_players = self.get_dhuum_bomb_pity()
        # Return necessary praise
        if i_players:
            self.add_lvps(i_players)
            lvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["LVP DHUUM BOMB"].format(lvp_names=lvp_names)
        return 
    
    ################################ CONDITIONS ################################
    
    # Old code, checks if player does green
    def is_green(self, i_player: int) -> bool:
        return self.get_mech_value(i_player, "Green port", "Dhuum Fight") > 0
        
    # Check if player stood in middle during succ
    def got_dhuum_suck(self, i_player: int):
        return self.get_mech_value(i_player, "Suck dmg") > 0
    
    # Check if player got hit by armslam
    def got_dhuum_shackle(self, i_player: int):
        return self.get_mech_value(i_player, "Shackles Dmg") > 1
        
    # Check if player got many bombs
    def got_dhuum_bomb_pity(self, i_player: int):
        return self.get_mech_value(i_player, "Bomb", "Main Fight") > 1
    
    ################################ DATA MECHAS ################################
    
    # Old code, returns how many times player got hit by cracks
    def get_cracks(self, i_player: int):
        return self.get_mech_value(i_player, "Cracks") 

    # Collect all people that stood in middle during succ
    def get_dhuum_suck(self):
        succed = []
        for i in self.player_list:
            if self.got_dhuum_suck(i):
                succed.append(i)
        return succed

    # Collect all people that AFK with shackle
    def get_dhuum_shackle(self):
        actual_grief_btw = []
        for i in self.player_list:
            if self.got_dhuum_shackle(i):
                actual_grief_btw.append(i)
        return actual_grief_btw
        
    # Collect all people that got a lot of bombs
    def get_dhuum_bomb_pity(self):
        bombers = []
        for i in self.player_list:
            if self.got_dhuum_bomb_pity(i):
                bombers.append(i)
        return bombers

################################ CA ################################

class CA(Boss):
    
    last    = None
    name    = "CA"
    wing    = 6
    boss_id = 43974

    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        CA.last  = self
        
        
    def get_mvp(self):
        # Create MVP prompt
        mvplist = "**MVPs** \n"
        
        # Check for mechanics
        msg_bad_dps = self.get_bad_dps()
        msg_noblock = self.mvp_CA_armslam()
        msg_bad_boons = self.get_bad_boons('Full Fight')
        msg_general = self.get_mvp_general()
        
        # Add prompts to flame if mechanics are garbage
        if msg_bad_dps:
            mvplist = mvplist + msg_bad_dps + "\n" 
            
        if msg_noblock:
            mvplist = mvplist + msg_noblock + "\n"
            
        if msg_bad_boons:
            mvplist = mvplist + msg_bad_boons

        if msg_general:
            mvplist = mvplist + msg_general 

        # Return full prompt
        return mvplist
    
    def get_lvp(self):
        # Create LVP prompt
        lvplist = "\n**LVPs** \n"
        
        # Check for mechanics
        msg_good_dps = self.get_lvp_dps_PMA()
        msg_good_bdps = self.get_lvp_bdps_PMA()
        msg_general = self.get_lvp_general('Full Fight')
        
        # Add prompts to praise if mechanics are bussin fr fr
        if msg_good_dps:
            lvplist = lvplist + msg_good_dps + "\n" 

        if msg_good_bdps:
            lvplist = lvplist + msg_good_bdps + "\n" 

        if msg_general:
            lvplist = lvplist + msg_general + "\n" 
            
        # Return full prompt
        return lvplist
  
    ################################ MVP ################################
    
    # Flame the supports for not block/stabing arm slam
    def mvp_CA_armslam(self):
        # Find victims
        victims = self.get_CA_armslam()
        # Get supports out of victimlist
        i_players = []
        for i in victims:
            if not self.is_support(i):
                i_players.append(i)
        # Return if no one got hatecrimed
        if not i_players:
            return
        # Return if less than 3 people got stunned (they were probably AFK in narnia)
        if len(i_players) < 3:
            return
        # Check victim subgroups
        victim_in_sub1 = False
        victim_in_sub2 = False
        
        Group_No = self.log.pjcontent['players'][2]['group']
        
        for i in i_players:
            if self.log.pjcontent['players'][i]['group'] == Group_No:
                victim_in_sub1 = True
            else:
                victim_in_sub2 = True 
        # Find supports
        supports_sub1 = []
        supports_sub2 = []
        supports_all = []
        for i in self.player_list:
            if self.is_support(i):
                supports_all.append(i)
                if self.log.pjcontent['players'][i]['group'] == Group_No:
                    supports_sub1.append(i)
                else:
                    supports_sub2.append(i)
        # Blame the correct supports based on subgroup
        param = victim_in_sub1 + 2*victim_in_sub2
        match param:
            case 1:
                supports = supports_sub1
            case 2:
                supports = supports_sub2
            case 3:
                supports = supports_all
        # Return necessary flame
        if i_players:
            self.add_mvps(supports)
            mvp_names = self.players_to_string(supports)
            self.add_lvps(i_players)
            cucks = self.players_to_string(i_players)
            return LANGUES["selected_language"]["MVP CA ARMSLAM"].format(mvp_names=mvp_names, cucked_players=cucks)
        return
    
    ################################ LVP ################################
    
    
    
    ################################ CONDITIONS ################################
    
    # Check if player got hit by armslam
    def got_CA_armslam(self, i_player: int):
        return self.get_mech_value(i_player, "Arm Slam") > 0
    
    ################################ DATA MECHAS ################################

    # Collect all people that got hit by arm slam
    def get_CA_armslam(self):
        ihatemysupport = []
        for i in self.player_list:
            if self.got_CA_armslam(i):
                ihatemysupport.append(i)
        return ihatemysupport

################################ LARGOS ################################

class LARGOS(Boss):
    
    last    = None
    name    = "LARGOS"
    wing    = 6
    boss_id = 21105

    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp    = self.get_mvp()
        self.lvp    = self.get_lvp()
        LARGOS.last = self
        
    def get_mvp(self):
        # Create MVP prompt
        mvplist = "**MVPs** \n"
        
        # Check for mechanics
        msg_dash = self.mvp_dash()
        msg_tornado = self.mvp_largos_tornado()
        msg_bubble = self.mvp_largos_bubble()
        msg_boonsteal = self.mvp_largos_boonsteal()
        msg_bad_boons = self.get_bad_boons('Full Fight')
        msg_general = self.get_mvp_general()
        
        # Add prompts to flame if mechanics are garbage
        if msg_dash:
            mvplist = mvplist + msg_dash + "\n" 
            
        if msg_tornado:
            mvplist = mvplist + msg_tornado + "\n" 
            
        if msg_bubble:
            mvplist = mvplist + msg_bubble + "\n" 
            
        if msg_boonsteal:
            mvplist = mvplist + msg_boonsteal + "\n" 
            
        if msg_bad_boons:
            mvplist = mvplist + msg_bad_boons

        if msg_general:
            mvplist = mvplist + msg_general 

        # Return full prompt
        return mvplist
    
    def get_lvp(self):
        # Create LVP prompt
        lvplist = "\n**LVPs** \n"
        
        # Check for mechanics
        msg_lvp_cc = self.get_lvp_cc_total()
        msg_good_dps = self.get_lvp_dps_PMA(2)
        msg_good_bdps = self.get_lvp_bdps_PMA(2)
        msg_general = self.get_lvp_general('Full Fight')
        
        # Add prompts to praise if mechanics are bussin fr fr
        if msg_lvp_cc:
            lvplist = lvplist + msg_lvp_cc + "\n" 

        if msg_good_dps:
            lvplist = lvplist + msg_good_dps + "\n" 

        if msg_good_bdps:
            lvplist = lvplist + msg_good_bdps + "\n" 

        if msg_general:
            lvplist = lvplist + msg_general + "\n" 
            
        # Return full prompt
        return lvplist

    ################################ MVP ################################
    
    # Old code, flames if you get hit by dash more than 7 times, otherwise does bad dps routine
    def mvp_dash(self):
        i_players, max_dash, _ = Stats.get_max_value(self, self.get_dash, exclude=[self.is_heal, self.is_tank])
        mvp_names              = self.players_to_string(i_players)
        if max_dash < 7:
            return self.get_bad_dps()
        else:
            self.add_mvps(i_players)
            if len(i_players) == 1:
                return LANGUES["selected_language"]["LARGOS MVP DASH S"].format(mvp_names=mvp_names, max_dash=max_dash)
            if len(i_players) > 1:
                return LANGUES["selected_language"]["LARGOS MVP DASH P"].format(mvp_names=mvp_names, max_dash=max_dash)
        return
    
    # Old code, flames if bad dps, idk, some magic shit going on in there
    def get_bad_dps(self, extra_exclude: list[classmethod]=[]):
        i_sup, sup_max_dmg, _ = Stats.get_max_value(self, self.get_dmg_boss, exclude=[self.is_dps])
        sup_name              = self.players_to_string(i_sup)
        bad_dps               = []
        for i in self.player_list:   
            if any(filter_func(i) for filter_func in extra_exclude) or self.is_dead(i) or self.is_support(i):
                continue
            dps = self.get_dmg_boss(i)
            if dps < sup_max_dmg:
                if not(self.name == "QUOIDIMM" and self.get_player_spe(i) == "Spellbreaker"): 
                    bad_dps.append(i)
        if bad_dps:
            self.add_mvps(bad_dps)
            bad_dps_name = self.players_to_string(bad_dps)
            if len(bad_dps) == 1:
                return LANGUES["selected_language"]["MVP BAD DPS S"].format(bad_dps_name=bad_dps_name, sup_name=sup_name)
            else:
                return LANGUES["selected_language"]["MVP BAD DPS P"].format(bad_dps_name=bad_dps_name, sup_name=sup_name)
                
    # Flame the people that AFK in tornado too much
    def mvp_largos_tornado(self):
        i_players = self.get_largos_tornado()
        # Return necessary flame
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["MVP LARGOS TORNADO"].format(mvp_names=mvp_names)
        return
        
    # Flame the people that got bubbled
    def mvp_largos_bubble(self):
        i_players = self.get_largos_bubble()
        # Return necessary flame
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            if len(mvp_names) == 1:
                return LANGUES["selected_language"]["MVP LARGOS BUBBLE S"].format(mvp_names=mvp_names)
            else:
                return LANGUES["selected_language"]["MVP LARGOS BUBBLE P"].format(mvp_names=mvp_names)
        return
        
    # Flame the people that got hit by boonsteal attack
    def mvp_largos_boonsteal(self):
        i_players = self.get_largos_boonsteal()
        # Return necessary flame
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["MVP LARGOS BOON"].format(mvp_names=mvp_names)
        return
    
    ################################ LVP ################################ 
    
    
    
    ################################ CONDITIONS ################################
    
    # Check if player is in tornado too much
    def got_largos_tornado(self, i_player: int):
        return self.get_mech_value(i_player, "Tornado") > 4
        
    # Check if player is in tornado too much
    def got_largos_bubble(self, i_player: int):
        return self.get_mech_value(i_player, "Float Bubble") > 0
        
    # Check if player is in tornado too much
    def got_largos_boonsteal(self, i_player: int):
        return self.get_mech_value(i_player, "Boon Steal") > 0
    
    ################################ DATA MECHAS ################################

    # Old code, Return amount of time player got hit by dash
    def get_dash(self, i_player: int):
        return self.get_mech_value(i_player, "Vapor Rush Charge")
    
    # Old code, corrects damage done for dps calcs
    def get_dmg_boss(self, i_player: int):
        dmg = self.log.pjcontent['players'][i_player]['dpsTargets'][0][self.real_phase_id]['damage']
        dmg += self.log.pjcontent['players'][i_player]['dpsTargets'][1][self.real_phase_id]['damage']
        return dmg
        
    # Collect all AFK people that are stacking water debuff in tornado
    def get_largos_tornado(self):
        AFK = []
        for i in self.player_list:
            if self.got_largos_tornado(i):
                AFK.append(i)
        return AFK
        
    # Collect all AFK people that got bubbled
    def get_largos_bubble(self):
        AFK = []
        for i in self.player_list:
            if self.got_largos_bubble(i):
                AFK.append(i)
        return AFK

    # Collect all AFK people that got hit by boonsteal attack
    def get_largos_boonsteal(self):
        AFK = []
        for i in self.player_list:
            if self.got_largos_boonsteal(i):
                AFK.append(i)
        return AFK

################################ QADIM ################################

class Q1(Boss):
    
    last    = None
    name    = "QADIM"
    wing    = 6
    boss_id = 20934
    
    center     = [411.5,431.1]
    fdp_radius = 70

    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        Q1.last  = self
        
    def get_mvp(self):
        # Create MVP prompt
        mvplist = "**MVPs** \n"
        
        # Check for mechanics
        msg_fdp = self.mvp_fdp()
        msg_wave = self.mvp_wave()
        msg_fire_aoe = self.mvp_q1_fire_aoe()
        msg_qadim_hitbox = self.mvp_q1_hitbox()
        msg_port = self.mvp_q1_port()
        
        q1_lamp, _, _ = Stats.get_max_value(self, self.get_q1_lamp)
        q1_kiter, _, _ = Stats.get_max_value(self, self.get_q1_kiter)
        msg_bad_boons = self.get_bad_boons('Full Fight', exclude=q1_lamp + q1_kiter)
        msg_general = self.get_mvp_general()
        
        # Add prompts to flame if mechanics are garbage
        if msg_fdp:
            mvplist = mvplist + msg_fdp + "\n" 
        
        if msg_wave:
            mvplist = mvplist + msg_wave + "\n" 
            
        if msg_fire_aoe:
            mvplist = mvplist + msg_fire_aoe + "\n" 
            
        if msg_qadim_hitbox:
            mvplist = mvplist + msg_qadim_hitbox + "\n" 
            
        if msg_port:
            mvplist = mvplist + msg_port + "\n" 
            
        if msg_bad_boons:
            mvplist = mvplist + msg_bad_boons

        if msg_general:
            mvplist = mvplist + msg_general 
            
        # Return full list
        return mvplist
    
    def get_lvp(self):
        # Create LVP prompt
        lvplist = "\n**LVPs** \n"
        
        # Check for mechanics
        msg_special_roles = self.lvp_q1_special_roles()
        q1_lamp, _, _ = Stats.get_max_value(self, self.get_q1_lamp)
        q1_kiter, _, _ = Stats.get_max_value(self, self.get_q1_kiter)
        msg_general = self.get_lvp_general('Full Fight', exclude=q1_lamp + q1_kiter)
        
        # Add prompts to praise if mechanics are bussin fr fr
        if msg_special_roles:
            lvplist = lvplist + msg_special_roles + "\n" 

        if msg_general:
            lvplist = lvplist + msg_general
        
        # Return full list    
        return lvplist
        
    ################################ MVP ################################
    
    # Old code, flames people who didn't go to a pylon
    def mvp_fdp(self):
        i_players = self.get_fdp()
        fdp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if len(i_players) == 1:
            return LANGUES["selected_language"]["QADIM MVP PYRE S"].format(fdp_names=fdp_names)
        if len(i_players) > 1:
            return LANGUES["selected_language"]["QADIM MVP PYRE P"].format(fdp_names=fdp_names)
    
    # Flames people who got hit by the shockwave the most
    def mvp_wave(self):
        i_players, max_waves, _ = Stats.get_max_value(self, self.get_wave)    
        mvp_names               = self.players_to_string(i_players)
        # Allow people to get hit by 1 wave
        if max_waves < 2:
            return
        # Otherwise return the necessary flame
        self.add_mvps(i_players)
        if len(i_players) == 1:
            return LANGUES["selected_language"]["QADIM MVP WAVE S"].format(mvp_names=mvp_names, max_waves=max_waves)
        if len(i_players) > 1:
            return LANGUES["selected_language"]["QADIM MVP WAVE P"].format(mvp_names=mvp_names, max_waves=max_waves)
        return
        
    # Flame the people that got hit by fire AoEs from the sky
    def mvp_q1_fire_aoe(self):
        i_players = self.get_q1_fire_aoe()
        # Return necessary flame
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["MVP QADIM FIRE AOE"].format(mvp_names=mvp_names)
        return
        
    # Flame the people that AFK in the hitbox
    def mvp_q1_hitbox(self):
        i_players = self.get_q1_hitbox()
        # Return necessary flame
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["MVP QADIM HITBOX"].format(mvp_names=mvp_names)
        return
        
    # Flame the people that got ported at least twice
    def mvp_q1_port(self):
        i_players = self.get_q1_port()
        # Return necessary flame
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["MVP QADIM PORT"].format(mvp_names=mvp_names)
        return
    
    ################################ LVP ################################ 
    
    # Praise the kiter & lamp 
    def lvp_q1_special_roles(self):
        i_players, _, _ = Stats.get_max_value(self, self.get_q1_lamp)
        i_players_2, _, _ = Stats.get_max_value(self, self.get_q1_kiter)
        i_players.append(i_players_2[0])
        # Return necessary praise
        if i_players:
            self.add_lvps(i_players)            
            lvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["LVP QADIM ROLES"].format(lvp_names=lvp_names)
        return
    
    ################################ CONDITIONS ################################
    
    # Check if player is in fire AoE
    def got_q1_fire_aoe(self, i_player: int):
        return self.get_mech_value(i_player, "Inferno Pool") > 1
        
    # Check if player is in Qadim hitbox
    def got_q1_hitbox(self, i_player: int):
        return self.get_mech_value(i_player, "Qadim Hitbox AoE") > 1
        
    # Check if player got ported multiple times
    def got_q1_port(self, i_player: int):
        return self.get_mech_value(i_player, "Port to Qadim") > 1
    
    ################################ DATA MECHAS ################################

    # Old code, Collect all people who didn't go to a pylon
    def get_fdp(self):
        fdp              = []
        start_p1, end_p1 = self.get_phase_timers("Qadim P1")
        start_p2, end_p2 = self.get_phase_timers("Qadim P2")
        for i in self.player_list:
            if not self.is_tank(i):
                add_fdp = True
                pos_p1  = self.get_player_pos(i, start=start_p1, end=end_p1)
                pos_p2  = self.get_player_pos(i, start=start_p2, end=end_p2)
                for pos in pos_p1:
                    dist = get_dist(pos, Q1.center)
                    if dist > Q1.fdp_radius:
                        add_fdp = False
                        break        
                for pos in pos_p2:
                    dist = get_dist(pos, Q1.center)
                    if dist > Q1.fdp_radius:
                        add_fdp = False
                        break 
                if add_fdp:
                    fdp.append(i)
        return fdp
 
    # Returns total shockwave hit value for each player (qadim + destroyer)
    def get_wave(self, i_player: int):
        total_shockwaves = self.get_mech_value(i_player, "Mace Shockwave")
        total_shockwaves = total_shockwaves + self.get_mech_value(i_player, "Destroyer Shockwave")
        return total_shockwaves
        
    # Collect all the clueless players who AFK at the fire aoe drop positions 
    def get_q1_fire_aoe(self):
        clueless = []
        for i in self.player_list:
            if self.got_q1_fire_aoe(i):
                clueless.append(i)
        return clueless
    
    # Collect all greeders who enter q1 hitbox
    def get_q1_hitbox(self):
        greeders = []
        for i in self.player_list:
            if self.got_q1_hitbox(i):
                greeders.append(i)
        return greeders
    
    # Collect all *tank players* who get ported multiple times  
    def get_q1_port(self):
        porters = []
        for i in self.player_list:
            if self.got_q1_port(i):
                porters.append(i)
        return porters
        
    # Return Qadim Lamp 
    def get_q1_lamp(self, i_player: int):
        return self.get_mech_value(i_player, "Lamp Return") > 2
        
    # Collect Qadim kiter by distance
    def get_q1_kiter(self, i_player: int):
        first_slub_time = 3800
        time_index = time_to_index(first_slub_time, self.time_base)  
        distance_score = 0
        # Distance score is distance to middle summed until 1st slubling spawn time
        for i in range(time_index):
            kiter_pos  = self.get_player_pos(i_player)[i]
            distance_score = distance_score + get_dist(kiter_pos, Q1.center)
        return distance_score

################################ ADINA ################################

class ADINA(Boss):
    
    last    = None
    name    = "ADINA"
    wing    = 7
    boss_id = 22006
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp   = self.get_mvp()
        self.lvp   = self.get_lvp()
        ADINA.last = self
        
    def get_mvp(self):
        # Create MVP prompt
        mvplist = "**MVPs** \n"
        
        # Check for mechanics
        msg_bad_dps = self.mvp_dmg_split()
        msg_blinded = self.mvp_adina_blinded()
        msg_knockback = self.mvp_adina_knockback()
        msg_bad_boons = self.get_bad_boons('Full Fight')
        msg_general = self.get_mvp_general()
        
        # Add prompts to flame if mechanics are garbage
        if msg_bad_dps:
            mvplist = mvplist + msg_bad_dps + "\n" 
            
        if msg_blinded:
            mvplist = mvplist + msg_blinded + "\n" 
            
        if msg_knockback:
            mvplist = mvplist + msg_knockback + "\n"

        if msg_bad_boons:
            mvplist = mvplist + msg_bad_boons

        if msg_general:
            mvplist = mvplist + msg_general 
            
        # Return full list
        return mvplist
    
    def get_lvp(self):
        # Create LVP prompt
        lvplist = "\n**LVPs** \n"
        
        # Check for mechanics
        msg_good_split = self.lvp_dmg_split()
        msg_good_bdps = self.get_lvp_bdps_PMA()
        msg_general = self.get_lvp_general('Full Fight')
        
        # Add prompts to praise if mechanics are bussin fr fr
        if msg_good_split:
            lvplist = lvplist + msg_good_split + "\n" 

        if msg_good_bdps:
            lvplist = lvplist + msg_good_bdps + "\n" 

        if msg_general:
            lvplist = lvplist + msg_general + "\n" 
        
        # Return full list    
        return lvplist
        
    ################################ MVP ################################
    
    # Old code, Flames lowest DPS non support person for splits
    def mvp_dmg_split(self):
        i_players, min_dmg, total_dmg = Stats.get_min_value(self, self.get_dmg_split, exclude=[self.is_support])
        mvp_names                     = self.players_to_string(i_players)
        dmg_ratio                     = min_dmg / total_dmg * 100
        self.add_mvps(i_players)
        return LANGUES["selected_language"]["ADINA MVP SPLIT"].format(mvp_names=mvp_names, dmg_ratio=dmg_ratio)
        
    # Flame the people that got blinded
    def mvp_adina_blinded(self):
        i_players = self.get_adina_blinded()
        # Return necessary flame
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["MVP ADINA BLINDED"].format(mvp_names=mvp_names)
        return
    
    # Flame the people that got hit by knockback attack
    def mvp_adina_knockback(self):
        i_players = self.get_adina_knockback()
        # Return necessary flame
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            number_mvp = len(i_players)
            if number_mvp == 1:
                return LANGUES["selected_language"]["MVP ADINA KNOCKBACK S"].format(mvp_names=mvp_names)
            else:
                return LANGUES["selected_language"]["MVP ADINA KNOCKBACK P"].format(mvp_names=mvp_names)          
        return
    
    ################################ LVP ################################    
    
    # Old code, Praises highest DPS person for splits
    def lvp_dmg_split(self):
        i_players, max_dmg, total_dmg = Stats.get_max_value(self, self.get_dmg_split) 
        lvp_names                     = self.players_to_string(i_players)
        dmg_ratio                     = max_dmg / total_dmg * 100
        self.add_lvps(i_players)
        return LANGUES["selected_language"]["ADINA LVP SPLIT"].format(lvp_names=lvp_names, dmg_ratio=dmg_ratio)
    
    ################################ CONDITIONS ################################
    
    # Check if player got blinded
    def got_adina_blinded(self, i_player: int):
        return self.get_mech_value(i_player, "Radiant Blindness") > 0
        
    # Check if player got hit by knockback
    def got_adina_knockback(self, i_player: int):
        return self.get_mech_value(i_player, "Perilous Pulse") > 0
    
    ################################ DATA MECHAS ################################
    
    # Old code, Collects all split damage for the squad
    def get_dmg_split(self, i_player: int):
        dmg_split1 = self.log.jcontent['phases'][2]['dpsStats'][i_player][0]
        dmg_split2 = self.log.jcontent['phases'][4]['dpsStats'][i_player][0]
        dmg_split3 = self.log.jcontent['phases'][6]['dpsStats'][i_player][0]
        return dmg_split1 + dmg_split2 + dmg_split3
        
    # Collect all the peepos that got blinded
    def get_adina_blinded(self):
        AFK = []
        for i in self.player_list:
            if self.got_adina_blinded(i):
                AFK.append(i)
        return AFK
        
    # Collect all the griefers that got hit by the knockback   
    def get_adina_knockback(self):
        griefers = []
        for i in self.player_list:
            if self.got_adina_knockback(i):
                griefers.append(i)
        return griefers
        

################################ SABIR ################################

class SABIR(Boss):
    
    last    = None
    name    = "SABIR"
    wing    = 7
    boss_id = 21964
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp   = self.get_mvp()
        self.lvp   = self.get_lvp()
        SABIR.last = self
        
    def get_mvp(self):
        # Create MVP prompt
        mvplist = "**MVPs** \n"
        
        # Check for mechanics
        msg_bad_cc = self.get_mvp_cc_boss()
        msg_shockwave_hit = self.mvp_sabir_shockwave()
        msg_big_tornado = self.mvp_sabir_big_tornado()
        msg_bad_boons = self.get_bad_boons('Full Fight')
        msg_general = self.get_mvp_general()
        
        # Add prompts to flame if mechanics are garbage
        if msg_bad_cc:
            mvplist = mvplist + msg_bad_cc + "\n" 
            
        if msg_shockwave_hit:
            mvplist = mvplist + msg_shockwave_hit + "\n" 
            
        if msg_big_tornado:
            mvplist = mvplist + msg_big_tornado + "\n" 
            
        if msg_bad_boons:
            mvplist = mvplist + msg_bad_boons

        if msg_general:
            mvplist = mvplist + msg_general 
        
        # Return full list
        return mvplist
    
    def get_lvp(self):
        # Create LVP prompt
        lvplist = "\n**LVPs** \n"
        
        # Check for mechanics
        msg_good_cc = self.get_lvp_cc_boss_PMA()
        msg_good_dps = self.get_lvp_dps_PMA()
        msg_good_bdps = self.get_lvp_bdps_PMA()
        msg_general = self.get_lvp_general('Full Fight')
        
        # Add prompts to praise if mechanics are bussin fr fr
        if msg_good_cc:
            lvplist = lvplist + msg_good_cc + "\n" 
    
        if msg_good_dps:
            lvplist = lvplist + msg_good_dps + "\n" 

        if msg_good_bdps:
            lvplist = lvplist + msg_good_bdps + "\n" 

        if msg_general:
            lvplist = lvplist + msg_general + "\n" 
        
        # Return full list    
        return lvplist

    ################################ MVP ################################
    
    # Flame the people that got hit by shockwave and downed
    def mvp_sabir_shockwave(self):
        i_players = self.get_sabir_shockwave()
        # Return necessary flame
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["MVP SABIR SHOCKWAVE"].format(mvp_names=mvp_names)
        return

    # Flame the people that went into orange tornadoes        
    def mvp_sabir_big_tornado(self):
        i_players = self.get_sabir_big_tornado()
        # Return necessary flame
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["MVP SABIR BIG TORNADO"].format(mvp_names=mvp_names)
        return
    
    ################################ LVP ################################
    
    
    
    ################################ CONDITIONS ################################
    
    # Check if player got hit by Sabir Shockwave
    def got_sabir_shockwave(self, i_player: int):
        return self.get_mech_value(i_player, "Shockwave Hit") > 0
    
    # Check if player got hit by orange tornadoes
    def got_sabir_big_tornado(self, i_player: int):
        # Check if player died on platforms (between phases) with tornadoes and picked the orange one
        try:
            # I got depression trying to figure out how to work this and there might be a better way but holy fuck
            died_offphase = self.log.pjcontent['players'][i_player]['deathRecap'][0]['toKill'][0]['id']
            if died_offphase == 23288:
                return True
            return False
        except:
            # Otherwise, check if player got hit by the big orange tornado on platform in the last phase
            return self.get_mech_value(i_player, "Big Tornado Hit") > 0
    
    ################################ DATA MECHAS ################################
    
    # Collect all the greeders that AFK'ed during shockwave
    def get_sabir_shockwave(self):
        greeder = []
        for i in self.player_list:
            if self.got_sabir_shockwave(i):
                greeder.append(i)
        return greeder
        
    # Collect all the peepos that wanted to end it all by orange tornado    
    def get_sabir_big_tornado(self):
        clueless = []
        for i in self.player_list:
            if self.got_sabir_big_tornado(i):
                clueless.append(i)
        return clueless

################################ QTP ################################

class QTP(Boss):
    
    last    = None
    name    = "QTP"
    wing    = 7
    boss_id = 22000

    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        QTP.last = self
        
    def get_mvp(self):
        # Create MVP prompt
        mvplist = "**MVPs** \n"
        
        # Check for mechanics
        msg_bad_dps = self.get_bad_dps(extra_exclude=[self.is_pylon])
        msg_cc = self.get_mvp_cc_total(extra_exclude=[self.is_pylon])
        msg_tanked_arrow = self.mvp_qtp_arrow_hit()
        msg_lightning_hit = self.mvp_qtp_lightning_hit()
        msg_bad_boons = self.get_bad_boons('Full Fight', exclude=[self.is_pylon])
        msg_general = self.get_mvp_general()
        
        # Add prompts to flame if mechanics are garbage
        if msg_bad_dps:
            mvplist = mvplist + msg_bad_dps + "\n" 
        
        if msg_cc:
            mvplist = mvplist + msg_cc + "\n" 
            
        if msg_tanked_arrow:
            mvplist = mvplist + msg_tanked_arrow + "\n" 
            
        if msg_lightning_hit:
            mvplist = mvplist + msg_lightning_hit + "\n" 
            
        if msg_bad_boons:
            mvplist = mvplist + msg_bad_boons

        if msg_general:
            mvplist = mvplist + msg_general

        # Return full list         
        return mvplist
    
    def get_lvp(self):
        # Create LVP prompt
        lvplist = "\n**LVPs** \n"
        
        # Check for mechanics
        msg_cc = self.get_lvp_cc_total()
        msg_lifted_twice = self.lvp_qtp_lifted_twice()
        msg_took_orb = self.lvp_qtp_took_orb()
        msg_kiters = self.lvp_qtp_kiters()
        msg_general = self.get_lvp_general('Full Fight', exclude=[self.is_pylon])
        
        # Add prompts to praise if mechanics are bussin fr fr
        if msg_cc:
            lvplist = lvplist + msg_cc + "\n" 
            
        if msg_lifted_twice:
            lvplist = lvplist + msg_lifted_twice + "\n" 
            
        if msg_took_orb:
            lvplist = lvplist + msg_took_orb + "\n" 

        if msg_kiters:
            lvplist = lvplist + msg_kiters + "\n" 

        if msg_general:
            lvplist = lvplist + msg_general + "\n" 
        
        # Return full list         
        return lvplist

    # This is old code, corrects for alac uptime without kiters i think
    def is_alac(self, i_player: int):
        min_alac_contrib     = 30
        alac_id              = 30328
        boon_path            = self.log.pjcontent['players'][i_player].get("groupBuffsActive")
        player_alac_contrib  = 0
        pylon_players_in_sub = []
        if boon_path:
            for boon in boon_path:
                if boon["id"] == alac_id:
                    player_alac_contrib = boon["buffData"][self.real_phase_id]["generation"]
            pylon_players_in_sub = [i for i in self.player_list if self.is_pylon(i) and self.get_player_group(i_player) == self.get_player_group(i)]
        corrected_uptime = player_alac_contrib * 5 / (4 - len(pylon_players_in_sub))
        return corrected_uptime >= min_alac_contrib
    
    # This is old code, corrects for quick uptime without kiters i think
    def is_quick(self, i_player: int):
        min_quick_contrib    = 30
        quick_id             = 1187
        boon_path            = self.log.pjcontent['players'][i_player].get("groupBuffsActive")
        player_quick_contrib = 0
        pylon_players_in_sub = []
        if boon_path:
            for boon in boon_path:
                if boon["id"] == quick_id:
                    player_quick_contrib = boon["buffData"][self.real_phase_id]["generation"]
            pylon_players_in_sub = [i for i in self.player_list if self.is_pylon(i) and self.get_player_group(i_player) == self.get_player_group(i)]
        corrected_uptime = player_quick_contrib * 5 / (4 - len(pylon_players_in_sub))
        return corrected_uptime >= min_quick_contrib

    # This is old code, idk ??? not even used here
    def get_dps_ranking(self):
        return self._get_dps_contrib([self.is_support, self.is_pylon])

    ################################ MVP ################################
    
    # Flame the people that got hit by arrow
    def mvp_qtp_arrow_hit(self):
        i_players = self.get_qtp_arrow_hit()
        # Return necessary flame
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["MVP QTP ARROW HIT"].format(mvp_names=mvp_names)
        return
    
    # Flame the people that got hit by the 3 orange circles that expand in size each time
    def mvp_qtp_lightning_hit(self):
        i_players = self.get_qtp_lightning_hit()
        # Return necessary flame
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["MVP QTP LIGHTNING HIT"].format(mvp_names=mvp_names)
        return
    
    ################################ LVP ################################
    
    # Praise the people that got unlucky and lifted multiple times
    def lvp_qtp_lifted_twice(self):
        i_players = self.get_qtp_lifted_twice()
        # Return necessary praise
        if i_players:
            self.add_lvps(i_players)
            lvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["LVP QTP LIFTED"].format(lvp_names=lvp_names)
        return
    
    # Praise the people that backed up the orb when pylon kiters got cancer and couldn't do it   
    def lvp_qtp_took_orb(self):
        i_players = self.get_qtp_took_orb()
        # Return necessary praise
        if i_players:
            self.add_lvps(i_players)
            lvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["LVP QTP ORB BACKUP"].format(lvp_names=lvp_names)
        return
    
    # Praise the kiters 
    def lvp_qtp_kiters(self):
        i_players = self.get_qtp_kiters()
        # Return necessary praise
        if i_players:
            self.add_lvps(i_players)
            lvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["LVP QTP KITERS"].format(lvp_names=lvp_names)
        return
    
    ################################ CONDITIONS ################################
    
    # Old code, Check if player is pylon kiter
    def is_pylon(self, i_player: int):
        return self.get_orb_caught(i_player) > 1
    
    # Check if player got lifted multiple times
    def got_lifted_twice(self, i_player: int):
        return self.get_mech_value(i_player, "Player lifted up") > 1 
    
    # Check if player got hit by arrow
    def got_arrow_hit(self, i_player: int):
        return self.get_mech_value(i_player, "Aimed Projectile") > 0
    
    # Check if player backed up the orb when kiters couldn't take it
    def got_orb_backup(self, i_player: int):
        if not self.is_pylon(i_player):
            return self.get_mech_value(i_player, "Critical Mass") > 0
        return False
    
    # Check if player got hit by the 3 orange circle aoes that expand in size each time 
    def got_lightning_hit(self, i_player: int):
        return self.get_mech_value(i_player, "Lightning Hit") > 0
    
    ################################ DATA MECHAS ################################

    # Old code, collects pylon people
    def get_orb_caught(self, i_player: int):
        return self.get_mech_value(i_player, "Critical Mass")
    
    # Collect all people who got lift up multiple times (I guess there can only be 1, I didn't think when I wrote this OK?)
    def get_qtp_lifted_twice(self):
        unlucky = []
        for i in self.player_list:
            if self.got_lifted_twice(i):
                unlucky.append(i)
        return unlucky
    
    # Collect all the people who got hit by the arrow (not cleaved, but when they were targeted and got hit)  
    def get_qtp_arrow_hit(self):
        no_jump = []
        for i in self.player_list:
            if self.got_arrow_hit(i):
                no_jump.append(i)
        return no_jump
    
    # Collect all the gamers who backed up the pylon by taking the orb    
    def get_qtp_took_orb(self):
        backup = []
        for i in self.player_list:
            if self.got_orb_backup(i):
                backup.append(i)
        return backup
    
    # Collect all the AFK players who got hit by 3 orange circles that expand in size each time
    def get_qtp_lightning_hit(self):
        afk_players = []
        for i in self.player_list:
            if self.got_lightning_hit(i):
                afk_players.append(i)
        return afk_players
    
    # Collect all the kiters
    def get_qtp_kiters(self):
        deadeyes = []
        for i in self.player_list:
            if self.is_pylon(i):
                deadeyes.append(i)
        return deadeyes
    
################################ GREER ################################

class GREER(Boss):
    
    last    = None
    name    = "GREER"
    wing    = 8
    boss_id = 26725

    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        GREER.last = self
        
    def get_mvp(self):
        # Create MVP prompt
        mvplist = "**MVPs** \n"
        
        # Check for mechanics
        msg_bad_dps = self.get_bad_dps()
        msg_corrupted = self.mvp_greer_corrupted()
        msg_got_hit_on_cc = self.mvp_greer_cc_hit()
        msg_knockback = self.mvp_greer_knockback()
        msg_bad_boons = self.get_bad_boons('Full Fight')
        msg_general = self.get_mvp_general()
        
        # Add prompts to flame if mechanics are garbage
        if msg_bad_dps:
            mvplist = mvplist + msg_bad_dps + "\n" 
            
        if msg_corrupted:
            mvplist = mvplist + msg_corrupted + "\n" 
            
        if msg_got_hit_on_cc:
            mvplist = mvplist + msg_got_hit_on_cc + "\n" 
            
        if msg_knockback:
            mvplist = mvplist + msg_knockback + "\n" 
            
        if msg_bad_boons:
            mvplist = mvplist + msg_bad_boons

        if msg_general:
            mvplist = mvplist + msg_general 
        
        # Return full list          
        return mvplist
    
    def get_lvp(self):
        # Create LVP prompt
        lvplist = "\n**LVPs** \n"
        
        # Check for mechanics
        msg_good_dps = self.get_lvp_dps_PMA(3)
        msg_good_cc = self.get_lvp_cc_total()
        msg_good_cleave = self.lvp_greer_cleave()
        msg_reflect_distort_placeholder = self.lvp_greer_reflect()
        msg_good_bdps = self.get_lvp_bdps_PMA(3)
        msg_general = self.get_lvp_general('Full Fight')
        
        # Add prompts to praise if mechanics are bussin fr fr
        if msg_good_dps:
            lvplist = lvplist + msg_good_dps + "\n" 

        if msg_good_bdps:
            lvplist = lvplist + msg_good_bdps + "\n" 
            
        if msg_good_cc:
            lvplist = lvplist + msg_good_cc + "\n" 
            
        if msg_good_cleave:
            lvplist = lvplist + msg_good_cleave + "\n"
            
        if msg_reflect_distort_placeholder:
            lvplist = lvplist + msg_reflect_distort_placeholder + "\n"

        if msg_general:
            lvplist = lvplist + msg_general + "\n"
        
        # Return full list  
        return lvplist

    ################################ MVP ################################
    
    # Flame the people that got hit by a corrupting attack at least 3 times
    def mvp_greer_corrupted(self):
        i_players = self.get_greer_corrupted()
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            number_mvp = len(i_players)
            if number_mvp == 1:
                return LANGUES["selected_language"]["MVP GREER CORRUPTED S"].format(mvp_names=mvp_names)
            else:
                return LANGUES["selected_language"]["MVP GREER CORRUPTED P"].format(mvp_names=mvp_names)
        return
    
    # Flame the people that AFK and get hit by many orange aoes while Greer is in CC phase (based on squad average)
    def mvp_greer_cc_hit(self):
        i_players = self.get_greer_cc_hit()
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["MVP GREER CC HIT"].format(mvp_names=mvp_names)
        return
    
    # Flame the people that get hit by an attack that knocks back more than 10 times
    def mvp_greer_knockback(self):
        i_players = self.get_greer_knockback()
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["MVP GREER KNOCKBACK"].format(mvp_names=mvp_names)
        return
    
    ################################ LVP ################################
    
    # Praise the people who are trying to cleave the small adds
    def lvp_greer_cleave(self):
        i_players = []
        for i in self.player_list:
            if self.is_heal(i):
                continue
            boss_total = self.log.pjcontent['players'][i]['dpsTargets'][0][self.real_phase_id]['damage']
            boss_total = boss_total + self.log.pjcontent['players'][i]['dpsTargets'][1][self.real_phase_id]['damage']
            boss_total = boss_total + self.log.pjcontent['players'][i]['dpsTargets'][2][self.real_phase_id]['damage']
            
            cleave_total = self.log.pjcontent['players'][i]['dpsAll'][0]['damage']

            if cleave_total / boss_total > 1.03:
                i_players.append(i)
        if(len(i_players))>0:
            self.add_lvps(i_players)
            lvp_names = self.players_to_string(i_players)   
            return LANGUES["selected_language"]["LVP GREER CLEAVE"].format(lvp_names=lvp_names)
        return
    
    # Praise the people who reflect/destroy projs
    def lvp_greer_reflect(self):
        i_players = self.get_greer_reflect()
        if(len(i_players))>0:
            self.add_lvps(i_players)
            lvp_names = self.players_to_string(i_players)  
            return LANGUES["selected_language"]["LVP GREER REFLECT"].format(lvp_names=lvp_names)
    
    ################################ CONDITIONS ################################
    
    # Check if player got corrupted more than 3 times
    def got_greer_corrupted(self, i_player: int):
        politics = self.get_mech_value(i_player, "Wave of Corruption Hit")
        politics = politics + self.get_mech_value(i_player, "Enfeebling Miasma Hit")
        politics = politics + self.get_mech_value(i_player, "Noxious Blight Hit")
        politics = politics + self.get_mech_value(i_player, "Rot Eruption Hit")
        if politics > 3:
            return True
        else:
            return False
    
    # Check if player took more than (1.2xSquad Average) hits from orange AoEs during Greer CC phase   
    def got_greer_cc_hit(self, i_player: int):
        total_hits = 0
        for i in self.player_list:
            total_hits = total_hits + self.get_mech_value(i, "Rot the World Hit")
        average_hit = total_hits / (i + 1)
        player_hit = self.get_mech_value(i_player, "Rot the World Hit")
        if player_hit > 1.2 * average_hit:
            return True
        else:
            return 
    
    # Check if player got hit by an attack that would knockback more than 10 times    
    def got_greer_knockback(self, i_player: int):
        afk_moment = self.get_mech_value(i_player, "Rake the Rot Hit")
        afk_moment = afk_moment + self.get_mech_value(i_player, "Sweep the Mold Hit")
        afk_moment = afk_moment + self.get_mech_value(i_player, "Cage of Decay Hit")
        afk_moment = afk_moment + self.get_mech_value(i_player, "Ripples of Rot Hit")
        if afk_moment > 10:
            return True
        else:
            return False
        
    # Check if player reflected/destroyed projectiles a ton
    def got_greer_reflect(self, i_player: int):
        # Go through the rotation
        for i in range(len(self.log.pjcontent['players'][i_player]['rotation'])):
            # Rev Bubble 
            if self.log.pjcontent['players'][i_player]['rotation'][i]['id'] == 29310:
                return i_player  
            # Feedback
            if self.log.pjcontent['players'][i_player]['rotation'][i]['id'] == 10302:
                return i_player  
            # CPC
            if self.log.pjcontent['players'][i_player]['rotation'][i]['id'] == 10689:
                return i_player  
            # Firebrand F3 bubble
            if self.log.pjcontent['players'][i_player]['rotation'][i]['id'] == 41836:
                return i_player  
            # Guard shield 5
            if self.log.pjcontent['players'][i_player]['rotation'][i]['id'] == 9091:
                return i_player  
            # Guard shield avenger utility
            if self.log.pjcontent['players'][i_player]['rotation'][i]['id'] == 9182:
                return i_player
            # Guard Wall
            if self.log.pjcontent['players'][i_player]['rotation'][i]['id'] == 9251:
                return i_player   
            # Add more whenever you feel like, i can think of a few but who uses those on greer lmao

        return
    
    ################################ DATA MECHAS ################################
    
    # Collect all the people that got corrupted
    def get_greer_corrupted(self):
        politicians = []
        for i in self.player_list:
            if self.got_greer_corrupted(i):
                politicians.append(i)
        return politicians 
    
    # Collect all the AFK people during Greer CC phase
    def get_greer_cc_hit(self):
        afk_players = []
        for i in self.player_list:
            if self.got_greer_cc_hit(i):
                afk_players.append(i)
        return afk_players 
    
    # Collect all the people that tank knockback attacks    
    def get_greer_knockback(self):
        afk_players = []
        for i in self.player_list:
            if self.got_greer_knockback(i):
                afk_players.append(i)
        return afk_players
    
    # Collect all the people that did a lot of reflect in the encounter    
    def get_greer_reflect(self):
        supports = []
        for i in self.player_list:
            if self.got_greer_reflect(i):
                supports.append(i)
        return supports
    
################################ DECIMA ################################

class DECIMA(Boss):
    
    last    = None
    name    = "DECIMA"
    wing    = 8
    boss_id = 26774

    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        DECIMA.last = self
        
        
    def get_mvp(self):
        # Create MVP prompt
        mvplist = "**MVPs** \n"
        
        # Check for mechanics
        msg_bad_dps = self.get_bad_dps()
        msg_took_red_arrow = self.mvp_decima_red_arrow()
        msg_no_greens = self.mvp_decima_greens()
        msg_green_greed = self.mvp_decima_green_greed()
        msg_bad_boons = self.get_bad_boons('Full Fight')
        msg_general = self.get_mvp_general()
        
        # Add prompts to flame if mechanics are garbage
        if msg_bad_dps:
            mvplist = mvplist + msg_bad_dps + "\n" 
            
        if msg_took_red_arrow:
            mvplist = mvplist + msg_took_red_arrow + "\n" 
            
        if msg_no_greens:
            mvplist = mvplist + msg_no_greens + "\n" 
            
        if msg_green_greed:
            mvplist = mvplist + msg_green_greed + "\n" 
            
        if msg_bad_boons:
            mvplist = mvplist + msg_bad_boons

        if msg_general:
            mvplist = mvplist + msg_general 
        
        # Return full list
        return  mvplist
    
    def get_lvp(self):
        # Create LVP prompt
        lvplist = "\n**LVPs** \n"
        
        # Check for mechanics
        msg_good_dps = self.get_lvp_dps_PMA()
        msg_good_cc = self.get_lvp_cc_total()
        msg_good_greens = self.lvp_decima_collect_greens()
        msg_good_bdps = self.get_lvp_bdps_PMA()
        msg_general = self.get_lvp_general('Full Fight')
        
        # Add prompts to praise if mechanics are bussin fr fr
        if msg_good_dps:
            lvplist = lvplist + msg_good_dps + "\n" 

        if msg_good_bdps:
            lvplist = lvplist + msg_good_bdps + "\n" 
            
        if msg_good_cc:
            lvplist = lvplist + msg_good_cc + "\n" 
            
        if msg_good_greens:
            lvplist = lvplist + msg_good_greens + "\n" 

        if msg_general:
            lvplist = lvplist + msg_general + "\n" 
        
        # Return full list
        return lvplist

    ################################ MVP ################################
    
    # Flame people who do less than (5% Squad Average) CC
    def mvp_decima_cc(self, extra_exclude: list[classmethod]=[]):
        players = self.player_list
        total_cc = 0
        i_players = []
        for i in players:
            total_cc = total_cc + self.get_cc_boss(i)
        
        for i in players:
            if self.get_cc_boss(i) < 0.05 * total_cc:
                i_players.append(i)
           
        self.add_mvps(i_players)  
        mvp_names  = self.players_to_string(i_players)
        number_mvp = len(i_players)
        if number_mvp == 1:
            return LANGUES["selected_language"]["MVP DECIMA CC S"].format(mvp_names=mvp_names)
        else:
            return LANGUES["selected_language"]["MVP DECIMA CC P"].format(mvp_names=mvp_names)
    
    # Flame people who took the red arrow over the main red arrow kiter    
    def mvp_decima_red_arrow(self):
        i_players = self.get_accidental_kiter()
        self.add_mvps(i_players)
        if i_players:
            mvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["MVP DECIMA ACCIDENTAL KITER"].format(mvp_names=mvp_names)
        return
    
    # Flame the people who do less than 6 ticks of Green during Phase 2 & 3 excluding kiters    
    def mvp_decima_greens(self):
        i_players = self.get_decima_greens()
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            number_mvp = len(i_players)
            if number_mvp == 1:
                return LANGUES["selected_language"]["MVP DECIMA NO GREEN S"].format(mvp_names=mvp_names)
            else:
                return LANGUES["selected_language"]["MVP DECIMA NO GREEN P"].format(mvp_names=mvp_names)
        return
    
    # Flame the people who take more greens in Phase 1, Split 1, Split 2 compared to Phase 2 & 3 excluding kiters. Extra flame if there is only 1 person
    def mvp_decima_green_greed(self):
        i_players = self.get_decima_green_greed()
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            number_mvp = len(i_players)
            if number_mvp == 1:
                greens_done = self.get_mech_value(i_players[0], "Absorbed Tier 1 Green", "Phase 2")
                greens_done = greens_done + self.get_mech_value(i_players[0], "Absorbed Tier 2 Green", "Phase 2")
                greens_done = greens_done + self.get_mech_value(i_players[0], "Absorbed Tier 3 Green", "Phase 2")
                greens_done = greens_done + self.get_mech_value(i_players[0], "Absorbed Tier 1 Green", "Phase 3")
                greens_done = greens_done + self.get_mech_value(i_players[0], "Absorbed Tier 2 Green", "Phase 3")
                greens_done = greens_done + self.get_mech_value(i_players[0], "Absorbed Tier 3 Green", "Phase 3")
        
                off_phase_greens = self.get_mech_value(i_players[0], "Absorbed Tier 1 Green", "Phase 1")
                off_phase_greens = off_phase_greens + self.get_mech_value(i_players[0], "Absorbed Tier 2 Green", "Phase 1")
                off_phase_greens = off_phase_greens + self.get_mech_value(i_players[0], "Absorbed Tier 3 Green", "Phase 1")
                off_phase_greens = off_phase_greens + self.get_mech_value(i_players[0], "Absorbed Tier 1 Green", "Split 1")
                off_phase_greens = off_phase_greens + self.get_mech_value(i_players[0], "Absorbed Tier 2 Green", "Split 1")
                off_phase_greens = off_phase_greens + self.get_mech_value(i_players[0], "Absorbed Tier 3 Green", "Split 1")
                off_phase_greens = off_phase_greens + self.get_mech_value(i_players[0], "Absorbed Tier 1 Green", "Split 2")
                off_phase_greens = off_phase_greens + self.get_mech_value(i_players[0], "Absorbed Tier 2 Green", "Split 2")
                off_phase_greens = off_phase_greens + self.get_mech_value(i_players[0], "Absorbed Tier 3 Green", "Split 2")
                greed_ratio = greens_done/off_phase_greens * 100
                return LANGUES["selected_language"]["MVP DECIMA GREEN GREED S"].format(mvp_names=mvp_names, green_ratio=greed_ratio)
            else:
                return LANGUES["selected_language"]["MVP DECIMA GREEN GREED P"].format(mvp_names=mvp_names)
        return
    
    ################################ LVP ################################
    
    # Praise people who collect more than (20% Squad) Greens
    def lvp_decima_collect_greens(self):
        max_greens = 0
        total_greens = 0
        i_tracked = -1
        for i in self.player_list:
            total_greens = total_greens + self.get_mech_value(i, "Absorbed Tier 1 Green")
            total_greens = total_greens + self.get_mech_value(i, "Absorbed Tier 2 Green")
            total_greens = total_greens + self.get_mech_value(i, "Absorbed Tier 3 Green")
            
            current_greens = self.get_mech_value(i, "Absorbed Tier 1 Green")
            current_greens = current_greens + self.get_mech_value(i, "Absorbed Tier 2 Green")
            current_greens = current_greens + self.get_mech_value(i, "Absorbed Tier 3 Green")
            if current_greens > max_greens:
                max_greens = current_greens
                i_players = self.get_player_name(i)
                i_tracked = i
        
        if total_greens == 0:
            return
        green_ratio = max_greens / total_greens * 100                     
        if green_ratio > 20:
            self.add_lvps([i_tracked])
            return LANGUES["selected_language"]["LVP DECIMA GREEN"].format(lvp_names=i_players, greens=max_greens, ratio=green_ratio)
        return
    
    ################################ CONDITIONS ################################
    
    # Check is non red arrow kiter person took the red arrow
    def got_red_arrow(self, i_player: int):
        max_red_arrows = 0
        for i in self.player_list:
            if self.get_mech_value(i, "Fluxlance (Red Arrow)") > max_red_arrows:
                max_red_arrows = self.get_mech_value(i, "Fluxlance (Red Arrow)")
        red_arrow = self.get_mech_value(i_player, "Fluxlance (Red Arrow)")
        if red_arrow > 0 and red_arrow < max_red_arrows:
            return True
        else:
            return False
    
    # Check if person is doing less than 6 ticks of Green in Phase 2 & 3 besides kiters
    def got_no_greens(self, i_player: int):
        kiter_check = self.get_mech_value(i_player, "Fluxlance Fusillade Hit")
        kiter_check = kiter_check + self.get_mech_value(i_player, "Fluxlance Salvo Hit")
        if kiter_check > 3:
            return False
            
        greens_done = 0
        greens_done = greens_done + self.get_mech_value(i_player, "Absorbed Tier 1 Green", "Phase 2")
        greens_done = greens_done + self.get_mech_value(i_player, "Absorbed Tier 2 Green", "Phase 2")
        greens_done = greens_done + self.get_mech_value(i_player, "Absorbed Tier 3 Green", "Phase 2")
        greens_done = greens_done + self.get_mech_value(i_player, "Absorbed Tier 1 Green", "Phase 3")
        greens_done = greens_done + self.get_mech_value(i_player, "Absorbed Tier 2 Green", "Phase 3")
        greens_done = greens_done + self.get_mech_value(i_player, "Absorbed Tier 3 Green", "Phase 3")
        
        if greens_done < 6:
            return True
        else:
            return False
    
    # Check if person collects more greens in Phase 1, Split 1, Split 2 compared to Phase 2 & 3 except kiters    
    def got_green_greed(self, i_player: int):
        kiter_check = self.get_mech_value(i_player, "Fluxlance Fusillade Hit")
        kiter_check = kiter_check + self.get_mech_value(i_player, "Fluxlance Salvo Hit")
        if kiter_check > 3:
            return False
            
        greens_done = 0
        greens_done = greens_done + self.get_mech_value(i_player, "Absorbed Tier 1 Green", "Phase 2")
        greens_done = greens_done + self.get_mech_value(i_player, "Absorbed Tier 2 Green", "Phase 2")
        greens_done = greens_done + self.get_mech_value(i_player, "Absorbed Tier 3 Green", "Phase 2")
        greens_done = greens_done + self.get_mech_value(i_player, "Absorbed Tier 1 Green", "Phase 3")
        greens_done = greens_done + self.get_mech_value(i_player, "Absorbed Tier 2 Green", "Phase 3")
        greens_done = greens_done + self.get_mech_value(i_player, "Absorbed Tier 3 Green", "Phase 3")
        
        off_phase_greens = 0
        off_phase_greens = off_phase_greens + self.get_mech_value(i_player, "Absorbed Tier 1 Green", "Phase 1")
        off_phase_greens = off_phase_greens + self.get_mech_value(i_player, "Absorbed Tier 2 Green", "Phase 1")
        off_phase_greens = off_phase_greens + self.get_mech_value(i_player, "Absorbed Tier 3 Green", "Phase 1")
        off_phase_greens = off_phase_greens + self.get_mech_value(i_player, "Absorbed Tier 1 Green", "Split 1")
        off_phase_greens = off_phase_greens + self.get_mech_value(i_player, "Absorbed Tier 2 Green", "Split 1")
        off_phase_greens = off_phase_greens + self.get_mech_value(i_player, "Absorbed Tier 3 Green", "Split 1")
        off_phase_greens = off_phase_greens + self.get_mech_value(i_player, "Absorbed Tier 1 Green", "Split 2")
        off_phase_greens = off_phase_greens + self.get_mech_value(i_player, "Absorbed Tier 2 Green", "Split 2")
        off_phase_greens = off_phase_greens + self.get_mech_value(i_player, "Absorbed Tier 3 Green", "Split 2")
        
        if greens_done < (off_phase_greens / 3):
            return True
        else:
            return False
            
    ################################ DATA MECHAS ################################
    
    # Collect the people that took the red arrow when they shouldn't have
    def get_accidental_kiter(self):
        bad_kiter = []
        for i in self.player_list:
            if self.got_red_arrow(i):
                bad_kiter.append(i)
        return bad_kiter  
    
    # Collect the people that do less than 6 green ticks in Phase 2 & 3 except kiters
    def get_decima_greens(self):
        greenless = []
        for i in self.player_list:
            if self.got_green_greed(i):
                continue
            if self.got_no_greens(i):
                greenless.append(i)
        return greenless  
     
    # Collect the people who do more greens in Phase 1, Split 1, Split 2 compared to Phase 2 & 3 except kiters         
    def get_decima_green_greed(self):
        green_greed = []
        for i in self.player_list:
            if self.got_green_greed(i):
                green_greed.append(i)
        return green_greed  
    
################################ URA ################################

class URA(Boss):
    
    last    = None
    name    = "URA"
    wing    = 8
    boss_id = 26712
    
    scaler  = 1#20.10672962

    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        URA.last = self
        
    def get_mvp(self):
        # Create MVP prompt
        mvplist = "**MVPs** \n"
        
        # Check for Mechanics
        msg_bad_dps = self.get_bad_dps()
        msg_ura_Shard = self.mvp_ura_Shard()
        msg_ura_SAK = self.mvp_ura_SAK()
        # !!! Voided until I can fix the code !!!   
        #msg_ura_Prison = self.mvp_ura_Prison()
        msg_ura_Exposed = self.mvp_ura_Exposed()
        msg_bad_boons = self.get_bad_boons('Full Fight')
        msg_general = self.get_mvp_general()
        
        # Add prompts to flame if mechanics are garbage
        if msg_ura_Shard:
            mvplist = mvplist + msg_ura_Shard + "\n" 
            
        if msg_ura_SAK:
            mvplist = mvplist + msg_ura_SAK + "\n" 

        # !!! Voided until I can fix the code !!!           
        #if msg_ura_Prison:
        #    mvplist = mvplist + msg_ura_Prison + "\n" 

        if msg_ura_Exposed:
            mvplist = mvplist + msg_ura_Exposed + "\n"
            
        if msg_bad_dps:
            mvplist = mvplist + msg_bad_dps + "\n" 
            
        if msg_bad_boons:
            mvplist = mvplist + msg_bad_boons

        if msg_general:
            mvplist = mvplist + msg_general 
        
        # Return full list
        return  mvplist
    
    def get_lvp(self):
        # Create LVP prompt
        lvplist = "\n**LVPs** \n"
        
        # Check for Mechanics
        msg_good_dps = self.get_lvp_dps_PMA()
        msg_titanspawn = self.lvp_ura_titanspawn()
        msg_good_bdps = self.get_lvp_bdps_PMA()
        msg_general = self.get_lvp_general('Full Fight')
        
        # Add prompts to praise if mechanics are bussin fr fr
        if msg_good_dps:
            lvplist = lvplist + msg_good_dps + "\n" 

        if msg_good_bdps:
            lvplist = lvplist + msg_good_bdps + "\n" 
            
        if msg_titanspawn:
            lvplist = lvplist + msg_titanspawn + "\n" 

        if msg_general:
            lvplist = lvplist + msg_general + "\n" 
        
        # Return full list
        return lvplist
        

    ################################ MVP ################################
    
    # Flame the people that don't use any Dispel (SAK)
    def mvp_ura_SAK(self):
        i_players = self.get_ura_SAK()
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            if len(i_players) == 1:
                return LANGUES["selected_language"]["URA MVP SAK S"].format(mvp_names=mvp_names)
            if len(i_players) > 1:
                return LANGUES["selected_language"]["URA MVP SAK P"].format(mvp_names=mvp_names)
        return

    # Flame the people that never pick up any bloodstone shards
    def mvp_ura_Shard(self):
        i_players = self.get_ura_Shard()
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            if len(i_players) == 1:
                return LANGUES["selected_language"]["URA MVP SHARD S"].format(mvp_names=mvp_names)
            if len(i_players) > 1:
                return LANGUES["selected_language"]["URA MVP SHARD P"].format(mvp_names=mvp_names)
        return  
    
    # VOIDED FUNCTION FOR NOW!!! Flame the people who trap others in steam prison
    def mvp_ura_Prison(self):
        i_players = self.get_terrorists()
        self.add_mvps(i_players)
        if i_players:
            mvp_names = self.players_to_string(i_players)
            return LANGUES["selected_language"]["URA MVP PRISON"].format(mvp_names=mvp_names)
        return
    
    # Flame the people that get more than 4 exposed stacks
    def mvp_ura_Exposed(self):
        i_players = self.get_ura_Exposed()
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            if len(i_players) == 1:
                return LANGUES["selected_language"]["URA MVP EXPOSED S"].format(mvp_names=mvp_names)
            if len(i_players) > 1:
                return LANGUES["selected_language"]["URA MVP EXPOSED P"].format(mvp_names=mvp_names)
        return  
    
    ################################ LVP ################################
    
    # Praise the person who does more than (30% Squad) CC on off targets (Titanspawn, geyser, etc) and has the highest CC in this regard
    def lvp_ura_titanspawn(self):
        players = self.player_list
        cc_god = ""
        titanspawn_cc = 0
        titanspawn_cc_total = 0
        i_tracked = -1
        for i in players:
            cc_dif = self.get_cc_total(i) - self.get_cc_boss(i)
            titanspawn_cc_total = titanspawn_cc_total + cc_dif
            if cc_dif > titanspawn_cc:
                titanspawn_cc = cc_dif
                cc_god = "__" + self.get_player_name(i) + "__"
                i_tracked = i
        
        cc_ratio = titanspawn_cc / titanspawn_cc_total * 100
        if titanspawn_cc > 0.3 * titanspawn_cc_total:
            self.add_lvps([i_tracked])
            return LANGUES["selected_language"]["URA LVP TITANSPAWN CC"].format(lvp_names=cc_god, max_cc=titanspawn_cc, cc_ratio=cc_ratio)
        return
    
    ################################ CONDITIONS ################################
    
    # Check if SAK was never used
    def ura_no_SAK(self, i_player: int):
        return self.get_mech_value(i_player, "Used Dispel") < 1    
    
    # Check if no shard was picked
    def ura_no_Shard(self, i_player: int):
        return self.get_mech_value(i_player, "Bloodstone Shard Pick-up") < 1   

    # VOIDED FUNCTION FOR NOW !!! Check if player is trapping others in the Steam Prison
    def is_terrorist(self, i_player: int):
        prison_history = self.get_mech_value(i_player, "Steam Prison Target")
        players = self.player_list
        player_name  = self.get_player_name(i_player)
        if prison_history:
            history      = []
            mech_history = self.log.pjcontent['mechanics']
            for mech in mech_history:
                for data in mech['mechanicsData']:
                    if data['actor'] == player_name:
                        if mech['name'] == "Ste.Prison.T":
                            Prison_time = data['time'] + 3000
                            Stuck_time = data['time'] + 4500
                            time_index = time_to_index(Prison_time, self.time_base)  
                            time_index_2 = time_to_index(Stuck_time, self.time_base)
                            
                            try:
                                bomb_pos = self.get_player_pos(i_player)[time_index]                                
                            except:
                                continue

                            
                            for i in players:
                                if i == i_player or self.is_dead(i):
                                    continue
                                try:
                                    i_pos = self.get_player_pos(i)[time_index_2]
                                    
                                except:
                                    return False
                                if get_dist(bomb_pos, i_pos) * URA.scaler <= 60:
                                    return True
        return False        
    
    # Check if player got more than 4 exposed stacks
    def is_ura_Exposed(self, i_player: int):
        return self.get_mech_value(i_player, "Exposed Applied") > 4 
    
    ################################ DATA MECHAS ################################
    
    # Collect all the people that don't use SAK
    def get_ura_SAK(self):
        no_SAK = []
        for i in self.player_list:
            if self.ura_no_SAK(i) and self.ura_no_Shard(i):
                continue
            if self.ura_no_SAK(i):
                no_SAK.append(i)
        return no_SAK  

    # Collect all the people that don't pick up shards
    def get_ura_Shard(self):
        no_Shard = []
        for i in self.player_list:
            if self.ura_no_Shard(i) and self.ura_no_SAK(i):
                no_Shard.append(i)
        return no_Shard  

    # VOIDED FUNCTION FOR NOW!!! Collect all the people that trapped others in Steam Prison
    def get_terrorists(self):
        terrotists = []
        for i in self.player_list:
            if self.is_terrorist(i):
                terrotists.append(i)
        return terrotists     

    # Collect all the people that got more than 4 exposed stacks
    def get_ura_Exposed(self):
        exposed = []
        for i in self.player_list:
            if self.is_ura_Exposed(i):
                exposed.append(i)
        return exposed         
    
################################ GOLEM CHAT STANDARD ################################

class GOLEM(Boss):
    
    last    = None
    name    = "GOLEM CHAT STANDARD"
    boss_id = 16199
    
    def __init__(self, log: Log):
        super().__init__(log)
        GOLEM.last = self