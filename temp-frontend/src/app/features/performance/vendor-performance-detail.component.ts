import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { catchError, forkJoin, of, throwError } from 'rxjs';
import {
  CommunicationPerformanceRecord,
  DeliveryPerformanceRecord,
  PerformanceService,
  QualityPerformanceRecord,
  ServiceRatingRecord,
  VendorPerformanceRecord
} from '../../core/services/performance.service';
import { IssuePanelComponent } from '../../shared/issue-panel.component';

@Component({ selector: 'app-vendor-performance-detail', standalone: true, imports: [CommonModule, RouterLink, IssuePanelComponent], templateUrl: './vendor-performance-detail.component.html', styleUrl: './vendor-performance-detail.component.css' })
export class VendorPerformanceDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly performanceService = inject(PerformanceService);
  private readonly authService = inject(AuthService);
  readonly vendorId = signal<number | null>(null);
  readonly currentRecord = signal<VendorPerformanceRecord | null>(null);
  readonly history = signal<VendorPerformanceRecord[]>([]);
  readonly deliveryRecords = signal<DeliveryPerformanceRecord[]>([]);
  readonly qualityRecords = signal<QualityPerformanceRecord[]>([]);
  readonly communicationRecords = signal<CommunicationPerformanceRecord[]>([]);
  readonly serviceRatings = signal<ServiceRatingRecord[]>([]);
  readonly loading = signal(true);
  readonly errorMessage = signal('');
  readonly successMessage = signal('');

  ngOnInit(): void {
    const success = history.state?.successMessage;
    if (typeof success === 'string') this.successMessage.set(success);
    const vendorId = Number(this.route.snapshot.paramMap.get('id'));
    if (!Number.isInteger(vendorId) || vendorId <= 0) { this.errorMessage.set('Invalid vendor id.'); this.loading.set(false); return; }
    this.vendorId.set(vendorId);
    this.loadDetails(vendorId);
  }

  scoreClass(score: number): string { return score >= 80 ? 'score-excellent' : score >= 60 ? 'score-good' : score >= 40 ? 'score-average' : 'score-poor'; }
  get canRecordPerformance(): boolean { return this.authService.hasRole('Administrator', 'Procurement Manager'); }

  get canViewVendorProfile(): boolean {
    return this.authService.hasRole('Administrator', 'Procurement Manager', 'Supply Chain Manager');
  }

  loadDetails(vendorId = this.vendorId()): void {
    if (!vendorId) return;
    this.loading.set(true); this.errorMessage.set('');
    forkJoin({
      current: this.performanceService.getVendorPerformance(vendorId).pipe(catchError((error: unknown) => this.notFoundAsEmpty(error))),
      history: this.performanceService.getPerformanceHistory(vendorId),
      delivery: this.performanceService.getDeliveryPerformance(vendorId),
      quality: this.performanceService.getQualityPerformance(vendorId),
      communication: this.performanceService.getCommunicationPerformance(vendorId),
      service: this.performanceService.getServiceRatings(vendorId)
    }).subscribe({
      next: ({ current, history, delivery, quality, communication, service }) => {
        this.currentRecord.set(current); this.history.set(history); this.deliveryRecords.set(delivery); this.qualityRecords.set(quality); this.communicationRecords.set(communication); this.serviceRatings.set(service); this.loading.set(false);
      },
      error: (error: unknown) => { this.errorMessage.set(this.readError(error)); this.loading.set(false); }
    });
  }

  private notFoundAsEmpty(error: unknown) {
    return error instanceof HttpErrorResponse && error.status === 404 ? of(null) : throwError(() => error);
  }

  private readError(error: unknown): string {
    const detail = typeof error === 'object' && error !== null && 'error' in error ? (error as { error?: { detail?: unknown } }).error?.detail : null;
    return typeof detail === 'string' ? detail : 'Unable to load vendor performance details. Please try again.';
  }
}
