import { useEffect, useState } from 'react';
import { apiService } from './services/api';
import { StatCard } from './components/StatCard';
import { Leaderboard } from './components/Leaderboard';
import { KDChart } from './components/KDChart';
import { MapWinRates } from './components/MapWinRates';
import { LastMatchCard } from './components/LastMatchCard';
import { AuthGate } from './components/AuthGate';
import {
  Trophy,
  TrendingUp,
  Map,
  Skull,
  Award,
} from 'lucide-react';
import { ThemeToggle } from './components/ThemeToggle';
import * as ApiTypes from './types/api';

function AppContent() {
  const [kdRatios, setKdRatios] = useState<ApiTypes.KDRatio[]>([]);
  const [kdOverTime, setKdOverTime] = useState<ApiTypes.KDOverTime[]>([]);
  const [mapWinRates, setMapWinRates] = useState<ApiTypes.MapWinRate[]>([]);
  const [lastMatch, setLastMatch] = useState<ApiTypes.LastMatch | null>(null);
  const [mapStats, setMapStats] = useState<ApiTypes.MapStats[]>([]);
  const [multiKills, setMultiKills] = useState<ApiTypes.MultiKillStats[]>([]);
  const [utilityDamage, setUtilityDamage] = useState<ApiTypes.UtilityDamageStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);

        // Fetch required data
        const [kdRatiosData, kdOverTimeData, mapWinRatesData, mapStatsData, multiKillsData, utilityDamageData] =
          await Promise.all([
            apiService.getKDRatios(),
            apiService.getKDOverTime(),
            apiService.getMapWinRates(),
            apiService.getMapStats(),
            apiService.getMultiKills(),
            apiService.getUtilityDamage(),
          ]);

        setKdRatios(kdRatiosData);
        setKdOverTime(kdOverTimeData);
        setMapWinRates(mapWinRatesData);
        setMapStats(mapStatsData);
        setMultiKills(multiKillsData);
        setUtilityDamage(utilityDamageData);

        // Try to fetch last match data (optional)
        try {
          const lastMatchData = await apiService.getLastMatch();
          setLastMatch(lastMatchData);
        } catch (lastMatchErr) {
          console.warn('Last match data not available:', lastMatchErr);
          setLastMatch(null);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#0f172a', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ border: '4px solid #3b82f6', borderTop: '4px solid transparent', borderRadius: '50%', width: '48px', height: '48px', animation: 'spin 1s linear infinite', margin: '0 auto 16px' }}></div>
          <p>Loading stats from API...</p>
          <p style={{ fontSize: '12px', marginTop: '8px', color: '#94a3b8' }}>API URL: {import.meta.env.VITE_API_URL || 'http://localhost:8000'}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#0f172a', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center', maxWidth: '600px', padding: '20px' }}>
          <h2 style={{ color: '#ef4444', marginBottom: '16px' }}>Error Loading Data</h2>
          <p style={{ marginBottom: '8px' }}>{error}</p>
          <p style={{ fontSize: '14px', color: '#94a3b8', marginBottom: '16px' }}>
            Make sure the API server is running at: {import.meta.env.VITE_API_URL || 'http://localhost:8000'}
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{ padding: '8px 16px', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const totalMatches = mapStats.length;
  const totalWins = mapStats.filter((m) => m.won === 1).length;
  const winRate = totalMatches > 0 ? (totalWins / totalMatches) * 100 : 0;

  const topPlayer = kdRatios.length > 0 ? kdRatios[0] : null;

  // Find the best map (highest win ratio)
  const bestMap = mapWinRates.length > 0
    ? mapWinRates.reduce((best, current) =>
        current.win_ratio > best.win_ratio ? current : best
      )
    : null;

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto p-6">
        <header className="mb-8">
          <div className="flex items-center justify-between">
            <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
              <Trophy className="h-10 w-10 text-yellow-500" />
              Pun-Central Stats Dashboard
            </h1>
            <ThemeToggle />
          </div>
          <p className="text-muted-foreground">
            FimLAN 2025 - One night, one LAN, one game. All the stats you need in one place.
          </p>
        </header>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-5 mb-6">
          <StatCard
            title="Total Matches"
            value={totalMatches}
            icon={Map}
            description="Matches played"
          />
          <StatCard
            title="Win Rate"
            value={`${winRate.toFixed(1)}%`}
            icon={Trophy}
            description={`${totalWins} wins / ${totalMatches - totalWins} losses`}
          />
          {topPlayer && (
            <StatCard
              title="Top Player"
              value={topPlayer.name}
              icon={Award}
              description={`${topPlayer.avg_kd.toFixed(2)} avg K/D`}
            />
          )}
          {bestMap && (
            <StatCard
              title="Best Map"
              value={bestMap.map_name.replace('de_', '')}
              icon={Map}
              description={`${(bestMap.win_ratio * 100).toFixed(1)}% win rate`}
            />
          )}
          {lastMatch && (
            <StatCard
              title="Last Match"
              value={lastMatch.match_info.won ? 'Victory' : 'Defeat'}
              icon={lastMatch.match_info.won ? TrendingUp : Skull}
              description={lastMatch.match_info.map_name.replace('de_', '')}
            />
          )}
        </div>


        {lastMatch && <LastMatchCard match={lastMatch} />}


        <div className="grid gap-6 lg:grid-cols-3 mt-6">
          <div className="lg:col-span-2">
            <Leaderboard players={kdRatios} multiKills={multiKills} utilityDamage={utilityDamage} />
          </div>
          <MapWinRates data={mapWinRates} />
        </div>

        <div className="mt-6">
          <KDChart data={kdOverTime} />
        </div>
      </div>
    </div>
  );
}


function App() {
  return (
    <AuthGate>
      <AppContent />
    </AuthGate>
  );
}

export default App;
