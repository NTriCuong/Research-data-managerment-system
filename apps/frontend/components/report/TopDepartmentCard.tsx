import { TopDepartmentItem } from "@/services/reports/report.service";
import { Building2 } from "lucide-react";

function TopDepartmentsCard({ items, loading }: { items: TopDepartmentItem[]; loading: boolean }) {
    const max = items[0]?.count ?? 1

    return (
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
                <Building2 size={16} className="text-gray-400" />
                <h3 className="text-sm font-semibold text-gray-700">Đơn vị đóng góp nhiều nhất</h3>
            </div>

            {loading ? (
                <div className="space-y-3">
                    {[1, 2, 3, 4, 5].map((i) => (
                        <div key={i} className="h-8 animate-pulse rounded bg-gray-100" />
                    ))}
                </div>
            ) : items.length === 0 ? (
                <p className="py-6 text-center text-sm text-gray-400">Không có dữ liệu</p>
            ) : (
                <div className="space-y-2.5">
                    {items.map((dept, idx) => (
                        <div key={dept.department_name} className="flex items-center gap-3">
                            <span className="w-5 text-right text-xs font-medium text-gray-400">
                                {idx + 1}
                            </span>
                            <div className="min-w-0 flex-1">
                                <div className="mb-1 flex items-center justify-between">
                                    <span className="truncate text-xs font-medium text-gray-700">
                                        {dept.department_name}
                                    </span>
                                    <span className="ml-2 shrink-0 text-xs text-gray-500">
                                        {dept.count}
                                    </span>
                                </div>
                                <div className="h-1.5 w-full overflow-hidden rounded-full bg-gray-100">
                                    <div
                                        className="h-full rounded-full bg-blue-500 transition-all duration-500"
                                        style={{ width: `${(dept.count / max) * 100}%` }}
                                    />
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
export default TopDepartmentsCard;