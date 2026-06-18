export const WORKFLOW_STATUS_LABEL: Record<string, string> = {
    draft: 'Bản nháp',
    pending_review: 'Chờ kiểm duyệt',
    revision_required: 'Yêu cầu sửa lại',
    pending_approval: 'Chờ phê duyệt',
    approved: 'Đã duyệt',
    rejected: 'Bị từ chối',
}

export const WORKFLOW_STATUS_BADGE_CLASS: Record<string, string> = {
    draft: 'bg-gray-100 text-gray-700',
    pending_review: 'bg-amber-100 text-amber-700',
    revision_required: 'bg-orange-100 text-orange-700',
    pending_approval: 'bg-blue-100 text-blue-700',
    approved: 'bg-green-100 text-green-700',
    rejected: 'bg-red-100 text-red-700',
}

export const ACCESS_LEVEL_LABEL: Record<string, string> = {
    private: 'Riêng tư',
    internal: 'Nội bộ',
    public: 'Công khai',
}

export const ACCESS_LEVEL_BADGE_CLASS: Record<string, string> = {
    private: 'bg-red-50 text-red-600',
    internal: 'bg-blue-50 text-blue-600',
    public: 'bg-green-50 text-green-600',
}
