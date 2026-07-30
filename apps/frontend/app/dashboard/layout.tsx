"use client";

import FirebaseInitializer from "@/components/filebase/FirebaseInitializer";
import AppSidebar, { type AppSidebarItem } from "@/components/app-sidebar";
import Header from "@/components/header/Header";
import ProtectedRoute from "@/components/ProtectedRoute";
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar";
import { useAppSelector } from "@/lib/hooks/hooks";
import { selectCurrentUser } from "@/store/slice/auth.slice";
import {
  BarChart3,
  Building2,
  FileText,
  House,
  Layers3,
  Plus,
  ScrollText,
  UserRoundSearch,
  Users,
  ListTodo,
  CircleGauge,
  ShieldCheck
} from "lucide-react";

const items_data_entry: AppSidebarItem[] = [
  { label: "Tổng quan", href: "/dashboard/data-entry/researches", icon: CircleGauge },
  { label: "Nghiên cứu mới", href: "/dashboard/data-entry/new-entry", icon: Plus },
];

const items_reviewer: AppSidebarItem[] = [
  { label: "Kiểm duyệt", href: "/dashboard/review/researches", icon: ListTodo },
];

const items_approver: AppSidebarItem[] = [
  { label: "Phê duyệt", href: "/dashboard/approval/researches", icon: ListTodo },
  { label: "Quyền truy cập", href: "/dashboard/approval/file-permissions", icon: ShieldCheck },
];

const items_super_admin: AppSidebarItem[] = [
  { label: "Tổng quan", href: "/dashboard/superadmin/", icon: House },
  { label: "Người dùng", href: "/dashboard/superadmin/users", icon: Users },
  { label: "Kho nghiên cứu", href: "/dashboard/superadmin/researches", icon: FileText },
  { label: "Đơn vị", href: "/dashboard/superadmin/departments", icon: Building2 },
  { label: "Loại sản phẩm", href: "/dashboard/superadmin/output-type", icon: Layers3 },
  { label: "Nhà nghiên cứu", href: "/dashboard/superadmin/researchers", icon: UserRoundSearch },
  { label: "Nhật ký", href: "/dashboard/superadmin/logs", icon: ScrollText },
];

const items_manager: AppSidebarItem[] = [
  { label: "Báo cáo", href: "/dashboard/reports", icon: BarChart3 },
];

const ROLE_SIDEBAR_ITEMS: Record<string, AppSidebarItem[]> = {
  "Data Entry User": items_data_entry,
  "Metadata Reviewer": items_reviewer,
  "Metadata Approver": items_approver,
  "Super Administrator": items_super_admin,
  "Research Manager": items_manager,
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
      <FirebaseInitializer />
      <SidebarProvider>
        <AppSidebar items={items} currentUser={currentUser} />
        <SidebarInset className="h-screen overflow-hidden">
          <Header />
          <main className="flex-1 overflow-y-auto">{children}</main>
        </SidebarInset>
      </SidebarProvider>
    </ProtectedRoute>
  );
}
