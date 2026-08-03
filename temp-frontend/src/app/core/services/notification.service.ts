import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { environment } from '../../../environments/environment';

type ApiRecord = Record<string, unknown>;
export interface Notification { id: number; title: string; message: string; type: string; isRead: boolean; createdAt: string | null; }
export interface NotificationList { items: Notification[]; total: number; unreadCount: number; }
@Injectable({ providedIn: 'root' })
export class NotificationService {
  private readonly http = inject(HttpClient); private readonly baseUrl = `${environment.apiUrl}/notifications`;
  list(): Observable<NotificationList> { return this.http.get<ApiRecord>(`${this.baseUrl}/`).pipe(map((response) => { const raw = Array.isArray(response['items']) ? response['items'] as ApiRecord[] : []; return { items: raw.map((item) => this.item(item)), total: this.number(response, 'total'), unreadCount: this.number(response, 'unreadCount', 'unread_count') }; })); }
  markRead(id: number): Observable<Notification> { return this.http.patch<ApiRecord>(`${this.baseUrl}/${id}/read`, {}).pipe(map((response) => this.item((response['notification'] as ApiRecord) ?? response))); }
  private item(item: ApiRecord): Notification { return { id: this.number(item, 'id'), title: this.text(item, 'title'), message: this.text(item, 'message'), type: this.text(item, 'type'), isRead: item['isRead'] === true || item['is_read'] === true, createdAt: this.optionalText(item, 'createdAt', 'created_at') }; }
  private number(item: ApiRecord, ...keys: string[]): number { const value = keys.map((key) => item[key]).find((entry) => entry !== undefined && entry !== null); return typeof value === 'number' ? value : Number(value) || 0; }
  private text(item: ApiRecord, ...keys: string[]): string { const value = keys.map((key) => item[key]).find((entry) => entry !== undefined && entry !== null); return typeof value === 'string' ? value : 'Not available'; }
  private optionalText(item: ApiRecord, ...keys: string[]): string | null { const value = keys.map((key) => item[key]).find((entry) => entry !== undefined && entry !== null); return typeof value === 'string' ? value : null; }
}
