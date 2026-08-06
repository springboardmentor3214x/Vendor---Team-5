import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ComplianceRecord, ComplianceService } from '../../../core/services/compliance.service';

type DashboardSection = Record<string, unknown>;
type DashboardResponse = Record<string, DashboardSection | undefined>;

@Component({
  selector: 'app-compliance-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="page-card">
      <div class="page-heading">
        <div>
          <span class="eyebrow">Governance workspace</span>
          <h2>Compliance Dashboard</h2>
          <p>Track contract compliance, document status, and notifications.</p>
        </div>
        <span class="live-badge">Live overview</span>
      </div>

      <p *ngIf="dashboardLoading()" class="state-message">Loading dashboard summary…</p>
      <p *ngIf="dashboardError()" class="alert alert-danger">{{ dashboardError() }}</p>

      <div *ngIf="dashboard() as data" class="dashboard-sections">
        <section class="summary-section">
          <h3>Compliance</h3>
          <div class="summary-grid">
            <article class="summary-card" *ngFor="let metric of complianceMetrics(data['compliance'])">
              <span>{{ metric.label }}</span><strong>{{ metric.value }}</strong>
            </article>
          </div>
        </section>

        <section class="summary-section">
          <h3>Contracts</h3>
          <div class="summary-grid">
            <article class="summary-card" *ngFor="let metric of contractMetrics(data['contracts'])">
              <span>{{ metric.label }}</span><strong>{{ metric.value }}</strong>
            </article>
          </div>
        </section>

        <section class="summary-section">
          <h3>Documents</h3>
          <div class="summary-grid">
            <article class="summary-card" *ngFor="let metric of documentMetrics(data['documents'])">
              <span>{{ metric.label }}</span><strong>{{ metric.value }}</strong>
            </article>
          </div>
        </section>

        <section class="summary-section">
          <h3>Notifications</h3>
          <div class="summary-grid summary-grid--compact">
            <article class="summary-card" *ngFor="let metric of notificationMetrics(data['notifications'])">
              <span>{{ metric.label }}</span><strong>{{ metric.value }}</strong>
            </article>
          </div>
        </section>
      </div>

      <div class="actions-panel">
        <h3>Manage vendor compliance</h3>
        <div class="bar">
          <input class="form-control" type="number" [(ngModel)]="vendorId" placeholder="Vendor ID" min="1">
          <button class="btn btn-primary" type="button" (click)="loadHistory()">Load history</button>
        </div>
        <form (ngSubmit)="verify()">
          <input class="form-control" [(ngModel)]="verifyStatus" name="verifyStatus" placeholder="Compliance status">
          <button class="btn btn-primary" type="submit">Verify compliance</button>
        </form>
        <p *ngIf="actionError()" class="alert alert-danger">{{ actionError() }}</p>
        <p *ngIf="historyLoading()" class="state-message">Loading compliance history…</p>
        <p *ngIf="historyLoaded() && !historyLoading() && !history().length" class="state-message">No compliance history was found for this vendor.</p>

        <table *ngIf="history().length">
          <tr><th>ID</th><th>Status</th><th></th></tr>
          <tr *ngFor="let item of history()">
            <td>{{ item.id }}</td>
            <td><input class="form-control" [(ngModel)]="item.status"></td>
            <td><button class="btn btn-primary" type="button" (click)="update(item)">Update status</button></td>
          </tr>
        </table>
      </div>
    </section>
  `,
  styles: [`
    section { color: var(--vr-navy); }
    h2, h3, p { margin-top: 0; }
    .page-heading { display:flex; justify-content:space-between; gap:1rem; align-items:flex-start; padding:1.25rem; border:1px solid #f3e8ff; border-radius:18px; background:linear-gradient(115deg,#fff7ed,#fff 58%,#f3e8ff); margin-bottom:1.25rem; }
    .page-heading p { color: #6b7280; margin-bottom: 0; }.eyebrow{display:block;color:#7c3aed;font-size:.72rem;font-weight:800;letter-spacing:.09em;text-transform:uppercase;margin-bottom:.3rem}.live-badge{background:#ecfdf5;color:#047857;border:1px solid #a7f3d0;border-radius:999px;padding:.38rem .65rem;font-size:.75rem;font-weight:800;white-space:nowrap}
    .dashboard-sections { display: grid; gap: 1rem; grid-template-columns:repeat(2,minmax(0,1fr)); }
    .summary-section { background:#fff;border:1px solid #e5e7eb;border-radius:18px;padding:1rem;box-shadow:0 8px 20px rgba(31,41,55,.06) }.summary-section h3, .actions-panel h3 { font-size: 1rem; margin-bottom: .75rem; }
    .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: .75rem; }
    .summary-grid--compact { grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }
    .summary-card { background: #fff; border: 1px solid #e5e7eb; border-top:4px solid #7c3aed; border-radius: 12px; padding: 1rem; min-height: 84px; display: flex; flex-direction: column; justify-content: space-between; }.summary-card:nth-child(4n+2){border-top-color:#f97316}.summary-card:nth-child(4n+3){border-top-color:#059669}.summary-card:nth-child(4n){border-top-color:#d97706}
    .summary-card span { color: #475569; font-size: .875rem; }
    .summary-card strong { color: var(--vr-navy); font-size: 1.5rem; margin-top: .5rem; }
    .actions-panel { border: 1px solid #e5e7eb; margin-top: 1.25rem; padding:1.25rem; border-radius:18px; background:#fff;box-shadow:0 8px 20px rgba(31,41,55,.06) }
    .bar, form { display: flex; gap: .75rem; margin: .75rem 0; align-items: center; }
    .bar .form-control, form .form-control { max-width: 320px; }
    .state-message { color: #64748b; padding: .75rem 0; }
    table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
    td, th { padding: .7rem; border-bottom: 1px solid var(--vr-border); text-align: left; }
    @media (max-width: 800px) { .dashboard-sections{grid-template-columns:1fr} }.bar,form{flex-wrap:wrap}@media (max-width: 640px) { .page-heading,.bar, form { align-items: stretch; flex-direction: column; } .bar .form-control, form .form-control { max-width: none; } }
  `]
})
export class ComplianceDashboardComponent {
  private service = inject(ComplianceService);

  vendorId = 0;
  verifyStatus = 'Compliant';
  readonly dashboard = signal<DashboardResponse | null>(null);
  readonly history = signal<ComplianceRecord[]>([]);
  readonly dashboardLoading = signal(true);
  readonly historyLoading = signal(false);
  readonly historyLoaded = signal(false);
  readonly dashboardError = signal('');
  readonly actionError = signal('');

  ngOnInit() {
    this.service.getDashboard().subscribe({
      next: data => { this.dashboard.set(data as DashboardResponse); this.dashboardLoading.set(false); },
      error: () => { this.dashboardError.set('Unable to load dashboard summary.'); this.dashboardLoading.set(false); }
    });
  }

  complianceMetrics(section?: DashboardSection) {
    return [
      this.metric('Total compliance records', section, 'totalComplianceRecords', 'total_compliance_records', 'total'),
      this.metric('Compliant', section, 'compliantCount', 'compliant_count', 'compliant'),
      this.metric('Non-compliant', section, 'nonCompliantCount', 'non_compliant_count', 'nonCompliant', 'non_compliant'),
      this.metric('Pending', section, 'pendingCount', 'pending_count', 'pending'),
      this.metric('Expired', section, 'expiredCount', 'expired_count', 'expired')
    ];
  }

  contractMetrics(section?: DashboardSection) {
    return [
      this.metric('Total contracts', section, 'totalContracts', 'total_contracts', 'total'),
      this.metric('Active contracts', section, 'activeContracts', 'active_contracts', 'active'),
      this.metric('Expired contracts', section, 'expiredContracts', 'expired_contracts', 'expired'),
      this.metric('Expiring soon', section, 'expiringSoon', 'expiring_soon', 'expiringSoonContracts', 'expiring_soon_contracts')
    ];
  }

  documentMetrics(section?: DashboardSection) {
    return [
      this.metric('Total documents', section, 'totalDocuments', 'total_documents', 'total'),
      this.metric('Total certifications', section, 'totalCertifications', 'total_certifications', 'certifications'),
      this.metric('Expired certifications', section, 'expiredCertifications', 'expired_certifications'),
      this.metric('Expiring soon certifications', section, 'expiringSoonCertifications', 'expiring_soon_certifications', 'expiringSoon', 'expiring_soon')
    ];
  }

  notificationMetrics(section?: DashboardSection) {
    return [
      this.metric('Total notifications', section, 'totalNotifications', 'total_notifications', 'total'),
      this.metric('Unread notifications', section, 'unreadNotifications', 'unread_notifications', 'unread')
    ];
  }

  loadHistory() {
    if (!this.vendorId) { this.actionError.set('Enter a vendor ID to load compliance history.'); return; }
    this.actionError.set(''); this.historyLoading.set(true); this.historyLoaded.set(false);
    this.service.getVendorCompliance(this.vendorId).subscribe({
      next: items => { this.history.set(items); this.historyLoading.set(false); this.historyLoaded.set(true); },
      error: () => { this.actionError.set('Unable to load compliance history.'); this.historyLoading.set(false); }
    });
  }

  verify() {
    if (!this.vendorId) { this.actionError.set('Enter a vendor ID to verify compliance.'); return; }
    this.actionError.set('');
    this.service.verifyCompliance({ vendor_id: this.vendorId, status: this.verifyStatus }).subscribe({
      next: () => this.loadHistory(),
      error: () => this.actionError.set('Unable to verify compliance.')
    });
  }

  update(item: ComplianceRecord) {
    this.actionError.set('');
    this.service.updateComplianceStatus(item.id, item.status ?? item.compliance_status ?? '').subscribe({
      next: () => this.loadHistory(),
      error: () => this.actionError.set('Unable to update compliance status.')
    });
  }

  private metric(label: string, section: DashboardSection | undefined, ...keys: string[]) {
    const value = keys.map(key => section?.[key]).find(item => item !== undefined && item !== null);
    return { label, value: typeof value === 'number' || typeof value === 'string' ? value : 0 };
  }
}
