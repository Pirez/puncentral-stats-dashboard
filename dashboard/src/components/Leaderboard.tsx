// Fireworks animation CSS
const fireworkStyles = `
@keyframes firework-explode {
  0% { opacity: 1; transform: scale(0.5) translateY(0); }
  80% { opacity: 1; }
  100% { opacity: 0; transform: scale(1.2) translateY(-30px); }
}
.firework-dot {
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  opacity: 0.85;
  pointer-events: none;
  animation: firework-explode 1s ease-out forwards;
}
.firework-dot.fw1 { background: #ffec3d; left: 10px; animation-delay: 0s; }
.firework-dot.fw2 { background: #ff4d4f; left: 30px; animation-delay: 0.15s; }
.firework-dot.fw3 { background: #40a9ff; left: 22px; animation-delay: 0.3s; }
.firework-dot.fw4 { background: #73d13d; left: 38px; animation-delay: 0.45s; }
.firework-dot.fw5 { background: #9254de; left: 5px; animation-delay: 0.6s; }
`;
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import * as ApiTypes from '../types/api';
import { Trophy, TrendingUp, TrendingDown, Flame, Zap, Target, Bomb, ArrowUpDown, User } from 'lucide-react';
import { getPlayerAvatar } from '../config/playerAvatars';
import { GifOrImg } from './GifOrImg';

interface LeaderboardProps {
  players: ApiTypes.KDRatio[];
  multiKills: ApiTypes.MultiKillStats[];
  utilityDamage: ApiTypes.UtilityDamageStats[];
}

interface PlayerWithPoints {
  name: string;
  avg_kd: number;
  last_match_kd: number;
  kd_change: number;
  total_aces: number;
  total_quads: number;
  total_triples: number;
  total_utility_dmg: number;
  kdPoints: number;
  utilityPoints: number;
  acesPoints: number;
  quadsPoints: number;
  triplesPoints: number;
  totalPoints: number;
}

type SortCategory = 'totalPoints' | 'avg_kd' | 'total_utility_dmg' | 'total_aces' | 'total_quads' | 'total_triples';

