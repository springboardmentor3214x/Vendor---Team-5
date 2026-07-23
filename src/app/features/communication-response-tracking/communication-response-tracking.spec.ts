import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CommunicationResponseTracking } from './communication-response-tracking';

describe('CommunicationResponseTracking', () => {
  let component: CommunicationResponseTracking;
  let fixture: ComponentFixture<CommunicationResponseTracking>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CommunicationResponseTracking],
    }).compileComponents();

    fixture = TestBed.createComponent(CommunicationResponseTracking);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
