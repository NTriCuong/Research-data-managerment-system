"use client";

import { CreateDomainRequest, CreateKeywordRequest, CreateResearcherRequest, referenceService, type StagingFile, type StagingResearchObjectDetail } from "@/services/reference/reference.service";
import { parseAxiosError } from "@/lib/axios/error-paser";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Select from "react-select";
import AddResearcherModal from "./add-researcher-modal";
import { toast } from 'sonner';
import AddKeywordModal from "./add-keyword-modal";
import AddDomainModal from "./add-research-domain-modal";
import AsyncSelect from "react-select/async";
import { FileText, CalendarRange, Tags, Users, Paperclip, Loader2, Trash2, Upload, X, type LucideIcon } from "lucide-react";
import {
    Attachment,
    AttachmentAction,
    AttachmentActions,
    AttachmentContent,
    AttachmentDescription,
    AttachmentGroup,
    AttachmentMedia,
    AttachmentTitle,
} from "@/components/ui/attachment";
import { isAccessLevelAllowed } from "@/lib/constants/workflow";

const AUTHOR_ROLES = [
    { value: "creator", label: "Người tạo (tác giả chính)" },
    { value: "contributor", label: "Người đóng góp" },
    { value: "supervisor", label: "Người hướng dẫn" },
    { value: "student_member", label: "Thành viên (sinh viên)" },
    { value: "corresponding_author", label: "Tác giả liên hệ" },
];

type AccessLevel = "private" | "internal" | "public";

const ACCESS_LEVEL_OPTIONS: { value: AccessLevel; label: string }[] = [
    { value: "private", label: "Riêng tư" },
    { value: "internal", label: "Nội bộ" },
    { value: "public", label: "Công khai" },
];

type AuthorForm = {
    researcher_id: string | null;
    full_name: string;
    email: string;
    affiliation: string;
    author_order: number;
    author_role: string;
};

const createEmptyAuthor = (author_order = 1): AuthorForm => ({
    researcher_id: null,
    full_name: "",
    email: "",
    affiliation: "",
    author_order,
    author_role: "creator",
});

type MetadataFormState = {
    title: string;
    output_type_id: string;
    department_id: string;
    access_level: AccessLevel | "";
    year: number | null;
    description: string;
    abstract: string;
    start_date: string;
    end_date: string;
    date_issued: string;
    publisher: string;
    language: string;
    identifier: string;
    external_url: string;
    source: string;
    relation: string;
    coverage: string;
    rights: string;

    domain_ids: string[];
    keyword_ids: string[];

    domain_name: string[];
    keyword_name: string[];

    authors: AuthorForm[];
};

function RequiredMark() {
    return <span className="text-red-500"> *</span>;
}

function FormSectionCard({
    icon: Icon,
    title,
    action,
    children,
}: {
    icon: LucideIcon;
    title: string;
    action?: React.ReactNode;
    children: React.ReactNode;
}) {
    return (
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <div className="mb-6 flex items-center justify-between">
                <h2 className="flex items-center gap-2 text-base font-semibold text-gray-900">
                    <Icon size={18} className="text-gray-400" />
                    {title}
                </h2>
                {action}
            </div>
            {children}
        </div>
    );
}

type FormMetadataProps = {
    stagingId?: string;
    initialDetail?: StagingResearchObjectDetail;
};

