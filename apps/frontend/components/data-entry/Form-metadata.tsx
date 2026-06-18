"use client";

import { CreateDomainRequest, CreateKeywordRequest, CreateResearcherRequest, referenceService } from "@/services/reference/reference.service";
import { useEffect, useState } from "react";
import Select from "react-select";
import ReactSelect from "react-select";
import AddResearcherModal from "./add-researcher-modal";
import { toast } from 'sonner';
import AddKeywordModal from "./add-keyword-modal";
import AddDomainModal from "./add-research-domain-modal";
import AsyncSelect from "react-select/async";


const AUTHOR_ROLES = [
    { value: "creator", label: "Creator" },
    { value: "contributor", label: "Contributor" },
    { value: "supervisor", label: "Supervisor" },
    { value: "student_member", label: "Student member" },
    { value: "corresponding_author", label: "Corresponding author" },
];

type AuthorForm = {
    researcher_id: string | null;
    full_name: string;
    email: string;
    affiliation: string;
    author_order: number;
    author_role: string;
};

type MetadataFormState = {
    title: string;
    output_type_id: string;
    department_id: string;
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


export default function FormMetadata() {
    const [openDomainModal, setOpenDomainModal] = useState(false);
    const [openKeywordModal, setOpenKeywordModal] = useState(false);
    const [openResearcherModal, setOpenResearcherModal] = useState(false);

    const [formData, setFormData] = useState<MetadataFormState>({
        title: "",
        output_type_id: "",
        department_id: "",
        year: null,
        description: "",
        abstract: "",
        start_date: "",
        end_date: "",
        date_issued: "",
        publisher: "",
        language: "vi",
        identifier: "",
        external_url: "",
        source: "",
        relation: "",
        coverage: "",
        rights: "",

        domain_ids: [],
        keyword_ids: [],

        domain_name: [],
        keyword_name: [],

        authors: []
    });

    const [departments, setDepartments] = useState<any[]>([]);
    const [outputTypes, setOutputTypes] = useState<any[]>([]);
    const [researchers, setResearchers] = useState<any[]>([]);
    const [authors, setAuthors] = useState<AuthorForm[]>([]);

    const [domains, setDomains] = useState<{ value: string; label: string }[]>([]);
    const [keywords, setKeywords] = useState<{ value: string; label: string }[]>([]);



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
            // getResearchers() đang return response.data.items
            const res = await referenceService.getResearchers();

            setResearchers(res);
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
            {
                researcher_id: null,
                full_name: "",
                email: "",
                affiliation: "",
                author_order: prev.length + 1,
                author_role: "creator",
            }
        ]);
    };

    useEffect(() => {
        fetchDepartments();
        fetchOutputTypes();
        fetchResearchers();
        fetchDomains();
        fetchKeywords();
    }, []);
    const handleSaveDraft = () => {
        console.log("🟡 SAVE DRAFT DATA:");

        console.log({
            ...formData,
            authors,
        });
    };

    const handleSubmit = () => {
        console.log("🟢 SUBMIT DATA:");

        console.log({
            ...formData,
            authors,
        });
    };
    return (
        <div className="mx-auto max-w-7xl space-y-8 p-6">
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
            <div className="rounded-xl border bg-white p-6 shadow-sm">
                <h2 className="mb-6 text-xl font-semibold">
                    Metadata Research
                </h2>

                <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
                    <div className="md:col-span-2">
                        <label className="mb-2 block text-sm font-medium">
                            Tiêu đề
                        </label>
                        <input
                            className="w-full rounded-lg border px-3 py-2"
                            placeholder="Research title"
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
                        <label className="mb-2 block text-sm font-medium">
                            Loại sản phẩm
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
                        <label className="mb-2 block text-sm font-medium">
                            Đơn vị
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
                        <label className="mb-2 block text-sm font-medium">
                            Năm
                        </label>

                        <input
                            type="number"
                            className="w-full rounded-lg border px-3 py-2"
                            value={formData.year ?? ""}
                            onChange={(e) =>
                                setFormData(prev => ({
                                    ...prev,
                                    year: e.target.value ? Number(e.target.value) : null,
                                }))
                            }
                        />
                    </div>

                    <div>
                        <label className="mb-2 block text-sm font-medium">
                            Ngôn ngữ
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
                        <label className="mb-2 block text-sm font-medium">
                            Mô tả
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
                        <label className="mb-2 block text-sm font-medium">
                            Tóm tắt
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
            </div>

            {/* Publication Information */}
            <div className="rounded-xl border bg-white p-6 shadow-sm">
                <h2 className="mb-6 text-xl font-semibold">
                    Publication Information
                </h2>

                <div className="grid grid-cols-1 gap-5 md:grid-cols-2">

                    {/* START DATE */}
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

                    {/* END DATE */}
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

                    {/* DATE ISSUED */}
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

                    {/* PUBLISHER */}
                    <input
                        className="w-full rounded-lg border px-3 py-2"
                        value={formData.publisher}
                        onChange={(e) =>
                            setFormData(prev => ({
                                ...prev,
                                publisher: e.target.value
                            }))
                        }
                    />

                    {/* IDENTIFIER */}
                    <input
                        className="w-full rounded-lg border px-3 py-2"
                        value={formData.identifier}
                        onChange={(e) =>
                            setFormData(prev => ({
                                ...prev,
                                identifier: e.target.value
                            }))
                        }
                    />

                    {/* EXTERNAL URL */}
                    <input
                        className="w-full rounded-lg border px-3 py-2"
                        value={formData.external_url}
                        onChange={(e) =>
                            setFormData(prev => ({
                                ...prev,
                                external_url: e.target.value
                            }))
                        }
                    />

                    {/* SOURCE */}
                    <input
                        className="w-full rounded-lg border px-3 py-2"
                        value={formData.source}
                        onChange={(e) =>
                            setFormData(prev => ({
                                ...prev,
                                source: e.target.value
                            }))
                        }
                    />

                    {/* RELATION */}
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

                    {/* COVERAGE */}
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

                    {/* RIGHTS */}
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

            <div className="rounded-xl border bg-white p-6 shadow-sm">
                <h2 className="mb-6 text-xl font-semibold">
                    Classification
                </h2>

                <div className="space-y-6">

                    {/* Domain */}
                    <div>
                        <label className="mb-2 block text-sm font-medium">
                            Phạm vi
                        </label>

                        <AsyncSelect
                            isMulti
                            cacheOptions
                            defaultOptions
                            loadOptions={async (inputValue) => {
                                const res = await referenceService.suggestDomains(inputValue, 20);

                                return res.map((d: any) => ({
                                    value: d.domain_id,
                                    label: d.domain_name,
                                }));
                            }}
                            onChange={(selected: any) => {
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
                        <label className="mb-2 block text-sm font-medium">
                            Từ khóa
                        </label>

                        <AsyncSelect
                            isMulti
                            cacheOptions
                            defaultOptions
                            loadOptions={async (inputValue) => {
                                const res = await referenceService.suggestKeywords(inputValue, 20);

                                return res.map((k: any) => ({
                                    value: k.keyword_id,
                                    label: k.keyword_text,
                                }));
                            }}
                            onChange={(selected: any) => {
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
            </div>

            <div className="rounded-xl border bg-white p-6 shadow-sm">
                {/* HEADER */}
                <div className="mb-6 flex items-center justify-between">
                    <h2 className="text-xl font-semibold">Authors</h2>

                    <button
                        type="button"
                        onClick={handleAddAuthor}
                        className="cursor-pointer rounded-lg bg-blue-600 px-4 py-2 text-white"
                    >
                        + Add Author
                    </button>
                </div>

                {/* LIST AUTHORS */}
                <div className="space-y-6">
                    {authors.map((author, index) => (
                        <div key={index} className="rounded-lg border p-5">

                            <div className="grid grid-cols-1 gap-5 md:grid-cols-2">

                                {/* ===================== RESEARCHER ===================== */}
                                <div>
                                    <label className="mb-2 block text-sm font-medium">
                                        Researcher
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
                                        + Add new researcher
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
                                    <label className="mb-2 block text-sm font-medium">
                                        Role
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
                                        <option value="">Select role</option>
                                        <option value="creator">creator</option>
                                        <option value="contributor">contributor</option>
                                        <option value="supervisor">supervisor</option>
                                        <option value="student_member">student_member</option>
                                        <option value="corresponding_author">
                                            corresponding_author
                                        </option>
                                    </select>
                                </div>

                                {/* ===================== EMAIL ===================== */}
                                <div>
                                    <label className="mb-2 block text-sm font-medium">
                                        Email
                                    </label>

                                    <input
                                        className="w-full rounded-lg border px-3 py-2"
                                        value={author.email}
                                        onChange={(e) => {
                                            const value = e.target.value;

                                            setAuthors(prev => {
                                                const updated = [...prev];

                                                updated[index] = {
                                                    ...updated[index],
                                                    email: value,
                                                };

                                                return updated;
                                            });
                                        }}
                                    />
                                </div>

                                {/* ===================== AFFILIATION ===================== */}
                                <div>
                                    <label className="mb-2 block text-sm font-medium">
                                        Affiliation
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
            </div>
            <div className="flex justify-end gap-4">
                <button
                    type="button"
                    onClick={handleSaveDraft}
                    className="rounded-lg border px-5 py-2"
                >
                    Save Draft
                </button>

                <button
                    type="button"
                    onClick={handleSubmit}
                    className="rounded-lg bg-blue-600 px-5 py-2 text-white"
                >
                    Submit
                </button>
            </div>

        </div>
    );
}