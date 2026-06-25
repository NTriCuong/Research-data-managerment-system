"use client";

import AppSidebar, { type AppSidebarItem } from "@/components/app-sidebar";
import Header from "@/components/header/Header";
import ProtectedRoute from "@/components/ProtectedRoute";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { useAppSelector } from "@/store/hooks";
import { selectCurrentUser } from "@/store/slice/auth.slice";
import {
  Building2,
  CheckCheck,
  ClipboardList,
  FileText,
  House,
  Layers3,
  Plus,
  ScrollText,
  UserRoundSearch,
  Users,
  ListTodo
} from "lucide-react";

const items_data_entry: AppSidebarItem[] = [
  { label: "Tổng quan", href: "/dashboard/data-entry/researches", icon: House },
  { label: "Nghiên cứu mới", href: "/dashboard/data-entry/new-entry", icon: Plus },
];

const items_reviewer: AppSidebarItem[] = [
  { label: "Kiểm duyệt", href: "/dashboard/review/researches", icon: ListTodo },
];

const items_approver: AppSidebarItem[] = [
  { label: "Kiểm duyệt", href: "/dashboard/approval/researches", icon: ListTodo },
];

const items_super_admin: AppSidebarItem[] = [
  { label: "Người dùng", href: "/dashboard/superadmin/users", icon: Users },
  { label: "Kho nghiên cứu", href: "/dashboard/superadmin/researches", icon: FileText },
  { label: "Đơn vị", href: "/dashboard/superadmin/departments", icon: Building2 },
  { label: "Loại sản phẩm", href: "/dashboard/superadmin/output-type", icon: Layers3 },
  { label: "Nhà nghiên cứu", href: "/dashboard/superadmin/researchers", icon: UserRoundSearch },
  { label: "Nhật ký", href: "/dashboard/superadmin/logs", icon: ScrollText },
];

const ROLE_SIDEBAR_ITEMS: Record<string, AppSidebarItem[]> = {
  "Data Entry User": items_data_entry,
  "Metadata Reviewer": items_reviewer,
  "Metadata Approver": items_approver,
  "Super Administrator": items_super_admin,
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const currentUser = useAppSelector(selectCurrentUser);
  const items = currentUser ? ROLE_SIDEBAR_ITEMS[currentUser.role_name] ?? [] : [];

  return (
    <ProtectedRoute>
      <SidebarProvider>
        <AppSidebar items={items} currentUser={currentUser} />
        <SidebarInset className="h-screen overflow-hidden">
          <div className="flex h-12 shrink-0 items-center border-b bg-background">
            <SidebarTrigger className="ml-2" />
            <div className="flex-1">
              <Header />
            </div>
          </div>
          <main className="flex-1 overflow-y-auto">{children}</main>
        </SidebarInset>
      </SidebarProvider>
    </ProtectedRoute>
  );
}
