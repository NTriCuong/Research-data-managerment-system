"use client";

import { useForm } from "react-hook-form";

type AddDomainModalProps = {
    open: boolean;
    onClose: () => void;
    onSubmit: (data: CreateDomainRequest) => Promise<void>;
};

export interface CreateDomainRequest {
    domain_code: string;
    domain_name: string;
    parent_domain_id?: string | null;
    description?: string;
    is_active: boolean;
}

export default function AddDomainModal({
    open,
    onClose,
    onSubmit,
}: AddDomainModalProps) {
    const { register, handleSubmit, reset } =
        useForm<CreateDomainRequest>({
            defaultValues: {
                domain_code: "",
                domain_name: "",
                parent_domain_id: null,
                description: "",
                is_active: true,
            },
        });

    if (!open) return null;

    const handleSave = async (data: CreateDomainRequest) => {
        await onSubmit(data);
        reset();
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
            <div className="w-full max-w-lg rounded-xl bg-white p-6">
                <h2 className="mb-5 text-xl font-semibold">
                    Thêm Domain
                </h2>

                <form
                    className="space-y-4"
                    onSubmit={handleSubmit(handleSave)}
                >
                    <div>
                        <label>Domain code</label>
                        <input
                            className="w-full rounded border px-3 py-2"
                            {...register("domain_code")}
                        />
                    </div>

                    <div>
                        <label>Domain name</label>
                        <input
                            className="w-full rounded border px-3 py-2"
                            {...register("domain_name", {
                                required: true,
                            })}
                        />
                    </div>

                    <div>
                        <label>Description</label>
                        <textarea
                            className="w-full rounded border px-3 py-2"
                            rows={3}
                            {...register("description")}
                        />
                    </div>

                    <div className="flex justify-end gap-3">
                        <button
                            type="button"
                            onClick={onClose}
                            className="cursor-pointer rounded border px-4 py-2"
                        >
                            Hủy
                        </button>

                        <button
                            type="submit"
                            className="cursor-pointer rounded bg-blue-600 px-4 py-2 text-white"
                        >
                            Lưu
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
