import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import * as ApiTypes from '../types/api';
import { Map } from 'lucide-react';

interface MapWinRatesProps {
  data: ApiTypes.MapWinRate[];
}

export const MapWinRates = ({ data }: MapWinRatesProps) => {
  const getBarColor = (winRatio: number) => {
    if (winRatio >= 0.6) return '#22c55e'; // green
    if (winRatio >= 0.4) return '#eab308'; // yellow
    return '#ef4444'; // red
  };

  const getMapIcon = (mapName: string) => {
    const icons: Record<string, string> = {
      'ancient': '🏛️',
      'anubis': '🏜️',
      'inferno': '🔥',
      'mirage': '🌴',
      'nuke': '☢️',
      'overpass': '🌉',
      'vertigo': '🏢',
      'dust2': '🏜️',
      'train': '🚂',
    };
    return icons[mapName.toLowerCase()] || '🗺️';
  };

  const formattedData = data.map(item => ({
    ...item,
    map_name: item.map_name.replace('de_', ''),
    win_percentage: parseFloat((item.win_ratio * 100).toFixed(1)),
  }));

  return (
    <Card className="col-span-full lg:col-span-1">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Map className="h-6 w-6" />
          Map Win Rates
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={formattedData} layout="vertical" margin={{ left: 10, right: 30 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" domain={[0, 100]} />
            <YAxis dataKey="map_name" type="category" width={70} tick={{ fontSize: 12 }} />
            <Tooltip
              formatter={(value: any, name: string) => {
                if (name === 'win_percentage') return [`${value}%`, 'Win Rate'];
                return [value, name];
              }}
            />
            <Bar dataKey="win_percentage" name="Win Rate (%)" radius={[0, 4, 4, 0]}>
              {formattedData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getBarColor(entry.win_ratio)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <div className="mt-4 space-y-2">
          {formattedData.map((map) => (
            <div key={map.map_name} className="flex justify-between items-center text-sm">
              <div className="flex items-center gap-2">
                <span className="text-lg">{getMapIcon(map.map_name)}</span>
                <span className="font-medium capitalize">{map.map_name}</span>
              </div>
              <span className="text-muted-foreground">
                {map.total_wins}W / {map.total_matches - map.total_wins}L
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
