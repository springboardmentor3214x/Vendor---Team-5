import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface PerformanceDashboard {
  total_vendors: number;
  average_overall_score: number;
  excellent_count: number;
  good_count: number;
  average_count: number;
  poor_count: number;
  total_completed_orders: number;
  total_delayed_deliveries: number;
  average_delivery_score: number;
  average_quality_score: number;
  average_communication_score: number;
  average_service_rating_score: number;
  completion_rate: number;
}

export interface VendorRanking {
  vendor_id: number;
  vendor_name: string | null;
  delivery_score: number;
  quality_score: number;
  communication_score: number;
  service_rating_score: number;
  overall_performance_score: number;
  rank_position: number;
}

export interface VendorPerformanceRecord {
  id: number;
  vendor_id: number;
  total_completed_orders: number;
  on_time_delivery_rate: number;
  delayed_delivery_count: number;
  average_quality_score: number;
  average_response_time: number;
  average_service_rating_score: number;
  overall_performance_score: number;
  performance_status: string | null;
  evaluation_date: string | null;
  notes: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface DeliveryPerformanceRecord {
  id: number;
  vendor_id: number;
  purchase_order_id: number;
  expected_delivery_date: string | null;
  actual_delivery_date: string | null;
  delay_days: number;
  delivery_status: string | null;
  remarks: string | null;
  created_at: string | null;
}

export interface QualityPerformanceRecord {
  id: number;
  vendor_id: number;
  purchase_order_id: number;
  inspection_date: string | null;
  material_quality: number;
  packaging_quality: number;
  quantity_accuracy: number;
  specification_compliance: number;
  product_defects: number;
  overall_quality_rating: number;
  inspector_remarks: string | null;
  created_at: string | null;
}

export interface CommunicationPerformanceRecord {
  id: number;
  vendor_id: number;
  purchase_order_id: number;
  message_sent_time: string | null;
  vendor_response_time: string | null;
  response_duration_minutes: number;
  communication_status: string | null;
  remarks: string | null;
  created_at: string | null;
}

export interface ServiceRatingRecord {
  id: number;
  vendor_id: number;
  purchase_order_id: number;
  professionalism: number;
  customer_support: number;
  documentation_quality: number;
  flexibility: number;
  communication_effectiveness: number;
  issue_resolution: number;
  overall_service_rating: number;
  comments: string | null;
  created_at: string | null;
}

export interface PerformanceActionResult {
  vendor_id: number;
  purchase_order_id: number;
  overall_score: number;
  performance_status: string | null;
  notes: string | null;
  evaluation_date: string | null;
}

export interface DeliveryPerformancePayload {
  vendorId: number;
  purchaseOrderId: number;
  expectedDeliveryDate: string;
  actualDeliveryDate: string;
  remarks?: string | null;
}

export interface QualityPerformancePayload {
  vendorId: number;
  purchaseOrderId: number;
  inspectionDate?: string | null;
  materialQuality: number;
  packagingQuality: number;
  quantityAccuracy: number;
  specificationCompliance: number;
  productDefects: number;
  inspectorRemarks?: string | null;
}

export interface CommunicationPerformancePayload {
  vendorId: number;
  purchaseOrderId: number;
  messageSentTime: string;
  vendorResponseTime: string;
  remarks?: string | null;
}

export interface ServiceRatingPayload {
  vendorId: number;
  purchaseOrderId: number;
  professionalism: number;
  customerSupport: number;
  documentationQuality: number;
  flexibility: number;
  communicationEffectiveness: number;
  issueResolution: number;
  comments?: string | null;
}

type ApiRecord = Record<string, unknown>;

@Injectable({ providedIn: 'root' })
export class PerformanceService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  getDashboard(): Observable<PerformanceDashboard> {
    return this.http.get<ApiRecord>(`${this.baseUrl}/performance/dashboard`).pipe(map((record) => this.mapDashboard(record)));
  }

  getRankings(): Observable<VendorRanking[]> {
    return this.http
      .get<ApiRecord>(`${this.baseUrl}/performance/rankings`)
      .pipe(map((record) => this.arrayValue(record, 'rankings').map((item) => this.mapRanking(item))));
  }

