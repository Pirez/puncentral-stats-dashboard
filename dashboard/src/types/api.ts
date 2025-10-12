export interface PlayerStats {
  match_id: string;
  kills_total: number;
  deaths_total: number;
  dmg: number;
  utility_dmg: number;
  he_dmg: number;
  molotov_dmg: number;
  headshot_kills_total: number;
  ace_rounds_total: number;
  quad_rounds_total: number;
  triple_rounds_total: number;
  mvps: number;
  name: string;
  created_at: string;
}

export interface MapStats {
  match_id: string;
  map_name: string;
  date_time: string;
  won: number;
  created_at: string;
}

export interface ChickenKills {
  name: string;
  chicken: number;
}

export interface MapWinRate {
  map_name: string;
  total_matches: number;
  total_wins: number;
  win_ratio: number;
}

export interface RankInfo {
  user_name: string;
  rank_new: number;
  rank_change: number;
}

export interface KDRatio {
  name: string;
  avg_kd: number;
  last_match_kd: number;
  kd_change: number;
}

export interface KDOverTime {
  name: string;
  match_id: string;
  date_time: string;
  map_name: string;
  match_kd: number;
}

export interface LastMatchPlayer {
  match_id: string;
  kills_total: number;
  deaths_total: number;
  dmg: number;
  utility_dmg: number;
  he_dmg: number;
  molotov_dmg: number;
  headshot_kills_total: number;
  ace_rounds_total: number;
  quad_rounds_total: number;
  triple_rounds_total: number;
  mvps: number;
  name: string;
  created_at: string;
}

export interface LastMatchInfo {
  map_name: string;
  date_time: string;
  won: boolean;
}

export interface LastMatch {
  players: LastMatchPlayer[];
  match_info: LastMatchInfo;
}

export interface MultiKillStats {
  name: string;
  total_aces: number;
  total_quads: number;
  total_triples: number;
  total_multi_kills: number;
}

export interface UtilityDamageStats {
  name: string;
  total_utility_dmg: number;
  avg_utility_dmg_per_match: number;
}
