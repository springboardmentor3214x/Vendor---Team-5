import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { NotificationService } from './notification.service';

describe('NotificationService', () => {
  let service: NotificationService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting()] });
    service = TestBed.inject(NotificationService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('sends selected history filters and maps the unread badge count', () => {
    service.list({ module: 'contract', priority: 'high', isRead: false }).subscribe((result) => {
      expect(result.unreadCount).toBe(1);
      expect(result.items[0]).toEqual(jasmine.objectContaining({ id: 8, isRead: false, relatedModule: 'contract' }));
    });

    const request = http.expectOne((candidate) => candidate.url.endsWith('/notifications/'));
    expect(request.request.params.get('module')).toBe('contract');
    expect(request.request.params.get('priority')).toBe('high');
    expect(request.request.params.get('isRead')).toBe('false');
    request.flush({ items: [{ id: 8, title: 'Contract expires soon', message: 'Action required', priority: 'high', related_module: 'contract', is_read: false }], total: 1, unread_count: 1 });
  });
});
