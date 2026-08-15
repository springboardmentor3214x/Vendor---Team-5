import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ReportCatalog, ReportChartData, ReportFilters, ReportFormat, ReportKey, ReportPreview, ReportService } from '../../core/services/report.service';

interface ReportCard { key: ReportKey; title: string; description: string; }

@Component({
  selector: 'app-reports', standalone: true, imports: [CommonModule, FormsModule], templateUrl: './reports.component.html', styleUrl: './reports.component.css'
})
export class ReportsComponent implements OnInit {
  private readonly reportService = inject(ReportService);
  readonly catalog = signal<ReportCatalog | null>(null); readonly loading = signal(true); readonly previewLoading = signal(false); readonly chartLoading = signal(false); readonly errorMessage = signal(''); readonly successMessage = signal(''); readonly exporting = signal<ReportFormat | null>(null); readonly preview = signal<ReportPreview | null>(null); readonly chart = signal<ReportChartData | null>(null);
  selectedReport: ReportKey = 'vendor-performance'; startDate = ''; endDate = ''; department = ''; vendorId: number | null = null; status = ''; reliabilityLevel = ''; sortBy = ''; sortOrder: 'asc' | 'desc' = 'asc';
  readonly reportCards: ReportCard[] = [
    { key: 'vendor-performance', title: 'Vendor performance', description: 'Delivery, quality, communication, service, and reliability results.' },
    { key: 'procurement', title: 'Procurement summary', description: 'Procurement requests, approvals, order costs, and workflow status.' },
    { key: 'purchase-orders', title: 'Purchase orders', description: 'Supplier purchase orders, delivery status, and invoice state.' },
    { key: 'contracts', title: 'Contracts', description: 'Contract lifecycle, expiry, and portfolio value.' },
    { key: 'compliance', title: 'Compliance', description: 'Verification records and compliance status.' },
    { key: 'executive-summary', title: 'Executive summary', description: 'Read-only leadership summary across persisted operations.' }
  ];
  ngOnInit(): void { this.loadReports(); this.loadPreview(); }
  loadReports(): void { this.loading.set(true); this.reportService.listReports().subscribe({ next: (catalog) => { this.catalog.set(catalog); this.loading.set(false); }, error: (error) => { this.errorMessage.set(this.readError(error)); this.loading.set(false); } }); }
  select(report: ReportKey): void { this.selectedReport = report; this.preview.set(null); this.chart.set(null); this.errorMessage.set(''); this.loadPreview(); }
  loadPreview(): void { this.previewLoading.set(true);this.chartLoading.set(true);this.errorMessage.set('');this.reportService.preview(this.selectedReport,this.filters()).subscribe({next:(preview)=>{this.preview.set(preview);this.previewLoading.set(false);},error:(error)=>{this.errorMessage.set(this.readError(error));this.previewLoading.set(false);}});this.reportService.chart(this.selectedReport,this.filters()).subscribe({next:(chart)=>{this.chart.set(chart);this.chartLoading.set(false);},error:()=>{this.chart.set(null);this.chartLoading.set(false);}}); }
  export(format: ReportFormat): void { this.exporting.set(format);this.errorMessage.set('');this.successMessage.set('');this.reportService.exportReport(this.selectedReport,format,this.filters()).subscribe({next:(file)=>{const url=URL.createObjectURL(file);const link=document.createElement('a');link.href=url;link.download=`${this.selectedReport}_report.${format==='excel'?'xlsx':format}`;link.click();URL.revokeObjectURL(url);this.successMessage.set(`${format.toUpperCase()} export downloaded.`);this.exporting.set(null);},error:(error)=>{this.errorMessage.set(this.readError(error));this.exporting.set(null);}}); }
  headers(): string[] { const row=this.preview()?.rows?.[0]; return row ? Object.keys(row) : []; }
  value(row: Record<string, unknown>, key: string): string { const value=row[key]; if(value===null||value===undefined||value==='')return '—';if(typeof value==='object')return JSON.stringify(value);return String(value); }
  reliabilityFilterAvailable(): boolean { return this.selectedReport === 'vendor-performance'; }
  maximum(values: number[]): number { return Math.max(...values, 1); }
  chartValue(index: number): number { return this.chart()?.datasets[0]?.data[index] ?? 0; }
  private filters(): ReportFilters { return {startDate:this.startDate||undefined,endDate:this.endDate||undefined,department:this.department||undefined,vendorId:this.vendorId||undefined,status:this.status||undefined,reliabilityLevel:this.reliabilityFilterAvailable()?this.reliabilityLevel||undefined:undefined,sortBy:this.sortBy||undefined,sortOrder:this.sortOrder}; }
  private readError(error: unknown): string { const detail=typeof error==='object'&&error!==null&&'error' in error?(error as {error?:{detail?:unknown}}).error?.detail:null;return typeof detail==='string'?detail:'Unable to load this report. Please check supported filters and try again.'; }
}
