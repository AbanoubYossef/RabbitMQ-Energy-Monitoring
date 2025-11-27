import React from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { HourlyData } from '../../api/monitoringApi';

interface EnergyChartProps {
  data: HourlyData[];
  chartType: 'bar' | 'line';
  title: string;
}

const EnergyChart: React.FC<EnergyChartProps> = ({ data, chartType, title }) => {
  // Format data for recharts
  const chartData = data.map((item) => ({
    hour: `${item.hour}:00`,
    consumption: parseFloat(item.total_consumption.toFixed(3)),
    measurements: item.measurement_count,
  }));

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 border border-gray-300 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-900">{payload[0].payload.hour}</p>
          <p className="text-sm text-indigo-600">
            Consumption: <span className="font-bold">{payload[0].value} kWh</span>
          </p>
          <p className="text-sm text-gray-600">
            Measurements: {payload[0].payload.measurements}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={400}>
        {chartType === 'bar' ? (
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="hour"
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
            />
            <YAxis
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
              label={{ value: 'Energy (kWh)', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar
              dataKey="consumption"
              fill="#4f46e5"
              name="Energy Consumption (kWh)"
              radius={[8, 8, 0, 0]}
            />
          </BarChart>
        ) : (
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="hour"
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
            />
            <YAxis
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
              label={{ value: 'Energy (kWh)', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line
              type="monotone"
              dataKey="consumption"
              stroke="#4f46e5"
              strokeWidth={3}
              name="Energy Consumption (kWh)"
              dot={{ fill: '#4f46e5', r: 5 }}
              activeDot={{ r: 7 }}
            />
          </LineChart>
        )}
      </ResponsiveContainer>
    </div>
  );
};

export default EnergyChart;
