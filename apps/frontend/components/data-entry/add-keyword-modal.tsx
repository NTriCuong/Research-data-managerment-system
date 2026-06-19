"use client";
import { useForm } from "react-hook-form";
export interface CreateKeywordRequest {
    keyword_text: string;
    normalized_text: string;
}

type AddKeywordModalProps = {
    open: boolean;
    onClose: () => void;
    onSubmit: (data: CreateKeywordRequest) => Promise<void>;
};

export default function AddKeywordModal({
    open,
    onClose,
    onSubmit,
}: AddKeywordModalProps) {

    const { register, handleSubmit, reset } =
        useForm<CreateKeywordRequest>();

    if (!open) return null;

    const handleSave = async (data: CreateKeywordRequest) => {
        await onSubmit(data);
        reset();
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
            <div className="w-full max-w-lg rounded-xl bg-white p-6">
                <h2 className="mb-5 text-xl font-semibold">
                    Thêm Keyword
                </h2>

                <form
                    className="space-y-4"
                    onSubmit={handleSubmit(handleSave)}
                >
                    <div>
                        <label>Keyword</label>
                        <input
                            className="w-full rounded border px-3 py-2"
                            {...register("keyword_text", {
                                required: true,
                            })}
                        />
                    </div>

                    <div>
                        <label>Normalized text</label>
                        <input
                            className="w-full rounded border px-3 py-2"
                            {...register("normalized_text")}
                        />
                    </div>

                    <div className="flex justify-end gap-3">
                        <button
                            type="button"
                            className="cursor-pointerrounded border px-4 py-2"
                            onClick={onClose}
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
