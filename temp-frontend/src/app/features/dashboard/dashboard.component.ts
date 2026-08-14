import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterLink } from '@angular/router';
import { AppRole, AuthService } from '../../core/services/auth.service';
import { ConversationSummary, DirectMessageService } from '../../core/services/direct-message.service';
import { environment } from '../../../environments/environment';

interface DashboardView {
  title: string;
  description: string;
  cards: { title: string; description: string; actionLabel: string; path: string; tone: string; icon: string; badge: string }[];
  highlights: string[];
  primaryAction: {
    label: string;
    path: string;
  };
}
interface DashboardKpi {
  label: string;
  value: number | string;
  icon: string;
  tone: string;
}
interface ChartSeries { title:string; labels:string[]; datasets:{label?:string;data:number[];backgroundColor?:string|string[];borderColor?:string}[]; }
interface ChartResponse { monthlyExpensesChart:ChartSeries; vendorPerformanceTrendChart:ChartSeries; categoryDistributionChart:ChartSeries; contractStatusChart:ChartSeries; }

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit {
  private readonly authService = inject(AuthService);
  private readonly http = inject(HttpClient);
  private readonly messages = inject(DirectMessageService);

  get view(): DashboardView {
    return this.views[this.authService.getUserRole() as AppRole] ?? this.views.Vendor;
  }

  readonly kpis = signal<DashboardKpi[]>([
    { label: 'Active vendors', value: 0, icon: '👥', tone: 'success' },
    { label: 'Open procurement', value: 0, icon: '📋', tone: 'primary' },
    { label: 'Invoices to review', value: 0, icon: '🧾', tone: 'warning' },
    { label: 'Active contracts', value: 0, icon: '📄', tone: 'info' }
  ]);
  readonly charts = signal<ChartResponse | null>(null);
  readonly conversations = signal<ConversationSummary[]>([]);
  readonly conversationError = signal('');

  get isVendor(): boolean { return this.authService.getUserRole() === 'Vendor'; }
  get canViewCharts(): boolean {
    return ['Administrator', 'Procurement Manager', 'Supply Chain Manager', 'Auditor'].includes(this.authService.getUserRole() ?? '');
  }

  ngOnInit(): void {
    const role = this.authService.getUserRole();
    if (role === 'Department User') {
      this.loadDepartmentDashboard();
      return;
    }
    if (this.canViewCharts) {
      this.http.get<ChartResponse>(`${environment.apiUrl}/dashboard/charts`).subscribe({
        next: charts => this.charts.set(charts), error: () => this.charts.set(null)
      });
    }
    if (role === 'Vendor') {
      this.messages.listConversations(5).subscribe({
        next: conversations => this.conversations.set(conversations),
        error: () => this.conversationError.set('Recent conversations could not be loaded.')
      });
    }
    if (role === 'Administrator') { this.http.get<Record<string, number>>(`${environment.apiUrl}/dashboard/admin`).subscribe({ next: (data) => this.setKpis([{label:'Active vendors',value:data['approvedVendors'] ?? 0,icon:'👥',tone:'success'},{label:'Procurement requests',value:data['totalProcurementRequests'] ?? 0,icon:'📋',tone:'primary'},{label:'Purchase orders',value:data['totalPurchaseOrders'] ?? 0,icon:'🧾',tone:'warning'},{label:'Active users',value:data['activeUsers'] ?? 0,icon:'👤',tone:'info'}]) }); return; }
    if (role === 'Procurement Manager' || role === 'Supply Chain Manager') { this.http.get<{procurementSummary?:Record<string,number>;deliverySummary?:Record<string,number>}>(`${environment.apiUrl}/dashboard/procurement`).subscribe({ next: (data) => { const s=data.procurementSummary ?? {}; const d=data.deliverySummary ?? {}; this.setKpis([{label:'Procurement requests',value:s['totalRequests'] ?? 0,icon:'📋',tone:'primary'},{label:'Pending approvals',value:s['pendingApprovals'] ?? 0,icon:'⏳',tone:'warning'},{label:'Active purchase orders',value:s['activePurchaseOrders'] ?? 0,icon:'📦',tone:'success'},{label:'Delayed deliveries',value:d['delayedDeliveries'] ?? 0,icon:'🚚',tone:'info'}]); } }); return; }
    if (role === 'Vendor') { this.http.get<Record<string,number>>(`${environment.apiUrl}/dashboard/vendor`).subscribe({ next: (data) => this.setKpis([{label:'Reliability score',value:data['reliabilityScore'] ?? 0,icon:'⭐',tone:'success'},{label:'Active orders',value:data['activePurchaseOrders'] ?? 0,icon:'📦',tone:'primary'},{label:'Unread messages',value:data['unreadMessages'] ?? 0,icon:'💬',tone:'warning'},{label:'Active contracts',value:data['activeContracts'] ?? 0,icon:'📄',tone:'info'}]) }); return; }
    this.http.get<{contracts?:Record<string,number>;compliance?:Record<string,number>;documents?:Record<string,number>;notifications?:Record<string,number>}>(`${environment.apiUrl}/dashboard`).subscribe({ next: (data) => this.setKpis([{label:'Active contracts',value:data.contracts?.['activeContracts'] ?? 0,icon:'📄',tone:'success'},{label:'Pending compliance',value:data.compliance?.['pendingCount'] ?? 0,icon:'✓',tone:'primary'},{label:'Documents',value:data.documents?.['totalDocuments'] ?? 0,icon:'📁',tone:'warning'},{label:'Unread alerts',value:data.notifications?.['unreadNotifications'] ?? 0,icon:'🔔',tone:'info'}]) });
  }

  private loadDepartmentDashboard(): void {
    this.setKpis([
      { label: 'Request workspace', value: 'Available', icon: '📋', tone: 'primary' },
      { label: 'Approval access', value: 'Manager-led', icon: '⏳', tone: 'warning' },
      { label: 'Purchase-order access', value: 'Manager-led', icon: '📦', tone: 'info' },
      { label: 'Profile', value: 'Ready', icon: '👤', tone: 'success' }
    ]);
  }

  private setKpis(kpis: DashboardKpi[]): void {
    this.kpis.set(kpis.map((kpi) => ({
      ...kpi,
      value: typeof kpi.value === 'number' ? Number(kpi.value) || 0 : kpi.value,
    })));
  }

  maximum(data: number[]): number { return Math.max(...data, 1); }
  linePoints(data: number[]): string { const max=this.maximum(data); return data.map((value,index)=>`${index*(300/Math.max(data.length-1,1))},${120-(value/max)*120}`).join(' '); }
  doughnut(data: number[], colors: string[]): string { const total=data.reduce((sum,value)=>sum+value,0)||1; let current=0; return data.map((value,index)=>{const start=current/total*360;current+=value;return `${colors[index%colors.length]} ${start}deg ${current/total*360}deg`;}).join(','); }
  hasChartData(chart: ChartSeries | undefined): boolean {
    return !!chart?.labels?.length && !!chart.datasets?.some((dataset) =>
      dataset.data?.some((value) => Number.isFinite(value))
    );
  }

  chartColors(_colors: string|string[]|undefined): string[] {
    // Keep analytics aligned with the application's existing red/pink palette,
    // regardless of the legacy colour hints returned by a dashboard endpoint.
    return ['#e11d48', '#fb7185', '#be123c', '#fda4af', '#9f1239'];
  }

  private readonly views: Record<AppRole, DashboardView> = {
    Administrator: {
      title: 'Administrator dashboard',
      description: 'Access the vendor, procurement, and performance workspaces available to your role.',
      cards: [
        { title: 'Vendor management', description: 'Review registered vendors and their current approval status.', actionLabel: 'Open vendors', path: '/vendors', tone: 'success', icon: '👥', badge: 'Directory' },
        { title: 'Procurement workflow', description: 'Manage requests, purchase orders, tracking, and invoices.', actionLabel: 'Open procurement', path: '/procurement', tone: 'primary', icon: '📋', badge: 'Operations' },
        { title: 'Performance monitoring', description: 'Review vendor performance records and rankings.', actionLabel: 'Open performance', path: '/performance', tone: 'info', icon: '📈', badge: 'Insights' }
      ],
      highlights: [
        'Review and action vendor records from the vendor workspace.',
        'Use your profile page to keep account information and credentials current.',
        'Additional operational modules remain accessible as their frontend integration is completed.'
      ],
      primaryAction: { label: 'Manage vendors', path: '/vendors' }
    },
    'Procurement Manager': {
      title: 'Procurement dashboard',
      description: 'Manage vendor records and progress pending supplier decisions.',
      cards: [
        { title: 'Vendor workspace', description: 'Review vendor records and statuses.', actionLabel: 'Open vendors', path: '/vendors', tone: 'success', icon: '👥', badge: 'Directory' },
        { title: 'Procurement workflow', description: 'Manage requests and purchase orders.', actionLabel: 'Open procurement', path: '/procurement', tone: 'primary', icon: '📋', badge: 'Operations' },
        { title: 'Performance monitoring', description: 'Review and record supplier performance.', actionLabel: 'Open performance', path: '/performance', tone: 'info', icon: '📈', badge: 'Insights' }
      ],
      highlights: [
        'Search vendor records by company, contact, and current status.',
        'Approve or reject pending vendors directly from their detail pages.',
        'Maintain your account details from the profile page.'
      ],
      primaryAction: { label: 'Open vendors', path: '/vendors' }
    },
    'Supply Chain Manager': {
      title: 'Supply chain dashboard',
      description: 'Monitor vendor status and participate in the approval workflow.',
      cards: [
        { title: 'Vendor workspace', description: 'Review vendor records and statuses.', actionLabel: 'Open vendors', path: '/vendors', tone: 'success', icon: '👥', badge: 'Directory' },
        { title: 'Procurement monitoring', description: 'Monitor purchase orders and delivery tracking.', actionLabel: 'Open procurement', path: '/procurement', tone: 'primary', icon: '🚚', badge: 'Operations' },
        { title: 'Performance monitoring', description: 'Review vendor performance and rankings.', actionLabel: 'Open performance', path: '/performance', tone: 'info', icon: '📈', badge: 'Insights' }
      ],
      highlights: [
        'Use filters to focus on vendors by status and approval state.',
        'Review vendor profiles before taking an approval decision.',
        'Maintain your account details from the profile page.'
      ],
      primaryAction: { label: 'Review vendors', path: '/vendors' }
    },
    Vendor: {
      title: 'Vendor dashboard',
      description: 'Your role-based workspace for account and vendor-related activity.',
      cards: [
        { title: 'Account profile', description: 'Review your registered account details.', actionLabel: 'Open profile', path: '/profile', tone: 'success', icon: '👤', badge: 'Account' },
        { title: 'Password controls', description: 'Update your password from your profile.', actionLabel: 'Manage profile', path: '/profile', tone: 'primary', icon: '🔐', badge: 'Security' }
      ],
      highlights: [
        'Keep your company and contact information up to date in your profile.',
        'Use the password controls in your profile to maintain account security.',
        'Vendor record access is limited to the permissions assigned to your role.'
      ],
      primaryAction: { label: 'Open profile', path: '/profile' }
    },
    'Finance Officer': {
      title: 'Finance dashboard',
      description: 'Your role-based workspace is ready for finance integrations.',
      cards: [
        { title: 'Invoice workspace', description: 'Review invoices and payment statuses.', actionLabel: 'Open invoices', path: '/procurement/invoices', tone: 'success', icon: '🧾', badge: 'Finance' },
        { title: 'Account profile', description: 'Review your registered account details.', actionLabel: 'Open profile', path: '/profile', tone: 'primary', icon: '👤', badge: 'Account' }
      ],
      highlights: [
        'Maintain your account and contact details from the profile page.',
        'Use the invoice workspace to review current payment activity.',
        'Your current access remains limited to the permissions assigned to your role.'
      ],
      primaryAction: { label: 'Open profile', path: '/profile' }
    },
    Auditor: {
      title: 'Auditor dashboard',
      description: 'Your role-based workspace is ready for audit integrations.',
      cards: [
        { title: 'Performance monitoring', description: 'Review performance records and rankings.', actionLabel: 'Open performance', path: '/performance', tone: 'success', icon: '📈', badge: 'Insights' },
        { title: 'Account profile', description: 'Review your registered account details.', actionLabel: 'Open profile', path: '/profile', tone: 'primary', icon: '👤', badge: 'Account' }
      ],
      highlights: [
        'Maintain your account and contact details from the profile page.',
        'Performance records remain read-only for your role in the frontend workflow.',
        'Your current access remains limited to the permissions assigned to your role.'
      ],
      primaryAction: { label: 'Open profile', path: '/profile' }
    },
    'Department User': {
      title: 'Department dashboard',
      description: 'Create and follow procurement requests for your department.',
      cards: [
        { title: 'New procurement request', description: 'Submit a request for the procurement workflow.', actionLabel: 'Create request', path: '/procurement/requests/new', tone: 'primary', icon: 'ðŸ“‹', badge: 'Requests' },
        { title: 'My procurement requests', description: 'Review submitted requests and their current approval status.', actionLabel: 'Open requests', path: '/procurement/requests', tone: 'success', icon: 'ðŸ“‚', badge: 'Tracking' },
        { title: 'Account profile', description: 'Review your registered account details and credentials.', actionLabel: 'Open profile', path: '/profile', tone: 'info', icon: 'ðŸ‘¤', badge: 'Account' }
      ],
      highlights: [
        'Submit complete request details to avoid approval delays.',
        'Follow request status from the procurement request workspace.',
        'Approval, vendor assignment, and purchase-order actions remain manager-controlled.'
      ],
      primaryAction: { label: 'Create request', path: '/procurement/requests/new' }
    }
  };
}
