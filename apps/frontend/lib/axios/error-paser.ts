import { AxiosError } from "axios";

export interface AppError { // cấu trúc của err sau khi đã đượ parse
    message: string;
    statusCode: number;
    code: string;
}
export const parseAxiosError = (error: AxiosError | any): AppError => {
    // Nếu lỗi đã được parse trước đó thì trả lại trực tiếp để tránh mất status gốc.
    if (
        typeof error?.statusCode === "number" &&
        typeof error?.message === "string" &&
        typeof error?.code === "string"
    ) {
        return {
            statusCode: error.statusCode,
            code: error.code,
            message: error.message,
        };
    }

    const data = error?.response?.data;
    // Ưu tiên lấy message từ response data, sau đó mới đến message của error gốc.
    let errMessage = data?.message ?? data?.detail ?? error?.message ?? 'Có lỗi xảy ra';

    if (Array.isArray(errMessage)) {
        errMessage = errMessage[0]?.message || errMessage[0];
    }

    if (typeof errMessage === 'object' && errMessage !== null) {
        errMessage = (errMessage as any).message || JSON.stringify(errMessage);
    }

    const isNetworkError = error?.code === "ERR_NETWORK";

    return {
        statusCode: data?.statusCode ?? error?.response?.status ?? (isNetworkError ? 0 : 500),
        code: data?.code ?? error?.code ?? 'UNKNOWN_ERROR',
        message: errMessage,
    };
};