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
          <h2>Compliance Dashboard</h2>
          <p>Track contract compliance, document status, and notifications.</p>
        </div>
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
    .page-heading p { color: #64748b; margin-bottom: 1.25rem; }
    .dashboard-sections { display: grid; gap: 1.25rem; }
    .summary-section h3, .actions-panel h3 { font-size: 1rem; margin-bottom: .75rem; }
    .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: .75rem; }
    .summary-grid--compact { grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }
    .summary-card { background: #eff6ff; border: 1px solid #dbeafe; border-radius: 12px; padding: 1rem; min-height: 84px; display: flex; flex-direction: column; justify-content: space-between; }
    .summary-card span { color: #475569; font-size: .875rem; }
    .summary-card strong { color: var(--vr-navy); font-size: 1.5rem; margin-top: .5rem; }
    .actions-panel { border-top: 1px solid var(--vr-border); margin-top: 1.5rem; padding-top: 1.25rem; }
    .bar, form { display: flex; gap: .75rem; margin: .75rem 0; align-items: center; }
    .bar .form-control, form .form-control { max-width: 320px; }
    .state-message { color: #64748b; padding: .75rem 0; }
    table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
    td, th { padding: .7rem; border-bottom: 1px solid var(--vr-border); text-align: left; }
    @media (max-width: 640px) { .bar, form { align-items: stretch; flex-direction: column; } .bar .form-control, form .form-control { max-width: none; } }
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
