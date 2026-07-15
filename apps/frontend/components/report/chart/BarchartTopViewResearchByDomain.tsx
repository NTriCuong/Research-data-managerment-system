"use client";

import {
    Bar,
    BarChart,
    CartesianGrid,
    Cell,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";

interface TopResearchByDomainItem {
    research_id: string;
    title: string;
    views: number;
}

// mock data - thay bằng data thật từ API sau
const mockData: TopResearchByDomainItem[] = [
    { research_id: "1", title: "Ứng dụng AI trong chẩn đoán hình ảnh y khoa", views: 451232 },
    { research_id: "2", title: "Phân tích dữ liệu lớn trong quản trị doanh nghiệp", views: 393478 },
    { research_id: "3", title: "Nghiên cứu vật liệu composite tiên tiến", views: 35671 },
    { research_id: "4", title: "Mô hình dự báo biến đổi khí hậu khu vực ĐBSCL", views: 341220 },
    { research_id: "5", title: "Blockchain trong chuỗi cung ứng nông sản", views: 3312 },
    { research_id: "6", title: "Tối ưu hóa năng lượng tái tạo", views: 252387 },
    { research_id: "7", title: "Xử lý ngôn ngữ tự nhiên tiếng Việt", views: 264415 },
    { research_id: "8", title: "An toàn thông tin trong hệ thống IoT", views: 24121 },
    { research_id: "9", title: "Robot tự hành trong nông nghiệp thông minh", views: 10098 },
    { research_id: "10", title: "Công nghệ sinh học trong xử lý nước thải", views: 179826 },
];

function truncateTitle(title: string, max = 30) {
    return title.length > max ? title.slice(0, max) + "…" : title;
}

interface BarchartTopViewResearchByDomainProps {
    data?: TopResearchByDomainItem[];
}

export default function BarchartTopViewResearchByDomain({
    data = mockData,
}: BarchartTopViewResearchByDomainProps) {
    const chartData = [...data]
        .sort((a, b) => b.views - a.views)
        .slice(0, 10)
        .map((item) => ({ ...item, shortTitle: truncateTitle(item.title) }));

    return (
        <div className="w-full rounded-lg border bg-white p-4 shadow-sm">
            <h3 className="mb-4 text-base font-medium">Top nghiên cứu theo lĩnh vực</h3>
            <ResponsiveContainer width="100%" height={420}>
                <BarChart
                    data={chartData}
                    layout="vertical"
                    margin={{ top: 8, right: 24, left: 8, bottom: 8 }}
                >
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                    <XAxis
                        type="number"
                        allowDecimals={false}
                        tickFormatter={(value: number) => value.toLocaleString("vi-VN")}
                    />
                    <YAxis
                        type="category"
                        dataKey="shortTitle"
                        width={220}
                        tick={{ fontSize: 12 }}
                    />
                    <Tooltip
                        formatter={(value) => [Number(value).toLocaleString(), "Lượt xem"]}
                        labelFormatter={(_, payload) => payload?.[0]?.payload?.title ?? ""}
                    />
                    <Bar dataKey="views" fill="#2a78d6" radius={[0, 4, 4, 0]}>
                        {chartData.map((entry) => (
                            <Cell key={entry.research_id} />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}