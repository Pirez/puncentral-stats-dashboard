import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { type LucideProps } from 'lucide-react';
import { type ForwardRefExoticComponent, type RefAttributes } from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: ForwardRefExoticComponent<Omit<LucideProps, "ref"> & RefAttributes<SVGSVGElement>>;
  description?: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
}

export const StatCard = ({ title, value, icon: Icon, description, trend }: StatCardProps) => {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {description && (
          <p className="text-xs text-muted-foreground">{description}</p>
        )}
        {trend && (
          <p className={`text-xs ${trend.isPositive ? 'text-green-500' : 'text-red-500'}`}>
            {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value).toFixed(2)}
          </p>
        )}
      </CardContent>
    </Card>
  );
};