export default function FormMetadata({ stagingId: editStagingId, initialDetail }: FormMetadataProps) {
    const router = useRouter();
    const isEditMode = !!editStagingId;

    const currentYear = new Date().getFullYear();
    const years = Array.from({ length: 50 }, (_, i) => currentYear - i);

    const [openDomainModal, setOpenDomainModal] = useState(false);
    const [openKeywordModal, setOpenKeywordModal] = useState(false);
    const [openResearcherModal, setOpenResearcherModal] = useState(false);
    const [openSubmitModal, setOpenSubmitModal] = useState(false);
    const [isDraftSaved, setIsDraftSaved] = useState(isEditMode);
    const [submitNote, setSubmitNote] = useState("");
    const [submitting, setSubmitting] = useState(false);

    const [stagingId, setStagingId] = useState<string | null>(editStagingId ?? null);
    const [files, setFiles] = useState<StagingFile[]>(initialDetail?.files ?? []);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [selectedFileAccessLevel, setSelectedFileAccessLevel] = useState<AccessLevel>(
        initialDetail?.access_level ?? "internal"
    );
    const [uploadingFile, setUploadingFile] = useState(false);
    const [updatingFileId, setUpdatingFileId] = useState<string | null>(null);

    const [formData, setFormData] = useState<MetadataFormState>({
        title: initialDetail?.title ?? "",
        output_type_id: initialDetail?.output_type_id ?? "",
        department_id: initialDetail?.department_id ?? "",
        access_level: initialDetail?.access_level ?? "",
        year: initialDetail?.year ?? null,
        description: initialDetail?.description ?? "",
        abstract: initialDetail?.abstract ?? "",
        start_date: initialDetail?.start_date ?? "",
        end_date: initialDetail?.end_date ?? "",
        date_issued: initialDetail?.date_issued ?? "",
        publisher: initialDetail?.publisher ?? "",
        language: initialDetail?.language ?? "vi",
        identifier: initialDetail?.identifier ?? "",
        external_url: initialDetail?.external_url ?? "",
        source: initialDetail?.source ?? "",
        relation: initialDetail?.relation ?? "",
        coverage: initialDetail?.coverage ?? "",
        rights: initialDetail?.rights ?? "",

        domain_ids: initialDetail?.domains.map(d => d.domain_id) ?? [],
        keyword_ids: initialDetail?.keywords.map(k => k.keyword_id) ?? [],

        domain_name: [],
        keyword_name: [],

        authors: []
    });

    const [departments, setDepartments] = useState<any[]>([]);
    const [outputTypes, setOutputTypes] = useState<any[]>([]);
    const [researchers, setResearchers] = useState<any[]>([]);
    const [authors, setAuthors] = useState<AuthorForm[]>(
        initialDetail?.authors.length ? initialDetail.authors.map(a => ({
            researcher_id: a.researcher_id,
            full_name: a.full_name,
            email: a.email ?? "",
            affiliation: a.affiliation ?? "",
            author_order: a.author_order,
            author_role: a.author_role,
        })) : [createEmptyAuthor()]
    );

    const [domains, setDomains] = useState<{ value: string; label: string }[]>([]);
    const [keywords, setKeywords] = useState<{ value: string; label: string }[]>([]);
    const [selectedDomains, setSelectedDomains] = useState<{ value: string; label: string }[]>(
        initialDetail?.domains.map(d => ({ value: d.domain_id, label: d.domain_name })) ?? []
    );
    const [selectedKeywords, setSelectedKeywords] = useState<{ value: string; label: string }[]>(
        initialDetail?.keywords.map(k => ({ value: k.keyword_id, label: k.keyword_text })) ?? []
    );



    const fetchDepartments = async () => {
        try {
            const res = await referenceService.getDepartments();

            // PaginatedResponse<Department>
            setDepartments(res.items);
        } catch (error) {
            console.error(error);
        }
    };

    const fetchOutputTypes = async () => {
        try {
            const res = await referenceService.getOutputTypes();

            // PaginatedResponse<OutputType>
            setOutputTypes(res.items);
        } catch (error) {
            console.error(error);
        }
    };

    const fetchResearchers = async () => {
        try {
            const res = await referenceService.getResearchers();
            setResearchers(res.items);
        } catch (error) {
            console.error(error);
        }
    };

    const fetchDomains = async () => {
        try {
            const res = await referenceService.getDomains();

            setDomains(
                res.map((item: any) => ({
                    value: item.domain_id,
                    label: item.domain_name,
                }))
            );
        } catch (error) {
            console.error(error);
        }
    };
    const fetchKeywords = async () => {
        try {
            const res = await referenceService.getKeywords();

            setKeywords(
                res.map((item: any) => ({
                    value: item.keyword_id,
                    label: item.keyword_text,
                }))
            );
        } catch (error) {
            console.error(error);
        }
    };

    const handleCreateResearcher = async (data: CreateResearcherRequest) => {
        try {
            await referenceService.createResearcher(data);

            await fetchResearchers();
            toast.info('Thêm nhà nghiên cứu thành công', {
                description: 'Nhà nghiên cứu đã được thêm vào danh sách. Bạn có thể chọn nhà nghiên cứu này trong danh sách.',
            })
            setOpenResearcherModal(false);
        } catch (error) {
            console.error(error);
        }
    };
    const handleCreateDomain = async (data: CreateDomainRequest) => {
        try {
            const created = await referenceService.createDomain(data);

            setDomains(prev => [
                ...prev,
                {
                    value: created.domain_id,
                    label: created.domain_name,
                }
            ]);

            toast.success("Thêm domain thành công");

            setOpenDomainModal(false);
        } catch (error) {
            console.error(error);
            toast.error("Thêm domain thất bại");
        }
    };

    const handleCreateKeyword = async (data: CreateKeywordRequest) => {
        try {
            const created = await referenceService.createKeyword(data);

            // thêm vào cache state (UX tốt hơn fetch lại toàn bộ)
            setKeywords(prev => [
                ...prev,
                {
                    value: created.keyword_id,
                    label: created.keyword_text,
                }
            ]);

            toast.success("Thêm keyword thành công");

            setOpenKeywordModal(false);
        } catch (error) {
            console.error(error);
            toast.error("Thêm keyword thất bại");
        }
    };

    const handleAddAuthor = () => {
        setAuthors(prev => [
            ...prev,
            createEmptyAuthor(prev.length + 1)
        ]);
    };

    const handleRemoveAuthor = (index: number) => {
        if (authors.length <= 1) {
            toast.error("Research phải có ít nhất một tác giả");
            return;
        }

        const removedAuthor = authors[index];
        setAuthors(prev =>
            prev
                .filter((_, itemIndex) => itemIndex !== index)
                .map((author, itemIndex) => ({ ...author, author_order: itemIndex + 1 }))
        );
        toast("Đã xóa tác giả", {
            action: {
                label: "Hoàn tác",
                onClick: () => {
                    setAuthors(prev => {
                        const restored = [...prev];
                        restored.splice(index, 0, removedAuthor);
                        return restored.map((author, itemIndex) => ({ ...author, author_order: itemIndex + 1 }));
                    });
                },
            },
        });
    };

    const fetchFiles = async (id: string) => {
        try {
            const res = await referenceService.getStagingFiles(id);
            setFiles(res);
        } catch (error) {
            console.error(error);
        }
    };

    useEffect(() => {
        fetchDepartments();
        fetchOutputTypes();
        fetchResearchers();
        fetchDomains();
        fetchKeywords();

        if (stagingId) {
            fetchFiles(stagingId);
        }
    }, []);

    const handleUploadFile = async () => {
        if (!stagingId) {
            toast.error("Vui lòng lưu bản nháp trước khi đính kèm tệp");
            return;
        }
        if (!selectedFile) {
            toast.error("Vui lòng chọn tệp cần đính kèm");
            return;
        }
        if (!formData.access_level) {
            toast.error("Vui lòng chọn mức truy cập trước khi tải tệp");
            return;
        }

        setUploadingFile(true);
        try {
            if (!isAccessLevelAllowed(selectedFileAccessLevel, formData.access_level)) {
                toast.error("Quyền truy cập tệp không được cao hơn quyền truy cập bài nghiên cứu");
                return;
            }
            const uploaded = await referenceService.uploadStagingFile(
                stagingId,
                selectedFile,
                selectedFileAccessLevel
            );
            setFiles(prev => [...prev, uploaded]);
            setSelectedFile(null);
            toast.success("Tải tệp lên thành công");
        } catch (error) {
            toast.error(parseAxiosError(error).message);
        } finally {
            setUploadingFile(false);
        }
    };

    const handleDeleteFile = async (fileId: string) => {
        if (!stagingId) return;

        try {
            await referenceService.deleteStagingFile(stagingId, fileId);
            setFiles(prev => prev.filter(f => f.file_id !== fileId));
            toast.success("Xoá tệp thành công");
        } catch (error) {
            toast.error(parseAxiosError(error).message);
        }
    };

    const handleFileAccessLevelChange = async (fileId: string, accessLevel: AccessLevel) => {
        if (!stagingId || !formData.access_level) return;
        if (!isAccessLevelAllowed(accessLevel, formData.access_level)) {
            toast.error("Quyền truy cập tệp không được cao hơn quyền truy cập bài nghiên cứu");
            return;
        }

        setUpdatingFileId(fileId);
        try {
            const updated = await referenceService.updateStagingFileAccessLevel(
                stagingId,
                fileId,
                accessLevel
            );
            setFiles((current) => current.map((file) => (file.file_id === fileId ? updated : file)));
            toast.success("Đã cập nhật quyền truy cập tệp");
        } catch (error) {
            toast.error(parseAxiosError(error).message);
        } finally {
            setUpdatingFileId(null);
        }
    };
    const handleSaveDraft = async () => {
        if (!formData.title.trim()) {
            toast.error("Vui lòng nhập tiêu đề nghiên cứu")
            return
        }
        if (!formData.output_type_id) {
            toast.error("Vui lòng chọn loại sản phẩm")
            return
        }
        if (!formData.department_id) {
            toast.error("Vui lòng chọn đơn vị")
            return
        }
        if (!formData.access_level) {
            toast.error("Vui lòng chọn mức truy cập")
            return
        }

        if (authors.length === 0) {
            toast.error("Research phải có ít nhất một tác giả")
            return
        }
        if (authors.some(author => !author.researcher_id)) {
            toast.error("Vui lòng chọn nhà nghiên cứu cho từng tác giả")
            return
        }

        try {
            const payload = {
                title: formData.title,
                output_type_id: formData.output_type_id,
                department_id: formData.department_id,
                access_level: formData.access_level,
                year: formData.year,
                description: formData.description,
                abstract: formData.abstract,
                start_date: formData.start_date || null,
                end_date: formData.end_date || null,
                date_issued: formData.date_issued || null,
                publisher: formData.publisher,
                language: formData.language,
                identifier: formData.identifier,
                external_url: formData.external_url || null,
                source: formData.source,
                relation: formData.relation,
                coverage: formData.coverage,
                rights: formData.rights,

                domain_ids: formData.domain_ids,
                keyword_ids: formData.keyword_ids,

                authors: authors,
            };

            if (stagingId) {
                await referenceService.updateMetadata(stagingId, payload);
                toast.success("Lưu thay đổi thành công");
            } else {
                const res = await referenceService.createMetadata(payload);
                setStagingId(res.staging_id);
                toast.success("Lưu bản nháp thành công");
            }
            setIsDraftSaved(true);
            router.push("/dashboard/data-entry/researches");
        } catch (error) {
            console.error(error);
            toast.error(parseAxiosError(error).message);
        }
    };

    const handleCancel = () => {
        router.push("/dashboard/data-entry/researches");
    };

    const handleSubmit = () => {
        if (files.length === 0) {
            toast.error("Cần đính kèm ít nhất một tệp trước khi gửi");
            return;
        }
        setOpenSubmitModal(true);
    };
    const handleConfirmSubmit = async () => {
        setSubmitting(true);
        try {
            await referenceService.submitForReview(stagingId ?? "", submitNote);

            toast.success("Gửi chờ kiểm duyệt thành công");
            setOpenSubmitModal(false);
            setSubmitNote("");

            if (isEditMode) {
                router.push("/dashboard/data-entry/researches");
            }
        } catch (error: any) {
            console.error("submit error", {
                status: error?.response?.status,
                data: error?.response?.data,
                message: error?.message,
            });
            toast.error(parseAxiosError(error).message);
        } finally {
            setSubmitting(false);
        }
    };
    return (
        <div className="bg-gray-50">
            <AddDomainModal
                open={openDomainModal}
                onClose={() => setOpenDomainModal(false)}
                onSubmit={handleCreateDomain}
            />

            <AddKeywordModal
                open={openKeywordModal}
                onClose={() => setOpenKeywordModal(false)}
                onSubmit={handleCreateKeyword}
            />

            <div className="mx-auto max-w-5xl space-y-6 p-6">

                <p className="text-sm text-gray-500">
                    Các trường có dấu<span className="font-medium text-red-500"> *</span> là bắt buộc.
                </p>

                <FormSectionCard icon={FileText} title="Thông tin bài nghiên cứu (Research Metadata)">
                    <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
                        <div className="md:col-span-2">
                            <label className="mb-2 block text-sm font-medium text-gray-700">
                                Tiêu đề (Title)<RequiredMark />
                            </label>
                            <input
                                className="w-full rounded-lg border px-3 py-2"
                                placeholder="Nhập tiêu đề nghiên cứu"
                                value={formData.title}
                                onChange={(e) =>
                                    setFormData(prev => ({
                                        ...prev,
                                        title: e.target.value,
                                    }))
                                }
                            />
                        </div>

                        <div>
                            <label className="mb-2 block text-sm font-medium text-gray-700">
                                Loại sản phẩm (Output Type)<RequiredMark />
                            </label>

                            <select
                                className="w-full rounded-lg border px-3 py-2"
                                value={formData.output_type_id}
                                onChange={(e) =>
                                    setFormData((prev) => ({
                                        ...prev,
                                        output_type_id: e.target.value,
                                    }))
                                }
                            >
                                <option value="">Chọn loại sản phẩm</option>

                                {outputTypes.map((item) => (
                                    <option
                                        key={item.output_type_id}
                                        value={item.output_type_id}
                                    >
                                        {item.type_name}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="mb-2 block text-sm font-medium text-gray-700">
                                Đơn vị (Department)<RequiredMark />
                            </label>

                            <select
                                className="w-full rounded-lg border px-3 py-2"
                                value={formData.department_id}
                                onChange={(e) =>
                                    setFormData((prev) => ({
                                        ...prev,
                                        department_id: e.target.value,
                                    }))
                                }
                            >
                                <option value="">Chọn đơn vị</option>

                                {departments.map((item) => (
                                    <option
                                        key={item.department_id}
                                        value={item.department_id}
                                    >
                                        {item.department_name}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="mb-2 block text-sm font-medium text-gray-700">
                                Mức truy cập (Access Level)<RequiredMark />
                            </label>

                            <select
                                className="w-full rounded-lg border px-3 py-2"
                                value={formData.access_level}
                                onChange={(e) => {
                                    const nextAccessLevel = e.target.value as AccessLevel | "";
                                    setFormData((prev) => ({
                                        ...prev,
                                        access_level: nextAccessLevel,
                                    }));
                                    if (
                                        nextAccessLevel
                                        && !isAccessLevelAllowed(selectedFileAccessLevel, nextAccessLevel)
                                    ) {
                                        setSelectedFileAccessLevel(nextAccessLevel);
                                    }
                                }}
                            >
                                <option value="">Chọn mức truy cập</option>
                                {ACCESS_LEVEL_OPTIONS.map((item) => (
                                    <option key={item.value} value={item.value}>
                                        {item.label}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="mb-2 block text-sm font-medium text-gray-700">
                                Năm (Year)<RequiredMark />
                            </label>

                            <select
                                className="w-full rounded-lg border px-3 py-2"
                                value={formData.year ?? ""}
                                onChange={(e) =>
                                    setFormData((prev) => ({
                                        ...prev,
                                        year: e.target.value ? Number(e.target.value) : null,
                                    }))
                                }
                            >
                                <option value="">Chọn năm</option>

                                {years.map((year) => (
                                    <option key={year} value={year}>
                                        {year}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="mb-2 block text-sm font-medium text-gray-700">
                                Ngôn ngữ (Language)
                            </label>

                            <select
                                className="w-full rounded-lg border px-3 py-2"
                                value={formData.language}
                                onChange={(e) =>
                                    setFormData(prev => ({
                                        ...prev,
                                        language: e.target.value,
                                    }))
                                }
                            >
                                <option value="vi">vi</option>
                                <option value="en">en</option>
                            </select>
                        </div>

                        <div className="md:col-span-2">
                            <label className="mb-2 block text-sm font-medium text-gray-700">
                                Mô tả (Description)
                            </label>

                            <textarea
                                rows={3}
                                className="w-full rounded-lg border px-3 py-2"
                                value={formData.description}
                                onChange={(e) =>
                                    setFormData(prev => ({
                                        ...prev,
                                        description: e.target.value,
                                    }))
                                }
                            />
                        </div>

                        <div className="md:col-span-2">
                            <label className="mb-2 block text-sm font-medium text-gray-700">
                                Tóm tắt (Abstract)
                            </label>
                            <textarea
                                rows={6}
                                className="w-full rounded-lg border px-3 py-2"
                                value={formData.abstract}
                                onChange={(e) =>
                                    setFormData(prev => ({
                                        ...prev,
                                        abstract: e.target.value,
                                    }))
                                }
                            />
                        </div>
                    </div>
                </FormSectionCard>

                <FormSectionCard icon={CalendarRange} title="Thông tin xuất bản (Publication Information)">
                    <div className="grid grid-cols-1 gap-5 md:grid-cols-2">

                        {/* START DATE */}
                        <div>
                            <label className="mb-2 block text-sm font-medium text-gray-700">
                                Ngày bắt đầu (Start Date)
                            </label>
                            <input
                                type="date"
                                className="w-full rounded-lg border px-3 py-2"
                                value={formData.start_date}
                                onChange={(e) =>
                                    setFormData(prev => ({
                                        ...prev,
                                        start_date: e.target.value
                                    }))
                                }
                            />
                        </div>

                        {/* END DATE */}
                        <div>
                            <label className="mb-2 block text-sm font-medium text-gray-700">
                                Ngày kết thúc (End Date)
                            </label>
                            <input
                                type="date"
                                className="w-full rounded-lg border px-3 py-2"
                                value={formData.end_date}
                                onChange={(e) =>
                                    setFormData(prev => ({
                                        ...prev,
                                        end_date: e.target.value
                                    }))
                                }
                            />
                        </div>

                        {/* DATE ISSUED */}
                        <div>
                            <label className="mb-2 block text-sm font-medium text-gray-700">
                                Ngày phát hành (Date Issued)
                            </label>
                            <input
                                type="date"
                                className="w-full rounded-lg border px-3 py-2"
                                value={formData.date_issued}
                                onChange={(e) =>
                                    setFormData(prev => ({
                                        ...prev,
                                        date_issued: e.target.value
                                    }))
                                }
                            />
                        </div>

                        {/* PUBLISHER */}
                        <div>
                            <label className="mb-2 block text-sm font-medium text-gray-700">
                                Nhà xuất bản (Publisher)
                            </label>
                            <input
                                className="w-full rounded-lg border px-3 py-2"
                                placeholder="Tên nhà xuất bản"
                                value={formData.publisher}
                                onChange={(e) =>
                                    setFormData(prev => ({
                                        ...prev,
                                        publisher: e.target.value
                                    }))
                                }
                            />
                        </div>

                        {/* IDENTIFIER */}
                        <div>
                            <label className="mb-2 block text-sm font-medium text-gray-700">
                                Mã định danh (Identifier)
                            </label>
                            <input
                                className="w-full rounded-lg border px-3 py-2"
                                placeholder="ISBN / DOI / Mã số"
                                value={formData.identifier}
                                onChange={(e) =>
                                    setFormData(prev => ({
                                        ...prev,
                                        identifier: e.target.value
                                    }))
                                }
                            />
                        </div>

                        {/* EXTERNAL URL */}
                        <div>
                            <label className="mb-2 block text-sm font-medium text-gray-700">
                                Đường dẫn ngoài (External URL)
                            </label>
                            <input
                                className="w-full rounded-lg border px-3 py-2"
                                placeholder="https://example.com"
                                value={formData.external_url}
                                onChange={(e) =>
                                    setFormData(prev => ({
                                        ...prev,
                                        external_url: e.target.value
                                    }))
                                }
                            />
                        </div>

                        {/* SOURCE */}
                        <div>
                            <label className="mb-2 block text-sm font-medium text-gray-700">
                                Nguồn (Source)
                            </label>
                            <input
                                className="w-full rounded-lg border px-3 py-2"
                                placeholder="Nguồn tài liệu"
                                value={formData.source}
                                onChange={(e) =>
                                    setFormData(prev => ({
                                        ...prev,
                                        source: e.target.value
                                    }))
                                }
                            />
                        </div>

                        {/* RELATION */}
                        <div>
                            <label className="mb-2 block text-sm font-medium text-gray-700">
                                Liên quan (Relation)
                            </label>
                            <input
                                className="w-full rounded-lg border px-3 py-2"
                                value={formData.relation}
                                onChange={(e) =>
                                    setFormData(prev => ({
                                        ...prev,
                                        relation: e.target.value
                                    }))
                                }
                            />
                        </div>

                        {/* COVERAGE */}
                        <div>
                            <label className="mb-2 block text-sm font-medium text-gray-700">
                                Phạm vi áp dụng (Coverage)
                            </label>
                            <input
                                className="w-full rounded-lg border px-3 py-2"
                                value={formData.coverage}
                                onChange={(e) =>
                                    setFormData(prev => ({
                                        ...prev,
                                        coverage: e.target.value
                                    }))
                                }
                            />
                        </div>

                        {/* RIGHTS */}
                        <div className="md:col-span-2">
                            <label className="mb-2 block text-sm font-medium text-gray-700">
                                Bản quyền (Rights)
                            </label>
                            <input
                                className="w-full rounded-lg border px-3 py-2"
                                value={formData.rights}
                                onChange={(e) =>
                                    setFormData(prev => ({
                                        ...prev,
                                        rights: e.target.value
                                    }))
                                }
                            />
                        </div>

                    </div>
                </FormSectionCard>

                <FormSectionCard icon={Tags} title="Phân loại (Classification)">
                    <div className="space-y-6">

                        {/* Domain */}
                        <div>
                            <label className="mb-2 block text-sm font-medium text-gray-700">
                                Phạm vi (Domain)<RequiredMark />
                            </label>

                            <AsyncSelect
                                isMulti
                                cacheOptions
                                defaultOptions
                                value={selectedDomains}
                                loadOptions={async (inputValue) => {
                                    const res = await referenceService.suggestDomains(inputValue, 20);

                                    return res.map((d: any) => ({
                                        value: d.domain_id,
                                        label: d.domain_name,
                                    }));
                                }}
                                onChange={(selected: any) => {
                                    setSelectedDomains(selected || []);
                                    setFormData(prev => ({
                                        ...prev,
                                        domain_ids: selected?.map((x: any) => x.value) || [],
                                    }));
                                }}
                            />
                            <button
                                type="button"
                                onClick={() => setOpenDomainModal(true)}
                                className="cursor-pointer mt-2 text-sm text-blue-600"
                            >
                                + Thêm domain mới
                            </button>
                        </div>

                        {/* Keyword */}
                        <div>
                            <label className="mb-2 block text-sm font-medium text-gray-700">
                                Từ khóa (Keyword)<RequiredMark />
                            </label>

                            <AsyncSelect
                                isMulti
                                cacheOptions
                                defaultOptions
                                value={selectedKeywords}
                                loadOptions={async (inputValue) => {
                                    const res = await referenceService.suggestKeywords(inputValue, 20);

                                    return res.map((k: any) => ({
                                        value: k.keyword_id,
                                        label: k.keyword_text,
                                    }));
                                }}
                                onChange={(selected: any) => {
                                    setSelectedKeywords(selected || []);
                                    setFormData(prev => ({
                                        ...prev,
                                        keyword_ids: selected?.map((x: any) => x.value) || [],
                                    }));
                                }}
                            />
                            <button
                                type="button"
                                onClick={() => setOpenKeywordModal(true)}
                                className="cursor-pointer mt-2 text-sm text-blue-600"
                            >
                                + Thêm keyword mới
                            </button>

                        </div>
                    </div>
                </FormSectionCard>

                <FormSectionCard
                    icon={Users}
                    title="Tác giả (Authors)"
                    action={
                        <button
                            type="button"
                            onClick={handleAddAuthor}
                            className="cursor-pointer rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                        >
                            + Thêm tác giả
                        </button>
                    }
                >
                    <div className="space-y-6">
                        {authors.length === 0 && (
                            <p className="text-sm text-gray-400">Chưa có tác giả nào, bấm &quot;+ Thêm tác giả&quot; để bắt đầu.</p>
                        )}
                        {authors.map((author, index) => (
                            <div key={index} className="rounded-lg border border-gray-200 p-5">
                                <div className="mb-4 flex items-center justify-between gap-3">
                                    <p className="text-sm font-medium text-gray-700">Tác giả {index + 1}</p>
                                    <button
                                        type="button"
                                        disabled={authors.length <= 1}
                                        onClick={() => handleRemoveAuthor(index)}
                                        className="inline-flex cursor-pointer items-center gap-1.5 rounded-lg border border-red-200 px-3 py-1.5 text-xs font-medium text-red-600 hover:bg-red-50 disabled:cursor-not-allowed disabled:border-gray-200 disabled:text-gray-300 disabled:hover:bg-transparent"
                                    >
                                        <Trash2 size={14} />
                                        Xóa
                                    </button>
                                </div>

                                <div className="grid grid-cols-1 gap-5 md:grid-cols-2">

                                    {/* ===================== RESEARCHER ===================== */}
                                    <div>
                                        <label className="mb-2 block text-sm font-medium text-gray-700">
                                            Nhà nghiên cứu (Researcher)<RequiredMark />
                                        </label>

                                        <Select
                                            options={researchers.map(r => ({
                                                value: r.researcher_id,
                                                label: r.full_name,
                                            }))}
                                            isSearchable
                                            value={
                                                author.researcher_id
                                                    ? {
                                                        value: author.researcher_id,
                                                        label: author.full_name,
                                                    }
                                                    : null
                                            }
                                            onChange={(selected: any) => {
                                                const r = researchers.find(
                                                    x => x.researcher_id === selected?.value
                                                );

                                                if (!r) return;

                                                setAuthors(prev => {
                                                    const updated = [...prev];

                                                    updated[index] = {
                                                        ...updated[index],
                                                        researcher_id: r.researcher_id,
                                                        full_name: r.full_name,
                                                        email: r.email, // AUTO FILL EMAIL
                                                    };

                                                    return updated;
                                                });
                                            }}
                                        />

                                        <button
                                            type="button"
                                            onClick={() => setOpenResearcherModal(true)}
                                            className="mt-2 text-sm text-blue-600 hover:underline"
                                        >
                                            + Thêm nhà nghiên cứu mới
                                        </button>

                                        <AddResearcherModal
                                            open={openResearcherModal}
                                            departments={departments}
                                            onClose={() => setOpenResearcherModal(false)}
                                            onSubmit={handleCreateResearcher}
                                        />
                                    </div>

                                    {/* ===================== ROLE ===================== */}
                                    <div>
                                        <label className="mb-2 block text-sm font-medium text-gray-700">
                                            Vai trò (Role)<RequiredMark />
                                        </label>

                                        <select
                                            className="w-full rounded-lg border px-3 py-2"
                                            value={author.author_role}
                                            onChange={(e) => {
                                                const value = e.target.value;

                                                setAuthors(prev => {
                                                    const updated = [...prev];

                                                    updated[index] = {
                                                        ...updated[index],
                                                        author_role: value,
                                                    };

                                                    return updated;
                                                });
                                            }}
                                        >
                                            <option value="">Chọn vai trò</option>
                                            {AUTHOR_ROLES.map((role) => (
                                                <option key={role.value} value={role.value}>
                                                    {role.label}
                                                </option>
                                            ))}
                                        </select>
                                    </div>

                                    {/* ===================== EMAIL ===================== */}
                                    <div>
                                        <label className="mb-2 block text-sm font-medium text-gray-700">
                                            Email
                                        </label>

                                        <input
                                            className="w-full rounded-lg border px-3 py-2"
                                            value={author.email}
                                            disabled={true}
                                        />
                                    </div>

                                    {/* ===================== AFFILIATION ===================== */}
                                    <div>
                                        <label className="mb-2 block text-sm font-medium text-gray-700">
                                            Đơn vị công tác (Affiliation)<RequiredMark />
                                        </label>

                                        <input
                                            className="w-full rounded-lg border px-3 py-2"
                                            value={author.affiliation}
                                            onChange={(e) => {
                                                const value = e.target.value;

                                                setAuthors(prev => {
                                                    const updated = [...prev];

                                                    updated[index] = {
                                                        ...updated[index],
                                                        affiliation: value,
                                                    };

                                                    return updated;
                                                });
                                            }}
                                        />
                                    </div>

                                </div>
                            </div>
                        ))}
                    </div>
                </FormSectionCard>

                <FormSectionCard icon={Paperclip} title="Tệp đính kèm (Attachments)">
                    <div className="mb-4 max-w-xs">
                        <label htmlFor="new-file-access-level" className="mb-2 block text-sm font-medium text-gray-700">
                            Quyền truy cập tệp mới
                        </label>
                        <select
                            id="new-file-access-level"
                            value={selectedFileAccessLevel}
                            disabled={!formData.access_level}
                            onChange={(event) => setSelectedFileAccessLevel(event.target.value as AccessLevel)}
                            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm disabled:bg-gray-100"
                        >
                            {ACCESS_LEVEL_OPTIONS
                                .filter((option) =>
                                    formData.access_level
                                    && isAccessLevelAllowed(option.value, formData.access_level)
                                )
                                .map((option) => (
                                    <option key={option.value} value={option.value}>{option.label}</option>
                                ))}
                        </select>
                    </div>
                    <div className={!stagingId ? "pointer-events-none opacity-50" : ""} aria-disabled={!stagingId}>
                        <Attachment state={stagingId ? (uploadingFile ? "uploading" : "idle") : "idle"} className="w-full">
                            <AttachmentMedia>
                                <Paperclip size={18} />
                            </AttachmentMedia>
                            <AttachmentContent>
                                <AttachmentTitle>{selectedFile ? selectedFile.name : "Chọn tệp đính kèm"}</AttachmentTitle>
                                <AttachmentDescription>
                                    {stagingId
                                        ? selectedFile
                                            ? `${(selectedFile.size / 1024 / 1024).toFixed(2)} MB`
                                            : "Có thể tải tệp sau khi metadata đã được lưu nháp"
                                        : "Lưu metadata trước để bật file attachment"}
                                </AttachmentDescription>
                            </AttachmentContent>
                            <AttachmentActions className="gap-2">
                                {selectedFile && (
                                    <AttachmentAction type="button" onClick={() => setSelectedFile(null)} aria-label="Bỏ chọn tệp">
                                        <X size={14} />
                                    </AttachmentAction>
                                )}
                                <label className="inline-flex cursor-pointer items-center gap-1.5 rounded-md border px-3 py-1.5 text-xs font-medium hover:bg-gray-50">
                                    <Paperclip size={14} />
                                    Chọn
                                    <input
                                        type="file"
                                        disabled={!stagingId || uploadingFile}
                                        onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
                                        className="sr-only"
                                    />
                                </label>
                                <AttachmentAction
                                    type="button"
                                    size="sm"
                                    disabled={!stagingId || !selectedFile || uploadingFile}
                                    onClick={handleUploadFile}
                                    className="gap-1.5"
                                    aria-label="Tải tệp lên"
                                >
                                    {uploadingFile ? <Loader2 size={14} className="animate-spin" /> : <Upload size={14} />}
                                    Tải lên
                                </AttachmentAction>
                            </AttachmentActions>
                        </Attachment>
                    </div>

                    {files.length > 0 && (
                        <AttachmentGroup className="mt-5">
                            {files.map((file) => (
                                <Attachment key={file.file_id} state="done" className="w-full max-w-full" orientation="vertical">
                                    <AttachmentMedia>
                                        <FileText size={18} />
                                    </AttachmentMedia>
                                    <AttachmentContent>
                                        <AttachmentTitle>{file.original_filename}</AttachmentTitle>
                                        <AttachmentDescription>
                                            {(file.file_size_bytes / 1024 / 1024).toFixed(2)} MB
                                        </AttachmentDescription>
                                    </AttachmentContent>
                                    <AttachmentActions className="gap-2">
                                        <select
                                            value={file.access_level}
                                            disabled={updatingFileId === file.file_id || !formData.access_level}
                                            onChange={(event) =>
                                                handleFileAccessLevelChange(file.file_id, event.target.value as AccessLevel)
                                            }
                                            aria-label={`Quyền truy cập của ${file.original_filename}`}
                                            className="rounded-md border border-gray-300 bg-white px-2 py-1.5 text-xs disabled:bg-gray-100"
                                        >
                                            {formData.access_level
                                                && !isAccessLevelAllowed(file.access_level, formData.access_level) && (
                                                    <option value={file.access_level} disabled>
                                                        {ACCESS_LEVEL_OPTIONS.find((option) => option.value === file.access_level)?.label}
                                                        {' - cần giảm quyền'}
                                                    </option>
                                                )}
                                            {ACCESS_LEVEL_OPTIONS
                                                .filter((option) =>
                                                    formData.access_level
                                                    && isAccessLevelAllowed(option.value, formData.access_level)
                                                )
                                                .map((option) => (
                                                    <option key={option.value} value={option.value}>{option.label}</option>
                                                ))}
                                        </select>
                                        <AttachmentAction type="button" onClick={() => handleDeleteFile(file.file_id)} aria-label="Xóa tệp">
                                            <X size={14} />
                                        </AttachmentAction>
                                    </AttachmentActions>
                                </Attachment>
                            ))}
                        </AttachmentGroup>
                    )}
                </FormSectionCard>
            </div>

            <div className="sticky bottom-0 border-t border-gray-200 bg-white px-6 py-4 shadow-[0_-2px_8px_rgba(0,0,0,0.04)]">
                <div className="mx-auto flex max-w-5xl flex-wrap justify-end gap-3">
                    <button
                        type="button"
                        onClick={handleCancel}
                        className="cursor-pointer rounded-lg border px-5 py-2 text-sm font-medium hover:bg-gray-50"
                    >
                        Hủy
                    </button>

                    <button
                        type="button"
                        onClick={handleSaveDraft}
                        className="cursor-pointer rounded-lg border px-5 py-2 text-sm font-medium hover:bg-gray-50"
                    >
                        {isEditMode ? "Lưu thay đổi" : "Lưu bản nháp"}
                    </button>

                    <button
                        type="button"
                        onClick={handleSubmit}
                        disabled={!isDraftSaved}
                        className="cursor-pointer rounded-lg bg-blue-600 px-5 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-300"
                    >
                        Gửi yêu cầu kiểm duyệt
                    </button>
                </div>
            </div>

            {openSubmitModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
                    <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-lg">
                        <h2 className="text-lg font-semibold">Gửi yêu cầu kiểm duyệt</h2>

                        <div className="mt-5 flex justify-end gap-3">
                            <button
                                className="cursor-pointer rounded-lg border px-4 py-2"
                                onClick={() => setOpenSubmitModal(false)}
                            >
                                Huỷ
                            </button>

                            <button
                                disabled={submitting}
                                className="flex cursor-pointer items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
                                onClick={handleConfirmSubmit}
                            >
                                {submitting && <Loader2 size={14} className="animate-spin" />}
                                Xác nhận
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
