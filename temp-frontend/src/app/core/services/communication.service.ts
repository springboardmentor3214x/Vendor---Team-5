import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface Message { id:number; subject?:string; message:string; vendorId?:number; discussionId?:number; isRead:boolean; createdAt:string; }
export interface Discussion { id:number; title:string; vendorId?:number; status:string; createdAt:string; participantCount?:number; messages?:Message[]; }
export interface ActivityLog { id:number; module:string; action:string; description?:string; createdAt:string; }
@Injectable({providedIn:'root'}) export class CommunicationService {
  private http=inject(HttpClient); private base=`${environment.apiUrl}/communications`;
  messages(vendorId?:number):Observable<Message[]>{let p=new HttpParams();if(vendorId)p=p.set('vendorId',vendorId);return this.http.get<Message[]>(`${this.base}/`,{params:p})}
  send(body:Record<string,unknown>){return this.http.post<Message>(`${this.base}/`,body)}
  discussions(){return this.http.get<Discussion[]>(`${this.base}/discussions`)}
  createDiscussion(body:Record<string,unknown>){return this.http.post<Discussion>(`${this.base}/discussions`,body)}
  logs(){return this.http.get<ActivityLog[]>(`${this.base}/activity-logs`)}
  markRead(id:number){return this.http.post<Message>(`${this.base}/${id}/read`,{})}
  upload(file:File,vendorId:number){const body=new FormData();body.append('file',file);body.append('vendorId',String(vendorId));return this.http.post<{id:number;filename:string}>(`${this.base}/files/upload`,body)}
  files(vendorId?:number){let p=new HttpParams();if(vendorId)p=p.set('vendorId',vendorId);return this.http.get<{id:number;filename:string;createdAt:string}[]>(`${this.base}/files`,{params:p})}
  unreadNotifications(){return this.http.get<{unreadCount:number}>(`${environment.apiUrl}/notifications/unread-count`)}
}
