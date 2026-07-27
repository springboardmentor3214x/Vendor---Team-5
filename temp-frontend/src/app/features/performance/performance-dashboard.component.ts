import { CommonModule } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { forkJoin } from 'rxjs';
import { PerformanceDashboard, PerformanceService, VendorRanking } from '../../core/services/performance.service';

@Component({
  selector: 'app-performance-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './performance-dashboard.component.html',
  styleUrl: './performance-dashboard.component.css'
})
export class PerformanceDashboardComponent {
  private readonly performanceService = inject(PerformanceService);
  readonly dashboard = signal<PerformanceDashboard | null>(null);
  readonly rankings = signal<VendorRanking[]>([]);
  readonly loading = signal(true);
  readonly errorMessage = signal('');
  readonly scoreDistribution = computed(() => {
    const dashboard = this.dashboard();
    if (!dashboard) return [];
    return [
      { label: 'Excellent', value: dashboard.excellent_count, tone: 'excellent' },
      { label: 'Good', value: dashboard.good_count, tone: 'good' },
      { label: 'Average', value: dashboard.average_count, tone: 'average' },
      { label: 'Poor', value: dashboard.poor_count, tone: 'poor' }
    ];
  });
  readonly averageMetrics = computed(() => {
    const dashboard = this.dashboard();
    if (!dashboard) return [];
    return [
      { label: 'Delivery', value: dashboard.average_delivery_score },
      { label: 'Quality', value: dashboard.average_quality_score },
      { label: 'Communication', value: dashboard.average_communication_score },
      { label: 'Service rating', value: dashboard.average_service_rating_score }
    ];
  });
  readonly distributionTotal = computed(() => this.scoreDistribution().reduce((total, item) => total + item.value, 0));

  ngOnInit(): void { this.loadDashboard(); }

  loadDashboard(): void {
    this.loading.set(true);
    this.errorMessage.set('');
    forkJoin({ dashboard: this.performanceService.getDashboard(), rankings: this.performanceService.getRankings() }).subscribe({
      next: ({ dashboard, rankings }) => { this.dashboard.set(dashboard); this.rankings.set(rankings); this.loading.set(false); },
      error: (error: unknown) => { this.errorMessage.set(this.readError(error)); this.loading.set(false); }
    });
  }

  scoreClass(score: number): string {
    if (score >= 80) return 'score-excellent';
    if (score >= 60) return 'score-good';
    if (score >= 40) return 'score-average';
    return 'score-poor';
  }

  distributionWidth(value: number): number {
    const total = this.distributionTotal();
    return total ? Math.round((value / total) * 100) : 0;
  }

  scoreWidth(value: number): number {
    return Math.max(0, Math.min(100, value));
  }

  private readError(error: unknown): string {
    const detail = typeof error === 'object' && error !== null && 'error' in error
      ? (error as { error?: { detail?: unknown } }).error?.detail
      : null;
    return typeof detail === 'string' ? detail : 'Unable to load vendor performance data. Please try again.';
  }
}
