import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { environment } from '../../../environments/environment';

type ApiRecord = Record<string, unknown>;
export interface Contract { id: number; vendorId: number; contractTitle: string; contractType: string | null; startDate: string; endDate: string | null; contractValue: number; status: string; complianceVerified: boolean; createdAt: string | null; updatedAt: string | null; }
export interface ContractPayload { vendorId: number; contractTitle: string; contractType?: string | null; startDate: string; endDate?: string | null; contractValue?: number; status?: string; complianceVerified?: boolean; }
export interface ContractUpdatePayload { contractTitle?: string; endDate?: string | null; contractValue?: number; status?: string; }
export interface RenewalPayload { newEndDate: string; renewalValue?: number; remarks?: string; }

@Injectable({ providedIn: 'root' })
export class ContractService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/contracts`;
  list(): Observable<Contract[]> { return this.http.get<ApiRecord[]>(`${this.baseUrl}/`).pipe(map((items) => items.map((item) => this.contract(item)))); }
  get(id: number): Observable<Contract> { return this.http.get<ApiRecord>(`${this.baseUrl}/${id}`).pipe(map((item) => this.contract(item))); }
  create(payload: ContractPayload): Observable<Contract> { return this.http.post<ApiRecord>(`${this.baseUrl}/`, payload).pipe(map((item) => this.contract(item))); }
  updateContract(id: number, payload: ContractUpdatePayload): Observable<Contract> { return this.http.patch<ApiRecord>(`${this.baseUrl}/${id}`, payload).pipe(map((item) => this.contract(item))); }
  deleteContract(id: number): Observable<void> { return this.http.delete<void>(`${this.baseUrl}/${id}`); }
  renewContract(id: number, payload: RenewalPayload): Observable<Contract> { return this.http.post<ApiRecord>(`${this.baseUrl}/${id}/renew`, payload).pipe(map((item) => this.contract(item))); }
  updateContractStatus(id: number, status: string): Observable<Contract> { return this.http.patch<ApiRecord>(`${this.baseUrl}/${id}/status`, null, { params: new HttpParams().set('status_str', status) }).pipe(map((item) => this.contract(item))); }
  expiring(): Observable<Contract[]> { return this.http.get<ApiRecord[]>(`${this.baseUrl}/expiring`).pipe(map((items) => items.map((item) => this.contract(item)))); }
  private contract(item: ApiRecord): Contract { return { id: this.number(item, 'id'), vendorId: this.number(item, 'vendorId', 'vendor_id'), contractTitle: this.text(item, 'contractTitle', 'contract_title'), contractType: this.optionalText(item, 'contractType', 'contract_type'), startDate: this.text(item, 'startDate', 'start_date'), endDate: this.optionalText(item, 'endDate', 'end_date'), contractValue: this.number(item, 'contractValue', 'contract_value'), status: this.text(item, 'status'), complianceVerified: this.boolean(item, 'complianceVerified', 'compliance_verified'), createdAt: this.optionalText(item, 'createdAt', 'created_at'), updatedAt: this.optionalText(item, 'updatedAt', 'updated_at') }; }
  private value(item: ApiRecord, ...keys: string[]): unknown { return keys.map((key) => item[key]).find((value) => value !== undefined && value !== null); }
  private number(item: ApiRecord, ...keys: string[]): number { const value = this.value(item, ...keys); return typeof value === 'number' ? value : Number(value) || 0; }
  private text(item: ApiRecord, ...keys: string[]): string { const value = this.value(item, ...keys); return typeof value === 'string' ? value : 'Not available'; }
  private optionalText(item: ApiRecord, ...keys: string[]): string | null { const value = this.value(item, ...keys); return typeof value === 'string' ? value : null; }
  private boolean(item: ApiRecord, ...keys: string[]): boolean { const value = this.value(item, ...keys); return value === true || value === 'true'; }
}
