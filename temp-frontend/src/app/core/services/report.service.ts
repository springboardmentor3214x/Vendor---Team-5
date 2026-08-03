import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { environment } from '../../../environments/environment';

export type ReportKey = 'vendor-performance' | 'procurement' | 'contracts' | 'compliance' | 'vendor-documents';

export interface ReportDefinition {
  key: string;
  title: string;
  format: string;
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

  loadTable(report: ReportKey): Observable<ReportTable> {
    return this.http
      .get(`${this.baseUrl}/${report}`, { responseType: 'text' })
      .pipe(map((csv) => this.parseCsv(csv)));
  }

  exportReport(report: ReportKey): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/${report}`, { responseType: 'blob' });
  }

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
