import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { DirectMessageService } from './direct-message.service';

describe('DirectMessageService', () => {
  let service: DirectMessageService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting()] });
    service = TestBed.inject(DirectMessageService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('maps conversation summaries returned by the direct-message API', () => {
    service.listConversations().subscribe((items) => {
      expect(items).toEqual([jasmine.objectContaining({ counterpartUserId: 12, counterpartName: 'Vendor User', unreadCount: 2 })]);
    });

    const request = http.expectOne((candidate) => candidate.url.endsWith('/messages/conversations'));
    expect(request.request.params.get('limit')).toBe('50');
    request.flush([{ counterpart_user_id: 12, counterpart_name: 'Vendor User', counterpart_email: 'vendor@example.test', last_message_content: 'Please confirm delivery', unread_count: 2 }]);
  });

  it('sends only the recipient and message payload supplied by the user', () => {
    service.send({ receiverId: 12, content: 'Confirmed', relatedEntityType: 'purchase_order', relatedEntityId: 5 }).subscribe((message) => expect(message.senderId).toBe(3));

    const request = http.expectOne((candidate) => candidate.url.endsWith('/messages'));
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({ receiverId: 12, content: 'Confirmed', relatedEntityType: 'purchase_order', relatedEntityId: 5 });
    request.flush({ id: 4, sender_id: 3, receiver_id: 12, content: 'Confirmed', related_entity_type: 'purchase_order', related_entity_id: 5, is_read: false });
  });
});
