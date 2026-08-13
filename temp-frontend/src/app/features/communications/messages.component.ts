import { CommonModule, DatePipe } from '@angular/common';
import { Component, OnDestroy, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import {
  ConversationSummary,
  DirectMessage,
  DirectMessageService,
  RelatedEntityType
} from '../../core/services/direct-message.service';

interface MessageContext { relatedEntityType?: RelatedEntityType; relatedEntityId?: number | null; }

@Component({
  selector: 'app-messages', standalone: true, imports: [CommonModule, FormsModule, DatePipe, RouterLink],
  template: `
    <section class="messages-page">
      <header class="page-header">
        <div><p class="eyebrow">Module 7 · Communication</p><h2>Messages</h2><p>Secure one-to-one conversations linked to accessible operational records.</p></div>
        <a class="btn btn-outline-primary" routerLink="/communications">Open communication hub</a>
      </header>
      <div class="message error-message" *ngIf="errorMessage()" role="alert">{{ errorMessage() }}</div>
      <div class="workspace">
        <aside class="conversation-list" aria-label="Conversations">
          <div class="list-heading"><h3>Conversations</h3><button class="icon-button" type="button" (click)="loadConversations()" [disabled]="loadingConversations()" aria-label="Refresh conversations">↻</button></div>
          <p class="empty-state compact" *ngIf="!loadingConversations() && !conversations().length">No direct messages yet. Open a supported vendor, purchase order, or contract to start one.</p>
          <button class="conversation" *ngFor="let item of conversations()" type="button" [class.selected]="item.counterpartUserId === selectedUserId()" (click)="openConversation(item.counterpartUserId)">
            <span class="avatar">{{ (item.counterpartName || item.counterpartEmail || '?').slice(0, 1) }}</span>
            <span class="conversation-copy"><strong>{{ item.counterpartName || item.counterpartEmail }}</strong><small>{{ item.lastMessageContent }}</small><time>{{ item.lastMessageAt | date:'short' }}</time></span>
            <span class="unread" *ngIf="item.unreadCount">{{ item.unreadCount }}</span>
          </button>
        </aside>
        <article class="thread-panel">
          <ng-container *ngIf="selectedUserId(); else selectPrompt">
            <header class="thread-header"><div><h3>{{ selectedName() }}</h3><small *ngIf="contextLabel()">Context: {{ contextLabel() }}</small></div><span class="secure-label">JWT scoped</span></header>
            <div class="thread" *ngIf="!loadingThread(); else loading"><p class="empty-state compact" *ngIf="!messages().length">No messages in this conversation yet. Send the first message below.</p><article *ngFor="let item of messages()" class="bubble" [class.own]="item.senderId === currentUserId"><p>{{ item.content }}</p><footer><span>{{ item.createdAt | date:'short' }}</span><span *ngIf="item.senderId === currentUserId && item.isRead">Seen</span></footer></article></div>
            <ng-template #loading><div class="thread-loading">Loading conversation…</div></ng-template>
            <form class="composer" (ngSubmit)="send()"><label class="visually-hidden" for="message-content">Message</label><textarea id="message-content" class="form-control" name="content" [(ngModel)]="draft" placeholder="Write a message…" required [disabled]="sending()"></textarea><button class="btn btn-primary" type="submit" [disabled]="sending() || !draft.trim()">{{ sending() ? 'Sending…' : 'Send' }}</button></form>
          </ng-container>
          <ng-template #selectPrompt><div class="select-prompt"><h3>Select a conversation</h3><p>Choose a previous conversation or use a contextual “Message” action from a vendor, purchase order, or contract.</p></div></ng-template>
        </article>
      </div>
    </section>`,
  styles: [`
    .messages-page{color:var(--vr-navy)} .workspace{display:grid;grid-template-columns:minmax(260px,320px) minmax(0,1fr);min-height:620px;border:1px solid var(--vr-border);border-radius:18px;background:#fff;overflow:hidden;box-shadow:0 12px 28px rgba(15,23,42,.06)}
    .conversation-list{background:#fff7f8;border-right:1px solid var(--vr-border);padding:.9rem;overflow:auto}.list-heading,.thread-header{display:flex;align-items:center;justify-content:space-between;gap:.75rem}.list-heading h3,.thread-header h3{margin:0;font-size:1.05rem}.icon-button{display:grid;place-items:center;border:1px solid #fecdd3;border-radius:9px;width:34px;height:34px;background:#fff;color:var(--vr-primary)}
    .conversation{display:flex;width:100%;align-items:flex-start;gap:.65rem;padding:.75rem;margin-top:.6rem;border:1px solid transparent;border-radius:13px;background:transparent;text-align:left}.conversation:hover,.conversation.selected{background:#fff;border-color:#fecdd3;box-shadow:0 3px 10px rgba(225,29,72,.05)}.avatar{display:grid;place-items:center;width:34px;height:34px;flex:0 0 34px;border-radius:50%;background:#ffe4e6;color:#9f1239;font-weight:800}.conversation-copy{display:grid;min-width:0;flex:1;gap:.15rem}.conversation-copy strong,.conversation-copy small{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.conversation-copy small,time{color:var(--vr-muted);font-size:.76rem}.unread{display:grid;place-items:center;min-width:22px;height:22px;padding:0 .3rem;border-radius:99px;background:var(--vr-primary);color:#fff;font-size:.72rem;font-weight:800}.compact{padding:1rem;font-size:.85rem}
    .thread-panel{display:flex;min-width:0;flex-direction:column;background:#fffafb}.thread-header{padding:1rem 1.2rem;border-bottom:1px solid var(--vr-border)}.secure-label{border-radius:99px;padding:.28rem .55rem;background:#ecfdf5;color:#166534;font-size:.72rem;font-weight:700}.thread{flex:1;min-height:410px;padding:1.15rem;overflow:auto;background:linear-gradient(135deg,#fff7f8,#fff)}.bubble{max-width:min(78%,620px);margin:.55rem 0;padding:.72rem .85rem;border:1px solid #fee2e2;border-radius:14px 14px 14px 3px;background:#fff;box-shadow:0 2px 8px rgba(31,41,55,.04)}.bubble.own{margin-left:auto;border-color:#fecdd3;border-radius:14px 14px 3px 14px;background:#fff1f2}.bubble p{margin:0;white-space:pre-wrap}.bubble footer{display:flex;justify-content:flex-end;gap:.5rem;margin-top:.35rem;color:var(--vr-muted);font-size:.7rem}.composer{display:grid;grid-template-columns:1fr auto;gap:.65rem;padding:1rem;border-top:1px solid var(--vr-border);background:#fff}.composer textarea{min-height:52px;resize:vertical}.thread-loading,.select-prompt{display:grid;place-content:center;flex:1;min-height:450px;padding:2rem;text-align:center;color:var(--vr-muted)}.select-prompt h3{color:var(--vr-navy)}
    @media(max-width:760px){.workspace{grid-template-columns:1fr}.conversation-list{max-height:270px;border-right:0;border-bottom:1px solid var(--vr-border)}.thread{min-height:320px}.composer{grid-template-columns:1fr}.composer .btn{width:100%}}
  `]
})
export class MessagesComponent implements OnInit, OnDestroy {
  private readonly api = inject(DirectMessageService); private readonly route = inject(ActivatedRoute); private readonly router = inject(Router); private readonly auth = inject(AuthService);
  readonly conversations = signal<ConversationSummary[]>([]); readonly messages = signal<DirectMessage[]>([]); readonly selectedUserId = signal<number | null>(null); readonly selectedName = signal('Conversation'); readonly errorMessage = signal(''); readonly loadingConversations = signal(false); readonly loadingThread = signal(false); readonly sending = signal(false); readonly context = signal<MessageContext>({});
  draft = ''; private routeSubscription?: ReturnType<ActivatedRoute['paramMap']['subscribe']>;
  get currentUserId(): number { return this.auth.getStoredUser()?.id ?? 0; }
  ngOnInit(): void { this.loadConversations(); this.routeSubscription = this.route.paramMap.subscribe((params) => { const id = Number(params.get('userId')); if (Number.isInteger(id) && id > 0) { this.context.set(this.readContext()); this.openConversation(id); } }); }
  ngOnDestroy(): void { this.routeSubscription?.unsubscribe(); }
  contextLabel(): string | null { const context = this.context(); return context.relatedEntityType && context.relatedEntityId ? `${context.relatedEntityType.replace('_',' ')} #${context.relatedEntityId}` : null; }
  loadConversations(): void { this.loadingConversations.set(true); this.api.listConversations(50).subscribe({next:(items)=>{this.conversations.set(items);this.loadingConversations.set(false);},error:(error)=>{this.errorMessage.set(this.error(error,'Unable to load conversations.'));this.loadingConversations.set(false);}}); }
  openConversation(userId: number): void { const current = this.conversations().find((item) => item.counterpartUserId === userId); this.selectedUserId.set(userId); this.selectedName.set(current?.counterpartName || current?.counterpartEmail || `User #${userId}`); this.loadThread(); if (this.route.snapshot.paramMap.get('userId') !== String(userId)) this.router.navigate(['/messages', userId], { queryParams: this.queryContext() }); }
  send(): void { const receiverId = this.selectedUserId(); if (!receiverId || !this.draft.trim() || this.sending()) return; this.sending.set(true); const context=this.context(); this.api.send({receiverId,content:this.draft.trim(),relatedEntityType:context.relatedEntityType,relatedEntityId:context.relatedEntityId}).subscribe({next:(message)=>{this.messages.update((items)=>[...items,message]);this.draft='';this.sending.set(false);this.loadConversations();},error:(error)=>{this.errorMessage.set(this.error(error,'Unable to send the message.'));this.sending.set(false);}}); }
  private loadThread(): void { const userId=this.selectedUserId(); if(!userId)return; this.loadingThread.set(true); this.errorMessage.set(''); this.api.getConversation(userId,this.context()).subscribe({next:(items)=>{this.messages.set(items);this.loadingThread.set(false);items.filter((message)=>message.receiverId===this.currentUserId&&!message.isRead).forEach((message)=>this.api.markRead(message.id).subscribe());this.loadConversations();},error:(error)=>{this.errorMessage.set(this.error(error,'Unable to load this conversation.'));this.loadingThread.set(false);}}); }
  private readContext(): MessageContext { const q=this.route.snapshot.queryParamMap; const type=q.get('relatedEntityType') as RelatedEntityType | null; const id=Number(q.get('relatedEntityId')); return type && type !== 'none' && Number.isInteger(id) && id>0 ? {relatedEntityType:type,relatedEntityId:id} : {}; }
  private queryContext(): Record<string,string|number> { const context=this.context(); return context.relatedEntityType&&context.relatedEntityId ? {relatedEntityType:context.relatedEntityType,relatedEntityId:context.relatedEntityId} : {}; }
  private error(error: unknown, fallback: string): string { const detail=typeof error==='object'&&error!==null&&'error' in error?(error as {error?:{detail?:unknown}}).error?.detail:null; return typeof detail==='string'?detail:fallback; }
}
