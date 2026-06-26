"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Globe2, Settings, type LucideIcon } from "lucide-react";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from "@/components/ui/sidebar";
import { TypographySmall } from "@/components/ui/typography";
import type { CurrentUser } from "@/store/slice/auth.slice";

export interface AppSidebarItem {
  label: string;
  href: string;
  icon?: LucideIcon;
}

interface AppSidebarProps {
  items: AppSidebarItem[];
  currentUser: CurrentUser | null;
}

function getInitials(name?: string) {
  if (!name) return "U";

  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
}

export default function AppSidebar({ items, currentUser }: AppSidebarProps) {
  const pathname = usePathname();
  const isSettingsActive = pathname === "/dashboard/settings";

  return (
    <Sidebar>
      <SidebarHeader className="items-center px-4 py-5">
        <Link href="/dashboard" className="flex w-full items-center justify-center">
          <Image
            src="/logo-stu.svg"
            alt="STU"
            width={176}
            height={56}
            priority
            className="h-20 w-auto group-data-[collapsible=icon]:h-8"
          />
        </Link>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Dashboard</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => {
                const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
                const Icon = item.icon;

                return (
                  <SidebarMenuItem key={item.href}>
                    <SidebarMenuButton asChild isActive={isActive} tooltip={item.label}>
                      <Link href={item.href}>
                        {Icon && <Icon />}
                        <span>{item.label}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="gap-2 border-t border-gray-200 p-2">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton asChild isActive={isSettingsActive} tooltip="Cài đặt cá nhân">
              <Link href="/dashboard/settings">
                <Settings />
                <span>Cài đặt trang cá nhân</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
          <SidebarMenuItem>
            <SidebarMenuButton asChild tooltip="Trang chủ">
              <Link href="/">
                <Globe2 />
                <span>Trang chủ</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>

        <Link
          href="/dashboard/settings"
          className="flex min-w-0 items-center gap-2 rounded-lg px-2 py-2 text-left transition hover:bg-gray-100"
        >
          <Avatar size="sm">
            <AvatarFallback>{getInitials(currentUser?.full_name)}</AvatarFallback>
          </Avatar>
          <div className="min-w-0 group-data-[collapsible=icon]:hidden">
            <TypographySmall as="p" className="truncate text-gray-900">
              {currentUser?.full_name ?? "Nguoi dung"}
            </TypographySmall>
            <TypographySmall as="p" className="truncate font-normal">
              {currentUser?.role_name ?? "Chua co vai tro"}
            </TypographySmall>
          </div>
        </Link>
      </SidebarFooter>

      <SidebarRail />
    </Sidebar>
  );
}
