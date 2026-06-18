"use client";

import { useState } from "react";

type Props = {
    departments: any[];
    open: boolean;
    onClose: () => void;
    onSubmit: (data: any) => Promise<void>;
};

export default function AddResearcherModal({
    departments,
    open,
    onClose,
    onSubmit,
}: Props) {

    const [form, setForm] = useState({
        full_name: "",
        email: "",
        orcid: "",
        department_id: "",
        academic_title: "",
        researcher_code: "",
        is_internal: true,
    });

    if (!open) return null;

    const handleChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
    ) => {
        const { name, value } = e.target;

        setForm((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleSubmit = async () => {
        await onSubmit(form);

        setForm({
            full_name: "",
            email: "",
            orcid: "",
            department_id: "",
            academic_title: "",
            researcher_code: "",
            is_internal: true,
        });

        onClose();
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
            <div className="w-full max-w-2xl rounded-xl bg-white p-6 shadow-xl">

                <div className="mb-6 flex items-center justify-between">
                    <h2 className="text-xl font-semibold">
                        Add Researcher
                    </h2>

                    <button
                        onClick={onClose}
                        className="text-gray-500 cursor-pointer"
                    >
                        ✕
                    </button>
                </div>

                <div className="grid grid-cols-2 gap-5">

                    <div className="col-span-2">
                        <label>Full name</label>
                        <input
                            name="full_name"
                            value={form.full_name}
                            onChange={handleChange}
                            className="w-full rounded-lg border px-3 py-2"
                        />
                    </div>

                    <div>
                        <label>Email</label>
                        <input
                            name="email"
                            value={form.email}
                            onChange={handleChange}
                            className="w-full rounded-lg border px-3 py-2"
                        />
                    </div>

                    <div>
                        <label>ORCID</label>
                        <input
                            name="orcid"
                            value={form.orcid}
                            onChange={handleChange}
                            className="w-full rounded-lg border px-3 py-2"
                        />
                    </div>

                    <div>
                        <label>Academic title</label>
                        <input
                            name="academic_title"
                            value={form.academic_title}
                            onChange={handleChange}
                            className="w-full rounded-lg border px-3 py-2"
                        />
                    </div>

                    <div>
                        <label>Researcher code</label>
                        <input
                            name="researcher_code"
                            value={form.researcher_code}
                            onChange={handleChange}
                            className="w-full rounded-lg border px-3 py-2"
                        />
                    </div>

                    <div className="col-span-2">
                        <label>Department</label>

                        <select
                            name="department_id"
                            value={form.department_id}
                            onChange={handleChange}
                            className="w-full rounded-lg border px-3 py-2"
                        >
                            <option value="">
                                Chọn đơn vị
                            </option>

                            {departments.map((d) => (
                                <option
                                    key={d.department_id}
                                    value={d.department_id}
                                >
                                    {d.department_name}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="col-span-2">
                        <label className="flex items-center gap-2">
                            <input
                                type="checkbox"
                                checked={form.is_internal}
                                onChange={(e) =>
                                    setForm((prev) => ({
                                        ...prev,
                                        is_internal: e.target.checked,
                                    }))
                                }
                            />

                            Internal researcher
                        </label>
                    </div>

                </div>

                <div className="mt-6 flex justify-end gap-3">

                    <button
                        onClick={onClose}
                        className="cursor-pointer rounded-lg border px-5 py-2"
                    >
                        Cancel
                    </button>

                    <button
                        onClick={handleSubmit}
                        className="cursor-pointer rounded-lg bg-blue-600 px-5 py-2 text-white"
                    >
                        Save
                    </button>

                </div>

            </div>
        </div>
    );
}