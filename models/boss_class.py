from datetime import datetime, timedelta, timezone
import requests
import pytz

from models.player_class import *
from const import ALL_PLAYERS, BOSS_DICT, CUSTOM_NAMES, BIG
from models.log_class import Log
import func
from languages import LANGUES

class Boss:  

    name       = None
    wing       = 0
    boss_id    = -1
    real_phase = "Full Fight"

    def __init__(self, log: Log):
        self.log                = log
        self.cm                 = self.is_cm()
        self.logName            = self.get_logName()
        self.mechanics          = self.get_mechanics()
        self.duration_ms        = self.get_duration_ms() 
        self.start_date         = self.get_start_date()
        self.end_date           = self.get_end_date()
        self.player_list        = self.get_player_list()
        self.wingman_time       = self.get_wingman_time()
        self.wingman_percentile = self.get_wingman_percentile()
        self.real_phase_id      = self.get_phase_id(self.real_phase)
        self.time_base          = self.get_time_base()
        self.mvp_accounts       = []
        self.lvp_accounts       = []
        for i in self.player_list:
            account = self.get_player_account(i)
            player  = ALL_PLAYERS.get(account)
            if not player:
                new_player           = Player(self, account)
                ALL_PLAYERS[account] = new_player
            else:
                player.add_boss(self)
                
    def __repr__(self) -> str:
        return self.log.url    
        
    ################################ Fonction pour attribus Boss ################################
    
    def is_cm(self):
        return self.log.pjcontent['isCM']
    
    def get_logName(self):
        return self.log.pjcontent['fightName']
    
    def get_mechanics(self):
        mechs        = []
        mechanic_map = self.log.jcontent['mechanicMap']
        for mechanic in mechanic_map:
            is_player_mechanic = mechanic['playerMech']
            if is_player_mechanic:
                mechs.append(mechanic)
                
        return mechs
    
    def get_duration_ms(self):
        return self.log.pjcontent['durationMS']
    
    def get_start_date(self):
        start_date_text = self.log.pjcontent['timeStartStd']
        date_format     = "%Y-%m-%d %H:%M:%S %z"
        start_date      = datetime.strptime(start_date_text, date_format)
        paris_timezone  = timezone(timedelta(hours=1))
        return start_date.astimezone(paris_timezone)
    
    def get_end_date(self):
        end_date_text  = self.log.pjcontent['timeEndStd']
        date_format    = "%Y-%m-%d %H:%M:%S %z"
        end_date       = datetime.strptime(end_date_text, date_format)
        paris_timezone = timezone(timedelta(hours=1))
        return end_date.astimezone(paris_timezone)

    def get_wingman_time(self):
        # return None
        w_boss_id = self.boss_id * (-1) ** self.cm
        url       = f"https://gw2wingman.nevermindcreations.de/api/boss?era=latest&bossID={w_boss_id}"
        r         = requests.get(url)
        if not r.ok:
            print("wingman faled")
            print(r.status_code)
            print(r.content)
            return None
        data = r.json()
        if data.get("error"):
            print("wingman failed")
            print(data["error"])
            return None
        return [data["duration_med"], data["duration_top"]]
    
    def get_player_list(self):
        real_players = []
        players      = self.log.pjcontent['players']
        for i_player, player in enumerate(players):
            if player['group'] < 50 and not self.is_buyer(i_player):
                real_players.append(i_player)
                
        return real_players
    
    def get_wingman_percentile(self):
        time_stamp = int(self.get_start_date().timestamp())
        requestUrl = f"https://gw2wingman.nevermindcreations.de/api/getPercentileByMetadata?bossID={self.boss_id}&isCM={self.cm}&duration={self.duration_ms}&timestamp={time_stamp}"
        infos      = requests.get(requestUrl).json()
        if infos.get("percentile"):
            return infos["percentile"]
        return                  
            
    ################################ CONDITIONS ################################

    def is_quick(self, i_player: int):
        min_quick_contrib    = 20
        quick_id             = 1187
        boon_path            = self.log.pjcontent['players'][i_player].get("groupBuffsActive")
        player_quick_contrib = 0
        if boon_path:
            for boon in boon_path:
                if boon["id"] == quick_id:
                    player_quick_contrib = boon["buffData"][self.real_phase_id]["generation"]
        return player_quick_contrib >= min_quick_contrib

    def is_alac(self, i_player: int):
        min_alac_contrib    = 20
        alac_id             = 30328
        boon_path           = self.log.pjcontent['players'][i_player].get("groupBuffsActive")
        player_alac_contrib = 0
        if boon_path:
            for boon in boon_path:
                if boon["id"] == alac_id:
                    player_alac_contrib = boon["buffData"][self.real_phase_id]["generation"]
        return player_alac_contrib >= min_alac_contrib

    def is_support(self, i_player: int):
        prof = self.log.pjcontent['players'][i_player]['profession']
        is_druid_supp = False
        delta = self.start_date - datetime(2022,7,17,23,0,0,tzinfo=pytz.FixedOffset(60))
        if prof == "Druid" and delta.total_seconds() < 0:
            is_druid_supp = True
        return self.is_quick(i_player) or self.is_alac(i_player) or is_druid_supp or self.is_bannerslave(i_player)
    
    def is_dps(self, i_player: int):
        return not self.is_support(i_player)
    
    def is_tank(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['toughness'] > 0
    
    def is_heal(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['healing'] > 0
    
    def is_dead(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['defenses'][0]['deadCount'] > 0
    
    def is_buyer(self, i_player: int):
        player_name = self.get_player_name(i_player)
        mechanics   = self.log.pjcontent.get('mechanics')
        if mechanics:
            death_history = [death for mech in mechanics if mech['name'] == "Dead" for death in mech['mechanicsData']]
            for death in death_history:
                if death['time'] < 20000 and death['actor'] == player_name:
                    return True
        try:
            rota = self.get_player_rotation(i_player)
        except:
            return True
        return False
    
    def is_buff_up(self, i_player: int, target_time: int, buff_name: str):
        buffmap = self.log.pjcontent['buffMap']
        buff_id = None
        for id, buff in buffmap.items():
            if buff['name'] == buff_name:
                buff_id = int(id[1:])
                break
        if buff_id is None:
            return False
        buffs = self.log.pjcontent['players'][i_player]['buffUptimes']
        for buff in buffs:
            if buff['id'] == buff_id:
                buffplot = buff['states']
                break
        xbuffplot = [pos[0] for pos in buffplot]
        ybuffplot = [pos[1] for pos in buffplot]
        
        left_value = None
        for time in xbuffplot:
            if time <= target_time:
                left_value = time
            else:
                break
        left_index = xbuffplot.index(left_value)
        if ybuffplot[left_index]:
            return True
        return False
    
    def is_dead_instant(self, i_player: int):
        downs_deaths = self.get_player_mech_history(i_player, ["Downed", "Dead"])
        if downs_deaths:
            if downs_deaths[-1]['name'] == "Dead":
                if len(downs_deaths) == 1:
                    return True
                if len(downs_deaths) > 1:
                    if downs_deaths[-2]['time'] < downs_deaths[-1]['time']-8000:
                        return True
        return False
    
    def is_condi(self, i_player: int):
        power_dmg = self.log.pjcontent['players'][i_player]['dpsAll'][0]['powerDamage']
        condi_dmg = self.log.pjcontent['players'][i_player]['dpsAll'][0]['condiDamage']
        return condi_dmg > power_dmg
    
    def is_power(self, i_player: int):
        return not self.is_condi(i_player)

    def is_bannerslave(self, i_player):
        delta = self.start_date - datetime(2022,7,17,23,0,0,tzinfo=pytz.FixedOffset(60))
        prof = self.log.pjcontent['players'][i_player]['profession']
        if prof == "Warrior" or prof == "Berserker" and delta.total_seconds() < 0:
            banner1 = 14449
            banner2 = 14417
            if self.log.pjcontent['players'][i_player].get('groupBuffs'):
                groupBuff = self.log.pjcontent['players'][i_player]['groupBuffs']
                for buff in groupBuff:
                    if buff['id'] == banner1 or buff['id'] == banner2:
                        return True
        return False
    
    ################################ DATA JOUEUR ################################
    
    def get_player_name(self, i_player: int):
        return self.log.jcontent['players'][i_player]['name']
    
    def get_player_account(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['account']
    
    def get_player_pos(self, i_player: int , start: int = 0, end: int = None):
        return self.log.pjcontent['players'][i_player]['combatReplayData']['positions'][start:end]
    
    def get_cc_boss(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['dpsTargets'][0][0]['breakbarDamage']
    
    def get_dmg_boss(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['dpsTargets'][0][self.real_phase_id]['damage']
    
    # Return Total Cleave
    def get_dmg_cleave(self, i_player: int, targets: int):
        dmg = 0
        for i in range(targets):
            dmg += self.log.pjcontent['players'][i_player]['dpsTargets'][i][self.real_phase_id]['damage']
        return dmg
    
    def get_cc_total(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['dpsAll'][0]['breakbarDamage']
    
    def get_player_id(self, name: str):
        players = self.log.pjcontent['players'] 
        for i_player, player in enumerate(players):
            if player['name'] == name:
                return i_player
        return None
    
    def get_player_spe(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['profession']
    
    def get_player_mech_history(self, i_player: int, mechs: list[str] = []):
        history      = []
        player_name  = self.get_player_name(i_player)
        mech_history = self.log.pjcontent['mechanics']
        for mech in mech_history:
            for data in mech['mechanicsData']:
                if data['actor'] == player_name:
                    if mechs:
                        if mech['name'] in mechs:
                            history.append({"name": mech['name'], "time": data['time']})
                    else:
                        history.append({"name": mech['name'], "time": data['time']})
        history.sort(key=lambda mech: mech["time"], reverse=False)
        return history
    
    def players_to_string(self, i_players: list[int]):
        name_list = []
        for i in i_players:
            account = self.get_player_account(i)
            custom_name = CUSTOM_NAMES.get(account)
            if custom_name:
                name_list.append(custom_name)
            else:
                name_list.append(self.get_player_name(i))
        return "__"+'__ / __'.join(name_list)+"__"
    
    def get_player_death_timer(self, i_player: int):
        if self.is_dead(i_player):
            mech_history = self.get_player_mech_history(i_player, ["Dead"])
            if mech_history:
                return mech_history[-1]['time']
        return
    
    def get_player_rotation(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['rotation']
    
    def time_entered_area(self, i_player: int, center: list[float], radius: float):
        poses = self.get_player_pos(i_player)
        for i, pos in enumerate(poses):
            if func.get_dist(pos, center) < radius:
                return i*150
        return
    
    def time_exited_area(self, i_player, center: list[float], radius: float):
        time_enter = self.time_entered_area(i_player, center, radius)
        if time_enter:
            i_enter = int(time_enter/150)
            poses   = self.get_player_pos(i_player)[i_enter:]
            for i, pos in enumerate(poses):
                if func.get_dist(pos, center) > radius:
                    return (i+i_enter) * 150
        return
    
    def add_mvps(self, players: list[int]):
        self.mvp_accounts = [self.get_player_account(i) for i in players]
        for i in players:
            account = self.get_player_account(i)
            ALL_PLAYERS[account].mvps += 1
                
    def add_lvps(self, players: list[int]):
        self.lvp_accounts = [self.get_player_account(i) for i in players]
        for i in players:
            account = self.get_player_account(i)
            ALL_PLAYERS[account].lvps += 1
            
    def _get_dps_contrib(self, exclude: list[classmethod]=[]):
        dps_ranking = {}
        max_dps     = 0
        for i in self.player_list:
            if any(filter_func(i) for filter_func in exclude):
                continue
            player_dps = self.log.pjcontent['players'][i]['dpsTargets'][0][self.real_phase_id]['damage']
            if player_dps > max_dps:
                max_dps = player_dps
            dps_ranking[self.log.pjcontent['players'][i]['account']] = player_dps
        for player in dps_ranking:
            dps_ranking[player] = 20 * dps_ranking[player] / max_dps
        return dps_ranking

    def get_dps_ranking(self):
        return self._get_dps_contrib([self.is_support])
    
    def get_player_group(self, i_player: int):
        return self.log.pjcontent["players"][i_player]["group"]
    
    def get_foodswap_count(self, i_player: int):
        foodSwapIcon  = "https://wiki.guildwars2.com/images/d/d6/Champion_of_the_Crown.png"
        foodSwapId    = []
        buffMap       = self.log.pjcontent["buffMap"]
        buffUptimes   = self.log.pjcontent["players"][i_player]["buffUptimes"]
        foodSwapCount = 0
        for buffName, data in buffMap.items():
            if data.get("icon") == foodSwapIcon:
                foodSwapId.append(int(buffName[1:]))
        for buff in buffUptimes:
            if buff["id"] in foodSwapId:
                for state in buff["states"]:
                    if state[1] == 1:
                        foodSwapCount += 1
        return foodSwapCount
    
    # Check if person was using writs
    def get_writ_user(self, i_player: int):
        
        food = 1
        if "consumables" in self.log.pjcontent["players"][i_player].keys():
            Cons = self.log.pjcontent["players"][i_player]['consumables']
        else: # No food
            food = 0

        if food == 1:
            for util in Cons:
                # Writ of Masterful Strength
                if util['id'] == 33297:
                    return True
                # Writ of Masterful Malice
                if util['id'] == 33836:
                    return True
                # Writ of Learned Malice
                if util['id'] == 31959:
                    return True
            
        return False


    ################################ MVP ################################
    
    def get_mvp_cc_boss(self, extra_exclude: list[classmethod]=[]):
        i_players, min_cc, total_cc = Stats.get_min_value(self, self.get_cc_boss, exclude=[*extra_exclude])
        if total_cc == 0:
            return
        self.add_mvps(i_players)  
        mvp_names  = self.players_to_string(i_players)
        cc_ratio   = min_cc / total_cc * 100
        number_mvp = len(i_players)  
        if min_cc == 0:
            if number_mvp == 1:
                return LANGUES["selected_language"]["MVP BOSS 0 CC S"].format(mvp_names=mvp_names)
            else:
                return LANGUES["selected_language"]["MVP BOSS 0 CC P"].format(mvp_names=mvp_names)
        else:
            if number_mvp == 1:
                return LANGUES["selected_language"]["MVP BOSS CC S"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
            else:
                return LANGUES["selected_language"]["MVP BOSS CC P"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
    
    def get_mvp_cc_total(self,extra_exclude: list[classmethod]=[]):
        i_players, min_cc, total_cc = Stats.get_min_value(self, self.get_cc_total, exclude=[*extra_exclude])
        if total_cc == 0:
            return
        self.add_mvps(i_players)  
        mvp_names  = self.players_to_string(i_players)
        cc_ratio   = min_cc / total_cc * 100
        number_mvp = len(i_players)  
        if min_cc == 0:
            if number_mvp == 1:
                return LANGUES["selected_language"]["MVP TOTAL 0 CC S"].format(mvp_names=mvp_names)
            else:
                return LANGUES["selected_language"]["MVP TOTAL 0 CC P"].format(mvp_names=mvp_names)
        else:
            if number_mvp == 1:
                return LANGUES["selected_language"]["MVP TOTAL CC S"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
            else:
                return LANGUES["selected_language"]["MVP TOTAL CC P"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
    
    def get_bad_dps(self, extra_exclude: list[classmethod]=[]):
        i_sup, sup_max_dmg, _ = Stats.get_max_value(self, self.get_dmg_boss, exclude=[self.is_dps, self.is_bannerslave])
        sup_name              = self.players_to_string(i_sup)
        bad_dps               = []
        for i in self.player_list:   
            if any(filter_func(i) for filter_func in extra_exclude) or self.is_dead(i) or self.is_support(i) or self.is_bannerslave(i) or self.is_heal(i):
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
    
    # General function that flames for different generic low boon uptime
    def get_bad_boons(self, phase: str, exclude: list[classmethod]=[]):
        
        alac_sub1 = 69
        alac_sub2 = 69
        quick_sub1 = 69
        quick_sub2 = 69
        heal_sub1 = 69
        heal_sub2 = 69
        soloheal = False
        
        Group_No = self.log.pjcontent['players'][2]['group']
        
        # Find supports
        for i in self.player_list:
            if self.is_alac(i):
                if self.log.pjcontent['players'][i]['group'] == Group_No:
                    alac_sub1 = i
                else:
                    alac_sub2 = i
            if self.is_quick(i):
                if self.log.pjcontent['players'][i]['group'] == Group_No:
                    quick_sub1 = i
                else:
                    quick_sub2 = i
            if self.is_heal(i):
                if self.log.pjcontent['players'][i]['group'] == Group_No:
                    heal_sub1 = i
                else:
                    heal_sub2 = i
        
        # If healer not tagged, check for toughness
        if heal_sub1 > 11:
            for i in self.player_list:
                if self.is_tank(i):
                    if self.log.pjcontent['players'][i]['group'] == Group_No:
                        heal_sub1 = i
        if heal_sub2 > 11:
            for i in self.player_list:
                if self.is_tank(i):
                    if not self.log.pjcontent['players'][i]['group'] == Group_No:
                        heal_sub2 = i

        # Generic flame if boon player situation is ???
        if alac_sub1 == 69 or alac_sub2 == 69 or quick_sub1 == 69 or quick_sub2 == 69:
            return LANGUES["selected_language"]["MVP BOON SETUP NO COM"]
        
        # Tag soloheal if exists
        if heal_sub1 == 69 and heal_sub2 < 69:
            soloheal = True
        if heal_sub2 == 69 and heal_sub1 < 69:
            soloheal = True
              
        # Get boon uptimes
        mvp_might_sub1 = []
        mvp_fury_sub1  = []
        mvp_quick_sub1 = []
        mvp_alac_sub1  = []
        mvp_prot_sub1  = []
        mvp_regen_sub1 = []
        mvp_swift_sub1 = []
        mvp_might_sub2 = []
        mvp_fury_sub2  = []
        mvp_quick_sub2 = []
        mvp_alac_sub2  = []
        mvp_prot_sub2  = []
        mvp_regen_sub2 = []
        mvp_swift_sub2 = []
        
        threshold = 0.75 # Boon uptime threshold
        
        for i in self.player_list:
            # Remove dead players
            try:
                if any(filter_func(i) for filter_func in exclude) or self.is_dead(i):
                    continue
            except:
                if len(exclude) > 0:
                    if i in exclude:
                        continue
                    if self.is_dead(i):
                        continue
                else:
                    if self.is_dead(i):
                        continue

            # Might    
            if self.log.pjcontent['players'][i]['group'] == Group_No:
                if self.get_boon_uptime(i, 'Might', phase) < 25 * threshold:
                    mvp_might_sub1.append(quick_sub1)
                    mvp_might_sub1.append(alac_sub1)
            else:
                if self.get_boon_uptime(i, 'Might', phase) < 25 * threshold:
                    mvp_might_sub2.append(quick_sub2)
                    mvp_might_sub2.append(alac_sub2)
            # Fury  
            if self.log.pjcontent['players'][i]['group'] == Group_No:
                if self.get_boon_uptime(i, 'Fury', phase) < threshold:
                    mvp_fury_sub1.append(quick_sub1)
                    mvp_fury_sub1.append(alac_sub1)
            else:
                if self.get_boon_uptime(i, 'Fury', phase) < threshold:
                    mvp_fury_sub2.append(quick_sub2)
                    mvp_fury_sub2.append(alac_sub2)
            # Quickness 
            if self.log.pjcontent['players'][i]['group'] == Group_No:
                if self.get_boon_uptime(i, 'Quickness', phase) < threshold:
                    mvp_quick_sub1.append(quick_sub1)
            else:
                if self.get_boon_uptime(i, 'Quickness', phase) < threshold:
                    mvp_quick_sub2.append(quick_sub2)
            # Alacrity 
            if self.log.pjcontent['players'][i]['group'] == Group_No:
                if self.get_boon_uptime(i, 'Alacrity', phase) < threshold:
                    mvp_alac_sub1.append(alac_sub1)
            else:
                if self.get_boon_uptime(i, 'Alacrity', phase) < threshold:
                    mvp_alac_sub2.append(alac_sub2)
            # Protection
            if self.log.pjcontent['players'][i]['group'] == Group_No:
                if self.get_boon_uptime(i, 'Protection', phase) < threshold:
                    if heal_sub1 == 69:
                        if not soloheal:
                            mvp_prot_sub1.append(alac_sub1)
                            mvp_prot_sub1.append(quick_sub1)
                    else:
                        mvp_prot_sub1.append(heal_sub1)
            else:
                if self.get_boon_uptime(i, 'Protection', phase) < threshold:
                    if heal_sub2 == 69:
                        if not soloheal:
                            mvp_prot_sub2.append(alac_sub2)
                            mvp_prot_sub2.append(quick_sub2)
                    else:
                        mvp_prot_sub2.append(heal_sub2)
            # Regeneration
            if self.log.pjcontent['players'][i]['group'] == Group_No:
                if self.get_boon_uptime(i, 'Regeneration', phase) < threshold:
                    if heal_sub1 == 69:
                        if not soloheal:
                            mvp_regen_sub1.append(alac_sub1)
                            mvp_regen_sub1.append(quick_sub1)
                    else:
                        mvp_regen_sub1.append(heal_sub1)
            else:
                if self.get_boon_uptime(i, 'Regeneration', phase) < threshold:
                    if heal_sub2 == 69:
                        if not soloheal:
                            mvp_regen_sub2.append(alac_sub2)
                            mvp_regen_sub2.append(quick_sub2)
                    else:
                        mvp_regen_sub2.append(heal_sub2)
            # Swiftness   
            if self.log.pjcontent['players'][i]['group'] == Group_No:
                if self.get_boon_uptime(i, 'Swiftness', phase) < threshold:
                    if heal_sub1 == 69:
                        if not soloheal:
                            mvp_swift_sub1.append(alac_sub1)
                            mvp_swift_sub1.append(quick_sub1)
                    else:
                        mvp_swift_sub1.append(heal_sub1)
            else:
                if self.get_boon_uptime(i, 'Swiftness', phase) < threshold:
                    if heal_sub2 == 69:
                        if not soloheal:
                            mvp_swift_sub2.append(alac_sub2)
                            mvp_swift_sub2.append(quick_sub2)
                    else:
                        mvp_swift_sub2.append(heal_sub2)

        # Manage MVPs
        
        mvp_might = []
        mvp_fury  = []
        mvp_quick = []
        mvp_alac  = []
        mvp_prot  = []
        mvp_regen = []
        mvp_swift = []
        prompt = str("")
        threshold = 1 # Player number threshold

        # Might
        if len(mvp_might_sub1) > 2 * threshold:
            mvp_might.append(mvp_might_sub1[0])
            mvp_might.append(mvp_might_sub1[1])
        if len(mvp_might_sub2) > 2 * threshold:
            mvp_might.append(mvp_might_sub2[0])
            mvp_might.append(mvp_might_sub2[1])             
        # Fury
        if len(mvp_fury_sub1) > 2 * threshold:
            mvp_fury.append(mvp_fury_sub1[0])
            mvp_fury.append(mvp_fury_sub1[1])
        if len(mvp_fury_sub2) > 2 * threshold:
            mvp_fury.append(mvp_fury_sub2[0])
            mvp_fury.append(mvp_fury_sub2[1])         
        # Quickness
        if len(mvp_quick_sub1) > threshold:
            mvp_quick.append(mvp_quick_sub1[0])
        if len(mvp_quick_sub2) > threshold:
            mvp_quick.append(mvp_quick_sub2[0])   
        # Alacrity    
        if len(mvp_alac_sub1) > threshold:
            mvp_alac.append(mvp_alac_sub1[0])
        if len(mvp_alac_sub2) > threshold:
            mvp_alac.append(mvp_alac_sub2[0])   
        # Protection
        if len(mvp_prot_sub1) > threshold:
            mvp_prot.append(mvp_prot_sub1[0])
        if len(mvp_prot_sub2) > threshold:
            mvp_prot.append(mvp_prot_sub2[0])
        # Regeneration
        if len(mvp_regen_sub1) > threshold:
            mvp_regen.append(mvp_regen_sub1[0])
        if len(mvp_regen_sub2) > threshold:
            mvp_regen.append(mvp_regen_sub2[0])        
        # Swiftness
        if len(mvp_swift_sub1) > 2 * threshold:
            if heal_sub1 == 69:
                if not soloheal:
                    mvp_swift.append(mvp_swift_sub1[0])
                    mvp_swift.append(mvp_swift_sub1[1])
                else:
                    mvp_swift.append(mvp_swift_sub1[0])
        if len(mvp_swift_sub2) > 2 * threshold:
            if heal_sub2 == 69:
                if not soloheal:
                    mvp_swift.append(mvp_swift_sub2[0])
                    mvp_swift.append(mvp_swift_sub2[1])
                else:
                    mvp_swift.append(mvp_swift_sub2[0])
             
        # Return Flame if quick or alac is missing on top of other boons
        # Quickness
        if len(mvp_quick) > 0:
            self.add_mvps(list(set(mvp_quick)))         
            mvp_name = []
            for mvp in mvp_quick:
                if mvp in (mvp_might + mvp_fury + mvp_prot + mvp_regen + mvp_swift):
                    mvp_name.append(mvp)                  
                    if mvp in mvp_might:
                        mvp_might.remove(mvp)
                    if mvp in mvp_fury:
                        mvp_fury.remove(mvp)
                    if mvp in mvp_prot:
                        mvp_prot.remove(mvp)
                    if mvp in mvp_regen:
                        mvp_regen.remove(mvp)
                    if mvp in mvp_swift:
                        mvp_swift.remove(mvp)
            mvp_quick = [mvp for mvp in mvp_quick if mvp not in mvp_name]
            mvp_names_2 = self.players_to_string(list(set(mvp_name)))       
            mvp_names = self.players_to_string(list(set(mvp_quick)))
            if len(mvp_name) > 0:
                prompt += LANGUES["selected_language"]["MVP QUICK MERGED"].format(mvp_names=mvp_names_2) + "\n"
            if len(mvp_quick) > 0:
                prompt += LANGUES["selected_language"]["MVP QUICK"].format(mvp_names=mvp_names) + "\n"

        # Alacrity
        if len(mvp_alac) > 0:
            self.add_mvps(list(set(mvp_alac)))
            mvp_name = []
            for mvp in mvp_alac:
                if mvp in (mvp_might + mvp_fury + mvp_prot + mvp_regen + mvp_swift):
                    mvp_name.append(mvp)     
                    if mvp in mvp_might:
                        mvp_might.remove(mvp)
                    if mvp in mvp_fury:
                        mvp_fury.remove(mvp)
                    if mvp in mvp_prot:
                        mvp_prot.remove(mvp)
                    if mvp in mvp_regen:
                        mvp_regen.remove(mvp)
                    if mvp in mvp_swift:
                        mvp_swift.remove(mvp)
            mvp_alac = [mvp for mvp in mvp_alac if mvp not in mvp_name]
            mvp_names_2 = self.players_to_string(list(set(mvp_name)))       
            mvp_names = self.players_to_string(list(set(mvp_alac)))    
            if len(mvp_name) > 0:
                prompt += LANGUES["selected_language"]["MVP ALAC MERGED"].format(mvp_names=mvp_names_2) + "\n"
            if len(mvp_alac) > 0:
                prompt += LANGUES["selected_language"]["MVP ALAC"].format(mvp_names=mvp_names) + "\n"

        # Return Flame, multiple boons missing

        mvp_boons = mvp_might + mvp_fury + mvp_prot + mvp_regen + mvp_swift
        dupes = [x for n, x in enumerate(mvp_boons) if x in mvp_boons[:n]]
        if len(dupes) > 0:
            self.add_mvps(list(dupes))
            mvp_names = self.players_to_string(list(set(dupes)))  
            prompt += LANGUES["selected_language"]["MVP BOON MERGED"].format(mvp_names=mvp_names) + "\n"

        for mvp in dupes:
            if mvp in mvp_might:
                mvp_might.remove(mvp)
            if mvp in mvp_fury:
                mvp_fury.remove(mvp)
            if mvp in mvp_prot:
                mvp_prot.remove(mvp)
            if mvp in mvp_regen:
                mvp_regen.remove(mvp)
            if mvp in mvp_swift:
                mvp_swift.remove(mvp)

        # Return Flame, individual boon missing

        # Might
        if len(mvp_might) > 0:
            self.add_mvps(list(set(mvp_might)))
            mvp_names = self.players_to_string(list(set(mvp_might)))
            prompt += LANGUES["selected_language"]["MVP MIGHT"].format(mvp_names=mvp_names)
            prompt += "\n"  
        # Fury
        if len(mvp_fury) > 0:
            self.add_mvps(list(set(mvp_fury)))
            mvp_names = self.players_to_string(list(set(mvp_fury)))
            prompt += LANGUES["selected_language"]["MVP FURY"].format(mvp_names=mvp_names)
            prompt += "\n"
        # Protection
        if len(mvp_prot) > 0:
            self.add_mvps(list(set(mvp_prot)))
            mvp_names = self.players_to_string(list(set(mvp_prot)))
            prompt += LANGUES["selected_language"]["MVP PROT"].format(mvp_names=mvp_names)
            prompt += "\n"
        # Regeneration
        if len(mvp_regen) > 0:
            self.add_mvps(list(set(mvp_regen)))
            mvp_names = self.players_to_string(list(set(mvp_regen)))
            prompt += LANGUES["selected_language"]["MVP REGEN"].format(mvp_names=mvp_names)
            prompt += "\n"
        # Swiftness
        if len(mvp_swift) > 0:
            self.add_mvps(list(set(mvp_swift)))
            mvp_names = self.players_to_string(list(set(mvp_swift)))
            prompt += LANGUES["selected_language"]["MVP SWIFT"].format(mvp_names=mvp_names)
            prompt += "\n"
        
        return prompt
    
    # Check if person is using food and flame if they aren't
    def get_no_food(self):

        no_food = []
        prompt = ""

        # Find people without food
        for i in self.player_list:
            # Skip healers
            if self.is_heal(i):
                continue
            
            # Check if a skill issue negative amount of food was used
            Con_check = list(self.log.pjcontent["players"][i].keys())
            if "consumables" not in Con_check:
                no_food.append(i)
                continue
            
            # Otherwise check writting
            Cons = self.log.pjcontent["players"][i]['consumables']
            count = 0
            count_lim = 2
            for util in Cons:
                # Don't count reinforced armor or malnourished or diminished
                if util['id'] == 9283 or util['id'] == 46587 or util['id'] == 46668:
                    # Increase count lim to account for if they refreshed food
                    if util['id'] == 46587:
                        count_lim = count_lim + 1
                    if util['id'] == 46668:
                        count_lim = count_lim + 1
                    continue
                else:
                    count = count + 1
            # If food + util not counted, add to flame list
            if count < count_lim:
                no_food.append(i)

        # Return the necessary flame
        if len(no_food) > 0:
            self.add_mvps(list(set(no_food)))
            mvp_names = self.players_to_string(list(set(no_food)))
            prompt += LANGUES["selected_language"]["MVP NO FOOD"].format(mvp_names=mvp_names)
            
        return prompt

    # Flame people who die early in the fight
    def get_buyer_POV(self):

        buyers = []
        boss_dura = self.duration_ms
        prompt = ""

        for i in self.player_list:
            if self.get_player_death_timer(i):
                if self.get_player_death_timer(i) / boss_dura < 0.5:
                    buyers.append(i)

        # Return the necessary flame
        if len(buyers) > 0:
            self.add_mvps(list(set(buyers)))
            mvp_names = self.players_to_string(list(set(buyers)))
            prompt += LANGUES["selected_language"]["MVP BUYER POV"].format(mvp_names=mvp_names)

        return prompt
    
    # General flame function
    def get_mvp_general(self):
        prompt = ""

        # Flame if no food
        prompt = prompt + self.get_no_food() + "\n"
        # Flame if buyer POV
        prompt = prompt + self.get_buyer_POV() + "\n"

        return prompt
    
    ################################ LVP ################################
    
    def get_lvp_cc_boss(self):
        i_players, max_cc, total_cc = Stats.get_max_value(self, self.get_cc_boss)
        if total_cc == 0:
            return
        self.add_lvps(i_players)
        lvp_names = self.players_to_string(i_players)
        cc_ratio  = max_cc / total_cc * 100
        return LANGUES["selected_language"]["LVP BOSS CC"].format(lvp_names=lvp_names, max_cc=max_cc, cc_ratio=cc_ratio)
    
    def get_lvp_cc_total(self):
        i_players, max_cc, total_cc = Stats.get_max_value(self, self.get_cc_total)
        if total_cc == 0:
            return
        self.add_lvps(i_players)
        lvp_names = self.players_to_string(i_players)
        cc_ratio  = max_cc / total_cc * 100
        return LANGUES["selected_language"]["LVP TOTAL CC"].format(lvp_names=lvp_names, max_cc=max_cc, cc_ratio=cc_ratio)
    
    def get_lvp_dps(self):
        i_players, max_dmg, total_dmg = Stats.get_max_value(self, self.get_dmg_boss)
        dmg_ratio                     = max_dmg / total_dmg * 100
        lvp_dps_name                  = self.players_to_string(i_players)
        dps                           = max_dmg / self.duration_ms
        foodSwapCount                 = self.get_foodswap_count(i_players[0])
        self.add_lvps(i_players) 
        if foodSwapCount:
            return LANGUES["selected_language"]["LVP DPS FOODSWAP"].format(lvp_dps_name=lvp_dps_name, max_dmg=max_dmg, dmg_ratio=dmg_ratio, dps=dps, foodSwapCount=foodSwapCount)
        return LANGUES["selected_language"]["LVP DPS"].format(lvp_dps_name=lvp_dps_name, max_dmg=max_dmg, dmg_ratio=dmg_ratio, dps=dps)

    # General function to get people who contributed a lot to CC
    def get_lvp_cc_boss_PMA(self):
        i_players, max_cc, total_cc = Stats.get_max_value(self, self.get_cc_boss)
        if total_cc == 0:
            return
        # Collect other players who did a lot of CC
        collective_cc = max_cc
        for i in self.player_list:
            if self.get_cc_boss(i) > 0.9 * max_cc:
                if i is not i_players[0]:
                    i_players.append(i)
                    collective_cc = collective_cc + self.get_cc_boss(i)
        self.add_lvps(i_players)
        lvp_names = self.players_to_string(i_players)
        cc_ratio  = collective_cc / total_cc * 100
        return LANGUES["selected_language"]["LVP BOSS CC PMA"].format(lvp_names=lvp_names, max_cc=collective_cc, cc_ratio=cc_ratio)
    
    # General function to get people who contributed a lot to CC
    def get_lvp_cc_cleave_PMA(self):
        i_players, max_cc, total_cc = Stats.get_max_value(self, self.get_cc_total)
        if total_cc == 0:
            return
        # Collect other players who did a lot of CC
        collective_cc = max_cc
        for i in self.player_list:
            if self.get_cc_total(i) > 0.9 * max_cc:
                if i is not i_players[0]:
                    i_players.append(i)
                    collective_cc = collective_cc + self.get_cc_total(i)
        self.add_lvps(i_players)
        lvp_names = self.players_to_string(i_players)
        cc_ratio  = collective_cc / total_cc * 100
        return LANGUES["selected_language"]["LVP BOSS CC PMA"].format(lvp_names=lvp_names, max_cc=collective_cc, cc_ratio=cc_ratio)
    


    # General function to get people who contributed a lot to DPS
    def get_lvp_dps_PMA(self, targets: int=1):
        # Find max damage and total damage
        max_dmg = 0
        total_dmg = 0
        for i in self.player_list:
            total_dmg += self.get_dmg_cleave(i,targets)
            if self.get_dmg_cleave(i,targets) > max_dmg:
                max_dmg = self.get_dmg_cleave(i,targets)

        # Collect other players who did a lot of DPS
        Food_Swappers = []
        Writ_Users = []
        Gamers = []
        i_players = []
        collective_DPS = 0
        for i in self.player_list:
            if self.get_dmg_cleave(i,targets) > 0.9 * max_dmg:
                i_players.append(i)
                collective_DPS = collective_DPS + self.get_dmg_cleave(i,targets) / self.duration_ms
                # Check if person food swapped
                if self.get_foodswap_count(i):
                    Food_Swappers.append(i)
                # Check if person used writs
                if self.get_writ_user(i):
                    Writ_Users.append(i)
                # Otherwise, add player to fair group
                if not(self.get_foodswap_count(i) or self.get_writ_user(i)):
                    Gamers.append(i)

        dmg_ratio  = (collective_DPS * self.duration_ms) / total_dmg * 100
        self.add_lvps(i_players)
        lvp_names = self.players_to_string(i_players)

        # Set groups for food/utility & flags
        gamer_flag = 0
        writ_flag = 0
        swap_flag = 0
        if len(Gamers)>0:
            gamer_names = self.players_to_string(Gamers)
            gamer_flag = 1
        if len(Writ_Users)>0:
            writ_names = self.players_to_string(Writ_Users)
            writ_flag = 10
        if len(Food_Swappers)>0:
            swap_names = self.players_to_string(Food_Swappers)
            swap_flag = 100

        flag = gamer_flag + writ_flag + swap_flag

        # Shame the group based on food/utility situation
        match flag:
            # Impossible case
            case 0:
                return
            # Fair DPS race, no writs or swaps
            case 1:
                return LANGUES["selected_language"]["LVP DPS 001 PMA"].format(lvp_names=gamer_names, dps=collective_DPS, dmg_ratio=dmg_ratio)
            # Writ users only
            case 10:
                return LANGUES["selected_language"]["LVP DPS 010 PMA"].format(lvp_names=writ_names, dps=collective_DPS, dmg_ratio=dmg_ratio)
            # Writ users AND normal people
            case 11:
                return LANGUES["selected_language"]["LVP DPS 011 PMA"].format(lvp_names=lvp_names, dps=collective_DPS, dmg_ratio=dmg_ratio, writ_names=writ_names)
            # Food swappers only
            case 100:
                return LANGUES["selected_language"]["LVP DPS 100 PMA"].format(lvp_names=swap_names, dps=collective_DPS, dmg_ratio=dmg_ratio)
            # Food swappers AND normal people
            case 101:
                return LANGUES["selected_language"]["LVP DPS 101 PMA"].format(lvp_names=lvp_names, dps=collective_DPS, dmg_ratio=dmg_ratio, swap_names=swap_names)
            # Food swappers AND writ users
            case 110:
                return LANGUES["selected_language"]["LVP DPS 110 PMA"].format(lvp_names=lvp_names, dps=collective_DPS, dmg_ratio=dmg_ratio, writ_names=writ_names, swap_names=swap_names)
            # Food swappers, writ users, normal people
            case 111:
                return LANGUES["selected_language"]["LVP DPS 111 PMA"].format(lvp_names=lvp_names, dps=collective_DPS, dmg_ratio=dmg_ratio, writ_names=writ_names, swap_names=swap_names, gamer_names=gamer_names)
        
        # Code somehow fucked up
        return
    
    # General function to get boondps who do well
    def get_lvp_bdps_PMA(self, targets: int=1):
        # Find max damage and total damage
        max_dmg = 0
        total_dmg = 0
        for i in self.player_list:
            total_dmg += self.get_dmg_cleave(i,targets)
            if self.get_dmg_cleave(i,targets) > max_dmg:
                max_dmg = self.get_dmg_cleave(i,targets)

        # Collect gamer bdps
        i_players = []
        collective_DPS = 0
        for i in self.player_list:
            # If no boon, skip
            if not (self.is_alac(i) or self.is_quick(i)):
                continue
            # If healer, skip
            if self.is_heal(i):
                continue
            # Check if bdps did dps
            if self.get_dmg_cleave(i,targets) > 0.75 * max_dmg:
                i_players.append(i)
                collective_DPS = collective_DPS + self.get_dmg_cleave(i,targets) / self.duration_ms

        dmg_ratio  = (collective_DPS * self.duration_ms) / total_dmg * 100
        söder_ratio  = (collective_DPS * self.duration_ms) / max_dmg * 100
        self.add_lvps(i_players)
        lvp_names = self.players_to_string(i_players)

        # Praise people if they exist. Descartes moment
        if len(i_players) == 1:
            return LANGUES["selected_language"]["LVP BDPS PMA S"].format(lvp_names=lvp_names, dps=collective_DPS, dmg_ratio=söder_ratio)
        if len(i_players) > 1:
            return LANGUES["selected_language"]["LVP BDPS PMA P"].format(lvp_names=lvp_names, dps=collective_DPS, dmg_ratio=dmg_ratio)

        # No bitches
        return
    
    # General function that praises for good boon uptime
    def get_good_boons(self, phase: str, exclude: list[classmethod]=[]):
        
        prompt = ""
        alac_sub1 = 69
        alac_sub2 = 69
        quick_sub1 = 69
        quick_sub2 = 69
        
        Group_No = self.log.pjcontent['players'][2]['group']
        
        # Find supports
        for i in self.player_list:
            if self.is_alac(i):
                if self.log.pjcontent['players'][i]['group'] == Group_No:
                    alac_sub1 = i
                else:
                    alac_sub2 = i
            if self.is_quick(i):
                if self.log.pjcontent['players'][i]['group'] == Group_No:
                    quick_sub1 = i
                else:
                    quick_sub2 = i

        # If boon player situation is cringe, then automatically flamed in MVP section
        if alac_sub1 == 69 or alac_sub2 == 69 or quick_sub1 == 69 or quick_sub2 == 69:
            return prompt
              
        # Get boon uptimes
        lvp_sub1 = []
        lvp_sub2 = []
        sub1 = 5
        sub2 = 5
        
        threshold = 0.96 # Boon uptime threshold
        
        for i in self.player_list:
            # Remove dead players
            try:
                if any(filter_func(i) for filter_func in exclude) or self.is_dead(i):
                    if self.log.pjcontent['players'][i]['group'] == Group_No:
                        sub1 = sub1 - 1
                    else:
                        sub2 = sub2 - 1
                    continue
            except:
                if len(exclude) > 0:
                    if i in exclude:
                        continue
                    if self.is_dead(i):
                        if self.log.pjcontent['players'][i]['group'] == Group_No:
                            sub1 = sub1 - 1
                        else:
                            sub2 = sub2 - 1
                        continue
                else:
                    if self.is_dead(i):
                        if self.log.pjcontent['players'][i]['group'] == Group_No:
                            sub1 = sub1 - 1
                        else:
                            sub2 = sub2 - 1
                        continue

            # Might    
            if self.log.pjcontent['players'][i]['group'] == Group_No:
                if self.get_boon_uptime(i, 'Might', phase) > 25 * threshold:
                    lvp_sub1.append(alac_sub1)
            else:
                if self.get_boon_uptime(i, 'Might', phase) > 25 * threshold:
                    lvp_sub2.append(alac_sub2)
            # Fury  
            if self.log.pjcontent['players'][i]['group'] == Group_No:
                if self.get_boon_uptime(i, 'Fury', phase) > threshold:
                    lvp_sub1.append(alac_sub1)
            else:
                if self.get_boon_uptime(i, 'Fury', phase) > threshold:
                    lvp_sub2.append(alac_sub2)
            # Quickness 
            if self.log.pjcontent['players'][i]['group'] == Group_No:
                if self.get_boon_uptime(i, 'Quickness', phase) > threshold:
                    lvp_sub1.append(quick_sub1)
            else:
                if self.get_boon_uptime(i, 'Quickness', phase) > threshold:
                    lvp_sub2.append(quick_sub2)
            # Alacrity 
            if self.log.pjcontent['players'][i]['group'] == Group_No:
                if self.get_boon_uptime(i, 'Alacrity', phase) > threshold:
                    lvp_sub1.append(alac_sub1)
            else:
                if self.get_boon_uptime(i, 'Alacrity', phase) > threshold:
                    lvp_sub2.append(alac_sub2)
            # Protection
            if self.log.pjcontent['players'][i]['group'] == Group_No:
                if self.get_boon_uptime(i, 'Protection', phase) > threshold:
                    lvp_sub1.append(alac_sub1)                            
            else:
                if self.get_boon_uptime(i, 'Protection', phase) > threshold:
                    lvp_sub2.append(alac_sub2)
            # Regeneration
            if self.log.pjcontent['players'][i]['group'] == Group_No:
                if self.get_boon_uptime(i, 'Regeneration', phase) > threshold:
                    lvp_sub1.append(alac_sub1)
            else:
                if self.get_boon_uptime(i, 'Regeneration', phase) > threshold:
                    lvp_sub2.append(alac_sub2)
            # Swiftness   
            if self.log.pjcontent['players'][i]['group'] == Group_No:
                if self.get_boon_uptime(i, 'Swiftness', phase) > threshold:
                    lvp_sub1.append(alac_sub1)
            else:
                if self.get_boon_uptime(i, 'Swiftness', phase) > threshold:
                    lvp_sub2.append(alac_sub2)

        # Collect boon players if they gave high boon uptime on everything
        i_players = []

        if len(lvp_sub1) > sub1 * 7 - 3 and sub1 > 0:
            i_players.append(alac_sub1)
            i_players.append(quick_sub1)
        if len(lvp_sub2) > sub2 * 7 - 3 and sub2 > 0:
            i_players.append(alac_sub2)
            i_players.append(quick_sub2)

        # Praise the boon players
        if len(i_players) > 0:
            self.add_lvps(i_players)
            lvp_names = self.players_to_string(i_players)
            prompt += LANGUES["selected_language"]["LVP BIG BOON"].format(lvp_names=lvp_names)
        return prompt
    
    # General praise function
    def get_lvp_general(self, phase: str, exclude: list[classmethod]=[]):
        prompt = ""

        # Praise supports if good boons
        prompt = prompt + self.get_good_boons(phase) + "\n"

        return prompt

    ################################ DATA BOSS ################################
    
    def get_pos_boss(self, start: int = 0, end: int = None):
        targets = self.log.pjcontent['targets']
        for target in targets:
            if target['id'] in BOSS_DICT.keys():
                return target['combatReplayData']['positions'][start:end]
        raise ValueError('No Boss in targets')
    
    def get_phase_timers(self, target_phase: str, inMilliSeconds=False):
        phases = self.log.pjcontent['phases']
        for phase in phases:
            if phase['name'] == target_phase:  
                start = phase['start']
                end   = phase['end']
                if inMilliSeconds:
                    return start, end
                return func.time_to_index(start, self.time_base), func.time_to_index(end, self.time_base)
        raise ValueError(f'{target_phase} not found')
    
    def get_mech_value(self, i_player: int, mech_name: str, phase: str="Full Fight"):
        phase      = self.get_phase_id(phase)
        mechs_list = [mech['name'] for mech in self.mechanics]
        if mech_name in mechs_list:
            i_mech = mechs_list.index(mech_name)
            return self.log.jcontent['phases'][phase]['mechanicStats'][i_player][i_mech][0]
        return 0
        
    def get_mech_value_nocringe(self, i_player: int, mech_num: str, phase: str="Full Fight"):
        phase      = self.get_phase_id(phase)
        return self.log.jcontent['phases'][phase]['mechanicStats'][i_player][mech_num][0]
        return 0
    
    def bosshp_to_time(self, hp: float):
        hp_percents = self.log.pjcontent['targets'][0]['healthPercents']
        for timer in hp_percents:
            if timer[1] < hp:
                return timer[0]
        return
    
    def get_mechanic_history(self, name: str):
        mechanics = self.log.pjcontent['mechanics']
        for mech in mechanics:
            if mech['fullName'] == name:
                return mech['mechanicsData']
        return
    
    def get_phase_id(self, name: str):
        phases = self.log.pjcontent["phases"]
        for i, phase in enumerate(phases):
            if phase["name"] == name:
                return i
        return 0  
    
    def get_time_base(self):
        delta = self.log.pjcontent["players"][0]["combatReplayData"]["end"]-self.log.pjcontent["players"][0]["combatReplayData"]["start"]
        lpos  = len(self.log.pjcontent["players"][0]["combatReplayData"]["positions"])
        return int(delta/lpos) 
        
    # Function to extract boon uptime on player during phase    
    def get_boon_uptime(self, i_player: int, i_buff: str, phase: str):
        
        # Sort the correct buff:        
        match i_buff:
            case 'Might':
                buff_id = 740
            case 'Fury':
                buff_id = 725
            case 'Quickness':
                buff_id = 1187
            case 'Alacrity':
                buff_id = 30328
            case 'Protection':
                buff_id = 717
            case 'Regeneration':
                buff_id = 718
            case 'Vigor':
                buff_id = 726
            case 'Aegis':
                buff_id = 743
            case 'Stability':
                buff_id = 1122
            case 'Swiftness':
                buff_id = 719
            case 'Resistance':
                buff_id = 26980
            case 'Resolution':
                buff_id = 873
        
        buffplot = []
        # Obtain buffs of player
        buffs = self.log.pjcontent['players'][i_player]['buffUptimes']
        for buff in buffs:
            if buff['id'] == buff_id:
                buffplot = buff['states']
                break
        
        # Get boon states & time of state change
        xbuffplot = [pos[0] for pos in buffplot]
        ybuffplot = [pos[1] for pos in buffplot]
        
        # Get phase time
        start, end = self.get_phase_timers(phase, inMilliSeconds=True)
        
        # Summation of boonstate * deltaTime
        mysum = 0
        for i in range(len(ybuffplot)):
            # Correct last data point and abort
            if i == (len(ybuffplot)-1) or xbuffplot[i+1] > end:
                mysum = mysum + (ybuffplot[i]) * (end - xbuffplot[i])
                break
            # Skip outside time range
            elif xbuffplot[i] < start and xbuffplot[i+1] < start:
                continue
            # Correct for time on summation data point starts on negative time but ends on positive
            elif xbuffplot[i] < start and xbuffplot[i+1] > start:
                mysum = mysum + (ybuffplot[i]) * (xbuffplot[i+1] - start)
            # Add data point sum = boon state * deltaTime
            else:
                mysum = mysum + (ybuffplot[i]) * (xbuffplot[i+1] - xbuffplot[i])
        
        # Boon uptime = boonstate * deltaTime / phase time
        boon_uptime = mysum / (end - start)
        
        return boon_uptime
            
    
class Stats:
    @staticmethod
    def get_max_value(boss : Boss,
                      fnc: classmethod, 
                      exclude: list[classmethod] = []):  
        if exclude is None:
            exclude = []
        value_max = -1
        value_tot = 0
        i_maxs    = []
        for i in boss.player_list:
            value      = fnc(i)
            value_tot += value
            if any(filter_func(i) for filter_func in exclude):
                continue
            if value > value_max:
                value_max = value
                i_maxs = [i]
            elif value == value_max:
                i_maxs.append(i)
        if value_max == 0:
            return [], value_max, value_tot
        return i_maxs, value_max, value_tot
        
    @staticmethod
    def get_min_value(boss : Boss,
                      fnc: classmethod, 
                      exclude: list[classmethod] = []):

        if exclude is None:
            exclude = []
        value_min = BIG
        value_tot = 0
        i_mins    = []
        for i in boss.player_list:
            value      = fnc(i)
            value_tot += value
            if any(filter_func(i) for filter_func in exclude):
                continue
            if value < value_min:
                value_min = value
                i_mins = [i]
            elif value == value_min:
                i_mins.append(i)
        return i_mins, value_min, value_tot

    @staticmethod
    def get_tot_value(boss : Boss,
                      fnc: classmethod, 
                      exclude: list[classmethod] = []):
                
        if exclude is None:
            exclude = []
        value_tot = 0
        for i in boss.player_list:
            if any(filter_func(i) for filter_func in exclude):
                continue
            value_tot += fnc(i)
        return value_tot