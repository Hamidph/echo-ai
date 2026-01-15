"use client";

import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import Card from "@/components/ui/Card";

interface ShareOfVoiceItem {
    brand: string;
    percentage: number;
}

interface ShareOfVoiceChartProps {
    data: ShareOfVoiceItem[];
}

const COLORS = ["#2563eb", "#8b5cf6", "#f59e0b", "#10b981", "#ef4444", "#6366f1"];

export function ShareOfVoiceChart({ data }: ShareOfVoiceChartProps) {
    if (!data || data.length === 0) {
        return (
            <Card className="h-[300px] flex items-center justify-center">
                <p className="text-slate-500">No share of voice data available yet.</p>
            </Card>
        );
    }

    return (
        <Card className="h-[300px]">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-slate-900">Share of Voice</h3>
            </div>
            <div className="h-[220px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={data}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={80}
                            paddingAngle={5}
                            dataKey="percentage"
                            nameKey="brand"
                        >
                            {data.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                        </Pie>
                        <Tooltip
                            contentStyle={{
                                backgroundColor: "#ffffff",
                                borderColor: "#e5e7eb",
                                color: "#1e293b",
                                borderRadius: "0.5rem",
                                boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                            }}
                            itemStyle={{ color: "#1e293b" }}
                            formatter={(value: number) => [`${value}%`, "Share"]}
                        />
                        <Legend
                            verticalAlign="middle"
                            align="right"
                            layout="vertical"
                            iconType="circle"
                            wrapperStyle={{ fontSize: "12px", color: "#64748b" }}
                        />
                    </PieChart>
                </ResponsiveContainer>
            </div>
        </Card>
    );
}
