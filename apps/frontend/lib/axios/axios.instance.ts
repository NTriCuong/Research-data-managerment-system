import axios from 'axios';
import { clientEnv } from '../env/client.env';

export const axiosInstance = axios.create({
    baseURL: clientEnv.NEXT_PUBLIC_API_URL,
    timeout: 15000,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true,
});

export default axiosInstance;