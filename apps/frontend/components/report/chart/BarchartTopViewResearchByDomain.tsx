"use client";

import { useEffect, useState } from "react";
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

import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { reportService, type TopResearchViewItem } from "@/services/reports/report.service";
import { referenceService, type Domain } from "@/services/reference/reference.service";

export const description = "Top nghiên cứu được xem nhiều nhất theo lĩnh vực";

function truncateTitle(title: string, max = 30) {
    return title.length > max ? title.slice(0, max) + "…" : title;
}

const MIN_YEAR = 2000;
const CURRENT_YEAR = new Date().getFullYear();
const YEAR_OPTIONS = Array.from(
    { length: CURRENT_YEAR - MIN_YEAR + 1 },
    (_, i) => CURRENT_YEAR - i,
);

interface BarchartTopViewResearchByDomainProps {
    limit?: number;
}

export default function BarchartTopViewResearchByDomain({
    limit = 10,
}: BarchartTopViewResearchByDomainProps) {
    const [year, setYear] = useState(CURRENT_YEAR);
    const [domains, setDomains] = useState<Domain[]>([]);
    const [domainId, setDomainId] = useState<string>("");
    const [data, setData] = useState<TopResearchViewItem[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        referenceService
            .getDomains(1, 100)
            .then((items: Domain[]) => {
                setDomains(items)
                if (items.length > 0) setDomainId(items[0].domain_id)
            })
            .catch(() => setDomains([]))
    }, [])

    useEffect(() => {
        if (!domainId) return
        let ignore = false
        setLoading(true)
        reportService
            .getTopResearchViewsByDomain(domainId, year, limit)
            .then((result) => {
                if (!ignore) setData(result)
            })
            .catch(() => {
                if (!ignore) setData([])
            })
            .finally(() => {
                if (!ignore) setLoading(false)
            })
        return () => {
            ignore = true
        }
    }, [domainId, year, limit])

    const chartData = [...data]
        .sort((a, b) => b.views - a.views)
        .slice(0, limit)
        .map((item) => ({ ...item, shortTitle: truncateTitle(item.title) }));

    return (
        <div className="w-full rounded-lg border bg-white p-4 shadow-sm">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
                <h3 className="text-base font-medium">Top nghiên cứu theo lĩnh vực</h3>
                <div className="flex items-center gap-2">
                    <Select value={domainId} onValueChange={setDomainId}>
                        <SelectTrigger size="sm" className="w-[200px]">
                            <SelectValue placeholder="Chọn lĩnh vực" />
                        </SelectTrigger>
                        <SelectContent>
                            {domains.map((d) => (
                                <SelectItem key={d.domain_id} value={d.domain_id}>
                                    {d.domain_name}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
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
                </div>
            </div>

            {loading ? (
                <p className="py-10 text-center text-sm text-muted-foreground">Đang tải...</p>
            ) : chartData.length === 0 ? (
                <p className="py-10 text-center text-sm text-muted-foreground">
                    Chưa có dữ liệu lượt xem cho lĩnh vực này trong năm {year}
                </p>
            ) : (
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
            )}
        </div>
    );
}
