import { CommonModule } from '@angular/common';
import { Component, HostListener, OnInit, inject, signal } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService, UserProfile } from '../core/services/auth.service';
import { Notification, NotificationService } from '../core/services/notification.service';

interface NavItem {
  label: string;
  path: string;
  exact: boolean;
  roles: string[];
}

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app-shell.component.html',
  styleUrl: './app-shell.component.css'
})
export class AppShellComponent implements OnInit {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly notificationService = inject(NotificationService);
  readonly unreadNotifications = signal(0);
  readonly recentNotifications = signal<Notification[]>([]);
  readonly notificationOpen = signal(false);

  get currentUser(): UserProfile | null {
    return this.authService.getStoredUser();
  }

  private readonly navItems: NavItem[] = [
    {
      label: 'Dashboard',
      path: '/dashboard',
      exact: true,
      roles: [
        'Administrator',
        'Procurement Manager',
        'Supply Chain Manager',
        'Vendor',
        'Finance Officer',
        'Auditor',
        'Department User'
      ]
    },
    {
      label: 'Vendors',
      path: '/vendors',
      exact: false,
      roles: ['Administrator', 'Procurement Manager', 'Supply Chain Manager']
    },
    {
      label: 'Procurement',
      path: '/procurement',
      exact: true,
      roles: ['Administrator', 'Procurement Manager', 'Supply Chain Manager']
    },
    {
      label: 'My procurement requests',
      path: '/procurement/requests',
      exact: false,
      roles: ['Department User']
    },
    {
      label: 'Invoices',
      path: '/procurement/invoices',
      exact: false,
      roles: ['Administrator', 'Procurement Manager', 'Finance Officer']
    },
    {
      label: 'Performance',
      path: '/performance',
      exact: true,
      roles: ['Administrator', 'Procurement Manager', 'Supply Chain Manager', 'Auditor']
    },
    {
      label: 'Reliability',
      path: '/reliability',
      exact: true,
      roles: ['Administrator', 'Procurement Manager', 'Supply Chain Manager', 'Auditor']
    },
    {
      label: 'Contract Repository',
      path: '/contracts',
      exact: true,
      roles: ['Administrator', 'Procurement Manager', 'Vendor', 'Auditor', 'Finance Officer']
    },
    {
      label: 'Compliance',
      path: '/contracts/compliance',
      exact: true,
      roles: ['Administrator', 'Procurement Manager', 'Auditor']
    },
    {
      label: 'Certifications',
      path: '/contracts/certifications',
      exact: true,
      roles: ['Administrator', 'Procurement Manager', 'Auditor']
    },
    {
      label: 'Vendor Documents',
      path: '/contracts/documents',
      exact: true,
      roles: ['Administrator', 'Procurement Manager', 'Auditor']
    },
    {
      label: 'Contract Notifications',
      path: '/contracts/notifications',
      exact: true,
      roles: ['Administrator', 'Procurement Manager', 'Auditor', 'Finance Officer']
    },
    {
      label: 'Communications',
      path: '/communications',
      exact: true,
      roles: ['Administrator', 'Procurement Manager', 'Supply Chain Manager', 'Vendor', 'Auditor']
    },
    {
      label: 'Messages',
      path: '/messages',
      exact: false,
      roles: ['Administrator', 'Procurement Manager', 'Supply Chain Manager', 'Vendor', 'Finance Officer', 'Auditor']
    },
    {
      label: 'Analytics',
      path: '/analytics',
      exact: true,
      roles: ['Administrator', 'Procurement Manager', 'Supply Chain Manager', 'Vendor', 'Finance Officer', 'Auditor']
    },
    {
      label: 'Reports',
      path: '/reports',
      exact: true,
      roles: ['Administrator', 'Procurement Manager', 'Supply Chain Manager', 'Finance Officer', 'Auditor']
    },
    {
      label: 'Profile',
      path: '/profile',
      exact: true,
      roles: [
        'Administrator',
        'Procurement Manager',
        'Supply Chain Manager',
        'Vendor',
        'Finance Officer',
        'Auditor',
        'Department User'
      ]
    }
  ];

  get visibleNavItems(): NavItem[] {
    const role = this.currentUser?.role;
    if (!role) {
      return [];
    }
    return this.navItems.filter((item) => item.roles.includes(role));
  }

  ngOnInit(): void { this.refreshNotifications(); }

  toggleNotifications(event: MouseEvent): void { event.stopPropagation(); this.notificationOpen.update((open) => !open); if (this.notificationOpen()) this.refreshNotifications(); }
  refreshNotifications(): void { this.notificationService.list().subscribe({ next: (result) => { this.recentNotifications.set(result.items.slice(0, 5)); this.unreadNotifications.set(result.unreadCount); }, error: () => { this.recentNotifications.set([]); this.unreadNotifications.set(0); } }); }
  openNotification(item: Notification): void { const destination = item.link || this.modulePath(item.relatedModule); const finish = () => { this.notificationOpen.set(false); this.refreshNotifications(); if (destination) this.router.navigateByUrl(destination); }; if (!item.isRead) { this.notificationService.markRead(item.id).subscribe({ next: finish, error: finish }); } else { finish(); } }
  openAllNotifications(): void { this.notificationOpen.set(false); this.router.navigateByUrl('/notifications'); }
  @HostListener('document:click') closeNotifications(): void { this.notificationOpen.set(false); }

  logout(): void {
    this.authService.logout();
    this.router.navigateByUrl('/login');
  }

  private modulePath(module: string | null): string | null { const value = (module || '').toLowerCase(); if (value.includes('contract')) return '/contracts'; if (value.includes('compliance')) return '/contracts/compliance'; if (value.includes('procurement')) return '/procurement'; if (value.includes('message')) return '/messages'; if (value.includes('performance')) return '/performance'; if (value.includes('reliability')) return '/reliability'; if (value.includes('vendor')) return '/vendors'; return null; }
}