  getVendorPerformance(vendorId: number): Observable<VendorPerformanceRecord> {
    return this.http.get<ApiRecord>(`${this.baseUrl}/performance/${vendorId}`).pipe(map((record) => this.mapPerformanceRecord(record)));
  }

  getPerformanceHistory(vendorId: number): Observable<VendorPerformanceRecord[]> {
    return this.http.get<ApiRecord[]>(`${this.baseUrl}/performance/history/${vendorId}`).pipe(map((records) => records.map((record) => this.mapPerformanceRecord(record))));
  }

  getDeliveryPerformance(vendorId: number): Observable<DeliveryPerformanceRecord[]> {
    return this.http.get<ApiRecord[]>(`${this.baseUrl}/performance/delivery/${vendorId}`).pipe(map((records) => records.map((record) => this.mapDelivery(record))));
  }

  getQualityPerformance(vendorId: number): Observable<QualityPerformanceRecord[]> {
    return this.http.get<ApiRecord[]>(`${this.baseUrl}/performance/quality/${vendorId}`).pipe(map((records) => records.map((record) => this.mapQuality(record))));
  }

  getCommunicationPerformance(vendorId: number): Observable<CommunicationPerformanceRecord[]> {
    return this.http.get<ApiRecord[]>(`${this.baseUrl}/performance/communication/${vendorId}`).pipe(map((records) => records.map((record) => this.mapCommunication(record))));
  }

  getServiceRatings(vendorId: number): Observable<ServiceRatingRecord[]> {
    return this.http.get<ApiRecord[]>(`${this.baseUrl}/performance/service-rating/${vendorId}`).pipe(map((records) => records.map((record) => this.mapServiceRating(record))));
  }

  recordDeliveryPerformance(payload: DeliveryPerformancePayload): Observable<PerformanceActionResult> {
    return this.recordAction('delivery', payload);
  }

  recordQualityPerformance(payload: QualityPerformancePayload): Observable<PerformanceActionResult> {
    return this.recordAction('quality', payload);
  }

  recordCommunicationPerformance(payload: CommunicationPerformancePayload): Observable<PerformanceActionResult> {
    return this.recordAction('communication', payload);
  }

  recordServiceRating(payload: ServiceRatingPayload): Observable<PerformanceActionResult> {
    return this.recordAction('service-rating', payload);
  }

  private mapDashboard(record: ApiRecord): PerformanceDashboard {
    return {
      total_vendors: this.numberValue(record, 'totalVendors', 'total_vendors') ?? 0,
      average_overall_score: this.numberValue(record, 'averageOverallScore', 'average_overall_score') ?? 0,
      excellent_count: this.numberValue(record, 'excellentCount', 'excellent_count') ?? 0,
      good_count: this.numberValue(record, 'goodCount', 'good_count') ?? 0,
      average_count: this.numberValue(record, 'averageCount', 'average_count') ?? 0,
      poor_count: this.numberValue(record, 'poorCount', 'poor_count') ?? 0,
      total_completed_orders: this.numberValue(record, 'totalCompletedOrders', 'total_completed_orders') ?? 0,
      total_delayed_deliveries: this.numberValue(record, 'totalDelayedDeliveries', 'total_delayed_deliveries') ?? 0,
      average_delivery_score: this.numberValue(record, 'averageDeliveryScore', 'average_delivery_score') ?? 0,
      average_quality_score: this.numberValue(record, 'averageQualityScore', 'average_quality_score') ?? 0,
      average_communication_score: this.numberValue(record, 'averageCommunicationScore', 'average_communication_score') ?? 0,
      average_service_rating_score: this.numberValue(record, 'averageServiceRatingScore', 'average_service_rating_score') ?? 0,
      completion_rate: this.numberValue(record, 'completionRate', 'completion_rate') ?? 0
    };
  }

