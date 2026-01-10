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
                <p className="text-slate-500">No trend data available yet.</p>
            </Card>
        );
    }

    return (
        <Card className="h-[300px]">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-slate-900">Visibility Trend (30 Days)</h3>
            </div>
            <div className="h-[220px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={formattedData}>
                        <defs>
                            <linearGradient id="colorVis" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#2563eb" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />
                        <XAxis
                            dataKey="displayDate"
                            stroke="#64748b"
                            fontSize={12}
                            tickLine={false}
                            axisLine={false}
                            minTickGap={30}
                        />
                        <YAxis
                            stroke="#64748b"
                            fontSize={12}
                            tickLine={false}
                            axisLine={false}
                            tickFormatter={(value) => `${value}%`}
                            domain={[0, 100]}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: "#ffffff",
                                borderColor: "#e5e7eb",
                                color: "#1e293b",
                                borderRadius: "0.5rem",
                                boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                            }}
                            itemStyle={{ color: "#2563eb" }}
                            formatter={(value: number) => [`${value}%`, "Visibility"]}
                        />
                        <Area
                            type="monotone"
                            dataKey="visibility_score"
                            stroke="#2563eb"
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
