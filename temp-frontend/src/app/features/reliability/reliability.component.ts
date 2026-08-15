import { CommonModule } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { catchError, forkJoin, of } from 'rxjs';
import { ReliabilityDashboard, ReliabilityDetails, ReliabilityRanking, ReliabilityRecommendation, ReliabilityRiskLevel, ReliabilityService, ReliabilityTrend } from '../../core/services/reliability.service';

interface Kpi { label: string; value: string | number; }

@Component({ selector: 'app-reliability', standalone: true, imports: [CommonModule], templateUrl: './reliability.component.html', styleUrl: './reliability.component.css' })
export class ReliabilityComponent {
  private readonly service = inject(ReliabilityService);
  readonly dashboard = signal<ReliabilityDashboard>({});
  readonly rankings = signal<ReliabilityRanking[]>([]);
  readonly riskLevels = signal<ReliabilityRiskLevel[]>([]);
  readonly recommendations = signal<ReliabilityRecommendation[]>([]);
  readonly selectedDetails = signal<ReliabilityDetails | null>(null);
  readonly trends = signal<ReliabilityTrend[]>([]);
  readonly selectedVendorId = signal<number | null>(null);
  readonly loading = signal(true); readonly selectedLoading = signal(false); readonly recalculating = signal(false);
  readonly errorMessage = signal(''); readonly search = signal(''); readonly riskFilter = signal('');
  readonly kpis = computed<Kpi[]>(() => this.dashboardKpis(this.dashboard()));
  readonly filteredRankings = computed(() => this.rankings().filter((item) => this.matches(item.vendorName, item.vendorCategory, item.riskLevel)));
  readonly filteredRecommendations = computed(() => this.recommendations().filter((item) => this.matches(item.vendorName, item.vendorCategory, item.riskLevel)));

  ngOnInit(): void { this.loadOverview(); }
  loadOverview(): void {
    this.loading.set(true); this.errorMessage.set('');
    forkJoin({ dashboard: this.safe(this.service.getDashboard(), {}), rankings: this.safe(this.service.getRankings(), []), riskLevels: this.safe(this.service.getRiskLevels(), []), recommendations: this.safe(this.service.getRecommendations(), []) }).subscribe((data) => {
      this.dashboard.set(data.dashboard); this.rankings.set(data.rankings); this.riskLevels.set(data.riskLevels); this.recommendations.set(data.recommendations); this.loading.set(false);
    });
  }
  selectVendor(vendorId: number): void {
    this.selectedVendorId.set(vendorId); this.selectedLoading.set(true); this.errorMessage.set('');
    forkJoin({ details: this.service.getDetails(vendorId), trends: this.service.getTrends(vendorId) }).subscribe({ next: (data) => { this.selectedDetails.set(data.details); this.trends.set(data.trends); this.selectedLoading.set(false); setTimeout(() => document.querySelector('.detail-panel')?.scrollIntoView({ behavior: 'smooth', block: 'start' })); }, error: (error: unknown) => { this.errorMessage.set(this.readError(error, 'Unable to load this vendor\'s reliability details.')); this.selectedLoading.set(false); } });
  }
  recalculateSelected(): void { const vendorId = this.selectedVendorId(); if (!vendorId) return; this.recalculating.set(true); this.service.recalculate(vendorId).subscribe({ next: (details) => { this.selectedDetails.set(details); this.recalculating.set(false); this.loadOverview(); }, error: (error: unknown) => { this.errorMessage.set(this.readError(error, 'Unable to recalculate vendor reliability.')); this.recalculating.set(false); } }); }
  recalculateAll(): void { this.recalculating.set(true); this.service.recalculateAll().subscribe({ next: () => { this.recalculating.set(false); this.loadOverview(); }, error: (error: unknown) => { this.errorMessage.set(this.readError(error, 'Unable to recalculate all vendors.')); this.recalculating.set(false); } }); }
  setSearch(event: Event): void { this.search.set((event.target as HTMLInputElement).value); }
  setRisk(event: Event): void { this.riskFilter.set((event.target as HTMLSelectElement).value); }
  private safe<T>(request: import('rxjs').Observable<T>, fallback: T): import('rxjs').Observable<T> { return request.pipe(catchError(() => of(fallback))); }
  private matches(name: string, category: string, risk: string): boolean { const query = this.search().trim().toLowerCase(); return (!query || `${name} ${category}`.toLowerCase().includes(query)) && (!this.riskFilter() || risk === this.riskFilter()); }
  private dashboardKpis(data: ReliabilityDashboard): Kpi[] { const source = typeof data['summary'] === 'object' && data['summary'] !== null && !Array.isArray(data['summary']) ? data['summary'] as Record<string, unknown> : data; return Object.entries(source).filter(([, value]) => typeof value === 'number' || typeof value === 'string').map(([key, value]) => ({ label: key.replace(/([A-Z])/g, ' $1').replace(/_/g, ' ').trim(), value: value as string | number })); }
  private readError(error: unknown, fallback: string): string { const detail = typeof error === 'object' && error !== null && 'error' in error ? (error as { error?: { detail?: unknown } }).error?.detail : null; return typeof detail === 'string' ? detail : fallback; }
}
