import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { environment } from '../../../environments/environment';

type ApiRecord = Record<string, unknown>;
export type RelatedEntityType = 'vendor' | 'procurement_request' | 'purchase_order' | 'contract' | 'none';

export interface DirectMessage {
  id: number;
  senderId: number;
  receiverId: number;
  content: string;
  relatedEntityType: RelatedEntityType;
  relatedEntityId: number | null;
  isRead: boolean;
  createdAt: string | null;
  readAt: string | null;
}

export interface ConversationSummary {
  counterpartUserId: number;
  counterpartName: string | null;
  counterpartEmail: string | null;
  lastMessageContent: string;
  lastMessageAt: string | null;
  unreadCount: number;
  relatedEntityType: RelatedEntityType | null;
  relatedEntityId: number | null;
}

export interface MessageContact {
  userId: number;
  fullName: string;
  email: string;
  role: string | null;
}

export interface MessagePayload {
  receiverId: number;
  content: string;
  relatedEntityType?: RelatedEntityType;
  relatedEntityId?: number | null;
}

@Injectable({ providedIn: 'root' })
export class DirectMessageService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/messages`;

  listConversations(limit = 50, offset = 0): Observable<ConversationSummary[]> {
    return this.http.get<ApiRecord[]>(`${this.baseUrl}/conversations`, {
      params: new HttpParams().set('limit', limit).set('offset', offset)
    }).pipe(map((items) => items.map((item) => this.conversation(item))));
  }

  getConversation(otherUserId: number, context?: { relatedEntityType?: RelatedEntityType; relatedEntityId?: number | null }): Observable<DirectMessage[]> {
    let params = new HttpParams();
    if (context?.relatedEntityType && context.relatedEntityType !== 'none') params = params.set('relatedEntityType', context.relatedEntityType);
    if (context?.relatedEntityId) params = params.set('relatedEntityId', context.relatedEntityId);
    return this.http.get<ApiRecord[]>(`${this.baseUrl}/conversations/${otherUserId}`, { params }).pipe(map((items) => items.map((item) => this.message(item))));
  }

  getContextContacts(entityType: RelatedEntityType, entityId: number): Observable<MessageContact[]> {
    return this.http.get<ApiRecord[]>(`${this.baseUrl}/contacts`, {
      params: new HttpParams().set('relatedEntityType', entityType).set('relatedEntityId', entityId)
    }).pipe(map((items) => items.map((item) => ({
      userId: this.number(item, 'userId', 'user_id'),
      fullName: this.text(item, 'fullName', 'full_name'),
      email: this.text(item, 'email'),
      role: this.optionalText(item, 'role')
    }))));
  }

  send(payload: MessagePayload): Observable<DirectMessage> {
    return this.http.post<ApiRecord>(this.baseUrl, payload).pipe(map((item) => this.message(item)));
  }

  markRead(messageId: number): Observable<DirectMessage> {
    return this.http.patch<ApiRecord>(`${this.baseUrl}/${messageId}/read`, {}).pipe(map((item) => this.message(item)));
  }

  unreadCount(): Observable<number> {
    return this.http.get<ApiRecord>(`${this.baseUrl}/unread-count`).pipe(map((result) => this.number(result, 'unread')));
  }

  private message(item: ApiRecord): DirectMessage {
    return {
      id: this.number(item, 'id'),
      senderId: this.number(item, 'senderId', 'sender_id'),
      receiverId: this.number(item, 'receiverId', 'receiver_id'),
      content: this.text(item, 'content'),
      relatedEntityType: (this.optionalText(item, 'relatedEntityType', 'related_entity_type') ?? 'none') as RelatedEntityType,
      relatedEntityId: this.optionalNumber(item, 'relatedEntityId', 'related_entity_id'),
      isRead: item['isRead'] === true || item['is_read'] === true,
      createdAt: this.optionalText(item, 'createdAt', 'created_at'),
      readAt: this.optionalText(item, 'readAt', 'read_at')
    };
  }

  private conversation(item: ApiRecord): ConversationSummary {
    return {
      counterpartUserId: this.number(item, 'counterpartUserId', 'counterpart_user_id'),
      counterpartName: this.optionalText(item, 'counterpartName', 'counterpart_name'),
      counterpartEmail: this.optionalText(item, 'counterpartEmail', 'counterpart_email'),
      lastMessageContent: this.text(item, 'lastMessageContent', 'last_message_content'),
      lastMessageAt: this.optionalText(item, 'lastMessageAt', 'last_message_at'),
      unreadCount: this.number(item, 'unreadCount', 'unread_count'),
      relatedEntityType: this.optionalText(item, 'relatedEntityType', 'related_entity_type') as RelatedEntityType | null,
      relatedEntityId: this.optionalNumber(item, 'relatedEntityId', 'related_entity_id')
    };
  }

  private value(item: ApiRecord, ...keys: string[]): unknown { return keys.map((key) => item[key]).find((value) => value !== undefined && value !== null); }
  private number(item: ApiRecord, ...keys: string[]): number { const value = this.value(item, ...keys); return typeof value === 'number' ? value : Number(value) || 0; }
  private optionalNumber(item: ApiRecord, ...keys: string[]): number | null { const value = this.value(item, ...keys); return typeof value === 'number' ? value : typeof value === 'string' && value !== '' ? Number(value) || null : null; }
  private text(item: ApiRecord, ...keys: string[]): string { const value = this.value(item, ...keys); return typeof value === 'string' ? value : ''; }
  private optionalText(item: ApiRecord, ...keys: string[]): string | null { const value = this.value(item, ...keys); return typeof value === 'string' ? value : null; }
}
