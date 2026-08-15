import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { environment } from '../../../environments/environment';

type ApiRecord = Record<string, unknown>;

export interface ReliabilityDashboard { [key: string]: unknown; }
export interface ReliabilityDetails {
  id: number; vendorId: number; deliveryScore: number; qualityScore: number;
  communicationScore: number; complianceScore: number; issueResolutionScore: number;
  reliabilityScore: number; riskLevel: string; recommendation: string; updatedAt: string | null;
}
export interface ReliabilityRanking {
  vendorId: number; vendorName: string; vendorCategory: string; reliabilityScore: number;
  riskLevel: string; rankPosition: number;
}
export interface ReliabilityRiskLevel {
  vendorId: number; vendorName: string; vendorCategory: string; reliabilityScore: number;
  riskLevel: string;
}
export interface ReliabilityTrend {
  id: number; vendorId: number; year: number; month: number; reliabilityScore: number;
  deliveryScore: number; qualityScore: number; communicationScore: number; complianceScore: number;
  issueResolutionScore: number; createdAt: string | null;
}
export interface ReliabilityRecommendation {
  id: number; vendorId: number; vendorName: string; vendorCategory: string;
  reliabilityScore: number; riskLevel: string; recommendationStatus: string; reason: string;
  updatedAt: string | null;
}

@Injectable({ providedIn: 'root' })
export class ReliabilityService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/reliability`;

  getDashboard(): Observable<ReliabilityDashboard> { return this.http.get<ApiRecord>(`${this.baseUrl}/dashboard`); }
  getDetails(vendorId: number): Observable<ReliabilityDetails> { return this.http.get<ApiRecord>(`${this.baseUrl}/details/${vendorId}`).pipe(map((item) => this.details(item))); }
  recalculate(vendorId: number): Observable<ReliabilityDetails> { return this.http.post<ApiRecord>(`${this.baseUrl}/recalculate/${vendorId}`, {}).pipe(map((item) => this.details(item))); }
  recalculateAll(): Observable<unknown> { return this.http.post(`${this.baseUrl}/recalculate-all`, {}); }
  getRankings(): Observable<ReliabilityRanking[]> { return this.http.get<ApiRecord[]>(`${this.baseUrl}/rankings`).pipe(map((items) => items.map((item) => this.ranking(item)))); }
  getRiskLevels(): Observable<ReliabilityRiskLevel[]> { return this.http.get<ApiRecord[]>(`${this.baseUrl}/risk-levels`).pipe(map((items) => items.map((item) => this.riskLevel(item)))); }
  getTrends(vendorId: number): Observable<ReliabilityTrend[]> { return this.http.get<ApiRecord[]>(`${this.baseUrl}/trends/${vendorId}`).pipe(map((items) => items.map((item) => this.trend(item)))); }
  getRecommendations(): Observable<ReliabilityRecommendation[]> { return this.http.get<ApiRecord[]>(`${this.baseUrl}/recommendations`).pipe(map((items) => items.map((item) => this.recommendation(item)))); }

  private details(item: ApiRecord): ReliabilityDetails { return { id: this.number(item, 'id'), vendorId: this.number(item, 'vendorId', 'vendor_id'), deliveryScore: this.number(item, 'deliveryScore', 'delivery_score'), qualityScore: this.number(item, 'qualityScore', 'quality_score'), communicationScore: this.number(item, 'communicationScore', 'communication_score'), complianceScore: this.number(item, 'complianceScore', 'compliance_score'), issueResolutionScore: this.number(item, 'issueResolutionScore', 'issue_resolution_score'), reliabilityScore: this.number(item, 'reliabilityScore', 'reliability_score'), riskLevel: this.text(item, 'riskLevel', 'risk_level'), recommendation: this.text(item, 'recommendation'), updatedAt: this.optionalText(item, 'updatedAt', 'updated_at') }; }
  private ranking(item: ApiRecord): ReliabilityRanking { return { vendorId: this.number(item, 'vendorId', 'vendor_id'), vendorName: this.text(item, 'vendorName', 'vendor_name'), vendorCategory: this.text(item, 'vendorCategory', 'vendor_category'), reliabilityScore: this.number(item, 'reliabilityScore', 'reliability_score'), riskLevel: this.text(item, 'riskLevel', 'risk_level'), rankPosition: this.number(item, 'rankPosition', 'rank_position') }; }
  private riskLevel(item: ApiRecord): ReliabilityRiskLevel { const ranking = this.ranking(item); return { vendorId: ranking.vendorId, vendorName: ranking.vendorName, vendorCategory: ranking.vendorCategory, reliabilityScore: ranking.reliabilityScore, riskLevel: ranking.riskLevel }; }
  private trend(item: ApiRecord): ReliabilityTrend { return { id: this.number(item, 'id'), vendorId: this.number(item, 'vendorId', 'vendor_id'), year: this.number(item, 'year'), month: this.number(item, 'month'), reliabilityScore: this.number(item, 'reliabilityScore', 'reliability_score'), deliveryScore: this.number(item, 'deliveryScore', 'delivery_score'), qualityScore: this.number(item, 'qualityScore', 'quality_score'), communicationScore: this.number(item, 'communicationScore', 'communication_score'), complianceScore: this.number(item, 'complianceScore', 'compliance_score'), issueResolutionScore: this.number(item, 'issueResolutionScore', 'issue_resolution_score'), createdAt: this.optionalText(item, 'createdAt', 'created_at') }; }
  private recommendation(item: ApiRecord): ReliabilityRecommendation { return { id: this.number(item, 'id'), vendorId: this.number(item, 'vendorId', 'vendor_id'), vendorName: this.text(item, 'vendorName', 'vendor_name'), vendorCategory: this.text(item, 'vendorCategory', 'vendor_category'), reliabilityScore: this.number(item, 'reliabilityScore', 'reliability_score'), riskLevel: this.text(item, 'riskLevel', 'risk_level'), recommendationStatus: this.text(item, 'recommendationStatus', 'recommendation_status'), reason: this.text(item, 'reason'), updatedAt: this.optionalText(item, 'updatedAt', 'updated_at') }; }
  private number(item: ApiRecord, ...keys: string[]): number { const value = this.value(item, keys); return typeof value === 'number' ? value : 0; }
  private text(item: ApiRecord, ...keys: string[]): string { return this.optionalText(item, ...keys) ?? 'Not available'; }
  private optionalText(item: ApiRecord, ...keys: string[]): string | null { const value = this.value(item, keys); return typeof value === 'string' ? value : null; }
  private value(item: ApiRecord, keys: string[]): unknown { for (const key of keys) if (item[key] !== undefined && item[key] !== null) return item[key]; return null; }
}
