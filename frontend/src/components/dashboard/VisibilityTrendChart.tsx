"use client";

import {
    Area,
    AreaChart,
    CartesianGrid,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";
import Card from "@/components/ui/Card";

interface TrendData {
    date: string;
    visibility_score: number;
}

interface VisibilityTrendChartProps {
    data: TrendData[];
}

export function VisibilityTrendChart({ data }: VisibilityTrendChartProps) {
    // Format date for display
    const formattedData = data.map((item) => ({
        ...item,
        displayDate: new Date(item.date).toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
        }),
    }));

    if (!data || data.length === 0) {
        return (
            <Card className="h-[300px] flex items-center justify-center">
                <p className="text-gray-500">No trend data available yet.</p>
            </Card>
        );
    }

    return (
        <Card className="h-[300px]">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">Visibility Trend (30 Days)</h3>
            </div>
            <div className="h-[220px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={formattedData}>
                        <defs>
                            <linearGradient id="colorVis" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                        <XAxis
                            dataKey="displayDate"
                            stroke="#9ca3af"
                            fontSize={12}
                            tickLine={false}
                            axisLine={false}
                            minTickGap={30}
                        />
                        <YAxis
                            stroke="#9ca3af"
                            fontSize={12}
                            tickLine={false}
                            axisLine={false}
                            tickFormatter={(value) => `${value}%`}
                            domain={[0, 100]}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: "#1f2937",
                                borderColor: "#374151",
                                color: "#f3f4f6",
                            }}
                            itemStyle={{ color: "#22d3ee" }}
                            formatter={(value: number) => [`${value}%`, "Visibility"]}
                        />
                        <Area
                            type="monotone"
                            dataKey="visibility_score"
                            stroke="#06b6d4"
                            fillOpacity={1}
                            fill="url(#colorVis)"
                            strokeWidth={2}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </Card>
    );
}
