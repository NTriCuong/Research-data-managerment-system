'use client'

import { useState } from 'react'
import { ClipboardList, LogIn, GitBranch } from 'lucide-react'

import AuditLogTab from '@/components/superadmin/logs/audit-log-tab'
import LoginLogTab from '@/components/superadmin/logs/login-log-tab'
import WorkflowLogTab from '@/components/superadmin/logs/workflow-log-tab'

type Tab = 'audit' | 'login' | 'workflow'

const TABS: { key: Tab; label: string; icon: React.ElementType }[] = [
    { key: 'audit', label: 'nhật ký kiểm tra', icon: ClipboardList },
    { key: 'login', label: 'Đăng nhập', icon: LogIn },
    { key: 'workflow', label: 'quy trình làm việc', icon: GitBranch },
]

export default function SuperAdminLogsPage() {
    const [activeTab, setActiveTab] = useState<Tab>('audit')

    return (
        <div className="space-y-6 p-6">
            <div>
                <h1 className="text-2xl font-semibold text-gray-900">Nhật ký hệ thống</h1>
                <p className="mt-1 text-sm text-gray-500">Theo dõi các hoạt động quản trị, đăng nhập và luồng xử lý.</p>
            </div>

            {/* Tab bar */}
            <div className="flex gap-1 rounded-xl border border-gray-200 bg-gray-50 p-1">
                {TABS.map(({ key, label, icon: Icon }) => (
                    <button
                        key={key}
                        onClick={() => setActiveTab(key)}
                        className={`flex flex-1 items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-all ${activeTab === key
                                ? 'bg-white text-gray-900 shadow-sm'
                                : 'text-gray-500 hover:text-gray-700'
                            }`}
                    >
                        <Icon size={15} />
                        {label}
                    </button>
                ))}
            </div>

            {/* Tab content */}
            {activeTab === 'audit' && <AuditLogTab />}
            {activeTab === 'login' && <LoginLogTab />}
            {activeTab === 'workflow' && <WorkflowLogTab />}
        </div>
    )
}
