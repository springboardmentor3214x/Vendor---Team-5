import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { environment } from '../../../environments/environment';

export type ReportKey = 'vendor-performance' | 'procurement' | 'purchase-orders' | 'contracts' | 'compliance' | 'executive-summary' | 'vendor-documents';
export type ReportFormat = 'csv' | 'pdf' | 'excel';

export interface ReportDefinition {
  key: string;
  title: string;
  formats?: string[];
  status: string;
}

export interface ReportCatalog {
  items: ReportDefinition[];
  generatedAt: string | null;
}

export interface ReportTable {
  headers: string[];
  rows: string[][];
}

export interface ReportPreview { reportType: string; rows: Record<string, unknown>[]; totalRows: number; }
export interface ReportFilters { startDate?: string; endDate?: string; department?: string; vendorId?: number; categoryId?: number; status?: string; reliabilityLevel?: string; sortBy?: string; sortOrder?: 'asc' | 'desc'; }
export interface ReportChartData { chartType: string; labels: string[]; datasets: { label: string; data: number[] }[]; reason: string | null; }

interface ReportCatalogApi {
  items?: ReportDefinition[];
  generated_at?: string;
  generatedAt?: string;
}

@Injectable({ providedIn: 'root' })
export class ReportService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/reports`;

  listReports(): Observable<ReportCatalog> {
    return this.http.get<ReportCatalogApi>(`${this.baseUrl}/`).pipe(
      map((response) => ({
        items: Array.isArray(response.items) ? response.items : [],
        generatedAt: response.generatedAt ?? response.generated_at ?? null
      }))
    );
  }

  preview(report: ReportKey, filters: ReportFilters = {}): Observable<ReportPreview> {
    return this.http.get<Record<string, unknown>>(`${this.baseUrl}/${report}/preview`, { params: this.params(filters) }).pipe(map((response) => ({
      reportType: this.text(response, 'reportType', 'report_type'), rows: Array.isArray(response['rows']) ? response['rows'] as Record<string, unknown>[] : [], totalRows: this.number(response, 'totalRows', 'total_rows')
    })));
  }

  chart(report: ReportKey, filters: ReportFilters = {}): Observable<ReportChartData> {
    return this.http.get<Record<string, unknown>>(`${this.baseUrl}/${report}/charts`, { params: this.params(filters) }).pipe(map((response) => {
      const raw = this.value(response, 'chartData', 'chart_data');
      const chart = raw && typeof raw === 'object' ? raw as Record<string, unknown> : {};
      const datasets = Array.isArray(chart['datasets']) ? chart['datasets'] as Record<string, unknown>[] : [];
      return {
        chartType: this.text(chart, 'chartType', 'chart_type') || 'none',
        labels: Array.isArray(chart['labels']) ? chart['labels'].map((label) => String(label)) : [],
        datasets: datasets.map((dataset) => ({ label: this.text(dataset, 'label'), data: Array.isArray(dataset['data']) ? dataset['data'].map((value) => Number(value) || 0) : [] })),
        reason: this.optionalText(response, 'reason')
      };
    }));
  }

  exportReport(report: ReportKey, format: ReportFormat, filters: ReportFilters = {}): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/${report}/export`, { params: this.params({ ...filters, format }), responseType: 'blob' });
  }

  private params(filters: object): HttpParams {
    let params = new HttpParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') params = params.set(key, String(value));
    });
    return params;
  }
  private value(item: Record<string, unknown>, ...keys: string[]): unknown { return keys.map((key) => item[key]).find((value) => value !== undefined && value !== null); }
  private number(item: Record<string, unknown>, ...keys: string[]): number { const value=this.value(item,...keys); return typeof value==='number'?value:Number(value)||0; }
  private text(item: Record<string, unknown>, ...keys: string[]): string { const value=this.value(item,...keys); return typeof value==='string'?value:''; }
  private optionalText(item: Record<string, unknown>, ...keys: string[]): string | null { const value=this.value(item,...keys); return typeof value==='string'?value:null; }

  private parseCsv(csv: string): ReportTable {
    const parsedRows: string[][] = [];
    let row: string[] = [];
    let cell = '';
    let quoted = false;

    for (let index = 0; index < csv.length; index += 1) {
      const character = csv[index];
      if (character === '"') {
        if (quoted && csv[index + 1] === '"') {
          cell += '"';
          index += 1;
        } else {
          quoted = !quoted;
        }
      } else if (character === ',' && !quoted) {
        row.push(cell);
        cell = '';
      } else if ((character === '\n' || character === '\r') && !quoted) {
        if (character === '\r' && csv[index + 1] === '\n') index += 1;
        row.push(cell);
        if (row.some((value) => value.length > 0)) parsedRows.push(row);
        row = [];
        cell = '';
      } else {
        cell += character;
      }
    }

    row.push(cell);
    if (row.some((value) => value.length > 0)) parsedRows.push(row);
    const [headers = [], ...rows] = parsedRows;
    return { headers, rows };
  }
}
