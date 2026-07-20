import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ServiceRating } from './service-rating';

describe('ServiceRating', () => {
  let component: ServiceRating;
  let fixture: ComponentFixture<ServiceRating>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ServiceRating],
    }).compileComponents();

    fixture = TestBed.createComponent(ServiceRating);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
