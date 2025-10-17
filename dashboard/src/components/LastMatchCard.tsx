import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import * as ApiTypes from '../types/api';
import { Clock, Trophy, Skull, Target } from 'lucide-react';
import { formatLocalDateTime } from '../lib/utils';

interface LastMatchCardProps {
  match: ApiTypes.LastMatch;
}

export const LastMatchCard = ({ match }: LastMatchCardProps) => {
  const { match_info, players } = match;

  return (
    <Card className="col-span-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-6 w-6" />
            Last Match
          </CardTitle>
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">
              {formatLocalDateTime(match_info.date_time)}
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
      <CardContent>
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
                <th className="text-center py-3 px-2">MVPs</th>
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
                      <td className="text-center py-3 px-2">{player.mvps}</td>
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
      </CardContent>
    </Card>
  );
};
