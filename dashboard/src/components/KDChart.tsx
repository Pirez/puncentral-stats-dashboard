import { useState } from 'react';
import { PLAYER_COLORS, DEFAULT_COLORS } from './playerColors';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import * as ApiTypes from '../types/api';
import { TrendingUp } from 'lucide-react';
import { utcToLocal, formatChartDateTime } from '../lib/utils';

interface KDChartProps {
  data: ApiTypes.KDOverTime[];
}



const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div style={{
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        border: '1px solid #334155',
        borderRadius: '8px',
        padding: '12px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)'
      }}>
        <p style={{ color: '#e2e8f0', fontWeight: 'bold', marginBottom: '8px', fontSize: '13px' }}>
          {label}
        </p>
        {payload.map((entry: any, index: number) => (
          <div key={index} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <div style={{
              width: '12px',
              height: '12px',
              backgroundColor: entry.color,
              borderRadius: '2px'
            }} />
            <span style={{ color: '#94a3b8', fontSize: '12px', minWidth: '80px' }}>
              {entry.name}:
            </span>
            <span style={{ color: '#e2e8f0', fontWeight: 'bold', fontSize: '13px' }}>
              {entry.value?.toFixed(2)}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export const KDChart = ({ data }: KDChartProps) => {
  // Group data by player
  const playerNames = [...new Set(data.map(d => d.name))].sort();

  // State to track which players are visible
  const [visiblePlayers, setVisiblePlayers] = useState<Record<string, boolean>>(
    playerNames.reduce((acc, name) => ({ ...acc, [name]: true }), {})
  );

  // Transform data for recharts - use match_id + time as unique key
  const matchGroups = new Map<string, any>();

  data.forEach((curr) => {
    const key = `${curr.match_id}`;
    if (!matchGroups.has(key)) {
      const formattedDate = formatChartDateTime(curr.date_time);
      matchGroups.set(key, {
        match_id: curr.match_id,
        date_time: formattedDate,
        map_name: curr.map_name.replace('de_', ''),
        full_date: curr.date_time,
      });
    }
    matchGroups.get(key)[curr.name] = curr.match_kd;
  });

  // Convert to array and sort by date (using UTC conversion for proper sorting)
  const transformedData = Array.from(matchGroups.values()).sort(
    (a, b) => utcToLocal(a.full_date).getTime() - utcToLocal(b.full_date).getTime()
  );

  // Handle legend click to toggle player visibility
  const handleLegendClick = (dataKey: string) => {
    setVisiblePlayers(prev => ({
      ...prev,
      [dataKey]: !prev[dataKey]
    }));
  };

  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-6 w-6" />
            K/D Ratio Over Time - {transformedData.length} Matches
          </div>
          <button
            onClick={() => setVisiblePlayers(playerNames.reduce((acc, name) => ({ ...acc, [name]: true }), {}))}
            className="text-sm px-3 py-1 rounded bg-primary/20 hover:bg-primary/30 transition-colors"
          >
            Show All
          </button>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={450}>
          <LineChart
            data={transformedData}
            margin={{ top: 5, right: 30, left: 0, bottom: 80 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis
              dataKey="date_time"
              tick={{ fontSize: 11, fill: '#94a3b8' }}
              angle={-45}
              textAnchor="end"
              height={80}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fontSize: 12, fill: '#94a3b8' }}
              label={{ value: 'K/D Ratio', angle: -90, position: 'insideLeft', fill: '#94a3b8' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ paddingTop: '20px', cursor: 'pointer' }}
              iconType="line"
              onClick={(e) => handleLegendClick(e.dataKey as string)}
            />
            {playerNames.map((name, index) => {
              // Use custom color for Nifty and Dybbis, fallback to default palette
              const color = PLAYER_COLORS[name] || DEFAULT_COLORS[index % DEFAULT_COLORS.length];
              return (
                <Line
                  key={name}
                  type="monotone"
                  dataKey={name}
                  stroke={color}
                  strokeWidth={2.5}
                  dot={{ r: 3, strokeWidth: 2 }}
                  activeDot={{ r: 7, strokeWidth: 2 }}
                  connectNulls
                  hide={!visiblePlayers[name]}
                  strokeOpacity={visiblePlayers[name] ? 1 : 0.2}
                />
              );
            })}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};
