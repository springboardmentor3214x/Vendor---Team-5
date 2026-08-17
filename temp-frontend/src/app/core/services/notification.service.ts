import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { environment } from '../../../environments/environment';

type ApiRecord = Record<string, unknown>;
export interface Notification {
  id: number; title: string; message: string; type: string; notificationType: string;
  relatedModule: string | null; relatedRecordId: number | null; priority: string;
  link: string | null; isRead: boolean; createdAt: string | null; readAt: string | null;
}
export interface NotificationList { items: Notification[]; total: number; unreadCount: number; }
export interface NotificationFilters { module?: string; priority?: string; isRead?: boolean; }
@Injectable({ providedIn: 'root' })
export class NotificationService {
  private readonly http = inject(HttpClient); private readonly baseUrl = `${environment.apiUrl}/notifications`;
  list(filters: NotificationFilters = {}): Observable<NotificationList> {
    const params: Record<string, string> = {};
    if (filters.module) params['module'] = filters.module;
    if (filters.priority) params['priority'] = filters.priority;
    if (filters.isRead !== undefined) params['isRead'] = String(filters.isRead);
    return this.http.get<ApiRecord>(`${this.baseUrl}/`, { params }).pipe(map((response) => { const raw = Array.isArray(response['items']) ? response['items'] as ApiRecord[] : []; return { items: raw.map((item) => this.item(item)), total: this.number(response, 'total'), unreadCount: this.number(response, 'unreadCount', 'unread_count') }; }));
  }
  markRead(id: number): Observable<Notification> { return this.http.patch<ApiRecord>(`${this.baseUrl}/${id}/read`, {}).pipe(map((response) => this.item((response['notification'] as ApiRecord) ?? response))); }
  markAllRead(): Observable<number> { return this.http.post<ApiRecord>(`${this.baseUrl}/read-all`, {}).pipe(map((response) => this.number(response, 'markedCount', 'marked_count'))); }
  unreadCount(): Observable<number> { return this.http.get<ApiRecord>(`${this.baseUrl}/unread-count`).pipe(map((response) => this.number(response, 'unreadCount', 'unread_count'))); }
  private item(item: ApiRecord): Notification { return { id: this.number(item, 'id'), title: this.text(item, 'title'), message: this.text(item, 'message'), type: this.text(item, 'type'), notificationType: this.text(item, 'notificationType', 'notification_type', 'type'), relatedModule: this.optionalText(item, 'relatedModule', 'related_module'), relatedRecordId: this.optionalNumber(item, 'relatedRecordId', 'related_record_id'), priority: this.text(item, 'priority'), link: this.optionalText(item, 'link'), isRead: item['isRead'] === true || item['is_read'] === true, createdAt: this.optionalText(item, 'createdAt', 'created_at'), readAt: this.optionalText(item, 'readAt', 'read_at') }; }
  private number(item: ApiRecord, ...keys: string[]): number { const value = keys.map((key) => item[key]).find((entry) => entry !== undefined && entry !== null); return typeof value === 'number' ? value : Number(value) || 0; }
  private text(item: ApiRecord, ...keys: string[]): string { const value = keys.map((key) => item[key]).find((entry) => entry !== undefined && entry !== null); return typeof value === 'string' ? value : 'Not available'; }
  private optionalText(item: ApiRecord, ...keys: string[]): string | null { const value = keys.map((key) => item[key]).find((entry) => entry !== undefined && entry !== null); return typeof value === 'string' ? value : null; }
  private optionalNumber(item: ApiRecord, ...keys: string[]): number | null { const value = keys.map((key) => item[key]).find((entry) => entry !== undefined && entry !== null); return typeof value === 'number' ? value : typeof value === 'string' && value !== '' ? Number(value) || null : null; }
}
