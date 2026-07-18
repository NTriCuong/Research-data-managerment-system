"use client"

import { useMemo, useState } from "react"
import { Trophy } from "lucide-react"
import { Bar, BarChart, LabelList, XAxis, YAxis } from "recharts"

import {
    Card,
    CardAction,
    CardContent,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import {
    ChartContainer,
    ChartTooltip,
    ChartTooltipContent,
    type ChartConfig,
} from "@/components/ui/chart"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"

export const description = "Top nghiên cứu được xem nhiều nhất trong năm"

interface TopResearchYearItem {
    research_id: string
    title: string
    views: number
}

// mock data - thay bằng data thật từ API sau (GET /reports/research-views/top/year?year=&limit=)
const mockData: Record<number, TopResearchYearItem[]> = {
    2026: [
        { research_id: "1", title: "Ứng dụng AI trong chẩn đoán hình ảnh y khoa", views: 45123 },
        { research_id: "2", title: "Phân tích dữ liệu lớn trong quản trị doanh nghiệp", views: 39347 },
        { research_id: "3", title: "Mô hình dự báo biến đổi khí hậu khu vực ĐBSCL", views: 34122 },
        { research_id: "4", title: "Xử lý ngôn ngữ tự nhiên tiếng Việt", views: 26441 },
        { research_id: "5", title: "Tối ưu hóa năng lượng tái tạo", views: 25238 },
        { research_id: "6", title: "Công nghệ sinh học trong xử lý nước thải", views: 17982 },
        { research_id: "7", title: "Nghiên cứu vật liệu composite tiên tiến", views: 15671 },
        { research_id: "8", title: "An toàn thông tin trong hệ thống IoT", views: 12412 },
        { research_id: "9", title: "Blockchain trong chuỗi cung ứng nông sản", views: 9312 },
        { research_id: "10", title: "Robot tự hành trong nông nghiệp thông minh", views: 6098 },
    ],
    2025: [
        { research_id: "11", title: "Nghiên cứu giống lúa chịu mặn ĐBSCL", views: 31220 },
        { research_id: "12", title: "Ứng dụng IoT trong nông nghiệp thông minh", views: 27890 },
        { research_id: "13", title: "Phân tích ngữ nghĩa văn bản pháp luật", views: 22140 },
        { research_id: "14", title: "Mô hình học sâu trong dự báo dịch bệnh", views: 18760 },
        { research_id: "15", title: "Vật liệu nano trong xử lý môi trường", views: 15980 },
        { research_id: "16", title: "Kinh tế tuần hoàn trong ngành dệt may", views: 12030 },
        { research_id: "17", title: "Hệ thống điện mặt trời áp mái", views: 9540 },
        { research_id: "18", title: "Bảo tồn đa dạng sinh học rừng ngập mặn", views: 7210 },
    ],
}

const chartConfig = {
    views: {
        label: "Lượt xem",
        color: "#3b82f6",
    },
} satisfies ChartConfig

const MIN_YEAR = 2000
const CURRENT_YEAR = new Date().getFullYear()
const YEAR_OPTIONS = Array.from(
    { length: CURRENT_YEAR - MIN_YEAR + 1 },
    (_, i) => CURRENT_YEAR - i,
)

function truncateTitle(title: string, max = 28) {
    return title.length > max ? `${title.slice(0, max)}…` : title
}

interface BarChartTopResearchByYearProps {
    data?: Record<number, TopResearchYearItem[]>
    limit?: number
}

export default function BarChartTopResearchByYear({
    data = mockData,
    limit = 10,
}: BarChartTopResearchByYearProps) {
    const [year, setYear] = useState(CURRENT_YEAR)

    const chartData = useMemo(() => {
        return [...(data[year] ?? [])]
            .sort((a, b) => b.views - a.views)
            .slice(0, limit)
            .map((item, index) => ({
                ...item,
                rank: index + 1,
                shortTitle: truncateTitle(item.title),
            }))
    }, [data, year, limit])

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Trophy className="h-4 w-4 text-amber-500" />
                    Top nghiên cứu được xem nhiều nhất năm
                </CardTitle>
                <CardAction>
                    <Select value={String(year)} onValueChange={(v) => setYear(Number(v))}>
                        <SelectTrigger size="sm" className="w-[92px]">
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            {YEAR_OPTIONS.map((y) => (
                                <SelectItem key={y} value={String(y)}>
                                    {y}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </CardAction>
            </CardHeader>
            <CardContent>
                {chartData.length === 0 ? (
                    <p className="py-10 text-center text-sm text-muted-foreground">
                        Chưa có dữ liệu lượt xem trong năm {year}
                    </p>
                ) : (
                    <ChartContainer
                        config={chartConfig}
                        className="w-full"
                        style={{ height: Math.max(chartData.length * 44, 120) }}
                    >
                        <BarChart
                            accessibilityLayer
                            data={chartData}
                            layout="vertical"
                            margin={{ left: 12, right: 36 }}
                        >
                            <XAxis type="number" dataKey="views" hide />
                            <YAxis
                                dataKey="shortTitle"
                                type="category"
                                tickLine={false}
                                tickMargin={10}
                                axisLine={false}
                                width={220}
                                tickFormatter={(value: string, index: number) =>
                                    `#${index + 1}  ${value}`
                                }
                            />
                            <ChartTooltip
                                cursor={false}
                                content={
                                    <ChartTooltipContent
                                        labelFormatter={(_, payload) => payload?.[0]?.payload?.title ?? ""}
                                    />
                                }
                            />
                            <Bar dataKey="views" fill="var(--color-views)" radius={5} barSize={20}>
                                <LabelList
                                    dataKey="views"
                                    position="right"
                                    className="fill-foreground"
                                    fontSize={12}
                                    formatter={(value) => Number(value).toLocaleString("vi-VN")}
                                />
                            </Bar>
                        </BarChart>
                    </ChartContainer>
                )}
            </CardContent>
            <CardFooter className="flex-col items-start gap-2 text-sm">
                <div className="leading-none text-muted-foreground">
                    Xếp hạng theo tổng lượt xem trong năm {year}
                </div>
            </CardFooter>
        </Card>
    )
}
