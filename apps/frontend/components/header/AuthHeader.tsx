import { Bell, User } from "lucide-react";
import type { CurrentUser } from "@/store/slice/auth.slice";

interface AuthHeaderProps {
    currentUser: CurrentUser;
}

export default function AuthHeader({ currentUser }: AuthHeaderProps) {
    return (
        <header className="relative flex h-12 items-center justify-end gap-7 border-b border-[#dcdcdc] bg-[#f7f7f7] pr-12.5">

            <button
                type="button"
                aria-label="Notifications"
                className="flex cursor-pointer items-center text-[#5f6f8c] transition hover:text-[#1f3568]"
            >
                <Bell size={22} />
            </button>
            <button
                type="button"
                aria-label="Account"
                title={currentUser.full_name}
                className="flex cursor-pointer items-center text-[#5f6f8c] transition hover:text-[#1f3568]"
            >
                <User size={22} />
            </button>
        </header>
    );
}
