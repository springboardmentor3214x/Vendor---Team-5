import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { ReportCatalog, ReportKey, ReportService } from '../../core/services/report.service';

interface ReportCard { key: ReportKey; title: string; description: string; }

@Component({ selector: 'app-reports', standalone: true, imports: [CommonModule], templateUrl: './reports.component.html', styleUrl: './reports.component.css' })
export class ReportsComponent {
  private readonly reportService = inject(ReportService);
  readonly catalog = signal<ReportCatalog | null>(null);
  readonly loading = signal(true); readonly errorMessage = signal(''); readonly exporting = signal<ReportKey | null>(null);
  readonly reportCards: ReportCard[] = [
    { key: 'vendor-performance', title: 'Vendor performance', description: 'Vendor performance measures and scores.' },
    { key: 'procurement', title: 'Procurement summary', description: 'Procurement requests, orders, and spending summary.' },
    { key: 'contracts', title: 'Contracts', description: 'Contract records and their current status.' },
    { key: 'compliance', title: 'Compliance', description: 'Vendor compliance status and related records.' },
    { key: 'vendor-documents', title: 'Vendor documents', description: 'Vendor document inventory and verification data.' }
  ];

  ngOnInit(): void { this.loadReports(); }
  loadReports(): void { this.loading.set(true); this.errorMessage.set(''); this.reportService.listReports().subscribe({ next: (catalog) => { this.catalog.set(catalog); this.loading.set(false); }, error: (error: unknown) => { this.errorMessage.set(this.readError(error)); this.loading.set(false); } }); }
  export(report: ReportKey): void { this.exporting.set(report); this.reportService.exportReport(report).subscribe({ next: (file) => { const url = URL.createObjectURL(file); const link = document.createElement('a'); link.href = url; link.download = `${report}_report.csv`; link.click(); URL.revokeObjectURL(url); this.exporting.set(null); }, error: (error: unknown) => { this.errorMessage.set(this.readError(error)); this.exporting.set(null); } }); }
  private readError(error: unknown): string { const detail = typeof error === 'object' && error !== null && 'error' in error ? (error as { error?: { detail?: unknown } }).error?.detail : null; return typeof detail === 'string' ? detail : 'Unable to load reports. Please try again.'; }
}
