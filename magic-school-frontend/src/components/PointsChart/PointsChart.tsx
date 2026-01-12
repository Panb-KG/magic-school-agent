import React from 'react';
import ReactECharts from 'echarts-for-react';
import type { PointsTrendData } from '@/types';

interface PointsChartProps {
  data: PointsTrendData;
}

export const PointsChart: React.FC<PointsChartProps> = ({ data }) => {
  const getOption = () => {
    const dates = data.data.map((item) => item.date);
    const points = data.data.map((item) => item.points);
    const dailyGains = data.data.map((item) => item.daily_gain);

    return {
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: '#7C3AED',
        textStyle: {
          color: '#333',
        },
      },
      legend: {
        data: ['总积分', '每日获得'],
        top: 10,
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: '15%',
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        data: dates,
        axisLine: {
          lineStyle: {
            color: '#7C3AED',
          },
        },
      },
      yAxis: [
        {
          type: 'value',
          name: '积分',
          position: 'left',
          axisLine: {
            show: true,
            lineStyle: {
              color: '#7C3AED',
            },
          },
          splitLine: {
            lineStyle: {
              type: 'dashed',
              color: '#E5E7EB',
            },
          },
        },
        {
          type: 'value',
          name: '每日获得',
          position: 'right',
          axisLine: {
            show: true,
            lineStyle: {
              color: '#F59E0B',
            },
          },
          splitLine: {
            show: false,
          },
        },
      ],
      series: [
        {
          name: '总积分',
          type: 'line',
          data: points,
          smooth: true,
          itemStyle: {
            color: '#7C3AED',
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(124, 58, 237, 0.3)' },
                { offset: 1, color: 'rgba(124, 58, 237, 0.05)' },
              ],
            },
          },
        },
        {
          name: '每日获得',
          type: 'bar',
          data: dailyGains,
          yAxisIndex: 1,
          itemStyle: {
            color: '#F59E0B',
            borderRadius: [4, 4, 0, 0],
          },
        },
      ],
    };
  };

  return (
    <div className="magic-card p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold magic-title">📈 积分趋势</h2>
        <span className="text-sm text-gray-500">
          近 {data.days} 天 · 总获得 {data.summary.total_gain} 分
        </span>
      </div>

      <ReactECharts option={getOption()} style={{ height: '400px' }} />

      {/* 统计摘要 */}
      <div className="grid grid-cols-3 gap-4 mt-6 pt-4 border-t border-gray-200">
        <div className="text-center">
          <div className="text-sm text-gray-600 mb-1">总获得</div>
          <div className="text-xl font-bold text-magic-primary">
            {data.summary.total_gain}
          </div>
          <div className="text-xs text-gray-500">积分</div>
        </div>
        <div className="text-center">
          <div className="text-sm text-gray-600 mb-1">日均获得</div>
          <div className="text-xl font-bold text-magic-secondary">
            {data.summary.average_daily_gain.toFixed(1)}
          </div>
          <div className="text-xs text-gray-500">积分/天</div>
        </div>
        <div className="text-center">
          <div className="text-sm text-gray-600 mb-1">最佳日</div>
          <div className="text-xl font-bold text-magic-accent">
            {data.summary.best_day}
          </div>
          <div className="text-xs text-gray-500">日期</div>
        </div>
      </div>
    </div>
  );
};