export const Leaderboard = ({ players, multiKills, utilityDamage }: LeaderboardProps) => {
  // Inject fireworks CSS once
  React.useEffect(() => {
    if (typeof document !== 'undefined' && !document.getElementById('firework-css')) {
      const style = document.createElement('style');
      style.id = 'firework-css';
      style.innerHTML = fireworkStyles;
      document.head.appendChild(style);
    }
  }, []);
  // Glossy effect for top player
  const [showGloss, setShowGloss] = useState(true);
  useEffect(() => {
    const timer = setTimeout(() => setShowGloss(false), 5000);
    return () => clearTimeout(timer);
  }, []);
  const [sortBy, setSortBy] = useState<SortCategory>('totalPoints');
  // State for ace flame fade-out
  const [showAceFlame, setShowAceFlame] = useState(true);
  const [flameOpacity, setFlameOpacity] = useState(1);

  // Fade out the flame after 1 minute
  useEffect(() => {
    if (!showAceFlame) return;
    setFlameOpacity(1); // Reset opacity if component remounts
  let fade: ReturnType<typeof setInterval> | null = null;
  const fadeStart = setTimeout(() => {
      let step = 0;
      const steps = 20;
      const interval = 2000 / steps;
      fade = setInterval(() => {
        step++;
        setFlameOpacity(1 - step / steps);
        if (step >= steps) {
          setShowAceFlame(false);
          if (fade) clearInterval(fade);
        }
      }, interval);
  }, 10000); // 10 seconds
    return () => {
      clearTimeout(fadeStart);
      if (fade) clearInterval(fade);
    };
  }, [showAceFlame]);

  const getRankColor = (index: number) => {
    if (index === 0) return 'text-yellow-500';
    if (index === 1) return 'text-gray-400';
    if (index === 2) return 'text-orange-600';
    return 'text-gray-600';
  };

  const getRankIcon = (index: number) => {
    if (index < 3) {
      return <Trophy className={`h-5 w-5 ${getRankColor(index)}`} />;
    }
    return <span className="text-muted-foreground">{index + 1}</span>;
  };

  // Create a map for quick lookup of multi-kill stats by player name
  const multiKillMap = new Map(multiKills.map(mk => [mk.name, mk]));
  const utilityDamageMap = new Map(utilityDamage.map(ud => [ud.name, ud]));

  // Calculate points for each category (5 points for 1st, 4 for 2nd, etc.)
  const calculatePoints = (values: number[]): Map<number, number> => {
    const sorted = [...new Set(values)].sort((a, b) => b - a);
    const pointsMap = new Map<number, number>();
    const maxPoints = Math.min(players.length, 5);

    sorted.forEach((value, index) => {
      pointsMap.set(value, Math.max(maxPoints - index, 1));
    });

    return pointsMap;
  };

  // Calculate points for each category
  const kdValues = players.map(p => p.avg_kd);
  const kdPointsMap = calculatePoints(kdValues);

  const utilityValues = utilityDamage.map(u => u.total_utility_dmg);
  const utilityPointsMap = calculatePoints(utilityValues);

  const acesValues = multiKills.map(m => m.total_aces);
  const acesPointsMap = calculatePoints(acesValues);

  const quadsValues = multiKills.map(m => m.total_quads);
  const quadsPointsMap = calculatePoints(quadsValues);

  const triplesValues = multiKills.map(m => m.total_triples);
  const triplesPointsMap = calculatePoints(triplesValues);

  // Combine all data with points
  const playersWithPoints: PlayerWithPoints[] = players.map(player => {
    const playerMultiKills = multiKillMap.get(player.name);
    const playerUtilityDmg = utilityDamageMap.get(player.name);

    const kdPoints = kdPointsMap.get(player.avg_kd) || 0;
    const utilityPoints = utilityPointsMap.get(playerUtilityDmg?.total_utility_dmg || 0) || 0;
    const acesPoints = acesPointsMap.get(playerMultiKills?.total_aces || 0) || 0;
    const quadsPoints = quadsPointsMap.get(playerMultiKills?.total_quads || 0) || 0;
    const triplesPoints = triplesPointsMap.get(playerMultiKills?.total_triples || 0) || 0;

    return {
      name: player.name,
      avg_kd: player.avg_kd,
      last_match_kd: player.last_match_kd,
      kd_change: player.kd_change,
      total_aces: playerMultiKills?.total_aces || 0,
      total_quads: playerMultiKills?.total_quads || 0,
      total_triples: playerMultiKills?.total_triples || 0,
      total_utility_dmg: playerUtilityDmg?.total_utility_dmg || 0,
      kdPoints,
      utilityPoints,
      acesPoints,
      quadsPoints,
      triplesPoints,
      totalPoints: kdPoints + utilityPoints + acesPoints + quadsPoints + triplesPoints,
    };
  });

  // Sort players based on selected category
  const sortedPlayers = [...playersWithPoints].sort((a, b) => {
    if (sortBy === 'totalPoints') return b.totalPoints - a.totalPoints;
    if (sortBy === 'avg_kd') return b.avg_kd - a.avg_kd;
    if (sortBy === 'total_utility_dmg') return b.total_utility_dmg - a.total_utility_dmg;
    if (sortBy === 'total_aces') return b.total_aces - a.total_aces;
    if (sortBy === 'total_quads') return b.total_quads - a.total_quads;
    if (sortBy === 'total_triples') return b.total_triples - a.total_triples;
    return 0;
  });

  return (
    <Card className="col-span-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Trophy className="h-6 w-6 text-yellow-500" />
            Player Leaderboard
          </CardTitle>
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Sort by:</span>
            <button
              onClick={() => setSortBy('totalPoints')}
              className={`text-sm px-3 py-1 rounded transition-colors ${
                sortBy === 'totalPoints'
                  ? 'bg-primary text-primary-foreground dark:bg-primary dark:text-primary-foreground'
                  : 'bg-white text-gray-900 hover:bg-gray-100 border border-gray-300 dark:bg-muted dark:text-foreground dark:hover:bg-muted/80 dark:border-border'
              }`}
            >
              Total Points
            </button>
            <button
              onClick={() => setSortBy('avg_kd')}
              className={`text-sm px-3 py-1 rounded transition-colors ${
                sortBy === 'avg_kd'
                  ? 'bg-primary text-primary-foreground dark:bg-primary dark:text-primary-foreground'
                  : 'bg-white text-gray-900 hover:bg-gray-100 border border-gray-300 dark:bg-muted dark:text-foreground dark:hover:bg-muted/80 dark:border-border'
              }`}
            >
              K/D
            </button>
            <button
              onClick={() => setSortBy('total_aces')}
              className={`text-sm px-3 py-1 rounded transition-colors ${
                sortBy === 'total_aces'
                  ? 'bg-primary text-primary-foreground dark:bg-primary dark:text-primary-foreground'
                  : 'bg-white text-gray-900 hover:bg-gray-100 border border-gray-300 dark:bg-muted dark:text-foreground dark:hover:bg-muted/80 dark:border-border'
              }`}
            >
              Aces
            </button>
            <button
              onClick={() => setSortBy('total_quads')}
              className={`text-sm px-3 py-1 rounded transition-colors ${
                sortBy === 'total_quads'
                  ? 'bg-primary text-primary-foreground dark:bg-primary dark:text-primary-foreground'
                  : 'bg-white text-gray-900 hover:bg-gray-100 border border-gray-300 dark:bg-muted dark:text-foreground dark:hover:bg-muted/80 dark:border-border'
              }`}
            >
              Quads
            </button>
            <button
              onClick={() => setSortBy('total_triples')}
              className={`text-sm px-3 py-1 rounded transition-colors ${
                sortBy === 'total_triples'
                  ? 'bg-primary text-primary-foreground dark:bg-primary dark:text-primary-foreground'
                  : 'bg-white text-gray-900 hover:bg-gray-100 border border-gray-300 dark:bg-muted dark:text-foreground dark:hover:bg-muted/80 dark:border-border'
              }`}
            >
              Triples
            </button>
            <button
              onClick={() => setSortBy('total_utility_dmg')}
              className={`text-sm px-3 py-1 rounded transition-colors ${
                sortBy === 'total_utility_dmg'
                  ? 'bg-primary text-primary-foreground dark:bg-primary dark:text-primary-foreground'
                  : 'bg-white text-gray-900 hover:bg-gray-100 border border-gray-300 dark:bg-muted dark:text-foreground dark:hover:bg-muted/80 dark:border-border'
              }`}
            >
              Utility
            </button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Find the player with the most aces */}
          {(() => {
            const maxAces = Math.max(...sortedPlayers.map(p => p.total_aces));
            return sortedPlayers.map((player, index) => {
              const isAcesLeader = player.total_aces === maxAces && maxAces > 0;
              return (
                <div
                  key={player.name}
                  className="flex items-center justify-between p-4 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="flex items-center justify-center w-8">
                      {getRankIcon(index)}
                    </div>
                    <div className="relative">
                      {getPlayerAvatar(player.name) ? (
                        <div className="relative w-16 h-16">
                          {index === 0 && showGloss && (
                            <>
                              {/* Animated fireworks dots */}
                              <span className="firework-dot fw1" style={{ top: -18 }} />
                              <span className="firework-dot fw2" style={{ top: -10 }} />
                              <span className="firework-dot fw3" style={{ top: -22 }} />
                              <span className="firework-dot fw4" style={{ top: -16 }} />
                              <span className="firework-dot fw5" style={{ top: -25 }} />
                            </>
                          )}
                          <GifOrImg
                            src={getPlayerAvatar(player.name) || ''}
                            alt={player.name}
                            className="w-16 h-16 rounded-full border-2 border-primary/30"
                          />
                        </div>
                      ) : (
                        <div className="w-16 h-16 rounded-full border-2 border-primary/30 bg-muted flex items-center justify-center">
                          <User className="h-8 w-8 text-muted-foreground" />
                        </div>
                      )}
                      {isAcesLeader && (
                        showAceFlame && maxAces > 0 && (
                          <span
                            className="absolute -top-2 -right-2 text-2xl animate-bounce"
                            style={{ zIndex: 3, opacity: flameOpacity, transition: 'opacity 0.1s linear' }}
                            title="Ace Leader"
                            role="img"
                            aria-label="flame"
                          >🔥</span>
                        )
                      )}
                    </div>
                    <div>
                      <p className="font-semibold text-lg">{player.name}</p>
                      <p className="text-sm text-muted-foreground">
                        K/D: {player.avg_kd.toFixed(2)} ({player.kdPoints}pts)
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="flex items-center gap-4">
                      <div className="text-center">
                        <div className="flex items-center gap-1 justify-center">
                          <Flame className="h-4 w-4 text-red-500" />
                          <p className="text-xs text-muted-foreground">Aces</p>
                        </div>
                        <p className="font-semibold text-red-500">{player.total_aces}</p>
                        <p className="text-xs text-muted-foreground">{player.acesPoints}pts</p>
                      </div>
                      <div className="text-center">
                        <div className="flex items-center gap-1 justify-center">
                          <Zap className="h-4 w-4 text-orange-500" />
                          <p className="text-xs text-muted-foreground">Quads</p>
                        </div>
                        <p className="font-semibold text-orange-500">{player.total_quads}</p>
                        <p className="text-xs text-muted-foreground">{player.quadsPoints}pts</p>
                      </div>
                      <div className="text-center">
                        <div className="flex items-center gap-1 justify-center">
                          <Target className="h-4 w-4 text-yellow-500" />
                          <p className="text-xs text-muted-foreground">Triples</p>
                        </div>
                        <p className="font-semibold text-yellow-500">{player.total_triples}</p>
                        <p className="text-xs text-muted-foreground">{player.triplesPoints}pts</p>
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="flex items-center gap-1 justify-center">
                        <Bomb className="h-4 w-4 text-purple-500" />
                        <p className="text-xs text-muted-foreground">Utility</p>
                      </div>
                      <p className="font-semibold text-purple-500">{player.total_utility_dmg.toLocaleString()}</p>
                      <p className="text-xs text-muted-foreground">{player.utilityPoints}pts</p>
                    </div>
                    <div className="text-center border-l-2 border-primary/30 pl-6">
                      <div className="flex items-center gap-1 justify-center">
                        <Trophy className="h-5 w-5 text-yellow-500" />
                        <p className="text-xs text-muted-foreground">Total</p>
                      </div>
                      <p className="font-bold text-2xl text-yellow-500">{player.totalPoints}</p>
                      <p className="text-xs text-muted-foreground">points</p>
                    </div>
                  </div>
                </div>
              );
            });
          })()}
        </div>
      </CardContent>
    </Card>
  );
};
