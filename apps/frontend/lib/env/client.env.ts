export const clientEnv = {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "",
    NEXT_PUBLIC_PUBLIC_HOME_BANNER_URL: process.env.NEXT_PUBLIC_PUBLIC_HOME_BANNER_URL || "",
};

if (!clientEnv.NEXT_PUBLIC_API_URL) {
    console.log(clientEnv);
    throw new Error("Missing env: NEXT_PUBLIC_API_URL");
}
