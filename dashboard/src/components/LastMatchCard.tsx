import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import * as ApiTypes from '../types/api';
import { Clock, Trophy, Skull, Target, ChevronDown, ChevronUp } from 'lucide-react';
import { apiService } from '../services/api';

interface LastMatchCardProps {
  match: ApiTypes.LastMatch;
}

export const LastMatchCard = ({ match: initialMatch }: LastMatchCardProps) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [allMatches, setAllMatches] = useState<ApiTypes.MapStats[]>([]);
  const [selectedMatchId, setSelectedMatchId] = useState<string>('');
  const [currentMatch, setCurrentMatch] = useState<ApiTypes.LastMatch>(initialMatch);
  const [loadingMatch, setLoadingMatch] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [matchDataCache, setMatchDataCache] = useState<Map<string, ApiTypes.LastMatch>>(new Map());

  // Fetch all matches for the dropdown
  useEffect(() => {
    const fetchMatches = async () => {
      try {
        setError(null);
        const matches = await apiService.getMapStats();
        // Sort by date descending (most recent first)
        const sortedMatches = matches.sort((a, b) =>
          new Date(b.date_time).getTime() - new Date(a.date_time).getTime()
        );
        setAllMatches(sortedMatches);
        // Set the initial match as selected
        if (sortedMatches.length > 0) {
          setSelectedMatchId(sortedMatches[0].match_id);
        }
      } catch (error) {
        console.error('Failed to fetch matches:', error);
        setError('Failed to load match history. Please try again later.');
      }
    };
    fetchMatches();
  }, []);

  // Fetch specific match data when selection changes
  useEffect(() => {
    // Get initial match ID more safely
    const initialMatchId = initialMatch.match_info?.date_time
      ? (initialMatch.players[0]?.match_id || '')
      : '';

    if (!selectedMatchId || selectedMatchId === initialMatchId) {
      setCurrentMatch(initialMatch);
      // Cache the initial match
      if (initialMatchId) {
        setMatchDataCache(prev => new Map(prev).set(initialMatchId, initialMatch));
      }
      return;
    }

    // Check cache first
    const cachedMatch = matchDataCache.get(selectedMatchId);
    if (cachedMatch) {
      setCurrentMatch(cachedMatch);
      return;
    }

    const fetchMatchData = async () => {
      setLoadingMatch(true);
      setError(null);
      try {
        const playerStats = await apiService.getPlayerStats();
        const matchPlayers = playerStats.filter(p => p.match_id === selectedMatchId);
        const matchInfo = allMatches.find(m => m.match_id === selectedMatchId);

        if (matchInfo) {
          const newMatch: ApiTypes.LastMatch = {
            players: matchPlayers.map(p => ({
              match_id: p.match_id,
              kills_total: p.kills_total,
              deaths_total: p.deaths_total,
              dmg: p.dmg,
              utility_dmg: p.utility_dmg,
              he_dmg: p.he_dmg,
              molotov_dmg: p.molotov_dmg,
              headshot_kills_total: p.headshot_kills_total,
              ace_rounds_total: p.ace_rounds_total,
              quad_rounds_total: p.quad_rounds_total,
              triple_rounds_total: p.triple_rounds_total,
              mvps: p.mvps,
              name: p.name,
              created_at: p.created_at,
            })),
            match_info: {
              map_name: matchInfo.map_name,
              date_time: matchInfo.date_time,
              won: matchInfo.won === 1,
            },
          };
          setCurrentMatch(newMatch);
          // Cache the fetched match
          setMatchDataCache(prev => new Map(prev).set(selectedMatchId, newMatch));
        }
      } catch (error) {
        console.error('Failed to fetch match data:', error);
        setError('Failed to load match details. Please try again.');
      } finally {
        setLoadingMatch(false);
      }
    };

    fetchMatchData();
  }, [selectedMatchId, initialMatch, allMatches, matchDataCache]);

  const { match_info, players } = currentMatch;

  return (
    <Card className="col-span-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="flex items-center gap-2 hover:opacity-80 transition-opacity"
              aria-label={isExpanded ? 'Collapse match details' : 'Expand match details'}
            >
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-6 w-6" />
                Match Details
                {isExpanded ? (
                  <ChevronUp className="h-5 w-5" />
                ) : (
                  <ChevronDown className="h-5 w-5" />
                )}
              </CardTitle>
            </button>
            {allMatches.length > 0 && (
              <select
                value={selectedMatchId}
                onChange={(e) => setSelectedMatchId(e.target.value)}
                className="px-3 py-1 rounded border border-border bg-background text-sm hover:bg-muted transition-colors"
                aria-label="Select match"
              >
                {allMatches.map((match, index) => (
                  <option key={match.match_id} value={match.match_id}>
                    {index === 0 ? 'Last Match - ' : ''}
                    {match.map_name.replace('de_', '')} - {new Date(match.date_time).toLocaleDateString()}
                  </option>
                ))}
              </select>
            )}
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">
              {new Date(match_info.date_time).toLocaleString()}
            </span>
            <span className="text-sm font-medium">{match_info.map_name.replace('de_', '')}</span>
            <span
              className={`px-3 py-1 rounded-full text-sm font-bold ${
                match_info.won
                  ? 'bg-green-500/20 text-green-500'
                  : 'bg-red-500/20 text-red-500'
              }`}
            >
              {match_info.won ? 'VICTORY' : 'DEFEAT'}
            </span>
          </div>
        </div>
      </CardHeader>
      {isExpanded && (
        <CardContent aria-expanded={isExpanded}>
          {error && (
            <div className="mb-4 p-3 rounded bg-red-500/10 border border-red-500/20 text-red-500 text-sm">
              {error}
            </div>
          )}
          {loadingMatch ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-2">Player</th>
                    <th className="text-center py-3 px-2">
                      <div className="flex items-center justify-center gap-1">
                        <Target className="h-4 w-4" />
                        K/D
                      </div>
                    </th>
                    <th className="text-center py-3 px-2">Kills</th>
                    <th className="text-center py-3 px-2">Deaths</th>
                    <th className="text-center py-3 px-2">Damage</th>
                    <th className="text-center py-3 px-2">
                      <div className="flex items-center justify-center gap-1">
                        <Skull className="h-4 w-4" />
                        HS
                      </div>
                    </th>
                    <th className="text-center py-3 px-2">
                      <div className="flex items-center justify-center gap-1">
                        <Trophy className="h-4 w-4" />
                        Multi
                      </div>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {players
                    .sort((a, b) => b.kills_total - a.kills_total)
                    .map((player) => {
                      const kd = (player.kills_total / Math.max(player.deaths_total, 1)).toFixed(2);
                      const multiKills = player.ace_rounds_total + player.quad_rounds_total + player.triple_rounds_total;

                      return (
                        <tr key={player.name} className="border-b hover:bg-muted/50">
                          <td className="py-3 px-2 font-semibold">{player.name}</td>
                          <td className="text-center py-3 px-2">
                            <span
                              className={`font-bold ${
                                parseFloat(kd) >= 1.5
                                  ? 'text-green-500'
                                  : parseFloat(kd) >= 1.0
                                  ? 'text-yellow-500'
                                  : 'text-red-500'
                              }`}
                            >
                              {kd}
                            </span>
                          </td>
                          <td className="text-center py-3 px-2 text-green-500 font-semibold">
                            {player.kills_total}
                          </td>
                          <td className="text-center py-3 px-2 text-red-500 font-semibold">
                            {player.deaths_total}
                          </td>
                          <td className="text-center py-3 px-2">{player.dmg}</td>
                          <td className="text-center py-3 px-2">{player.headshot_kills_total}</td>
                          <td className="text-center py-3 px-2">
                            {multiKills > 0 && (
                              <span className="text-yellow-500 font-bold">{multiKills}</span>
                            )}
                            {multiKills === 0 && <span className="text-muted-foreground">0</span>}
                          </td>
                        </tr>
                      );
                    })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      )}
    </Card>
  );
};