  private mapRanking(record: ApiRecord): VendorRanking {
    return {
      vendor_id: this.numberValue(record, 'vendorId', 'vendor_id') ?? 0,
      vendor_name: this.stringValue(record, 'vendorName', 'vendor_name'),
      delivery_score: this.numberValue(record, 'deliveryScore', 'delivery_score') ?? 0,
      quality_score: this.numberValue(record, 'qualityScore', 'quality_score') ?? 0,
      communication_score: this.numberValue(record, 'communicationScore', 'communication_score') ?? 0,
      service_rating_score: this.numberValue(record, 'serviceRatingScore', 'service_rating_score') ?? 0,
      overall_performance_score: this.numberValue(record, 'overallPerformanceScore', 'overall_performance_score') ?? 0,
      rank_position: this.numberValue(record, 'rankPosition', 'rank_position') ?? 0
    };
  }

  private mapPerformanceRecord(record: ApiRecord): VendorPerformanceRecord {
    return {
      id: this.numberValue(record, 'id') ?? 0,
      vendor_id: this.numberValue(record, 'vendorId', 'vendor_id') ?? 0,
      total_completed_orders: this.numberValue(record, 'totalCompletedOrders', 'total_completed_orders') ?? 0,
      on_time_delivery_rate: this.numberValue(record, 'onTimeDeliveryRate', 'on_time_delivery_rate') ?? 0,
      delayed_delivery_count: this.numberValue(record, 'delayedDeliveryCount', 'delayed_delivery_count') ?? 0,
      average_quality_score: this.numberValue(record, 'averageQualityScore', 'average_quality_score') ?? 0,
      average_response_time: this.numberValue(record, 'averageResponseTime', 'average_response_time') ?? 0,
      average_service_rating_score: this.numberValue(record, 'averageServiceRatingScore', 'average_service_rating_score') ?? 0,
      overall_performance_score: this.numberValue(record, 'overallPerformanceScore', 'overall_performance_score') ?? 0,
      performance_status: this.stringValue(record, 'performanceStatus', 'performance_status'),
      evaluation_date: this.stringValue(record, 'evaluationDate', 'evaluation_date'),
      notes: this.stringValue(record, 'notes'),
      created_at: this.stringValue(record, 'createdAt', 'created_at'),
      updated_at: this.stringValue(record, 'updatedAt', 'updated_at')
    };
  }

  private mapDelivery(record: ApiRecord): DeliveryPerformanceRecord {
    return {
      id: this.numberValue(record, 'id') ?? 0, vendor_id: this.numberValue(record, 'vendorId', 'vendor_id') ?? 0, purchase_order_id: this.numberValue(record, 'purchaseOrderId', 'purchase_order_id') ?? 0,
      expected_delivery_date: this.stringValue(record, 'expectedDeliveryDate', 'expected_delivery_date'), actual_delivery_date: this.stringValue(record, 'actualDeliveryDate', 'actual_delivery_date'), delay_days: this.numberValue(record, 'delayDays', 'delay_days') ?? 0,
      delivery_status: this.stringValue(record, 'deliveryStatus', 'delivery_status'), remarks: this.stringValue(record, 'remarks'), created_at: this.stringValue(record, 'createdAt', 'created_at')
    };
  }

  private mapQuality(record: ApiRecord): QualityPerformanceRecord {
    return {
      id: this.numberValue(record, 'id') ?? 0, vendor_id: this.numberValue(record, 'vendorId', 'vendor_id') ?? 0, purchase_order_id: this.numberValue(record, 'purchaseOrderId', 'purchase_order_id') ?? 0,
      inspection_date: this.stringValue(record, 'inspectionDate', 'inspection_date'), material_quality: this.numberValue(record, 'materialQuality', 'material_quality') ?? 0, packaging_quality: this.numberValue(record, 'packagingQuality', 'packaging_quality') ?? 0,
      quantity_accuracy: this.numberValue(record, 'quantityAccuracy', 'quantity_accuracy') ?? 0, specification_compliance: this.numberValue(record, 'specificationCompliance', 'specification_compliance') ?? 0,
      product_defects: this.numberValue(record, 'productDefects', 'product_defects') ?? 0, overall_quality_rating: this.numberValue(record, 'overallQualityRating', 'overall_quality_rating') ?? 0,
      inspector_remarks: this.stringValue(record, 'inspectorRemarks', 'inspector_remarks'), created_at: this.stringValue(record, 'createdAt', 'created_at')
    };
  }

