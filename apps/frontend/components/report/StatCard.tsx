function StatCard({
    icon: Icon,
    label,
    value,
    sub,
    iconColor,
    loading,
}: {
    icon: React.ElementType
    label: string
    value: string | number
    sub?: string
    iconColor: string
    loading: boolean
}) {

    return (
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
            <div className="flex items-start justify-between">
                <div>
                    <p className="text-sm text-gray-500">{label}</p>
                    {loading ? (
                        <div className="mt-2 h-8 w-24 animate-pulse rounded bg-gray-100" />
                    ) : (
                        <p className="mt-1 text-3xl font-bold text-gray-900">{value}</p>
                    )}
                    {sub && !loading && (
                        <p className="mt-1 text-xs text-gray-400">{sub}</p>
                    )}
                </div>
                <div className={`rounded-lg p-2.5 ${iconColor}`}>
                    <Icon size={20} className="text-white" />
                </div>
            </div>
        </div>
    )
}
export default StatCard;