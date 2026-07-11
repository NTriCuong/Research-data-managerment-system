import { StatusBreakdownItem } from "@/services/reports/report.service";
import { BarChart3 } from "lucide-react";
import {
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    Tooltip,
    Legend,
} from "recharts";

export const STATUS_CONFIG: Record<
    string,
    {
        label: string;
        color: string;
        bg: string;
        hex: string;
    }
> = {
    draft: {
        label: 'Bản nháp',
        color: 'bg-gray-400',
        bg: 'bg-gray-50',
        hex: '#9CA3AF',
    },
    pending_review: {
        label: 'Chờ xét duyệt',
        color: 'bg-yellow-400',
        bg: 'bg-yellow-50',
        hex: '#FACC15',
    },
    revision_required: {
        label: 'Yêu cầu sửa',
        color: 'bg-orange-400',
        bg: 'bg-orange-50',
        hex: '#FB923C',
    },
    approved: {
        label: 'Đã duyệt',
        color: 'bg-green-500',
        bg: 'bg-green-50',
        hex: '#22C55E',
    },
    rejected: {
        label: 'Từ chối',
        color: 'bg-red-500',
        bg: 'bg-red-50',
        hex: '#EF4444',
    },
    published: {
        label: 'Đã xuất bản',
        color: 'bg-blue-500',
        bg: 'bg-blue-50',
        hex: '#3B82F6',
    },
    pending_approval: {
        label: 'Chờ phê duyệt',
        color: 'bg-indigo-400',
        bg: 'bg-indigo-50',
        hex: '#818CF8',
    },
}
function StatusBreakdownCard({ items, loading }: { items: StatusBreakdownItem[]; loading: boolean }) {
    const total = items.reduce((s, i) => s + i.count, 0)
    console.log(items);
    const chartData = items.map(item => ({
        name: STATUS_CONFIG[item.status]?.label ?? item.status,
        value: item.count,
        color: STATUS_CONFIG[item.status]?.hex ?? "#94a3b8",
    }));

    return (
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
                <BarChart3 size={16} className="text-gray-400" />
                <h3 className="text-sm font-semibold text-gray-700">Phân bổ trạng thái</h3>
            </div>

            {loading ? (
                <div className="space-y-3">
                    {[1, 2, 3, 4].map((i) => (
                        <div key={i} className="h-8 animate-pulse rounded bg-gray-100" />
                    ))}
                </div>
            ) : total === 0 ? (
                <p className="py-6 text-center text-sm text-gray-400">Không có dữ liệu</p>
            ) : (
                <ResponsiveContainer width="100%" height={320}>
                    <PieChart>
                        <Legend
                            verticalAlign="top"
                            align="left"
                            layout="vertical"
                            wrapperStyle={{
                                paddingBottom: 20,
                                fontSize: 13,
                            }}
                        />
                        <Pie
                            data={chartData}
                            dataKey="value"
                            nameKey="name"
                            cx="50%"
                            cy="50%"
                            innerRadius={70}
                            outerRadius={110}
                            paddingAngle={2}
                            label
                            labelLine
                        >
                            {chartData.map((entry) => (
                                <Cell
                                    key={entry.name}
                                    fill={entry.color}
                                />
                            ))}
                        </Pie>

                        <Tooltip />
                    </PieChart>
                </ResponsiveContainer>
            )}
        </div>
    )
}
export default StatusBreakdownCard;