  private mapCommunication(record: ApiRecord): CommunicationPerformanceRecord {
    return {
      id: this.numberValue(record, 'id') ?? 0, vendor_id: this.numberValue(record, 'vendorId', 'vendor_id') ?? 0, purchase_order_id: this.numberValue(record, 'purchaseOrderId', 'purchase_order_id') ?? 0,
      message_sent_time: this.stringValue(record, 'messageSentTime', 'message_sent_time'), vendor_response_time: this.stringValue(record, 'vendorResponseTime', 'vendor_response_time'),
      response_duration_minutes: this.numberValue(record, 'responseDurationMinutes', 'response_duration_minutes') ?? 0, communication_status: this.stringValue(record, 'communicationStatus', 'communication_status'),
      remarks: this.stringValue(record, 'remarks'), created_at: this.stringValue(record, 'createdAt', 'created_at')
    };
  }

  private mapServiceRating(record: ApiRecord): ServiceRatingRecord {
    return {
      id: this.numberValue(record, 'id') ?? 0, vendor_id: this.numberValue(record, 'vendorId', 'vendor_id') ?? 0, purchase_order_id: this.numberValue(record, 'purchaseOrderId', 'purchase_order_id') ?? 0,
      professionalism: this.numberValue(record, 'professionalism') ?? 0, customer_support: this.numberValue(record, 'customerSupport', 'customer_support') ?? 0,
      documentation_quality: this.numberValue(record, 'documentationQuality', 'documentation_quality') ?? 0, flexibility: this.numberValue(record, 'flexibility') ?? 0,
      communication_effectiveness: this.numberValue(record, 'communicationEffectiveness', 'communication_effectiveness') ?? 0, issue_resolution: this.numberValue(record, 'issueResolution', 'issue_resolution') ?? 0,
      overall_service_rating: this.numberValue(record, 'overallServiceRating', 'overall_service_rating') ?? 0, comments: this.stringValue(record, 'comments'), created_at: this.stringValue(record, 'createdAt', 'created_at')
    };
  }

  private recordAction(action: 'delivery' | 'quality' | 'communication' | 'service-rating', payload: object): Observable<PerformanceActionResult> {
    return this.http.post<ApiRecord>(`${this.baseUrl}/performance/${action}`, payload).pipe(map((record) => this.mapActionResult(record)));
  }

  private mapActionResult(record: ApiRecord): PerformanceActionResult {
    return {
      vendor_id: this.numberValue(record, 'vendorId', 'vendor_id') ?? 0,
      purchase_order_id: this.numberValue(record, 'purchaseOrderId', 'purchase_order_id') ?? 0,
      overall_score: this.numberValue(record, 'overallScore', 'overall_score') ?? 0,
      performance_status: this.stringValue(record, 'performanceStatus', 'performance_status'),
      notes: this.stringValue(record, 'notes'),
      evaluation_date: this.stringValue(record, 'evaluationDate', 'evaluation_date')
    };
  }

  private numberValue(record: ApiRecord, ...keys: string[]): number | null {
    const value = this.value(record, keys);
    return typeof value === 'number' ? value : null;
  }

  private stringValue(record: ApiRecord, ...keys: string[]): string | null {
    const value = this.value(record, keys);
    return typeof value === 'string' ? value : null;
  }

  private arrayValue(record: ApiRecord, key: string): ApiRecord[] {
    const value = record[key];
    return Array.isArray(value) ? value.filter((item): item is ApiRecord => typeof item === 'object' && item !== null) : [];
  }

  private value(record: ApiRecord, keys: string[]): unknown {
    for (const key of keys) {
      if (record[key] !== undefined && record[key] !== null) return record[key];
    }
    return null;
  }
}
